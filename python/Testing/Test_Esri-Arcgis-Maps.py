#Importing modules
import json
import requests
import os
import polyline as poly

#API key for Esri-Arcgis-Maps
Token_Esri=os.environ.get('Esri-Arcgis-Maps_API_Key')
#API key for Tollguru
Tolls_Key = os.environ.get('TollGuru_API_Key')


'''Fetching Geocodes from Esri-Arcgis-Maps'''
def get_geocodes_from_arcgis(address): 
    url="https://geocode.arcgis.com/arcgis/rest/services/World/GeocodeServer/findAddressCandidates" 
    para={'f': 'json' , 'singleLine' : address , 'outFields' : 'Match_addr,Addr_type'}
    longitude,latitude=requests.get(url,params=para).json()['candidates'][0]['location'].values()
    return(longitude,latitude)     #note it returns long lat

'''Fetching Polyline from Esri-Arcgis-Maps'''
def get_polyline_from_arcgis(source_longitude,source_latitude,destination_longitude,destination_latitude):
    #url to post request
    arcgis_url = "https://route.arcgis.com/arcgis/rest/services/World/Route/NAServer/Route_World/solve"
    #prepare payload in similar structure and update feature coordinates 
    payload = {
        "type":"features",
        "features":  [
            {
                "geometry": {                #source coordinates
                             "x": source_longitude,
                             "y": source_latitude,
                             }
                },
            {
                "geometry": {               #destination coordinates
                             "x": destination_longitude, 
                             "y": destination_latitude
                             }
                }
            ]
        }
    #response file after post to the given link using payload as value for stop and providing other parameters
    response_from_arcgis=requests.post(arcgis_url,data = {'f': 'json','token': Token_Esri,'stops':json.dumps(payload)},timeout=200).json()
    #making a list for all coordinates to make polyline NOTE ARCGIS provides lon-lat pairs but we need lat-lon pairs
    coordinate_list=[i[::-1] for i in response_from_arcgis['routes']['features'][0]['geometry']['paths'][0]]
    #Encoding coordinate lists into polyline
    polyline_from_arcgis=poly.encode(coordinate_list)
    return(polyline_from_arcgis)
    
    

'''Calling Tollguru API'''
def get_rates_from_tollguru(polyline):
    #Tollguru querry url
    Tolls_URL = 'https://dev.tollguru.com/v1/calc/route'
    
    #Tollguru resquest parameters
    headers = {
                'Content-type': 'application/json',
                'x-api-key': Tolls_Key
                }
    params = {
                #Explore https://tollguru.com/developers/docs/ to get best of all the parameter that tollguru has to offer 
                'source': "esri",
                'polyline': polyline ,                      # this is the encoded polyline that we made     
                'vehicleType': '2AxlesAuto',                #'''Visit https://tollguru.com/developers/docs/#vehicle-types to know more options'''
                'departure_time' : "2021-01-05T09:46:08Z"   #'''Visit https://en.wikipedia.org/wiki/Unix_time to know the time format'''
                }
    #Requesting Tollguru with parameters
    response_tollguru= requests.post(Tolls_URL, json=params, headers=headers).json()
    #checking for errors or printing rates
    if str(response_tollguru).find('message')==-1:
        return(response_tollguru['route']['costs'])
    else:
        raise Exception(response_tollguru['message'])
                
'''Testing'''
#Importing Functions
from csv import reader,writer
import time
temp_list=[]
with open('testCases.csv','r') as f:
    csv_reader=reader(f)
    for count,i in enumerate(csv_reader):
        #if count>2:
        #   break
        if count==0:
            i.extend(("Input_polyline","Tollguru_Tag_Cost","Tollguru_Cash_Cost","Tollguru_QueryTime_In_Sec"))
        else:
            try:
                source_longitude,source_latitude=get_geocodes_from_arcgis(i[1])
                destination_longitude,destination_latitude=get_geocodes_from_arcgis(i[2])
                polyline=get_polyline_from_arcgis(source_longitude,source_latitude,destination_longitude,destination_latitude)
                i.append(polyline)
            except:
                i.append("Routing Error") 
            
            start=time.time()
            try:
                rates=get_rates_from_tollguru(polyline)
            except:
                i.append(False)
            time_taken=(time.time()-start)
            if rates=={}:
                i.append((None,None))
            else:
                try:
                    tag=rates['tag']
                except:
                    tag=None
                try:
                    cash=rates['cash']
                except :
                    cash=None
                i.extend((tag,cash))
            i.append(time_taken)
        #print(f"{len(i)}   {i}\n")
        temp_list.append(i)

with open('testCases_result.csv','w') as f:
    writer(f).writerows(temp_list)

'''Testing Ends'''

#Importing modules
import json
import requests
import os
import polyline as poly

'''Fetching Polyline from Esri-Arcgis-Maps'''

#API key for Esri-Arcgis-Maps
token_Esri=os.environ.get('Esri-Arcgis-Maps_API_Key')

#url to post request
arcgis_url = "https://route.arcgis.com/arcgis/rest/services/World/Route/NAServer/Route_World/solve"

#prepare payload in similar structure and update feature coordinates 
payload = {
  "type":"features",
  "features":  [
    {
      "geometry": {                #source coordinates
        "x": -96.7970,
        "y": 32.7767
      }
    },
    {
      "geometry": {               #destination coordinates
        "x": -74.0060, 
        "y": 40.7128
      }
    }
  ]
}

#response file after post to the given link using payload as value for stop and providing other parameters
response_from_arcgis=requests.post(arcgis_url,data = {'f': 'json','token': token_Esri,'stops':json.dumps(payload)}).json()

#making a list for all coordinates to make polyline NOTE ARCGIS provides lon-lat pairs but we need lat-lon pairs
coordinate_list=[i[::-1] for i in response_from_arcgis['routes']['features'][0]['geometry']['paths'][0]]

##Encoding coordinate lists into polyline
polyline_from_Arcgis=poly.encode(coordinate_list)




'''Calling Tollguru API'''

#API key for Tollguru
Tolls_Key = os.environ.get('TollGuru_API_Key')

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
            'polyline': polyline_from_Arcgis ,          # this is the encoded polyline that we made     
            'vehicleType': '2AxlesAuto',                #'''Visit https://tollguru.com/developers/docs/#vehicle-types to know more options'''
            'departure_time' : "2021-01-05T09:46:08Z"   #'''Visit https://en.wikipedia.org/wiki/Unix_time to know the time format'''
        }

#Requesting Tollguru with parameters
response_tollguru= requests.post(Tolls_URL, json=params, headers=headers).json()

#checking for errors or printing rates
if str(response_tollguru).find('message')==-1:
    print('\n The Rates Are ')
    #extracting rates from Tollguru response is no error
    print(*response_tollguru['route']['costs'].items(),end="\n\n")
else:
    raise Exception(response_tollguru['message'])
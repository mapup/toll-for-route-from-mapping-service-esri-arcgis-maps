# Importing modules
import json
import requests
import os
import polyline as poly

ESRI_ARCGIS_API_KEY = os.environ.get("ESRI_ARCGIS_API_KEY")
ESRI_ARCGIS_API_URL = "https://route.arcgis.com/arcgis/rest/services/World/Route/NAServer/Route_World/solve"
ESRI_ARCGIS_GEOCODE_API_URL = "https://geocode.arcgis.com/arcgis/rest/services/World/GeocodeServer/findAddressCandidates"

TOLLGURU_API_KEY = os.environ.get("TOLLGURU_API_KEY")
TOLLGURU_API_URL = "https://apis.tollguru.com/toll/v2"
POLYLINE_ENDPOINT = "complete-polyline-from-mapping-service"

source = "Philadelphia, PA"
destination = "New York, NY"

# Explore https://tollguru.com/toll-api-docs to get best of all the parameter that tollguru has to offer
request_parameters = {
    "vehicle": {
        "type": "2AxlesAuto",
    },
    # Visit https://en.wikipedia.org/wiki/Unix_time to know the time format
    "departure_time": "2021-01-05T09:46:08Z",
}


def get_geocodes_from_arcgis(address):
    """Fetching Geocodes from Esri-Arcgis-Maps"""

    params = {
        "f": "json",
        "singleLine": address,
        "outFields": "Match_addr,Addr_type",
    }
    longitude, latitude = (
        requests.get(ESRI_ARCGIS_GEOCODE_API_URL, params=params)
        .json()["candidates"][0]["location"]
        .values()
    )
    return (longitude, latitude)  # note it returns long lat


def get_polyline_from_arcgis(
    source_longitude, source_latitude, destination_longitude, destination_latitude
):
    """Fetching Polyline from Esri-Arcgis-Maps"""

    # prepare payload in similar structure and update feature coordinates
    payload = {
        "type": "features",
        "features": [
            {
                "geometry": {  # source coordinates
                    "x": source_longitude,
                    "y": source_latitude,
                }
            },
            {
                "geometry": {  # destination coordinates
                    "x": destination_longitude,
                    "y": destination_latitude,
                }
            },
        ],
    }
    # response file after post to the given link using payload as value for stop and providing other parameters
    response_from_arcgis = requests.post(
        ESRI_ARCGIS_API_URL,
        data={"f": "json", "token": ESRI_ARCGIS_API_KEY, "stops": json.dumps(payload)},
        timeout=200,
    ).json()
    # making a list for all coordinates to make polyline NOTE ARCGIS provides lon-lat pairs but we need lat-lon pairs
    coordinate_list = [
        i[::-1]
        for i in response_from_arcgis["routes"]["features"][0]["geometry"]["paths"][0]
    ]
    # Encoding coordinate lists into polyline
    polyline_from_arcgis = poly.encode(coordinate_list)
    return polyline_from_arcgis


"""Calling Tollguru API"""


def get_rates_from_tollguru(polyline):
    # Tollguru querry url
    # Tollguru resquest parameters
    headers = {"Content-type": "application/json", "x-api-key": TOLLGURU_API_KEY}
    params = {
        **request_parameters,
        "source": "esri",
        "polyline": polyline,  # this is the encoded polyline that we made
    }
    # Requesting Tollguru with parameters
    response_tollguru = requests.post(
        f"{TOLLGURU_API_URL}/{POLYLINE_ENDPOINT}", json=params, headers=headers
    ).json()
    # checking for errors or printing rates
    if str(response_tollguru).find("message") == -1:
        return response_tollguru["route"]["costs"]
    else:
        raise Exception(response_tollguru["message"])


"""Program Starts"""
# Step 1 :Getting Geocodes from Arcgis for Source and Destination
source_longitude, source_latitude = get_geocodes_from_arcgis(source)
destination_longitude, destination_latitude = get_geocodes_from_arcgis(destination)

# Step 2 : Get Polyline from Arcgis
polyline_from_arcgis = get_polyline_from_arcgis(
    source_longitude, source_latitude, destination_longitude, destination_latitude
)

# Step 3 : Get rates from Tollguru
rates_from_tollguru = get_rates_from_tollguru(polyline_from_arcgis)

# Print the rates of all the available modes of payment
if rates_from_tollguru == {}:
    print("The route doesn't have tolls")
else:
    print(f"The rates are \n {rates_from_tollguru}")

"""Program Ends"""

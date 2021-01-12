require 'HTTParty'
require 'json'
require "fast_polylines"
require 'uri'

# Source Details Hash - X >> Longitude and y >> Latitude
SOURCE = { "x" => -96.7970, "y" => 32.7767 }
# Destination Details Hash - X >> Longitude and y >> Latitude
DESTINATION = { "x" => -74.0060, "y" => 40.7128 }

# POST Request to ARCGIS for Coordinate Pairs
KEY = ENV['ARCGIS_KEY']
ARCGIS_URL = "https://route.arcgis.com/arcgis/rest/services/World/Route/NAServer/Route_World/solve"
arcgis_headers = {'content-type' => 'application/x-www-form-urlencoded'}
arcgis_body = {
    'f'=> "json",'token'=> KEY,                       
    'stops' => {"type" => "features", "features" =>  [{ "geometry" => SOURCE},
                                                      { "geometry" => DESTINATION}] }}

RESPONSE = HTTParty.post(ARCGIS_URL,:body => URI.encode_www_form(arcgis_body),:headers => arcgis_headers).body
json_parsed = JSON.parse(RESPONSE)

# Extracting coordinates polyline from JSON. HERE coordinates are encoded to google polyline after flipping
arcgis_coordinates_array = (json_parsed['routes']['features'].map {|x| x['geometry']}.pop)['paths'].pop
arcgis_coordinates_flipped = arcgis_coordinates_array.map {|x,y| [y,x]}
google_encoded_polyline = FastPolylines.encode(arcgis_coordinates_flipped)

# Sending POST request to TollGuru
TOLLGURU_URL = 'https://dev.tollguru.com/v1/calc/route'
TOLLGURU_KEY = ENV['TOLLGURU_KEY']
headers = {'content-type' => 'application/json', 'x-api-key' => TOLLGURU_KEY}
body = {'source' => "esri", 'polyline' => google_encoded_polyline, 'vehicleType' => "2AxlesAuto", 'departure_time' => "2021-01-05T09:46:08Z"}
tollguru_response = HTTParty.post(TOLLGURU_URL,:body => body.to_json, :headers => headers)
require 'HTTParty'
require 'json'
require "fast_polylines"
require 'uri'
require 'cgi'

ESRI_ARCGIS_API_KEY = ENV['ESRI_ARCGIS_API_KEY']
ESRI_ARCGIS_API_URL = 'https://route.arcgis.com/arcgis/rest/services/World/Route/NAServer/Route_World/solve';
ESRI_ARCGIS_GEOCODE_API_URL = "https://geocode.arcgis.com/arcgis/rest/services/World/GeocodeServer/findAddressCandidates"

TOLLGURU_API_KEY = ENV['TOLLGURU_API_KEY'] # API key for Tollguru
TOLLGURU_API_URL = 'https//api.tollguru.com/toll/v2' # Base URL for TollGuru Toll API
POLYLINE_ENDPOINT = 'complete-polyline-from-mapping-service'

source = 'Philadelphia, PA'
destination = 'New York, NY'

# Explore https://tollguru.com/toll-api-docs to get the best of all the parameters that tollguru has to offer
request_parameters = {
  "vehicle": {
    "type": "2AxlesAuto",
  },
  # Visit https://en.wikipedia.org/wiki/Unix_time to know the time format
  "departure_time": "2021-01-05T09:46:08Z",
}

# Using Geocode API to get latitude-longitude values
def get_coord_hash(loc)
    params = {"f"=> "json",'singleLine' => CGI::escape(loc), 'maxlocations' => 1}
    geocoding_url = ESRI_ARCGIS_GEOCODE_API_URL
    coord = JSON.parse(HTTParty.post(geocoding_url,:body => URI.encode_www_form(params)).body)
    return  coord['candidates'].pop['location']
end

# POST Request to ARCGIS for Coordinate Pairs
arcgis_headers = {'content-type' => 'application/x-www-form-urlencoded'}
arcgis_body = {
    'f'=> "json",'token'=> ESRI_ARCGIS_API_KEY,                       
    'stops' => {"type" => "features", "features" =>  [{ "geometry" => source},
                                                      { "geometry" => destination}] }}

RESPONSE = HTTParty.post(ESRI_ARCGIS_API_URL,:body => URI.encode_www_form(arcgis_body),:headers => arcgis_headers).body
json_parsed = JSON.parse(RESPONSE)

# Extracting coordinates polyline from JSON. Coordinates are encoded to google polyline after flipping
arcgis_coordinates_array = (json_parsed['routes']['features'].map {|x| x['geometry']}.pop)['paths'].pop
arcgis_coordinates_flipped = arcgis_coordinates_array.map {|x,y| [y,x]}
google_encoded_polyline = FastPolylines.encode(arcgis_coordinates_flipped)

# Sending POST request to TollGuru
headers = {'content-type': 'application/json', 'x-api-key': TOLLGURU_API_KEY}
body = {
  'source': "esri",
  'polyline': google_encoded_polyline,
  **request_parameters,
}
tollguru_response = HTTParty.post("#{TOLLGURU_API_URL}/#{POLYLINE_ENDPOINT}",:body => body.to_json, :headers => headers)

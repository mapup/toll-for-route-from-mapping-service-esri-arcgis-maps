require 'HTTParty'
require 'json'
require "fast_polylines"
require 'uri'
require 'cgi'

def get_toll_rate(source,destination)
    # Using Geocode API to get latitude-longitude values
    def get_coord_hash(loc)
        params = {"f"=> "json",'singleLine' => CGI::escape(loc), 'maxlocations' => 1}
        geocoding_url = "https://geocode.arcgis.com/arcgis/rest/services/World/GeocodeServer/findAddressCandidates"
        coord = JSON.parse(HTTParty.post(geocoding_url,:body => URI.encode_www_form(params)).body)
        return  coord['candidates'].pop['location']
    end

    # # Source Details Hash - X >> Longitude and y >> Latitude
    source = get_coord_hash(source)
    # # Destination Details Hash - X >> Longitude and y >> Latitude
    destination = get_coord_hash(destination)

    # POST Request to ARCGIS for Coordinate Pairs
    key = ENV['ARCGIS_KEY']
    arcgis_url = "https://route.arcgis.com/arcgis/rest/services/World/Route/NAServer/Route_World/solve"
    arcgis_headers = {'content-type' => 'application/x-www-form-urlencoded'}
    arcgis_body = {
        'f'=> "json",'token'=> key,                       
        'stops' => {"type" => "features", "features" =>  [{ "geometry" => source},
                                                        { "geometry" => destination}] }}

    response = HTTParty.post(arcgis_url,:body => URI.encode_www_form(arcgis_body),:headers => arcgis_headers).body
    json_parsed = JSON.parse(response)

    # Extracting coordinates polyline from JSON. Coordinates are encoded to google polyline after flipping
    arcgis_coordinates_array = (json_parsed['routes']['features'].map {|x| x['geometry']}.pop)['paths'].pop
    arcgis_coordinates_flipped = arcgis_coordinates_array.map {|x,y| [y,x]}
    google_encoded_polyline = FastPolylines.encode(arcgis_coordinates_flipped)

    # Sending POST request to TollGuru
    tollguru_url = 'https://dev.tollguru.com/v1/calc/route'
    tollguru_key = ENV['TOLLGURU_KEY']
    headers = {'content-type' => 'application/json', 'x-api-key' => tollguru_key}
    body = {'source' => "esri", 'polyline' => google_encoded_polyline, 'vehicleType' => "2AxlesAuto", 'departure_time' => "2021-01-05T09:46:08Z"}
    tollguru_response = HTTParty.post(tollguru_url,:body => body.to_json, :headers => headers)
    begin
        toll_body = JSON.parse(tollguru_response.body)    
        if toll_body["route"]["hasTolls"] == true
            return google_encoded_polyline,toll_body["route"]["costs"]["tag"], toll_body["route"]["costs"]["cash"] 
        else
            raise "No tolls encountered in this route"
        end
    rescue Exception => e
        puts e.message 
    end

end
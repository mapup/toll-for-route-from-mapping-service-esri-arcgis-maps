# [ArcGIS For Developer](https://developers.arcgis.com)

### Get token to access ArcGIS APIs (if you have an API key skip this)
#### Step 1: Get API Token
* Create an account to access [ArcGIS For Developer](https://developers.arcgis.com/dashboard)
* go to [signup](https://developers.arcgis.com/sign-up/)
* if you have an account login at https://developers.arcgis.com/sign-in/

#### Step 2: creating a token
* Once logged in you can find a temporary token at [ArcGIS For Developer](https://developers.arcgis.com/dashboard)
* You can also create an application and generate tokens for it.

With this in place, make a POST request: https://route.arcgis.com/arcgis/rest/services/World/Route/NAServer/Route_World/solve
With `content-type: 'application/x-www-form-urlencoded'` and body with
following keys
* Here SOURCE and DESTINATION are hashes with (x,y) pairs containing longitude and latitude coords. Also use `URI.encode_www_form` to convert Hash to form

```
arcgis_headers = {'content-type' => 'application/x-www-form-urlencoded'}
arcgis_body = {
    'f'=> "json",'token'=> KEY,                       
    'stops' => {"type" => "features", "features" =>  [{ "geometry" => SOURCE},
                                                      { "geometry" => DESTINATION}] }}
```

### Note:
You should see full path as series of coordinates. Coordinates must be flipped before converting to
`polyline` using `FastPolylines` gem

```ruby
RESPONSE = HTTParty.post(ARCGIS_URL,:body => URI.encode_www_form(arcgis_body),:headers => arcgis_headers).body
json_parsed = JSON.parse(RESPONSE)

# Extracting coordinates from JSON. HERE coordinates are encoded to google polyline
arcgis_coordinates_array = (json_parsed['routes']['features'].map {|x| x['geometry']}.pop)['paths'].pop
arcgis_coordinates_flipped = arcgis_coordinates_array.map {|x,y| [y,x]}
google_encoded_polyline = FastPolylines.encode(arcgis_coordinates_flipped)

```

Note:

We extracted the polyline for a route from ArcGIS Routing API.

We need to send this route polyline to TollGuru API to receive toll information

## [TollGuru API](https://tollguru.com/developers/docs/)

### Get key to access TollGuru polyline API
* create a dev account to receive a [free key from TollGuru](https://tollguru.com/developers/get-api-key)
* suggest adding `vehicleType` parameter. Tolls for cars are different than trucks and therefore if `vehicleType` is not specified, may not receive accurate tolls. For example, tolls are generally higher for trucks than cars. If `vehicleType` is not specified, by default tolls are returned for 2-axle cars. 
* Similarly, `departure_time` is important for locations where tolls change based on time-of-the-day.

the last line can be changed to following

```ruby
# Sending POST request to TollGuru
TOLLGURU_URL = 'https://dev.tollguru.com/v1/calc/route'
TOLLGURU_KEY = ENV['TOLLGURU_KEY']
headers = {'content-type' => 'application/json', 'x-api-key' => TOLLGURU_KEY}
body = {'source' => "esri", 'polyline' => google_encoded_polyline, 'vehicleType' => "2AxlesAuto", 'departure_time' => "2021-01-05T09:46:08Z"}
tollguru_response = HTTParty.post(TOLLGURU_URL,:body => body.to_json, :headers => headers)

```

The working code can be found in main.rb file.

## License
ISC License (ISC). Copyright 2020 &copy;TollGuru. https://tollguru.com/

Permission to use, copy, modify, and/or distribute this software for any purpose with or without fee is hereby granted, provided that the above copyright notice and this permission notice appear in all copies.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

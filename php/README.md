# [ArcGIS For Developer](https://developers.arcgis.com)

### Get token to access ArcGIS APIs (if you have an API key skip this)
#### Step 1: Get API Token
* Create an account to access [ArcGIS For Developer](https://developers.arcgis.com/dashboard)
* go to [signup](https://developers.arcgis.com/sign-up/)
* if you have an account login at https://developers.arcgis.com/sign-in/

#### Step 2: creating a token
* Once logged in you can find a temporary token at [ArcGIS For Developer](https://developers.arcgis.com/dashboard)
* You can also create an application and generate tokens for it.
* Refer to [Route service with synchronous execution](https://developers.arcgis.com/rest/network/api-reference/route-synchronous-service.htm) to get an in depth idea of various post request 
  parameters.
  
#### Step 3: Getting Geocodes for Source and Destination from ArcGIS
* Use the following code to call ArcGIS API to fetch the geocode of the locations
```php

function getCord($address){
$esri = curl_init();
curl_setopt_array($esri, array(
  CURLOPT_URL => 'https://geocode.arcgis.com/arcgis/rest/services/World/GeocodeServer/findAddressCandidates',
  CURLOPT_RETURNTRANSFER => true,
  CURLOPT_ENCODING => '',
  CURLOPT_MAXREDIRS => 10,
  CURLOPT_TIMEOUT => 0,
  CURLOPT_FOLLOWLOCATION => true,
  CURLOPT_HTTP_VERSION => CURL_HTTP_VERSION_1_1,
  CURLOPT_CUSTOMREQUEST => 'POST',
  CURLOPT_HTTPHEADER => array(
  	'content-type' => 'application/x-www-form-urlencoded'),
  CURLOPT_POSTFIELDS => array(
    'f' => 'json',
	'singleLine' => $address,
	'outFields' => 'Match_addr,Addr_type')
));

$responseJson = curl_exec($esri);
curl_close($esri);

$response = json_decode($responseJson, true);

$location = array(
	'x' => $response['candidates']['0']['location']['y'],
  'y' => $response['candidates']['0']['location']['x']
);

return $location;
}

```
With this in place, make a POST request: https://route.arcgis.com/arcgis/rest/services/World/Route/NAServer/Route_World/solve

#### Step 4: Extracting polyline from ArcGIS using Source-Destination Geocodes

With `$stop variable` with following keys

```php

//connecting to esri...
$esri = curl_init();

$stop = '{
  "type":"features",
  "features":  [
    {
      "geometry": {
        "x": -96.7970,
        "y": 32.7767
      }
    },
    {
      "geometry": {
        "x": -74.0060, 
        "y": 40.7128
      }
    }
  ]
}';

curl_setopt_array($esri, array(
  CURLOPT_URL => 'https://route.arcgis.com/arcgis/rest/services/World/Route/NAServer/Route_World/solve',
  CURLOPT_RETURNTRANSFER => true,
  CURLOPT_ENCODING => '',
  CURLOPT_MAXREDIRS => 10,
  CURLOPT_TIMEOUT => 0,
  CURLOPT_FOLLOWLOCATION => true,
  CURLOPT_HTTP_VERSION => CURL_HTTP_VERSION_1_1,
  CURLOPT_CUSTOMREQUEST => 'POST',
  CURLOPT_HTTPHEADER => array(
  	'content-type' => 'application/x-www-form-urlencoded'),
  CURLOPT_POSTFIELDS => array(
    'f' => 'json',
    'token' => 'esri_arcgis_token',
    'stops' => $stop)
));

$response = curl_exec($esri);
$err = curl_error($esri);

curl_close($esri);

if ($err) {
    echo "cURL Error #:" . $err;
} else {
    echo "200 : OK\n";
}

$data = json_decode($response, true);

$points = $data['routes']['features']['0']['geometry']['paths']['0'];


```

### Note:
* You should see full path as series of coordinates which we are storing in `$points`, we convert it to
`polyline`
* Code to get the `polyline` can be found at https://github.com/emcconville/google-map-polyline-encoding-tool


```php

$revPoints = array();
foreach ($points as $i) {
  array_push($revPoints, $i['1']);
  array_push($revPoints, $i['0']);
}
//creating polyline...
require_once(__DIR__.'/Polyline.php');
$polyline = Polyline::encode($revPoints);

```

Note:

We extracted the polyline for a route from ArcGIS Routing API.

We need to send this route polyline to TollGuru API to receive toll information

## [TollGuru API](https://tollguru.com/developers/docs/)

### Get key to access TollGuru polyline API
* create a dev account to receive a [free key from TollGuru](https://tollguru.com/developers/get-api-key)
* suggest adding `vehicleType` parameter. Tolls for cars are different than trucks and therefore if `vehicleType` is not specified, may not receive accurate tolls. For example, tolls are generally higher for trucks than cars. If `vehicleType` is not specified, by default tolls are returned for 2-axle cars. 
* Similarly, `departure_time` is important for locations where tolls change based on time-of-the-day.
* Use the following code to get rates from TollGuru.

```php

//using tollguru API..
$curl = curl_init();

curl_setopt($curl, CURLOPT_SSL_VERIFYHOST, false);
curl_setopt($curl, CURLOPT_SSL_VERIFYPEER, false);


$postdata = array(
  "source" => "gmaps",
  "polyline" => $polyline
);

//json encoding source and polyline to send as postfields...
$encode_postData = json_encode($postdata);

curl_setopt_array($curl, array(
CURLOPT_URL => "https://dev.tollguru.com/v1/calc/route",
CURLOPT_RETURNTRANSFER => true,
CURLOPT_ENCODING => "",
CURLOPT_MAXREDIRS => 10,
CURLOPT_TIMEOUT => 300,
CURLOPT_HTTP_VERSION => CURL_HTTP_VERSION_1_1,
CURLOPT_CUSTOMREQUEST => "POST",

//sending ptv polyline to tollguru..
CURLOPT_POSTFIELDS => $encode_postData,
CURLOPT_HTTPHEADER => array(
              "content-type: application/json",
              "x-api-key: tollguru_api_key"),
));

$response = curl_exec($curl);
$err = curl_error($curl);

curl_close($curl);
$err = curl_error($curl);
if ($err) {
    echo "cURL Error #:" . $err;
} else {
    echo "200 : OK\n";
}

//response from tollguru..
$data = json_decode($response, true);
print_r($data['route']['costs']);

```

The working code can be found in `php_curl_esri.php` file.

## License
ISC License (ISC). Copyright 2020 &copy;TollGuru. https://tollguru.com/

Permission to use, copy, modify, and/or distribute this software for any purpose with or without fee is hereby granted, provided that the above copyright notice and this permission notice appear in all copies.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

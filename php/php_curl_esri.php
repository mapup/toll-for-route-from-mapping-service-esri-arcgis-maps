<?php

$ESRI_ARCGIS_API_KEY = getenv('ESRI_ARCGIS_API_KEY');
$ESRI_ARCGIS_API_URL = 'https://route.arcgis.com/arcgis/rest/services/World/Route/NAServer/Route_World/solve';

$TOLLGURU_API_KEY = getenv('TOLLGURU_API_KEY');
$TOLLGURU_API_URL = 'https://apis.tollguru.com/toll/v2';
$POLYLINE_ENDPOINT = 'complete-polyline-from-mapping-service';

$source = array('x' => -75.16218, 'y' => 39.95222); // Philadelphia, PA
$destination = array('x' => -74.0060, 'y' => 40.7128); // New York, NY

// Explore https://tollguru.com/toll-api-docs to get the best of all the parameters that tollguru has to offer
$request_parameters = array(
    "vehicle" => array(
        "type" => "2AxlesAuto",
    ),
    // Visit https://en.wikipedia.org/wiki/Unix_time to know the time format
    "departure_time" => "2021-01-05T09:46:08Z",
);

//connecting to esri...
$esri = curl_init();

$stop = '{
  "type":"features",
  "features":  [
    { "geometry": ' . json_encode($source) . ' },
    { "geometry": ' . json_encode($destination) . ' }
  ]
}';

curl_setopt_array($esri, array(
  CURLOPT_URL => $ESRI_ARCGIS_API_URL,
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
    'token' => $ESRI_ARCGIS_API_KEY,
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

$revPoints = array();
foreach ($points as $i) {
  array_push($revPoints, $i['1']);
  array_push($revPoints, $i['0']);
}
// Creating polyline...
require_once(__DIR__.'/Polyline.php');
$polyline = Polyline::encode($revPoints);


// Using TollGuru API
$curl = curl_init();

curl_setopt($curl, CURLOPT_SSL_VERIFYHOST, false);
curl_setopt($curl, CURLOPT_SSL_VERIFYPEER, false);

$postdata = array(
  "source" => "esri",
  "polyline" => $polyline,
  ...$request_parameters,
);

// JSON encoded source and polyline to send as postfields
$encode_postData = json_encode($postdata);

curl_setopt_array($curl, array(
  CURLOPT_URL => $TOLLGURU_API_URL . "/" . $POLYLINE_ENDPOINT,
  CURLOPT_RETURNTRANSFER => true,
  CURLOPT_ENCODING => "",
  CURLOPT_MAXREDIRS => 10,
  CURLOPT_TIMEOUT => 300,
  CURLOPT_HTTP_VERSION => CURL_HTTP_VERSION_1_1,
  CURLOPT_CUSTOMREQUEST => "POST",
  CURLOPT_POSTFIELDS => $encode_postData,
  CURLOPT_HTTPHEADER => array(
    "content-type: application/json",
    "x-api-key: ".$TOLLGURU_API_KEY),
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

// Response from TollGuru
$data = json_decode($response, true);
print_r($data['route']['costs']);
?>

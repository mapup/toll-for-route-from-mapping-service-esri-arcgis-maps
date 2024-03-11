<?php

$ESRI_ARCGIS_API_KEY = getenv('ESRI_ARCGIS_API_KEY');
$ESRI_ARCGIS_API_URL = 'https://route.arcgis.com/arcgis/rest/services/World/Route/NAServer/Route_World/solve';

$TOLLGURU_API_KEY = getenv('TOLLGURU_API_KEY');
$TOLLGURU_API_URL = 'https://apis.tollguru.com/toll/v2';
$POLYLINE_ENDPOINT = 'complete-polyline-from-mapping-service';

// Explore https://tollguru.com/toll-api-docs to get the best of all the parameters that tollguru has to offer
$request_parameters = array(
  "vehicle" => array(
    "type" => "2AxlesAuto",
  ),
  // Visit https://en.wikipedia.org/wiki/Unix_time to know the time format
  "departure_time" => "2021-01-05T09:46:08Z",
);

//calling helper files...
require_once(__DIR__.'/test_location.php');
require_once(__DIR__.'/get_lat_long.php');
foreach ($locdata as $item) {
  echo "QUERY: {FROM: ".$item['from'].'}{TO: '.$item['to'].'}';
  echo "\n";
  $source = getCord($item['from']);
  $source_longitude = $source['y'];
  $source_latitude = $source['x'];
  $destination = getCord($item['to']);
  $destination_longitude = $destination['y'];
  $destination_latitude = $destination['x'];


  //connecting to esri api...
  $esri = curl_init();

  $stop = '{
    "type":"features",
    "features":  [
    {
    "geometry": {
    "x": '.$source_longitude.',
    "y": '.$source_latitude.'
    }
    },
    {
    "geometry": {
    "x": '.$destination_longitude.',
    "y": '.$destination_latitude.'
    }
    }
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
  //creating polyline...
  require_once(__DIR__.'/Polyline.php');
  $polyline = Polyline::encode($revPoints);


  //using tollguru API...
  $curl = curl_init();

  curl_setopt($curl, CURLOPT_SSL_VERIFYHOST, false);
  curl_setopt($curl, CURLOPT_SSL_VERIFYPEER, false);


  $postdata = array(
    "source" => "esri",
    "polyline" => $polyline,
    ...$request_parameters,
  );

  //json encoding source and polyline to send as postfields...
  $encode_postData = json_encode($postdata);

  curl_setopt_array($curl, array(
    CURLOPT_URL => $TOLLGURU_API_URL . "/" . $POLYLINE_ENDPOINT,
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
      "x-api-key: " . $TOLLGURU_API_KEY),
  ));

  $response = curl_exec($curl);
  $err = curl_error($curl);

  curl_close($curl);

  if ($err) {
    echo "cURL Error #:" . $err;
  } else {
    echo "200 : OK\n";
  }

  //response from tollguru..
  $data = json_decode($response, true);

  $tag = $data['route']['costs']['tag'];
  $cash = $data['route']['costs']['cash'];

  $dumpFile = fopen("dump.txt", "a") or die("unable to open file!");
  fwrite($dumpFile, "from =>");
  fwrite($dumpFile, $item['from'].PHP_EOL);
  fwrite($dumpFile, "to =>");
  fwrite($dumpFile, $item['to'].PHP_EOL);
  fwrite($dumpFile, "polyline =>".PHP_EOL);
  fwrite($dumpFile, $polyline.PHP_EOL);
  fwrite($dumpFile, "tag =>");
  fwrite($dumpFile, $tag.PHP_EOL);
  fwrite($dumpFile, "cash =>");
  fwrite($dumpFile, $cash.PHP_EOL);
  fwrite($dumpFile, "*************************************************************************".PHP_EOL);

  echo "tag = ";
  print_r($data['route']['costs']['tag']);
  echo "\ncash = ";
  print_r($data['route']['costs']['cash']);
  echo "\n";
  echo "**************************************************************************\n";
}
?>

<?php
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
?>


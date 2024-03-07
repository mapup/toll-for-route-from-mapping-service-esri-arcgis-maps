const request = require("request");
const polyline = require("polyline");

const ESRI_ARCGIS_API_KEY = process.env.ESRI_ARCGIS_API_KEY;
const ESRI_ARCGIS_API_URL = 'https://route.arcgis.com/arcgis/rest/services/World/Route/NAServer/Route_World/solve';

const TOLLGURU_API_KEY = process.env.TOLLGURU_API_KEY;
const TOLLGURU_API_URL = 'https://apis.tollguru.com/toll/v2'
const POLYLINE_ENDPOINT = 'complete-polyline-from-mapping-service'

const source = { x: -75.16218, y: 39.95222, }; // Philadelphia, PA
const destination = { x: -74.0060, y: 40.7128 }; // New York, NY

// Explore https://tollguru.com/toll-api-docs to get the best of all the parameters that tollguru has to offer
const requestParameters = {
  "vehicle": {
    "type": "2AxlesAuto",
  },
  // Visit https://en.wikipedia.org/wiki/Unix_time to know the time format
  "departure_time": "2021-01-05T09:46:08Z",
}

const flatten = (arr, x) => arr.concat(x);

// JSON path "$..paths"
const getPoints = body => body.routes.features
  .map(feature => feature.geometry.paths)
  .reduce(flatten)
  .reduce(flatten)
  .map(([x, y]) => [y, x])

const getPolyline = body => polyline.encode(getPoints(JSON.parse(body)));

const payload = {
  "type": "features",
  "features": [
    { "geometry": source },
    { "geometry": destination }
  ]
}

const getRoute = (cb) => request.post({
  url: ESRI_ARCGIS_API_URL,
  form: {
    f: 'json',
    token: ESRI_ARCGIS_API_KEY,
    stops: JSON.stringify(payload)
  }
}, cb);

const handleRoute = (e, r, body) => {
  const _polyline = getPolyline(body);
  console.log(_polyline);

  request.post({
    url: `${TOLLGURU_API_URL}/${POLYLINE_ENDPOINT}`,
    headers: {
      'content-type': 'application/json',
      'x-api-key': TOLLGURU_API_KEY
    },
    body: JSON.stringify({
      source: "esri",
      polyline: _polyline,
      ...requestParameters,
    })
  }, (e, r, body) => {
    console.log(e);
    console.log(JSON.parse(body))
  })
}

getRoute(handleRoute);

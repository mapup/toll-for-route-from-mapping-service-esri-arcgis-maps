const request = require("request");
const polyline = require("polyline");

// REST API key from ArcGIS and Tollguru
//const key = process.env.ARCGIS_KEY;
//const key = "82xSDVLH6_3eY8z_bTApvA208e5n8SlAuOvIIK1mC-qK5hE3fuvJfqBMg4n28Jyd4eqqQZDpb_XIWu3yvU5cEhnxj5_4uMP5LnaeCuS03q89IkKanGw2RcefQfHu4rXx-3Q49hac9PYTA7rA5HtoVg.."
const key ="5wN7kZ6uAnvDxcRk3SeeCjbBM4Zivxjka5nh0etoROvIN-IN9xRN_7ULyiZTTxP-K5aSF6bfz_ETu3_bgswtLGu617gNgxiv1G_-NJgbdd3qypgGmnRVMbrVHuTcQHCV7X3kCk8jKzQjRlbVPNHNIpRbqlsl5J67F_dbYjZqK5oVk-6gBPbOZ6nZl17tHZ8-cJmhzSSXrkC5qWFOOXbOzhVTrCvo7EF7D2Vf7pmwhwo."


const tollguruKey = process.env.TOLLGURU_KEY;

// Dallas, TX
const source = {
    longitude: '-96.7970',
    latitude: '32.7767',
}

// New York, NY
const destination = {
    longitude: '-74.0060',
    latitude: '40.7128'
};

const url = `https://route.arcgis.com/arcgis/rest/services/World/Route/NAServer/Route_World/solve`;


const head = arr => arr[0];
const flatten = (arr, x) => arr.concat(x);

// JSON path "$..paths"
const getPoints = body => body.routes.features
  .map(feature => feature.geometry.paths)
  .reduce(flatten)
  .reduce(flatten)
  .map(([x, y]) => [y, x])

const getPolyline = body => polyline.encode(getPoints(JSON.parse(body)));


const payload = {
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
}



const getRoute = (cb) => request.post(
  {
    url,
    form: {
      f: 'json',
      token: key,
      stops: JSON.stringify(payload)
    }
  },
  cb
);

const tollguruUrl = 'https://dev.tollguru.com/v1/calc/route';


const handleRoute = (e, r, body) =>  {

  console.log(body);
  const _polyline = getPolyline(body);
  console.log(_polyline);

  request.post(
    {
      url: tollguruUrl,
      headers: {
        'content-type': 'application/json',
        'x-api-key': tollguruKey
      },
      body: JSON.stringify({ source: "esri", polyline: _polyline })
    },
    (e, r, body) => {
      console.log(e);
      console.log(body)
    }
  )
}

getRoute(handleRoute);

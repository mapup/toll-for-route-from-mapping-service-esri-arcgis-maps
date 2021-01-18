# [ArcGIS For Developer](https://developers.arcgis.com)

### Get token to access ArcGIS APIs (if you have an API key skip this)
#### Step 1: Get API Token
* Create an account to access [ArcGIS For Developer](https://developers.arcgis.com/dashboard)
* go to signup link https://developers.arcgis.com/sign-up/
* if you have an account login at https://developers.arcgis.com/sign-in/

#### Step 2: creating a token
* Once logged in you can find a temporary token at https://developers.arcgis.com/dashboard
* You can also create an application and generate tokens for it.

With this in place, make a POST request: https://route.arcgis.com/arcgis/rest/services/World/Route/NAServer/Route_World/solve
With `content-type: 'application/x-www-form-urlencoded'` and body with
following keys

```
{
  f: "json",
  token: ${token},
  stops: `{
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
   }`
}
```

### Note:
You should see full path as series of coordinates, we convert it to
`polyline`

```javascript

// JSON path "$..paths"
const getPoints = body => body.routes.features
  .map(feature => feature.geometry.paths)
  .reduce(flatten)
  .reduce(flatten)
  .map(([x, y]) => [y, x])
```

```javascript
const request = require("request");
const polyline = require("polyline");

// REST API key from ArcGIS and Tollguru
const key = process.env.ARCGIS_KEY;
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

const handleRoute = (e, r, body) = console.log(getPolyline(body))
getRoute(handleRoute);
```

Note:

We extracted the polyline for a route from ArcGIS Routing API.

We need to send this route polyline to TollGuru API to receive toll information

## [TollGuru API](https://tollguru.com/developers/docs/)

### Get key to access TollGuru polyline API
* create a dev account to receive a free key from TollGuru https://tollguru.com/developers/get-api-key
* suggest adding `vehicleType` parameter. Tolls for cars are different than trucks and therefore if `vehicleType` is not specified, may not receive accurate tolls. For example, tolls are generally higher for trucks than cars. If `vehicleType` is not specified, by default tolls are returned for 2-axle cars. 
* Similarly, `departure_time` is important for locations where tolls change based on time-of-the-day.

the last line can be changed to following

```javascript

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
      body: JSON.stringify({
        source: "esri",
        polyline: _polyline,
        vehicleType: "2AxlesAuto",
        departure_time: "2021-01-05T09:46:08Z"
      })
    },
    (e, r, body) => {
      console.log(e);
      console.log(body)
    }
  )
}

getRoute(handleRoute);
```

The working code can be found in index.js file.

## License
ISC License (ISC). Copyright 2020 &copy;TollGuru. https://tollguru.com/

Permission to use, copy, modify, and/or distribute this software for any purpose with or without fee is hereby granted, provided that the above copyright notice and this permission notice appear in all copies.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

global.__base = __dirname + '/';

var
  use_https = true,
  argv = require('minimist')(process.argv.slice(2)),
  https = require('https'),
  fs = require('fs'),
  app = require('express')(),
  _ = require('lodash'),
  parser = require('xmldom').DOMParser,
  XMLHttpRequest = require("xmlhttprequest").XMLHttpRequest,
  sendPostRequest = require('request').post,
  cors = require('cors');

////////// EXPERIMENT GLOBAL PARAMS //////////

var gameport;

if (argv.gameport) {
  gameport = argv.gameport;
  console.log('using port ' + gameport);
} else {
  gameport = 8886;
  console.log('no gameport specified: using 8886\nUse the --gameport flag to change');
}

// we launch store.js ourselves
// find free internal port
store_port = server.address.port(0);

if (argv.local_store){
  console.log('using local store on port ' + store_port);
  // launch store.js
  var store_process = require('child_process').spawn('node', [__dirname + '/store_local.js', '--port', store_port]);
} else {
  console.log('using mongoDB store on port ' + store_port);
  // launch store.js
  var store_process = require('child_process').spawn('node', [__dirname + '/store.js', '--port', store_port]);
}

try {
  var privateKey = fs.readFileSync('/etc/letsencrypt/live/cogtoolslab.org/privkey.pem'),
    certificate = fs.readFileSync('/etc/letsencrypt/live/cogtoolslab.org/cert.pem'),
    intermed = fs.readFileSync('/etc/letsencrypt/live/cogtoolslab.org/chain.pem'),
    options = { key: privateKey, cert: certificate, ca: intermed },
    server = require('https').createServer(options, app).listen(gameport),
    io = require('socket.io')(server);
} catch (err) {
  console.log("cannot find SSL certificates; falling back to http");
  var server = app.listen(gameport),
    io = require('socket.io')(server);
}

// serve stuff that the client requests
app.get('/*', (req, res) => {
  serveFile(req, res);
});

io.on('connection', function (socket) {

  // on request serve the stimulus data
  socket.on('getStims', function (data) {
    console.log('getStims');
    var proj_name = data.proj_name;
    var exp_name = data.exp_name;
    var iter_name = data.iter_name;
    initializeWithTrials(socket, proj_name, exp_name, iter_name);
    // write data to db upon getting current data
    socket.on('currentData', function (data) {
      console.log('currentData received: ' + JSON.stringify(data));
      // Increment games list in mongo here
      var proj_name = data.proj_name;
      var exp_name = data.exp_name;
      var iter_name = data.iter_name;
      writeDataToMongo(data, proj_name, exp_name, iter_name);
    });

  });

  FORBIDDEN_FILES = ["auth.json"]

  var serveFile = function (req, res) {
    var fileName = req.params[0];
    if (FORBIDDEN_FILES.includes(fileName)) {
      // Don't serve files that contain secrets
      console.log("Forbidden file requested: " + filename);
      return;
    }
    console.log('\t :: Express :: file requested: ' + fileName);
    return res.sendFile(fileName, { root: __dirname });
  };

  function omit(obj, props) { //helper function to remove _id of stim object
    props = props instanceof Array ? props : [props]
    return eval(`(({${props.join(',')}, ...o}) => o)(obj)`)
  }

  function initializeWithTrials(socket, proj_name, collection, it_name) {
    var gameid = UUID();
    // var colname = 'human-physics-benchmarking-dominoes-pilot_production_1'; //insert STIMULI DATASETNAME here
    sendPostRequest('http://localhost:8023/db/getstims', {
      json: {
        dbname: proj_name + '_stims',
        colname: collection,
        it_name: it_name,
        gameid: gameid
      }
    }, (error, res, body) => {
      if (!error && res.statusCode === 200 && typeof body !== 'undefined') {
        // send trial list (and id) to client
        var packet = {
          gameid: gameid,
          stims: omit(body.stims, ['_id']),
          familiarization_stims: omit(body.familiarization_stims, ['_id']),
          stim_version: body.stim_version, //TODO fix stim version
          // TODO add other properties here

        };
        socket.emit('stims', packet);
      } else {
        console.log(`error getting stims: ${error} ${body}`);
      }
    });
  }

  var UUID = function () {
    var baseName = (Math.floor(Math.random() * 10) + '' +
      Math.floor(Math.random() * 10) + '' +
      Math.floor(Math.random() * 10) + '' +
      Math.floor(Math.random() * 10));
    var template = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx';
    var id = baseName + '-' + template.replace(/[xy]/g, function (c) {
      var r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);
      return v.toString(16);
    });
    return id;
  };

  var writeDataToMongo = function (data, proj_name, collection, it_name) {
    var db = proj_name + '_resp';
    sendPostRequest(
      'http://localhost:8023/db/insert',
      { json: data,
        dbname: db,
        colname: collection,
        it_name: it_name },
      (error, res, body) => {
        if (!error && res.statusCode === 200) {
          console.log(`sent data to store`);
        } else {
          console.log(`error sending data to store: ${error} ${body}`);
        }
      }
    );
  };

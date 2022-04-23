'use strict';

const _ = require('lodash');
const bodyParser = require('body-parser');
const express = require('express');
const fs = require('fs');
const colors = require('colors/safe');
const json2csv = require('json2csv').parse;
const path = require('path');
const app = express();
var argv = require('minimist')(process.argv.slice(2));

const port = argv.port || 8012;

console.log(`store running at http://localhost:${port}`);

function makeMessage(text) {
  return `${colors.blue('[store]')} ${text}`;
}

function log(text) {
  console.log(makeMessage(text));
}

function failure(response, text) {
  const message = makeMessage(text);
  console.error(message);
  return response.status(500).send(message);
}

const write = async (filename, data) => {
    // output file in the same folder
    let rows;
    // If file doesn't exist, we will create new file and add rows with headers.    
    if (!fs.existsSync(filename)) {
        fs.mkdirSync(path.dirname(filename));
        rows = json2csv(data, { header: true });
    } else {
        // Rows without headers.
        rows = json2csv(data, { header: false });
    }
    // Append file function can create new file too.
    fs.appendFileSync(filename, rows);
    // Always add new line if file already exists.
    fs.appendFileSync(filename, "\r\n");
}

function serve() {
    app.use(bodyParser.json());
    app.use(bodyParser.urlencoded({ extended: true}));

    app.post('/db/insert', (request, response) => {
      if (!request.body) {
        return failure(response, '/db/insert needs post request body');
      }
      console.log(`got request to insert into ${request.body.colname}`);

      const databaseName = request.body.dbname;
      const collectionName = request.body.colname;
      if (!collectionName) {
        return failure(response, '/db/insert needs collection');
      }
      if (!databaseName) {
        return failure(response, '/db/insert needs database');
      }

      const data = _.omit(request.body, ['colname', 'dbname']);

      const ResponsePath = path.resolve(__dirname, `../results/${databaseName}_resp/${collectionName}.csv`);
      var data_csv = [data];
      write(ResponsePath, data_csv);
      console.log(`inserting data: ${JSON.stringify(data).substring(0,200)}`);
    });

    app.post('/db/getstims', (request, response) => {
      if (!request.body) {
        return failure(response, '/db/getstims needs post request body');
      }
      console.log(`got request to get stims from ${request.body.dbname}/${request.body.colname}`);

      const databaseName = request.body.dbname;
      const collectionName = request.body.colname;
      if (!collectionName) {
        return failure(response, '/db/getstims needs collection');
      }
      if (!databaseName) {
        return failure(response, '/db/getstims needs database');
      }

      const StimuliPath = path.resolve(__dirname, `../stimuli/${databaseName}/${collectionName}.json`);
      var stimuli = require(StimuliPath);
      response.send(stimuli);
    });  

    app.listen(port, () => {
      log(`running at http://localhost:${port}`);
    });
}

serve();
var connect = require('connect');
var fs = require('fs');
var exec = require('child_process').exec;
var dns = require('dns');
var application_root = __dirname,
    express = require('express'),
    bodyParser = require('body-parser'),
    methodOverride = require('method-override'),
    errorhandler = require('errorhandler'),
        path = require('path');
        var databaseUrl = '127.0.0.1:27017/stv2';
var collections = ['hosts'];
var db = require('mongojs').connect(databaseUrl, collections);
    var app = express();


      var ip = "10.10.10.10";
      var cmd = 'python ./scripts/scanone.py -node ' + ip;
      var child = exec(cmd, function(error) {
        if (error != null) {
          console.log('701 node_server could not execute the python script.');
          console.log(error);
        } else {
          console.log("ran")
        };
      });


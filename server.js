// CODEX
// 
// version -- 0.1
// version date -- 09-26-2014
// author -- Peter Fraedrich
//
//


// ================ SETUP ========================== // 

    var connect = require('connect');
    var sys = require('sys');
    var exec = require('child_process').exec;
    var fs = require ('fs');
    var dns = require('dns');
    var application_root = __dirname,
        express = require('express'),
        bodyParser = require('body-parser'),
        methodOverride = require('method-override'),
        errorhandler = require('errorhandler'),
            path = require('path');
            var databaseUrl = '127.0.0.1:27017/codex';
    var collections = ['entries'];
    var db = require('mongojs').connect(databaseUrl, collections);
        var app = express();
  
    var httpPort = 80;
    var apiPort = 666;

// ================ CONFIG ========================= //
   
    var allowCrossDomain = function(req, res, next) {
      res.header('Access-Control-Allow-Origin', '*');
      //res.header('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE');
      res.header('Access-Control-Allow-Methods', '*');
      res.header('Access-Control-Allow-Headers', '*');
      //res.header('Access-Control-Allow-Headers', 'X-Requested-With, Accept, Origin, Referer, User-Agent, Content-Type, Authorization');
     
      // intercept OPTIONS method
      if (req.method === 'OPTIONS') {
        res.send(200);
      }
      else {
        next();
      }
    };

    app.use(allowCrossDomain);   // make sure this is is called before the router
    app.use(bodyParser());
    app.use(methodOverride());
    app.use(errorhandler());
    app.use(express.static(path.join(application_root, "public")));

    if (fs.statSync('./log/node_server.log')["size"] < 2) {
      fs.writeFile('./log/node_server.log', "");
    };
     if (fs.statSync('./log/angularjs.log')["size"] < 2) {
      fs.writeFile('./log/angularjs.log', "");
    };

// ================ INTERNAL FUNCTIONS ===============//

  // gets date and time for log function
  function GetDateTime() {

      var date = new Date();
      var hour = date.getHours();
      hour = (hour < 10 ? "0" : "") + hour;
      var min = date.getMinutes();
      min = (min < 10 ? "0" : "") + min;
      var sec = date.getSeconds();
      sec = (sec < 10 ? "0" : "") + sec;
      var year = date.getFullYear();
      var month = date.getMonth();
      month = (month < 10 ? "0" : "") + month;
      var day = date.getDate();
      day = (day < 10 ? "0" : "") + day;
      return year + ":" + month + ":" + day + "::" + hour + ":" + min + "." + sec + " -- ";
  }

  // NODE log function
  function log(code, message) {
      timestamp = GetDateTime();
      message = timestamp + code +  " -- " + message + "\n";
      filename = './log/node_server.log';
      currentlog = fs.readFileSync(filename,'utf-8');
      oldlog = fs.statSync(filename)
      if (oldlog["size"] > 5000000.0) { // moves log to .old if its over 5mb and clears current log
          fs.writeFile('./log/node_server.log.old', currentlog);
          fs.writeFile(filename, GetDateTime()+ " -- 000 -- Cleaned up the logfile.");
      };
      fs.appendFile(filename, message, function (err) {
        if (err) return console.log("could not write to logfile" + err);
      });
  };

  // ANGULAR log function
  function ngLog(code, message) {
      timestamp = GetDateTime();
      message = timestamp + code +  " -- " + message + "\n";
      filename = './log/angularjs.log';
      currentlog = fs.readFileSync(filename,'utf-8');
      oldlog = fs.statSync(filename)
      if (oldlog["size"] > 5000000.0) { // moves log to .old if its over 5mb and clears current log
          fs.writeFile('./log/angularjs.log.old', currentlog);
          fs.writeFile(filename, GetDateTime()+ " -- 000 -- Cleaned up the logfile.");
      };
      fs.appendFile(filename, message, function (err) {
        if (err) return console.log("could not write to logfile" + err);
      });
  };


// ================ ANGULAR LOGGING ================ //

    app.post('/angularlog', function (req, res) {

      var jsonData = JSON.parse(req.body.mydata);
      ngLog(jsonData.errcode,jsonData.errmsg);
      res.send('1');

    });


// ================ API ============================ //

//// TEST API HOOK
    app.get('/api', function (req, res) {
        res.send('API OK <br><br> DB URL: ' + databaseUrl);
    });

//// GET HOSTS / REFRESH
    app.get('/get', function (req, res) {
        db.entries.find({}, function(err, ipaddr) { 
        if( err || !ipaddr) {
          res.writeHead(200, {'Content-type': 'application/text'});
          res.end()
          log("101", "Nothing found in DB at " + databaseUrl + " or there was an error with the GET.");
        }
        else 
        {
            res.writeHead(200, {'Content-Type': 'application/json'}); 
            str='['
            ipaddr.forEach( function(row) {
                str = str + '{ "ipaddr" : "' + row.ipaddr + '", "dnsname" : "' + row.dnsname + '", "nickname" : "' + row.nickname + '", "reserved" : "' + row.reserved + '", "notes" : "' + row.notes + '", "subnet" : "' + row.subnet + '", "vlan" : "' + row.vlan + '", "type" : "' + row.type + '", "health" : "' + row.health + '", "ipA" : "' + row.ipA + '", "ipB" : "' + row.ipB + '", "ipC" : "' + row.ipC + '", "ipD" : "' + row.ipD + '", "location" : "' + row.location + '" }' + ',\n';
            });
            str = str.trim();
            str = str.substring(0,str.length-1);
            str = str + ']';
            res.end(str);
            }
        });
    });

//// ADD NEW HOST
    app.post('/add', function (req, res) {
      //console.log(req.body.mydata);
      var jsonData = JSON.parse(req.body.mydata);
      var ip = jsonData.ipaddr;
      // do a DNS lookup on new IP's
        try {
          dns.reverse(ip, function (err, resolve) {
            if (err) {
              // if nothing found, put in blanks for the dnsname and save to DB
              log("201","DNS found nothing for IP " + jsonData.ipaddr);
              jsonData.dnsname = ''
              db.entries.save({
                dnsname: jsonData.dnsname,
                nickname: jsonData.nickname,
                ipaddr: jsonData.ipaddr, 
                subnet: jsonData.subnet, 
                vlan: jsonData.vlan, 
                type: jsonData.type, 
                location: jsonData.location, 
                notes: jsonData.notes, 
                reserved: jsonData.reserved, 
                health: "green.png", 
                ipA: jsonData.ipA,
                ipB: jsonData.ipB,
                ipC: jsonData.ipC,
                ipD: jsonData.ipD
              },
               function(err, saved) {
                  if( err || !saved ) { 
                    res.end("server not saved"); 
                    log("202","Entry was not saved, there was an error.");
                  } else { 
                    res.end("server saved"); 
                  };
               });
            } else {
              // if somethings is resolved, add it to jsonData and save to DB
              jsonData.dnsname = resolve[0].toString();
              //console.log("DNS name found for " + jsonData.ipaddr + ", resolved to " + jsonData.dnsname);
              db.entries.save({dnsname: jsonData.dnsname, 
               dnsname: jsonData.dnsname,
                nickname: jsonData.nickname,
                ipaddr: jsonData.ipaddr, 
                subnet: jsonData.subnet, 
                vlan: jsonData.vlan, 
                type: jsonData.type, 
                location: jsonData.location, 
                notes: jsonData.notes, 
                reserved: jsonData.reserved, 
                health: "green.png",
                ipA: jsonData.ipA,
                ipB: jsonData.ipB,
                ipC: jsonData.ipC,
                ipD: jsonData.ipD  
              },
               function(err, saved) {
                  if( err || !saved ) { 
                    res.end("server not saved"); 
                    log("203","Entry was not saved, there was an error.");
                  } else { 
                    res.end("server saved"); 
                  };
               });
            };
          });
        } catch (err) {
          // if nothing found, put in blanks for the dnsname and save to DB
          log("204", "DNS error " + jsonData.ipaddr);
              jsonData.dnsname = ''
              db.entries.save({
                dnsname: jsonData.dnsname,
                nickname: jsonData.nickname,
                ipaddr: jsonData.ipaddr, 
                subnet: jsonData.subnet, 
                vlan: jsonData.vlan, 
                type: jsonData.type, 
                location: jsonData.location, 
                notes: jsonData.notes, 
                reserved: jsonData.reserved, 
                health: "green.png", 
                ipA: jsonData.ipA,
                ipB: jsonData.ipB,
                ipC: jsonData.ipC,
                ipD: jsonData.ipD
              },
               function(err, saved) {
                  if( err || !saved ) { 
                    res.end("server not saved"); 
                    log("204","Entry was not saved, there was an error.");
                  } else { 
                    res.end("server saved"); 
                  };
               });
        };
      
    });

//// SAVE CHANGED HOST
    app.post('/save', function (req, res){
           var jsonData = JSON.parse(req.body.mydata);
           var query = jsonData.oip;
           db.entries.update({ipaddr:query}, {$set : {nickname: jsonData.nickname, ipaddr: jsonData.ipaddr, subnet: jsonData.subnet, vlan: jsonData.vlan, type: jsonData.type, location: jsonData.location, notes: jsonData.notes, reserved: jsonData.reserved, ipA: jsonData.ipA, ipB: jsonData.ipB, ipC: jsonData.ipC, ipD: jsonData.ipD} },
                function(err, saved) {
                  if( err || !saved ) { 
                    res.end("server not saved"); 
                    log("302","Entry was not saved, there was an error.");
                  } else { 
                    res.end("server saved"); 
                  };
               });

    });

//// DELETE HOST
    app.post('/delete', function (req, res) {
        var row = JSON.parse(req.body.mydata);
        db.entries.remove(row, 
          function(err) {
            if (!err) {
              res.send("entry deleted");
            } else {
              log("401","There was an error deleting the entry or with the POST operation.");
            };
          });
    });

//// LOOKUP HOST - PREVENT DUPLICATE ENTRIES
    app.post('/lookup', function (req, res) {
        var lookup = req.body.mydata;
        var jsonData = JSON.parse(req.body.mydata);
        // look up the IP in the DB to make sure it's not already there
        try {
          db.entries.find(jsonData).toArray(function(err, result) { 
              try {
                // get the length of the result, if its 0 then its a uniquq IP
                len = result.length;
              }
              catch(err) {
                log("501","There was an error reading the length of the result.");
              }
                  // nothing found, send response code back to Angular
                  if (len === 0) {
                      // console.log("Nothing found!");
                      res.writeHead(200, {'Content-Type': 'application/json'}); 
                      stra='[{"response":"0"}]'; 
                      res.end( stra);
                  } else {
                      // oops found something, send the response code back to Angular
                      res.writeHead(200, {'Content-Type': 'application/json'}); 
                      //str='[';
                      strb='[{"response":"1"}]';                
                      res.end( strb);
                  };
              // clear the len var for the next lookup
              len = 0;
          });
        }
        catch(err) {
          log("502","There was an error fecthing from the DB at " + databaseUrl + " or an error with the POST.");
        }
    });

///////////////////// PYTHON API HOOKS ////////////////////////////

//// RESCAN DB
    app.post('/rescanall', function (req, res) {
      var child = exec('python ./scripts/scanall.py -node', function(error) {
        if (error != null) {
          log('601','node_server could not execute python script.');
          res.send("0");
        } else {
          //console.log('Running python script');
          res.send("1");
        };
      });
    });

//// RESCAN ONE
    app.post('/rescanone', function (req, res){
      var jsonData = JSON.parse(req.body.mydata);
      var cmd = 'python ./scripts/scanone.py -node ' + jsonData.ipaddr;
      var child = exec(cmd, function(error) {
        if (error != null) {
          log('701','node_server could not execute the python script.');
          res.send("0");
        } else {
          //console.log('Running python script.');
          res.send("1");
        };
      });
    });

//// SCAN SUBNET
    app.post('/scan', function (req, res){
      var jsonData = JSON.parse(req.body.mydata);
      var cmd = 'python ./scripts/scansubnet.py -node ' + jsonData.ipaddr;
      var child = exec(cmd, function(error) {
        if (error != null) {
          log('801','node_server could not execute the python script.');
          res.send("0");
        } else {
          //console.log('Running python script.');
          res.send("1");
        };
      });
    });

//// DELETE ALL
    app.post('/drop', function (req, res){
      var cmd = 'python ./scripts/dropdb.py -node';
      var child = exec(cmd, function(error) {
        if (error != null) {
          log('901','node_server could not execute the python script.');
          res.send("0");
        } else {
          log('999','The entries database was dropped. Hope you have backups.');
          res.send("1");
        };
      });
    });

// ============= LISTEN ==================== //

connect ()
  .use(connect.static(__dirname)).listen(httpPort);
console.log('Server listening on port 80');
app.listen(apiPort);
console.log('API listening on port 666');
log("001","The sever started up successfully.");


// EOF

// CODEX
// 
// version -- 0.1
// version date -- 09-26-2014
// author -- Peter Fraedrich
//
//

// ======== INIT APP ===================//

var app = angular.module('codex', ['ui']);

app.config(['$httpProvider', function($httpProvider) {
    $httpProvider.defaults.useXDomain = true;
    /*delete $httpProvider.defaults.headers.common['X-Requested-With'];*/
    }
]);

// ========= CONTROLLERS =================//

app.controller('codexList', ['$scope', '$timeout', '$http', '$templateCache', function($scope, $timeout, $http, $templateCache) {

    var method = 'POST';
    var rooturl = 'http://192.168.1.9:666';
    var oip = '';

    $scope.codeStatus = "";

    // === logging function === //

    $scope.strEncode = function(string) {

        var str = string.replace(/\n/g,'%n');
        str = str.replace(/\\/g,'%s');
        str = str.replace(/"/g,"%quot");
        str = str.replace(/&/g,"%amp");
        return str;
    }

    $scope.strDecode = function(string) {

        var str = string.replace(/%n/g,'\n');
        str = str.replace(/%s/g,'\\');
        str = str.replace(/%quot/g,'"');
        str = str.replace(/%amp/g,"&");
        return str
    }
    
    $scope.logger = function (code, message) {

        var err = {
            errcode: code,
            errmsg: message
        };
        var jdata = "mydata=" + JSON.stringify(err);
        $http({
            method: 'POST',
            url: rooturl+'/angularlog',
            data: jdata,
            headers: {'Content-Type': 'application/x-www-form-urlencoded'},
            cache: $templateCache,
        }).
        success(function(response) {
            $scope.nothing();
        }).
        error(function(response){
            $scope.codeStatus = response || "Request failed";
            console.log('101 -- HTTP error - fn. logger');
        });


    };

    // list hosts
    $scope.list = function() {

        var url = rooturl+'/get';
        $http.get(url).then(function(res) {
            $scope.entries = res.data;         
        });
    };
     
    $scope.nothing = function() {

    };

    $scope.triggerlog = function() {
        var logdata = {
            errcode: '666',
            errmsg: 'logtest'
        };
        var jdata = "mydata=" + JSON.stringify(logdata);
        $http({
            method: 'POST',
            url: rooturl+'/angularlog',
            data: jdata,
            headers: {'Content-Type': 'application/x-www-form-urlencoded'},
            cache: $templateCache,
        }).
        success(function(response) {
            $scope.logger('100','HTTP success');
        }).
        error(function(response){
            $scope.codeStatus = response || "Request failed";
            $scope.logger('101','HTTP error');
        });

    };

    $scope.edit = function(row) {

        
        $scope.hide = false;
        $scope.editIpaddr = $scope.strDecode(row.ipaddr);
        $scope.editNickname = $scope.strDecode(row.nickname);
        $scope.editHeader = $scope.strDecode(row.nickname);
        $scope.editDnsname = $scope.strDecode(row.dnsname);
        $scope.editSubnet = $scope.strDecode(row.subnet);
        $scope.editLocation = $scope.strDecode(row.location);
        $scope.editNotes = $scope.strDecode(row.notes);
        $scope.editReserved = row.reserved;
        $scope.editType = row.type;
        $scope.editVlan = $scope.strDecode(row.vlan);
        oip = $scope.strDecode(row.ipaddr);
        $scope.editHealth = row.health;


    };

    $scope.edithide = function () {

        $scope.hide = ($scope.hide) ? false : true;
        return $scope.hide;

    };

    $scope.viewhide = function () {

        $scope.viewhide = ($scope.viewhide) ? false : true;
        return $scope.viewhide;

    };

    $scope.filterhide = function () {

        $scope.filteropen = ($scope.filteropen) ? false : true;
        return $scope.filteropen;
    };

    $scope.addhide = function () {

        $scope.addopen = ($scope.addopen) ? false : true;
        return $scope.addopen;
    };

    $scope.adminhide = function () {

        $scope.adminopen = ($scope.adminopen) ? false : true;
        return $scope.adminopen;
    };

    $scope.addcancel = function () {

        $scope.ipaddr = '';
        $scope.nickname = '';
        $scope.type = '';
        $scope.subnet = '';
        $scope.vlan = '';
        $scope.location = '';
        $scope.notes = '';
        $scope.reserved = "clear.png";
        $scope.addhide();

    }

    $scope.viewOptions = function() {

        $scope.viewhide = false;

    };

    $scope.viewSave = function() {

        $scope.viewhide = true;

    };

    $scope.saveEdit = function () {

        //// DATA VALIDATION
        // check IP address to make sure there is one
        if ($scope.editIpaddr == null) {
            alert("ERROR: IP address cannot be blank.")
        } else {
            $scope.editIpaddr = $scope.strEncode($scope.editIpaddr);
            var ipData = { ipaddr: $scope.editIpaddr, };
            // split IP into octets for sorting
            var octets = ($scope.editIpaddr).split(".");
            $scope.ipA = parseFloat(octets[0]);
            $scope.ipB = parseFloat(octets[1]);
            $scope.ipC = parseFloat(octets[2]);
            $scope.ipD = parseFloat(octets[3]);
        };
        
        /// check to see if fields are null & fix + special character encoding
        if ($scope.editNickname == null) {
            $scope.editNickname = ''
        } else {
            $scope.editNickname = $scope.strEncode($scope.editNickname);
        };
        if ($scope.editReserved == null) {
            $scope.editReserved = 'clear.png'
        };
        if ($scope.editType == null) {
            $scope.editType = ''
        };
        if ($scope.editSubnet == null) {
            $scope.editSubnet = ''
        } else {
            $scope.editSubnet = $scope.strEncode($scope.editSubnet);
        };
        if ($scope.editVlan == null) {
            $scope.editVlan = ''
        } else {
            $scope.editVlan = $scope.strEncode($scope.editVlan);
        };
        if ($scope.editLocation == null) {
            $scope.editLocation = ''
        } else {
            $scope.editLocation = $scope.strEncode($scope.editLocation);
        };
        if ($scope.editNotes == null) {
            $scope.editNotes = ''
        } else {
            $scope.editNotes = $scope.strEncode($scope.editNotes);
        };

        if ($scope.editIpaddr != oip) {

                var iplookup = 'mydata='+JSON.stringify(ipData);

                $http({
                    method: 'POST',
                    url: rooturl+'/lookup',
                    data: iplookup,
                    headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                    cache: $templateCache,
                }).
                then( function(res) {

                    /// If IP address already in DB, return error and prompt user
                    if (res.data[0].response==="1") {
                        alert("IP address exists!\nPlease choose another.");
                    } else if ($scope.editIpaddr.length < 6) {
                        alert("IP address is required!");

                    } else {
                    /// if everything is OK, write JSON obejct and submit to Node API for DB 

                    var formData = {
                        ipaddr: $scope.editIpaddr,
                        nickname: $scope.editNickname,
                        subnet: $scope.editSubnet,
                        vlan: $scope.editVlan,
                        type: $scope.editType,
                        location: $scope.editLocation,
                        notes: $scope.editNotes,
                        reserved: $scope.editReserved,
                        oip: oip,
                        ipA: $scope.ipA,
                        ipB: $scope.ipB,
                        ipC: $scope.ipC,
                        ipD: $scope.ipD 
                        };

                    var jdata = 'mydata=' + JSON.stringify(formData);

                    $http({
                        method: 'POST',
                        url: rooturl+'/save',
                        data: jdata,
                        headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                        cache: $templateCache,
                    }).
                    success(function(response) {
                        $scope.logger('100','HTTP success');
                    }).
                    error(function(response){
                        $scope.codeStatus = response || "Request failed";
                        $scope.logger('101','HTTP error - fn. add');
                    });

                    $scope.edithide();
                    $timeout(function() {$scope.list()}, 500)
                            
                    };

                });

        } else {

            var formData = {
                    ipaddr: $scope.editIpaddr,
                    nickname: $scope.editNickname,
                    subnet: $scope.editSubnet,
                    vlan: $scope.editVlan,
                    type: $scope.editType,
                    location: $scope.editLocation,
                    notes: $scope.editNotes,
                    reserved: $scope.editReserved,
                    oip: oip,
                    ipA: $scope.ipA,
                    ipB: $scope.ipB,
                    ipC: $scope.ipC,
                    ipD: $scope.ipD 
                    };

                var jdata = 'mydata=' + JSON.stringify(formData);

                $http({
                    method: 'POST',
                    url: rooturl+'/save',
                    data: jdata,
                    headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                    cache: $templateCache,
                }).
                success(function(response) {
                    $scope.logger('100','HTTP success');
                }).
                error(function(response){
                    $scope.codeStatus = response || "Request failed";
                    $scope.logger('101','HTTP error - fn. add');
                });

                $scope.edithide();
                $timeout(function() {$scope.list()}, 500)
                        
        };
    };


        /*
       // split IP into octets for sorting
        var octets = ($scope.editIpaddr).split(".");
        $scope.ipA = octets[0];
        $scope.ipB = octets[1];
        $scope.ipC = octets[2];
        $scope.ipD = octets[3];

        notes = $scope.editNotes;
        $scope.editNotes = $scope.strEncode(notes);

        var formData = {
            ipaddr: $scope.editIpaddr,
            oip: oip,
            //dnsname: $scope.editDnsname,
            type: $scope.editType,
            nickname: $scope.editNickname,
            subnet: $scope.editSubnet,
            vlan: $scope.editVlan,
            location: $scope.editLocation,
            notes: $scope.editNotes,
            reserved: $scope.editReserved,
            health: $scope.editHealth,
            ipA: $scope.ipA,
            ipB: $scope.ipB,
            ipC: $scope.ipC,
            ipD: $scope.ipD
            };

        var jdata = 'mydata=' + JSON.stringify(formData);

        $http({
            method: 'POST',
            url: rooturl+'/save',
            data: jdata,
            headers: {'Content-Type': 'application/x-www-form-urlencoded'},
            cache: $templateCache,
        }).
        success(function(response) {
            $scope.logger('100','HTTP success');
        }).
        error(function(response){
            $scope.codeStatus = response || "Request failed";
            $scope.logger('101','HTTP error - fn. saveEdit');
        });

        $scope.edithide();
        $timeout(function() {$scope.list()}, 500)
*/

    $scope.refresh = function () {
        $scope.list();
    };

    $scope.delete = function(row) {

        var rowData = {
            ipaddr: row.ipaddr,
        };

        var delurl = rooturl+"/delete";
        var jdata = "mydata="+JSON.stringify(rowData);
        var delmethod = 'POST';

        $http({
            method: 'POST',
            data: jdata,
            url: rooturl+'/delete',
            headers: {'Content-Type': 'application/x-www-form-urlencoded'},
            cache: $templateCache
        }).
        success(function(response) {
            $scope.logger('100','HTTP success');
        }).
        error(function(response){
            $scope.codeStatus = response || "Request failed";
            $scope.logger('101','HTTP error - fn. delete');
        });
        $scope.list();
        return false;


    };

    $scope.add = function () {

        //// DATA VALIDATION
        // check IP address to make sure there is one
        if ($scope.ipaddr == null) {
            alert("ERROR: IP address cannot be blank.")
        } else {
            $scope.ipaddr = $scope.strEncode($scope.ipaddr);
            var ipData = { ipaddr: $scope.ipaddr, };
            // split IP into octets for sorting
            var octets = ($scope.ipaddr).split(".");
            $scope.ipA = parseFloat(octets[0]);
            $scope.ipB = parseFloat(octets[1]);
            $scope.ipC = parseFloat(octets[2]);
            $scope.ipD = parseFloat(octets[3]);
        };
        
        /// check to see if fields are null & fix + special character encoding
        if ($scope.nickname == null) {
            $scope.nickname = ''
        } else {
            $scope.nickname = $scope.strEncode($scope.nickname);
        };
        if ($scope.reserved == null) {
            $scope.reserved = 'clear.png'
        };
        if ($scope.type == null) {
            $scope.type = ''
        };
        if ($scope.subnet == null) {
            $scope.subnet = ''
        } else {
            $scope.subnet = $scope.strEncode($scope.subnet);
        };
        if ($scope.vlan == null) {
            $scope.vlan = ''
        } else {
            $scope.vlan = $scope.strEncode($scope.vlan);
        };
        if ($scope.location == null) {
            $scope.location = ''
        } else {
            $scope.location = $scope.strEncode($scope.location);
        };
        if ($scope.notes == null) {
            $scope.notes = ''
        } else {
            $scope.notes = $scope.strEncode($scope.notes);
        };

        var iplookup = 'mydata='+JSON.stringify(ipData);

        $http({
            method: 'POST',
            url: rooturl+'/lookup',
            data: iplookup,
            headers: {'Content-Type': 'application/x-www-form-urlencoded'},
            cache: $templateCache,
        }).
        then( function(res) {

            /// If IP address already in DB, return error and prompt user
            if (res.data[0].response==="1") {
                alert("IP address exists!\nPlease choose another.");
            } else if ($scope.ipaddr.length < 6) {
                alert("IP address is required!");

            }
            /// if everything is OK, write JSON obejct and submit to Node API for DB 
            else {

                var formData = {
                    ipaddr: $scope.ipaddr,
                    nickname: $scope.nickname,
                    subnet: $scope.subnet,
                    vlan: $scope.vlan,
                    type: $scope.type,
                    location: $scope.location,
                    notes: $scope.notes,
                    reserved: $scope.reserved,
                    health: 'green.png',
                    ipA: $scope.ipA,
                    ipB: $scope.ipB,
                    ipC: $scope.ipC,
                    ipD: $scope.ipD 
                    };

                var jdata = 'mydata=' + JSON.stringify(formData);

                $http({
                    method: 'POST',
                    url: rooturl+'/add',
                    data: jdata,
                    headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                    cache: $templateCache,
                }).
                success(function(response) {
                    $scope.logger('100','HTTP success');
                }).
                error(function(response){
                    $scope.codeStatus = response || "Request failed";
                    $scope.logger('101','HTTP error - fn. add');
                });

                $scope.ipaddr = '';
                $scope.nickname = '';
                $scope.subnet = '';
                $scope.vlan = '';
                $scope.type = '';
                $scope.location = '';
                $scope.notes = '';
                $scope.reserved = 'clear.png';
                $scope.addhide();
                        
            };

        });
    

    $timeout(function() {$scope.list()}, 500);


    };

    $scope.rescanAll = function () {

        alert('Re-scanning all entries.\nThis could take some time depending on the number of entries.')
        $http({
            method: 'POST',
            url: rooturl+'/rescanall',
            data: "crawl db",
            headers: {'Content-Type': 'application/x-www-form-urlencoded'},
            cache: $templateCache,
        }).
        success(function(response) {
            $scope.logger('100','HTTP success');
            alert("Entry scanning finished.");
        }).
        error(function(response){
            $scope.codeStatus = response || "Request failed";
            $scope.logger('101','HTTP error - fn. rescanAll');
            alert("There was a problem. HTTP ERR 101\nIf this issue persists please contact support.");
        });
        $scope.adminhide();
    };

    $scope.rescanOne = function (row) {

        var ipdata = { ipaddr: row.ipaddr }; 
        var jdata = "mydata=" + JSON.stringify(ipdata);

        $http({
            method: 'POST',
            url: rooturl+'/rescanone',
            data: jdata,
            headers: {'Content-Type': 'application/x-www-form-urlencoded'},
            cache: $templateCache,
        }).
        success(function(response) {
            $scope.logger('100','HTTP success');
        }).
        error(function(response){
            $scope.codeStatus = response || "Request failed";
            $scope.logger('101','HTTP error - fn. rescanOne');
        });
        $timeout(function() {$scope.list()}, 1001);
    };

    $scope.drop = function () {
        
        var c = confirm("Are you sure you want to delete the entire codex?\n -- THIS CANNOT BE UNDONE --");
        if ( c == true ) {

            $http({
                method: 'POST',
                url: rooturl+'/drop',
                data: "drop",
                headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                cache: $templateCache,
            }).
            success(function(response) {
                $scope.logger('100','HTTP success');
            }).
            error(function(response){
                $scope.codeStatus = response || "Request failed";
                $scope.logger('101','HTTP error - fn. drop');
            });
            $timeout(function() {$scope.list()}, 1001);
            $scope.adminhide();
        } else {
            alert("Aborted!")
            $scope.adminhide()
        };
    };

    $scope.scanSubnet = function () {

        alert("Starting subnet scan.\nThis could take some time.")
        $http({
            method: 'POST',
            url: rooturl+'/scan',
            data: "scan",
            headers: {'Content-Type': 'application/x-www-form-urlencoded'},
            cache: $templateCache,
        }).
        success(function(response) {
            console.log(response);
            $scope.logger('100','HTTP success');
            alert("Subnet scan completed successfully.");
        }).
        error(function(response){
            $scope.codeStatus = response || "Request failed";
            console.log(response);
            $scope.logger('101','HTTP error - fn. scanSubnet');
            alert("There was an error. HTTP ERR 101\nIf this problem persists please contact support.");
        });
        $scope.adminhide();
    };

    // Thanks to Josep on StackOverflow for this brilliant workaround!
    $scope.ipOrder = function(row){
    return (
            (parseInt(row.ipA)*Math.pow(256,3))+
            (parseInt(row.ipB)*Math.pow(256,2))+
            (parseInt(row.ipC)*256)+
            parseInt(row.ipD));
    };

app.filter('unique', function() {
    return function(input, key) {
        var unique = {};
        var uniqueList = [];
        for(var i = 0; i < input.length; i++){
            if (typeof unique[input[i][key]] == "undefined"){
                unique[input[i][key]] = "";
                uniqueList.push(input[i]);
            }
        }
        return uniqueList;

    };

});

// ============= ON LOAD FUNCTION CALLS ======//

    $scope.list();
    $scope.hide = true;
    $scope.viewhide = true;
    $scope.addopen = true;
    

}]);

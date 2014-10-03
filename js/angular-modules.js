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
    var rooturl = 'http://10.10.10.132:666';
    var oip = '';

    $scope.codeStatus = "";

    // list hosts
    $scope.list = function() {

        var url = rooturl+'/get';
        $http.get(url).then(function(res) {
            $scope.entries = res.data;
        });
    };
     
    $scope.nothing = function() {

    };

    $scope.edit = function(row) {

        
        $scope.hide = false;
        $scope.editIpaddr = row.ipaddr;
        $scope.editNickname = row.nickname;
        $scope.editHeader = row.nickname;
        $scope.editDnsname = row.dnsname;
        $scope.editSubnet = row.subnet;
        $scope.editLocation = row.location;
        $scope.editNotes = row.notes;
        $scope.editReserved = row.reserved;
        $scope.editType = row.type;
        $scope.editVlan = row.vlan;
        oip = row.ipaddr;
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

       console.log("saving to DB");
       // split IP into octets for sorting
        var octets = ($scope.editIpaddr).split(".");
        $scope.ipA = octets[0];
        $scope.ipB = octets[1];
        $scope.ipC = octets[2];
        $scope.ipD = octets[3];

        notes = $scope.editNotes;
        $scope.editNotes = notes.replace('\n',' ');

        var formData = {
            ipaddr: $scope.editIpaddr,
            oip: oip,
            dnsname: $scope.editDnsname,
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

        console.log(formData);

        $http({
            method: 'POST',
            url: rooturl+'/save',
            data: jdata,
            headers: {'Content-Type': 'application/x-www-form-urlencoded'},
            cache: $templateCache,
        }).
        success(function(response) {
            console.log("success");
            $scope.codeStatus = response.data;
            console.log($scope.codeStatus);
        }).
        error(function(response){
            console.log("error");
            $scope.codeStatus = response || "Request failed";
            console.log($scope.codeStatus);
        });

        $scope.edithide();
        $timeout(function() {$scope.list()}, 500)

    };

    $scope.refresh = function () {
        $scope.list();
        console.log('refreshed the page');

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
            console.log("success");
            $scope.codeStatus = response.data;
            console.log($scope.codeStatus);
        }).
        error(function(response){
            console.log("error");
            $scope.codeStatus = response || "Request failed";
            console.log($scope.codeStatus);
        });
        $scope.list();
        return false;


    };

    $scope.add = function () {

        var ipData = {
            ipaddr: $scope.ipaddr,
        };

        // split IP into octets for sorting
        var octets = ($scope.ipaddr).split(".");
        $scope.ipA = octets[0];
        $scope.ipB = octets[1];
        $scope.ipC = octets[2];
        $scope.ipD = octets[3];
        console.log($scope.ipA, $scope.ipB, $scope.ipC, $scope.ipD);

        /// check to see if fields are null & fix 
        if ($scope.nickname == null) {
            $scope.nickname = ''
        };
        if ($scope.reserved == null) {
            $scope.reserved = 'clear.png'
        };
        if ($scope.type == null) {
            $scope.type = ''
        };
        if ($scope.subnet == null) {
            $scope.subnet = ''
        };
        if ($scope.vlan == null) {
            $scope.vlan = ''
        };
        if ($scope.location == null) {
            $scope.location = ''
        };
        if ($scope.notes == null) {
            $scope.notes = ''
        };
        
        notes = $scope.notes;
        $scope.notes = notes.replace('\n',' ');

        var iplookup = 'mydata='+JSON.stringify(ipData);
        
        console.log(iplookup);

        $http({
            method: 'POST',
            url: rooturl+'/lookup',
            data: iplookup,
            headers: {'Content-Type': 'application/x-www-form-urlencoded'},
            cache: $templateCache,
        }).
        then( function(res) {

            console.log(res.data);
            if (res.data[0].response==="1") {

                alert("IP address exists!\nPlease choose another.");
            } else if ($scope.ipaddr.length < 6) {
                alert("IP address is required!");

            }

            else {

                console.log("ip doesn't exist, do write to db function");
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
                    console.log("success");
                    $scope.codeStatus = response.data;
                    console.log($scope.codeStatus);
                }).
                error(function(response){
                    console.log("error");
                    $scope.codeStatus = response || "Request failed";
                    console.log($scope.codeStatus);
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

app.filter('newline', function(text) {
    return text.replace('<RET>','<br>');
});


// ============= ON LOAD FUNCTION CALLS ======//

    $scope.list();
    $scope.hide = true;
    $scope.viewhide = true;
    $scope.addopen = true;
    

}]);

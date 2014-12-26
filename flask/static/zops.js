/**
 * User: Evren Esat Ozkan
 * Date: 24/12/14
 * Time: 14:22
 */
var maxMEM = 0
var maxCPU = 0
var maxRPS = 0
var rpsGauge = new JustGage({
          id: "rps",
          value: 0,
          min: 0,
          max: 20000,
          title: "Request Per Second",
          label: "rq",
            shadowOpacity: 1,
        shadowSize: 0,
        shadowVerticalOffset: 10
        });

var cpuGauge = new JustGage({
          id: "cpu",
          value: 0,
          min: 0,
          max: 100,
          title: "CPU Usage",
          label: "%",
            shadowOpacity: 1,
        shadowSize: 0,
        shadowVerticalOffset: 10
        });

var memGauge = new JustGage({
          id: "mem",
          value: 0,
          min: 0,
          max: 1000,
          title: "Memory Usage",
          label: "Mb",
            shadowOpacity: 1,
        shadowSize: 0,
        shadowVerticalOffset: 10
        });

ZERO_VAL_COUNT = 0;
totalReq = 0;
totalSecs = 0;
function updateRPS(value) {
    // RPS report period is lower than 1s, so one time we have a real rps value other time a fake zero value.
    // if we get sequence of zeros, then we can assume that RPS actually go to zero.
    val = parseInt(value)
    console.log(val);
    if (val > maxRPS) {
        maxRPS = val
        updateMaxValues()
    }
    if(val){
        totalReq += val
        totalSecs += 1
    }
    if (val || ZERO_VAL_COUNT > 5) {
        rpsGauge.refresh(val);
        ZERO_VAL_COUNT = 0;
        updateMaxValues()
    } else {
        ZERO_VAL_COUNT += 1
    }
}

function updateCPU(value) {
    val = Math.round(parseFloat(value) * 100) / 100;
    if (val > maxCPU) {
        maxCPU = val
        updateMaxValues()
    }
    cpuGauge.refresh(val);
    //document.getElementById("cpud").innerHTML = disp + '% ';

}

function updateMEM(value) {
    val = parseInt(parseInt(value) / 1024)
    if (val > maxMEM) {
        maxMEM = val
        updateMaxValues()
    }
    memGauge.refresh(val);
    //document.getElementById("memd").innerHTML = parseInt(val / 1024) + ' MB';
}

function updateMaxValues() {
    maxStats = "<b>Max Values</b>"
    maxStats += "<br>Max CPU: " + maxCPU +"% ";
    maxStats += " | Max Memory: " + maxMEM + " MB";
    maxStats += " | Max RPS: " + maxRPS;
    maxStats += " | Mean RPS: " + parseInt(totalReq / totalSecs);
    document.getElementById("maxVals").innerHTML = maxStats
}

function updateServerData(data) {
    srvData = ''
    maxMEM = 0
    maxCPU = 0
    maxRPS = 0
for (var key in data) {
    if (data.hasOwnProperty(key)) {
            srvData +="<b>"+ key +"</b><br>" + data[key] + "<br>"
    }
    document.getElementById("srvData").innerHTML = srvData
}
}
var lastUpdate = 0
function runit() {
    oboe('/data.json').node('rp.*', function (data) {
        console.log(data)
        if (data.countMethod && data.countMethod != "undefined") {
            updateServerData(data)
        }else if(data.CPU && data.CPU != 'undefined'){
            lastUpdate = Date.now();
            updateRPS(data.RPS);
            updateMEM(data.MEM);
            updateCPU(data.CPU);
        }

    });
}
runit()
//setInterval("runIfRequired()",3000);
//function runIfRequired(){
//    if (Date.now() - lastUpdate > 5) {
//        runit();
//    }
//}
//runIfRequired()

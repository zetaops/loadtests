/**
 * User: Evren Esat Ozkan
 * Date: 24/12/14
 * Time: 14:22
 */
var maxMEM = 0, maxCPU = 0, maxRPS = 0, totalReq = 0, totalSecs = 0, zeroValCount = 0;
var rpsGauge = new JustGage({
    id: "rps",
    title: "Request Per Second",
    max: 20000,
    value: 0, min: 0, valueFontColor: '#fff', titleFontColor: '#fff', shadowOpacity: 1, shadowSize: 0, shadowVerticalOffset: 10
});

var cpuGauge = new JustGage({
    id: "cpu",
    title: "CPU Usage",
    max: 100,
    value: 0, min: 0, valueFontColor: '#fff', titleFontColor: '#fff', shadowOpacity: 1, shadowSize: 0, shadowVerticalOffset: 10
});

var memGauge = new JustGage({
    id: "mem",
    title: "Memory Usage",
    label: "Mb",
    max: 1000,
    value: 0, min: 0, valueFontColor: '#fff', titleFontColor: '#fff', shadowOpacity: 1, shadowSize: 0, shadowVerticalOffset: 10
});


function updateRPS(value) {
    // updates rps gauge
    // collects rps data to calculate mean value.
    // Sometimes we get fake zeros for RPS data, so we ignore them,
    // but if we get a sequence of zeros, then we can assume that RPS actually go to zero.
    val = parseInt(value)
    console.log(val);
    if (val > maxRPS) {
        maxRPS = val;
    }
    if (val) {
        totalReq += val
        totalSecs += 1
    }
    if (val || zeroValCount > 5) {
        rpsGauge.refresh(val);
        zeroValCount = 0;
        updateMaxValues()
    } else {
        zeroValCount += 1
    }

}

function updateCPU(value) {
    // updates cpu gauge
    val = Math.round(parseFloat(value) * 100) / 100;
    if (val > maxCPU) {
        maxCPU = val
        updateMaxValues()
    }
    cpuGauge.refresh(val);
}

function updateMEM(value) {
    // updates memory gauge
    val = parseInt(parseInt(value) / 1024)
    if (val > maxMEM) {
        maxMEM = val
        updateMaxValues()
    }
    memGauge.refresh(val);
    //document.getElementById("memd").innerHTML = parseInt(val / 1024) + ' MB';
}

function updateMaxValues() {
    // displays max values
    maxStats = "<b>Max Values</b>"
    maxStats += "<br>Max CPU: " + maxCPU + "% ";
    maxStats += " | Max Memory: " + maxMEM + " MB";
    maxStats += " | Max RPS: " + maxRPS;
    if (totalSecs > 25)maxStats += " | Mean RPS: " + parseInt(totalReq / totalSecs);
    document.getElementById("maxVals").innerHTML = maxStats
}

function updateServerData(data) {
    // dispalys server software information from the start of the json stream
    srvData = ''
    for (var key in data) {
        if (data.hasOwnProperty(key)) {
            srvData += "<b>" + key + "</b><br>" + data[key] + "<br>"
        }
        document.getElementById("srvData").innerHTML = srvData
    }
}

function runit() {
    // consumes json stream and passes the revelant data to related functions
    oboe('/data.json').node('rp.*', function (data) {
        console.log(data)
        if (data.RPSCountingMethod && data.RPSCountingMethod != "undefined") {
            updateServerData(data)
        } else if (data.CPU && data.CPU != 'undefined') {
            updateRPS(data.RPS);
            updateMEM(data.MEM);
            updateCPU(data.CPU);
        }

    }).fail(function () {
        setTimeout("runit()", 2000);
    });
}
runit();


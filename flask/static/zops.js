/**
 * User: Evren Esat Ozkan
 * Date: 24/12/14
 * Time: 14:22
 */

var opts = {
  lines: 12, // The number of lines to draw
  angle: 0.15, // The length of each line
  lineWidth: 0.44, // The line thickness
  pointer: {
    length: 0.9, // The radius of the inner circle
    strokeWidth: 0.035, // The rotation offset
    color: '#000000' // Fill color
  },
  limitMax: 'false',   // If true, the pointer will not go past the end of the gauge
  colorStart: '#6FADCF',   // Colors
  colorStop: '#8FC0DA',    // just experiment with them
  strokeColor: '#E0E0E0',   // to see which ones work best for you
  generateGradient: true
};
var target = document.getElementById('foo'); // your canvas element
var gauge = new Gauge(target).setOptions(opts); // create sexy gauge!
gauge.maxValue = 5000; // set max gauge value
gauge.animationSpeed = 32; // set animation speed (32 is default value)


function updateGauge(value){
    gauge.set(parseInt(value)); // set actual value
}
function runit() {
    oboe('/data.json').node('{RPS}', function (data) {

        console.log(data)
        updateGauge(data.RPS)

    });
}

runit();

import os
from flask import Response, Flask
from stats_generator import StatsGenerator

app = Flask(__name__)
app.debug = os.environ.get('DEBUGMODE', '') != ''

if os.environ.get('USE_PYCOUNTERS') == '1':
    # pycounter's import has side effects :(
    # immediately creates a thread which crashes the server when combined with gevent
    from pycount import occurrence
else:
    occurrence = lambda m: 0


@app.route("/load")
def ping():
    occurrence("requests_frequency")
    return "HINNNN.."


@app.route('/data.json')
def data_visulation():
    # returns a streaming json data for monitoring webserver software's status
    sg = StatsGenerator()
    return Response(sg.generate_stats(), mimetype='application/json')


if __name__ == "__main__":
    app.run(host='0.0.0.0')

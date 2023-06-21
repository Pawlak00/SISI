from flask import Flask
from tensorflow.keras.models import load_model
import tensorflow as tf 
import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS

bucket = "org"
org = "org"
url = "http://localhost:8086"
token = "1DY5ZHHn8I-ggzazl3BJMzgl8u-RkTmPbRxUbCYl1v-bj7UWlNlOhgfHqDZvJ8Zc779IzD8mfmczGBr4lNUwKQ=="

client = influxdb_client.InfluxDBClient(
   url=url,
   token=token,
   org=org
)

query_api = client.query_api()

app = Flask(__name__)
model = None


def make_influx_call(id):
    
    query = 'from(bucket:"org")\
        |> range(start: -200m)\
        |> filter(fn:(r) => r._measurement == "{id}")'.format(id = id)
    print(query)
    result = query_api.query(org=org, query=query)
    results = []
    for table in result:
        for record in table.records:
            results.append(record.get_value())
    results = tf.constant([[results[-12:]]], dtype= float)
    results = tf.reshape(results, (1, 12,1))
    return results 

@app.route("/predict/<string:container_id>", methods=['POST'])
def predict(container_id):
    input = make_influx_call(container_id)
    output = model.predict(input)
    return output.tolist()


if __name__ == '__main__':
    try:
        port = int(sys.argv[1]) # This is for a command-line argument
    except:
        port = 12345 # If you don't provide any port then the port will be set to 12345
   
    # load model
    model = load_model('model.h5')
    app.run(port=port, debug=True)

from influxdb import InfluxDBClient

def writeInfluxDBPoint(influxServer, influxPort):

    client = InfluxDBClient(host=influxServer, port=influxPort)
    client.switch_database('fritzbox')
    
    json_body = [
        {
            "measurement": "ains",
            "tags": {
                "ain": "087610010433",
                "name": "FRITZ!DECT Wohnzimmer"
            },
            #"time": "2018-03-28T8:01:00Z",
            "fields": {
                "temperature": 25.5,
                "power": 850
            }
        }
    ]
    client.write_points(json_body)

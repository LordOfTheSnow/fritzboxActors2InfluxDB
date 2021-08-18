from influxdb import InfluxDBClient
from FritzActor import *

def writeInfluxDBPoint(influxDbClient, fritzActor):
  
    json_body = [
        {
            "measurement": "ains",
            "tags": {
                "ain": fritzActor.ain,
                "name": fritzActor.name
            },
            "fields": {
                "temperature": fritzActor.temp,
                "power": fritzActor.power,
                "energy": fritzActor.energy
            },
            "time": fritzActor.timestamp
        }
    ]
    influxDbClient.write_points(json_body)

from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from influxdb_client.domain.write_precision import *
from FritzActor import *

def writeInfluxDBPoint(influxDbClient, bucket, fritzActor):

    with influxDbClient.write_api() as write_api:

        dict_structure = {
            "measurement": "ains",
            "tags": {
                "ain": fritzActor.ain,
                "name": fritzActor.name
            },
            "fields": {
                "temperature": fritzActor.temp,
                "power": fritzActor.power,
                "energy": fritzActor.energy,
                "state": fritzActor.state
            },
            "time": fritzActor.timestamp
        }
        point = Point.from_dict(dict_structure, WritePrecision.MS)
        write_api.write(bucket=bucket, record=point)

    # json_body = [
    #     {
    #         "measurement": "ains",
    #         "tags": {
    #             "ain": fritzActor.ain,
    #             "name": fritzActor.name
    #         },
    #         "fields": {
    #             "temperature": fritzActor.temp,
    #             "power": fritzActor.power,
    #             "energy": fritzActor.energy,
    #             "state": fritzActor.state
    #         },
    #         "time": fritzActor.timestamp
    #     }
    # ]

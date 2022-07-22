import sys
import logging
from datetime import datetime
from dotenv import load_dotenv
import os 

from FritzActor import *
from fritzUtils import *
from Influx import *

from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

def main():
    # read fritz.box credentials and config values from enviroment variables from file ".env"
    load_dotenv()
    fritzUrl=os.environ.get('fritzUrl', default="http://fritz.box")
    fritzUser=os.environ.get('fritzUser')
    fritzPassword=os.environ.get('fritzPassword')
  
    # logging
    loglevel = eval(os.environ.get('loglevel', default="logging.INFO"))
    logfilename = os.environ.get('logfilename', default="fritz.log")
    logging.basicConfig(filename=logfilename, level=loglevel, format='%(asctime)s %(levelname)s %(name)s %(message)s', datefmt='%d.%m.%Y %H:%M:%S')

    if (not (fritzUrl and fritzUser and fritzPassword) ):
        logging.exception("FritzBox URL and/or FritzBox login credentials are missing. Program terminated.")
        sys.exit("FritzBox URL and/or FritzBox login credentials are missing. Program terminated.")

    influxVersion=os.environ.get("influxVersion", default=2)

    # read InfluxDB config values from file ".env"
    influxServer=os.environ.get('influxServer')
    influxPort=os.environ.get("influxPort", default=8086)
    influxDbName=os.environ.get("influxDbName", default="fritzbox")
    influxRetentionPolicy=os.environ.get("influxRetentionPolicy")

    influxUrl=os.environ.get('INFLUXDB_V2_URL')

    # get the session id from the FritzBox that is needed for all later commands
    SID = getFritzBoxSID(url=fritzUrl, user=fritzUser, password=fritzPassword)
    if (SID == "0000000000000000"):
        print (f"SID: {SID}")
        sys.exit("No valid session id retrieved, probably the login credentials are incorrect.")  

    # create empty list to be filled with the FritzBox actors (the FritzBox power sockets) later
    fritzActors = []

    # now get the ids (AINs) of all power sockets
    command = f"{fritzUrl}webservices/homeautoswitch.lua?switchcmd=getswitchlist&sid={SID}"
    fritzAINs = sendFritzRequest(command).split(",")

    utcnow = datetime.utcnow() # current date and time (in UTC to avoid ambiguties with InfluxDB), save for all looped calls to have the same time for each request for all AINs
    logging.debug(f"utcnow: {utcnow}")

    # loop over each power socket
    for fritzAIN in fritzAINs:

        # get the name 
        command = f"{fritzUrl}webservices/homeautoswitch.lua?switchcmd=getswitchname&ain={fritzAIN}&sid={SID}"
        ain_name = sendFritzRequest(command)

        # get the state
        command = f"{fritzUrl}webservices/homeautoswitch.lua?switchcmd=getswitchstate&ain={fritzAIN}&sid={SID}"
        ain_state = sendFritzRequest(command)

        # get the current temperature (the return value is multiplied by ten, e.g. 25,5° == 255)
        command = f"{fritzUrl}webservices/homeautoswitch.lua?switchcmd=gettemperature&ain={fritzAIN}&sid={SID}"
        ain_temp = sendFritzRequest(command)

        # get the current power consumption in mW
        command = f"{fritzUrl}webservices/homeautoswitch.lua?switchcmd=getswitchpower&ain={fritzAIN}&sid={SID}"
        ain_power = sendFritzRequest(command)

        # get the current energy need in Wh
        command = f"{fritzUrl}webservices/homeautoswitch.lua?switchcmd=getswitchenergy&ain={fritzAIN}&sid={SID}"
        ain_energy = sendFritzRequest(command)

        # create new instance of a FritzActor and initialize it with the values from above
        fritzActor = FritzActor(fritzAIN, ain_name, ain_state, float(ain_temp)/10.0, int(ain_power), int(ain_energy), utcnow.isoformat())
        # append that instance to the list of FritzActors for later use
        fritzActors.append(fritzActor)


    if influxVersion == "1":
        if (not (influxServer and influxPort and influxDbName)):
            logging.exception("InfluxDB configuration parameters are missing. Program terminated.")
            sys.exit("InfluxDB configuration parameters are missing. Program terminated.")

        bucket = influxDbName
        if influxRetentionPolicy:
            bucket += "/" + influxRetentionPolicy
        with InfluxDBClient(url=f"http://{influxServer}:{influxPort}", org='-') as influxDbClient:

            for fritzActor in fritzActors:
                print (f"ain: {fritzActor.ain}, name: {fritzActor.name}, state: {fritzActor.state}, temp: {fritzActor.temp} °C, power: {fritzActor.power} mW, energy: {fritzActor.energy}, time (UTC): {fritzActor.timestamp}")
                writeInfluxDBPoint(influxDbClient, bucket, fritzActor)

    # logout, throw away SID
    # make sure to call this because the number of active sessions in a FritzBox is limited
    sendFritzLogout(fritzUrl,SID)


if __name__ == '__main__':
    main()

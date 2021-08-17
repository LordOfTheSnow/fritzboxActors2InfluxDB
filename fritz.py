import sys
import logging
from datetime import datetime
from dotenv import load_dotenv
import os 

from FritzActor import *
from fritzUtils import *
from Influx import *

def main():
    # basic configuration
    logging.basicConfig(filename='fritz.log', level=logging.DEBUG, format='%(asctime)s %(levelname)s %(name)s %(message)s', datefmt='%d.%m.%Y %H:%M:%S')

    # read fritz.box credentials from enviroment variables from file ".env"
    load_dotenv()
    fritzUrl=os.environ.get('fritzUrl')
    fritzUser=os.environ.get('fritzUser')
    fritzPassword=os.environ.get('fritzPassword')

    if (not (fritzUrl and fritzUser and fritzPassword) ):
        logging.exception("FritzBox URL and/or FritzBox login credentials are missing. Program terminated.")
        sys.exit("FritzBox URL and/or FritzBox login credentials are missing. Program terminated.")

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

    now = datetime.now() # current date and time, save for all looped calls to have the same time for each request for all AINs

    # loop over each power socket
    for fritzAIN in fritzAINs:

        # get the name 
        command = f"{fritzUrl}webservices/homeautoswitch.lua?switchcmd=getswitchname&ain={fritzAIN}&sid={SID}"
        ain_name = sendFritzRequest(command)

        # get the current temperature (the return value is multiplied by ten, e.g. 25,5° == 255)
        command = f"{fritzUrl}webservices/homeautoswitch.lua?switchcmd=gettemperature&ain={fritzAIN}&sid={SID}"
        ain_temp = sendFritzRequest(command)

        # get the current power consumption in mW
        command = f"{fritzUrl}webservices/homeautoswitch.lua?switchcmd=getswitchpower&ain={fritzAIN}&sid={SID}"
        ain_power = sendFritzRequest(command)

        # create new instance of a FritzActor and initialize it with the values from above
        fritzActor = FritzActor(fritzAIN, ain_name, float(ain_temp)/10.0, ain_power, now.strftime("%d.%m.%Y, %H:%M:%S"))
        # append that instance to the list of FritzActors for later use
        fritzActors.append(fritzActor)


    for fritzActor in fritzActors:
        print (f"ain: {fritzActor.ain}, name: {fritzActor.name}, temp: {fritzActor.temp} °C, power: {fritzActor.power} mW, time: {fritzActor.timestamp}")




    influxServer = "raspberrypi4"
    influxPort = 8086
    writeInfluxDBPoint(influxServer, influxPort)

    # logout, throw away SID
    # make sure to call this because the number of active sessions in a FritzBox is limited
    sendFritzLogout(fritzUrl,SID)


if __name__ == '__main__':
    main()
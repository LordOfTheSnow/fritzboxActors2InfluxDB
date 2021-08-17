import sys
import logging
from datetime import datetime
from dotenv import load_dotenv
import os 

from FritzActor import *
from fritzUtils import *

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

    SID = getFritzBoxSID(url=fritzUrl, user=fritzUser, password=fritzPassword)
    if (SID == "0000000000000000"):
        print (f"SID: {SID}")
        sys.exit("No valid session id retrieved, probably the login credentials are incorrect.")  

    fritzActors = []

    command = f"{fritzUrl}webservices/homeautoswitch.lua?switchcmd=getswitchlist&sid={SID}"
    fritzAINs = sendFritzRequest(command).split(",")

    now = datetime.now() # current date and time
    for fritzAIN in fritzAINs:
        command = f"{fritzUrl}webservices/homeautoswitch.lua?switchcmd=getswitchname&ain={fritzAIN}&sid={SID}"
        ain_name = sendFritzRequest(command)

        command = f"{fritzUrl}webservices/homeautoswitch.lua?switchcmd=gettemperature&ain={fritzAIN}&sid={SID}"
        ain_temp = sendFritzRequest(command)

        command = f"{fritzUrl}webservices/homeautoswitch.lua?switchcmd=getswitchpower&ain={fritzAIN}&sid={SID}"
        ain_power = sendFritzRequest(command)

        fritzActor = FritzActor(fritzAIN, ain_name, float(ain_temp)/10.0, ain_power, now.strftime("%d.%m.%Y, %H:%M:%S"))
        fritzActors.append(fritzActor)


    for fritzActor in fritzActors:
        print (f"ain: {fritzActor.ain}, name: {fritzActor.name}, temp: {fritzActor.temp} °C, power: {fritzActor.power} mW, time: {fritzActor.timestamp}")

    # logout, throw away SID
    sendFritzLogout(fritzUrl,SID)


if __name__ == '__main__':
    main()
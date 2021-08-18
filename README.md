# fritzboxActors2InfluxDB

## What is it?

This is my first attempt to create a Python script that reads temperature and energy data from AVM's (Fritz!) Smart Plugs (== power switches) FRITZ!DECT 200 (see https://en.avm.de/products/fritzdect/fritzdect-200/).

The main script **fritzGetAINValues.py** is to be called periodically via cron or a similar technique. It will retrieve 
* the AIN (actor identification number?)
* the name of the actor (as given in the Fritz!Box configuration page for smart home devices)
* the current temperature
* the current power consumption in mW
* the overall engery consumption in Wh since initialization or last reset of that actor
* the current timestamp in UTC timezone

It will then store these values in an InfluxDB in a measurement named _ains_.

## Disclaimer

I am not a professional programmer (any more), thus this code will most probably not live up to current standards. Still I tried to write clean code and tried to comment the most important parts to make it easier to understand. Feel free to comment and when possible, I will try to improve it in the future.

**I will take no responsibility whatsoever for any damage that may result by using this code.**

## How it works

### Requirements

* Python 3.7 or higher (may work below 3.7)
* additional Python modules: see reqirements.txt
* Influx DB 1.8 reachable from your network (2.0 may work as well, but is untested)

### Installation

1. Clone the git repository from https://github.com/LordOfTheSnow/fritzboxActors2InfluxDB.git into that 
2. Change to the created directory
3. Create a Python virtual environment with `python3 -m venv venv`
4. Activate that virtual environment with `source venv/bin/activate`
5. Install the required Python modules via pip: `pip install -r requirements.txt`
6. Create a file _.env_ and put in the configuration values

#### Configuration values (.env)

* fritzUrl = "http://fritz.box/" - note the trailing slash!
* fritzUser = "USER WITH SMART HOME RIGHTS"
* fritzPassword = "PASSWORD OF THAT USER"
* influxServer = "hostname of Influx DB Server" - hostname only, no schema, no trailing slash!, e.g. "raspberrypi" or "192.168.178.4"
* influxPort = 8086
* influxDbName = "fritzbox"

The InfluxDB server and the database "fritzbox" have to exist already (well maybe not the database, it might get created on the first write attempt, I am not sure). I used the following influx command to create the InfluxDB:

`create database fritzbox with duration 365d replication 1 shard duration 7d name one_year`

Use shorter values for the _duration_ and _shard duration_ if you want to. (The _duration_ values will determine how long the data will be stored until it will be automatically removed.)


### Usage 

7. From within the virtual environment, call the script with `python fritzGetAINValues.py`.

The script will output the current values for the smart plugs that it finds.


#### Run via periodically via cron

If you want to run this script periodically via cron, you can call the wrapper script **cronscript.sh**.

Call `crontab -e` to edit the cron table (crontab), e.g.: 

```
# m h  dom mon dow   command
*/5 * * * * /home/pi/src/fritzboxActors2InfluxDB/cronscript.sh
```
This will run the command every five minutes. Edit the path to the script to wherever you put it. 
The script assumes you have a Python virtual environment created with `python3 -m venv venv` in the same directory where you checked out the repository. The script will activate the virtual environment, call the Python interpreter with the script and will deactivate the virtual environment then.



### Main subroutine

The script to run is **fritzGetAINValues.py**. All other files just contain helper functions or class definitions.

The script expects various config values in a file called **.env** (for obvious reasons not provided in this repository).




### Files and data created

1. ./fritz.log - Logfile, set the appropriate log level in this line of code in **fritzGetAINValues.py**:

`logging.basicConfig(filename='fritz.log', level=logging.INFO, format='%(asctime)s %(levelname)s %(name)s %(message)s', datefmt='%d.%m.%Y %H:%M:%S')`

This program does output (some) error messages on the console and into the logfile. Set the loglevel to `level=logging.DEBUG` to get more infos.

**WARNING: No log rotation has been implemented yet, so expect a large log file if you do not turn off DEBUG level!**

2. measurement _ains_ in the Influx DB configured under _influxDbName_

```
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
```

## Known bugs & limitations

* Currently database authentiction is not yet supported but most probably will be in the future
* If you grouped your actors in the Fritzbox, this script will most probably fail as groups are found additionally to the individual actors. This will be most probably corrected in the future as well.

## Additional documentation used (German)

* https://avm.de/fileadmin/user_upload/Global/Service/Schnittstellen/AHA-HTTP-Interface.pdf
* https://avm.de/fileadmin/user_upload/Global/Service/Schnittstellen/AVM_Technical_Note_-_Session_ID.pdf
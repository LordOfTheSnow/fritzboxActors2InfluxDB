import requests
import logging
import hashlib
import xml.etree.ElementTree as ET

def sendFritzRequest(url):

    # send request
    fritzResponse = requests.get(url)

    if (fritzResponse.status_code == requests.codes.ok):
        responseText = fritzResponse.text.strip()
        logging.debug('responseText: '+responseText)
        return responseText
    else:
        logging.error("HTTP request [" + url + "] failed with status code " + fritzResponse.status_code)
        fritzResponse.raise_for_status()
        return "" # shouldn't be reached anyway

def getFritzBoxSID(url, user, password):

    ### Login
    ### Get challenge to create response
    command = f"{url}login_sid.lua"
    api_response = sendFritzRequest(command)
    response_xml = ET.fromstring(api_response)

    for item in response_xml.findall('./Challenge'):
        challenge = item.text
    
    ### Create response for Login
    md5 = hashlib.md5()
    md5.update(challenge.encode('utf-16le'))
    md5.update('-'.encode('utf-16le'))
    md5.update(password.encode('utf-16le'))
    response = challenge + '-' + md5.hexdigest()
    
    command = f"{url}login_sid.lua?username={user}&response={response}"
    api_response = sendFritzRequest(command)
    response_xml = ET.fromstring(api_response)

    ### Get SID
    for item in response_xml.findall('./SID'):
        SID = item.text
    logging.debug('SID: '+SID)
    return SID

def sendFritzLogout(fritzUrl,SID):
    # logout, destroy SID
    command = f"{fritzUrl}login_sid.lua?logout=dummy&sid={SID}"
    sendFritzRequest(command)


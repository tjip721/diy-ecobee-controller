# ecobee Remote Controller
# Simple Python script to control ecobee temp remotely for a thermostat
#
import json
import requests
import shelve
import time
import sys

import subprocess
from pyecobee_lib import Ecobee

API_KEY = 'U6aRpYOCBXbAAciG92WHQlHOoh0YZO7u'
API_TOKEN = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IlJFWXhNVEpDT0Rnek9UaERRelJHTkRCRlFqZEdNVGxETnpaR1JUZzRNalEwTmtWR01UQkdPQSJ9.eyJpc3MiOiJodHRwczovL2F1dGguZWNvYmVlLmNvbS8iLCJzdWIiOiJhdXRoMHw2YzNlYmU2YS0wNDE2LTQ4M2MtOTFhOC0xMzkxYzc2NDE2NDciLCJhdWQiOlsiaHR0cHM6Ly9kZXZlbG9wZXItYXBwcy5lY29iZWUuY29tL2FwaS92MSIsImh0dHBzOi8vZWNvYmVlLXByb2QuYXV0aDAuY29tL3VzZXJpbmZvIl0sImlhdCI6MTY4NjYwNDI5NCwiZXhwIjoxNjg2NjA3ODk0LCJhenAiOiJVNmFScFlPQ0JYYkFBY2lHOTJXSFFsSE9vaDBZWk83dSIsInNjb3BlIjoib3BlbmlkIHNtYXJ0V3JpdGUgb2ZmbGluZV9hY2Nlc3MifQ.WuY_6t1TTvFH957A8kcUfnn9cegewmcrPMBC9lkVUFUI9FkqAR5Wq80vao02ui61RihUiPu-qzzzLB3yF8r85hpNwGX5Fiu_fUzF1_3b_ykyAcUgS2K19otAjjkMbiuPB9pfl1xwx8Q0_4Z1PmpnOWlRgEzcwmomUoQEw7akDxKarpx8FZcHVfyCgeTJkq5M9ttrbVuw9bVBOtYhsyI7-5TqtgvJTAjJGrRPh424tTz_vDqy1urJ6em2lwpIXhulU4Gcip1evF2aaJhzXj2dnTQSvQ-WlDKmbi1-AnfMiahIe-7wY5g03epzxlJ-NFd-I2kl7v_xIUp7aUx-uEz0RQ"
refresh_token = "6aPo_99Tx2xkezGLspDl0ZshEbJ4AHglZWhL9-LjtfTEA"

# ecobee API Urls, thermostat identifier and default set temperature
api_url_base = 'https://api.ecobee.com/1/'
auth_url_base = 'https://api.ecobee.com/token'
thermostat_id = 'THERMOSTAT ID'
maxHi = 740
maxLow = 670
ecobeeActualTemp = 0
ecobeeSetTemp = 0
ecobeeMode = ''


def main():
    #Sudo code the behavior I want

    # If a monitored door is ajar for >2 minutes
    # Get the current hi & low setting limits
    # Set the ecobee to hold between those limits

    # If the monitored door is then closed again for 5 minutes resume schedule
    ecobee = Ecobee(config_filename='ecobee.conf')
    my_ecobee = ecobee.get_thermostat(0)
    print(my_ecobee["settings"])
    ecobee.set_hold_temp(0, 75, 63)
    ecobee.send_message(0, "Thermostat currently being set by Raspberry Pi Open Door Manager")
    # ecobee.resume_program(0)


    return



# Function to get thermostat information
def get_thermostat_info():
    update_authorization()
    config = shelve.open('ecobeeConfig')
    current_api_token = config['api_token']

    headers = {'Content-Type': 'application/json',
               'Authorization': 'Bearer {0}'.format(current_api_token)}

    # Get basic thermostat settings
    params = [{"selection":{"selectionType":"thermostats","selectionMatch":thermostat_id,"includeRuntime":True}}]
    params_json = json.dumps(params[0])

    api_url = '{0}thermostat?format=json&body='.format(api_url_base)

    response = requests.get(api_url + params_json, headers=headers)

    if response.status_code == 200:
        resp_dict = json.loads(response.text)
        print('Name: ' + resp_dict['thermostatList'][0]['name'])
        print('Actual Temperature: ' + str(resp_dict['thermostatList'][0]['runtime']['actualTemperature']))
        print('Desired Heating Temperature: ' + str(resp_dict['thermostatList'][0]['runtime']['desiredHeat']))
        print('Desired Cooling Temperature: ' + str(resp_dict['thermostatList'][0]['runtime']['desiredCool']))

        if ecobeeMode == 'heat':
            actualTemperature = int(resp_dict['thermostatList'][0]['runtime']['actualTemperature'])
            desiredTemperature = int(resp_dict['thermostatList'][0]['runtime']['desiredHeat'])
            return actualTemperature,desiredTemperature;
        elif ecobeeMode == 'cool':
            actualTemperature = int(resp_dict['thermostatList'][0]['runtime']['actualTemperature'])
            desiredTemperature = int(resp_dict['thermostatList'][0]['runtime']['desiredCool'])
            return actualTemperature,desiredTemperature;
        elif ecobeeMode == 'off':
            actualTemperature = int(resp_dict['thermostatList'][0]['runtime']['actualTemperature'])
            desiredTemperature = int(resp_dict['thermostatList'][0]['runtime']['actualTemperature'])
            return actualTemperature,desiredTemperature;
    else:
        return -1


# Function to get thermostat mode
def get_thermostat_mode():
    update_authorization()
    config = shelve.open('ecobeeConfig')
    current_api_token = config['api_token']

    headers = {'Content-Type': 'application/json',
                   'Authorization': 'Bearer {0}'.format(current_api_token)}

    # Get basic thermostat settings
    params = [{"selection": {"selectionType": "thermostats", "selectionMatch": thermostat_id, "includeSettings": True}}]
    params_json = json.dumps(params[0])

    api_url = '{0}thermostat?format=json&body='.format(api_url_base)

    response = requests.get(api_url + params_json, headers=headers)

    if response.status_code == 200:
        resp_dict = json.loads(response.text)
        print('HVAC Mode: ' + str(resp_dict['thermostatList'][0]['settings']['hvacMode']))
        return str(resp_dict['thermostatList'][0]['settings']['hvacMode'])
    else:
        return ''

# Function to update ecobee API authorization
def update_authorization():
    # Make a call to see if the current token is valid
    config = shelve.open('ecobeeConfig')
    current_api_token = config['api_token']

    headers = {'Content-Type': 'application/json',
                   'Authorization': 'Bearer {0}'.format(current_api_token)}

    # Get basic thermostat settings
    params = [{"selection": {"selectionType": "thermostats", "selectionMatch": thermostat_id, "includeSettings": True}}]
    params_json = json.dumps(params[0])

    api_url = '{0}thermostat?format=json&body='.format(api_url_base)

    response = requests.get(api_url + params_json, headers=headers)

    if response.status_code == 200:
        print('Current token still valid, returning.')
        return ''
    else:
        current_refresh_token = config['refresh_token']
        params = {'grant_type': 'refresh_token',
                  'refresh_token': current_refresh_token,
                  'client_id': API_KEY}

        response = requests.post(auth_url_base,params=params)

        if response.status_code == 200:
            print('Token was expired, getting new token.')
            print(response.text)
            config['api_token'] = response.json()['access_token']
            config['refresh_token'] = response.json()['refresh_token']
            config.close()
        else:
            print(response.status_code)

# Function to set ecobee temperature
def set_thermostat(setHoldTemperature):
    update_authorization()
    config = shelve.open('ecobeeConfig')
    current_api_token = config['api_token']

    headers = {'Content-Type': 'application/json',
               'Authorization': 'Bearer {0}'.format(current_api_token)}

    params = [{"selection":{"selectionType":"thermostats","selectionMatch":thermostat_id},"functions":[{"type":"setHold","params":{"holdType":"nextTransition","heatHoldTemp":setHoldTemperature,"coolHoldTemp":setHoldTemperature}}]}]
    params_json = json.dumps(params[0])

    api_url = '{0}thermostat?format=json'.format(api_url_base)

    response = requests.post(api_url,params_json,headers=headers)

    if response.status_code == 200:
        print(response.text)
    else:
        print(response.status_code)

# # Setup while loop precondition variables
# prev_millis = int(round(time.time() * 1000))

# perform_update = False

# # Clear Display then Set Values
# draw.rectangle((0, 0, width, height), outline=0, fill=0)
# draw.text((x, top), "Pausing 1m"  , font=fontTitle, fill=255)
# draw.text((x, top + 18),  "Booting up...", font=fontSubtitle, fill=255)
# disp.image(image)
# disp.display()
# time.sleep(.1)


# time.sleep(60)


# try:
#     ecobeeMode = get_thermostat_mode()
#     ecobeeActualTemp, ecobeeSetTemp = get_thermostat_info()
# except Exception as e:
#     # Clear Display then Set Values
#     draw.rectangle((0, 0, width, height), outline=0, fill=0)
#     draw.text((x, top), "Exception", font=fontTitle, fill=255)
#     draw.text((x, top + 20), "Connect error...", font=fontSubtitle, fill=255)
#     disp.image(image)
#     disp.display()
#     time.sleep(.1)


# #Main Execution Loop
# while True:
#     ecobeeActualTempBase = str(ecobeeActualTemp)[0:2]
#     ecobeeActualTempDigits = str(ecobeeActualTemp)[2]

#     if(int(ecobeeActualTempDigits) >= 5):
#         ecobeeActualLCD = int(ecobeeActualTempBase) + 1
#     else:
#         ecobeeActualLCD = int(ecobeeActualTempBase)

#     # Clear Display then Set Values
#     draw.rectangle((0, 0, width, height), outline=0, fill=0)
#     draw.text((x, top), 'Temp: ' + str(ecobeeActualLCD), font=fontTitle, fill=255)

#     if(ecobeeSetTemp == maxHi or ecobeeSetTemp == maxLow):
#         draw.text((x, top + 20), 'Set: ' + str(ecobeeSetTemp)[0:2] + '*' + '  ' + ecobeeMode.title() , font=fontSubtitle, fill=255)
#     else:
#         draw.text((x, top + 20), 'Set: ' + str(ecobeeSetTemp)[0:2] + '  ' + ecobeeMode.title() , font=fontSubtitle, fill=255)

#     disp.image(image)
#     disp.display()
#     time.sleep(.1)

#     millis = int(round(time.time() * 1000))


#     input_state_lower = GPIO.input(18)
#     input_state_raise = GPIO.input(12)

#     try:
#         # Software debouncing
#         if ((millis - prev_millis) > 250):
#             # Cycle through different displays
#             if (input_state_raise == False):
#                 if (ecobeeMode != 'off'):
#                     if((ecobeeSetTemp + 10) > maxHi):
#                         print('Max High Already Set')
#                     else:
#                         ecobeeSetTemp += 10
#                         print('Setting temperature to: ' + str(ecobeeSetTemp))
#                         perform_update = True
#                         prev_millis = int(round(time.time() * 1000))
#                         input_state_raise = False

#             # Trigger action based on current display
#             elif (input_state_lower == False):
#                 if (ecobeeMode != 'off'):
#                     if((ecobeeSetTemp - 10) < maxLow):
#                         print('Max Low Already Set')
#                     else:
#                         ecobeeSetTemp -= 10
#                         print('Setting temperature to: ' + str(ecobeeSetTemp))
#                         perform_update = True
#                         prev_millis = int(round(time.time() * 1000))
#                         input_state_lower = False

#         # Only update actual desired setting every 10 seconds
#         if ((millis - prev_millis) > 10000):
#             if(perform_update == True):
#                 if(ecobeeMode != 'off'):
#                     set_thermostat(ecobeeSetTemp)
#                     time.sleep(4)
#                     ecobeeActualTemp, ecobeeSetTemp = get_thermostat_info()
#                     print('Local ecobee remote temperature setting: ' + str(ecobeeSetTemp))
#                     prev_millis = int(round(time.time() * 1000))
#                     perform_update = False

#                 perform_update = False

#         # Only get thermostat information every 1 minute when active
#         if ((millis - prev_millis) > 60000):
#             ecobeeMode = ''
#             ecobeeMode = get_thermostat_mode()
#             ecobeeActualTemp, ecobeeSetTemp = get_thermostat_info()
#             print('Local ecobee remote temperature setting: ' + str(ecobeeSetTemp))
#             prev_millis = int(round(time.time() * 1000))

#         time.sleep(0.1)
#     except Exception, e:
#         # Clear Display then Set Values
#         draw.rectangle((0, 0, width, height), outline=0, fill=0)
#         draw.text((x, top), "Exception", font=fontTitle, fill=255)
#         draw.text((x, top + 20), "Connect error...", font=fontSubtitle, fill=255)
#         disp.image(image)
#         disp.display()
#         time.sleep(.1)


if __name__ == "__main__":
    main()
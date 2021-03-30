from prometheus_client import start_http_server, Info, Gauge, Histogram
import time
import requests
import datetime
import subprocess

#change with your endpoint
endpoint_url = "http://localhost:8888/status"

#interval between api calls in seconds, dont set too fast to avoid issues
interval = 60

def getBlockTime(last_block, current_block):
    last_Block_time = subprocess.run()
    return True

#function to get data from status endpoint with requests
def fetchStatusEndpoint(endpoint_url):
    r = requests.get(endpoint_url)
    return r.json()

def roundLengthSeconds(time_string):
    date_time = datetime.datetime.strptime(time_string, "%Mm %Ss %fms")
    a_timedelta = date_time - datetime.datetime(1900, 1, 1)
    seconds = a_timedelta.total_seconds()
    return seconds

#function to parse endpoint data into more condensed version
def parseEndpointData(data):
    parsed = {}
    parsed['is_validator'] = 0
    if data['round_length'] == None:
        data['round_length'] = 'N/A'
    else:
        data['round_length'] = str(data['round_length'])
        parsed['is_validator'] = 1

    parsed['round_length_in_seconds'] = 0

    if data['round_length'] != 'N/A':
        parsed['round_length_in_seconds'] = roundLengthSeconds(data['round_length'])

    parsed['general_info'] = {
        'api_version': data['api_version'],
        'chainspec_name': data['chainspec_name'],
        'starting_state_root_hash': data['starting_state_root_hash'],
        'round_length': data['round_length'],
        'build_version': data['build_version']
    }

    parsed['next_upgrade'] = {}
    parsed['is_upgrade_pending'] = 0

    if data['next_upgrade'] == None:
        parsed['next_upgrade']['next_upgrade_activation_point'] = 'N/A'
        parsed['next_upgrade']['next_upgrade_protocol_version'] = 'N/A'
    else:
        parsed['next_upgrade']['next_upgrade_activation_point'] = str(data['next_upgrade']['activation_point'])
        parsed['next_upgrade']['next_upgrade_protocol_version'] = data['next_upgrade']['protocol_version']
        parsed['is_upgrade_pending'] = 1

    parsed['peer_count'] = len(data['peers'])

    try:
        parsed['era_id'] = data['last_added_block_info']['era_id']
    except:
        parsed['era_id'] = 0

    try:
        parsed['height'] = data['last_added_block_info']['height']
    except:
        parsed['height'] = 0

    #add timestamp to general info and upgrade
    try:
        parsed['general_info']['timestamp'] = data['last_added_block_info']['timestamp']
    except:
        parsed['general_info']['timestamp'] = 0

    try:
        parsed['next_upgrade']['timestamp'] = data['last_added_block_info']['timestamp']
    except:
        parsed['next_upgrade']['timestamp'] = 0

    #delete from last_added_block_info as they are now seperated for guages
    del data['last_added_block_info']['era_id']
    del data['last_added_block_info']['height']

    parsed['last_added_block_info'] = data['last_added_block_info']

    return parsed

#set up info metrics

gi = Info('casper_exporter_general_info', 'General Information')
nu = Info('casper_exporter_next_upgrade', 'Information about the next upgrade if available')
labi = Info('casper_exporter_last_added_block_info', 'Casper node last added block info')
pc = Gauge('casper_exporter_peer_count', 'Casper Node Connected Peers')
eid = Gauge('casper_exporter_era_id', 'Casper Node Era ID')
h = Gauge('casper_exporter_height', 'Casper Node Block Height')
iv = Gauge('casper_exporter_is_validator', 'Is node an active validator?')
up = Gauge('casper_exporter_is_upgrade_pending', 'Is there an upgrade waiting to happen?')
rls = Gauge('casper_exporter_round_length_in_seconds', 'Round length in seconds and ms (Unix) as gauge')


#function to  update info metrics
def infoMetrics():
    data = fetchStatusEndpoint(endpoint_url)
    parsed_data = parseEndpointData(data)
    gi.info(parsed_data['general_info'])
    nu.info(parsed_data['next_upgrade'])
    labi.info(parsed_data['last_added_block_info'])
    pc.set(parsed_data['peer_count'])
    eid.set(parsed_data['era_id'])
    h.set(parsed_data['height'])
    iv.set(parsed_data['is_validator'])
    up.set(parsed_data['is_upgrade_pending'])
    rls.set(parsed_data['round_length_in_seconds'])



if __name__ == '__main__':
    # Start up the server to expose the metrics.
    start_http_server(8123)
    # collect data every x seconds
    while True:
        infoMetrics()
        #change interval variable for different time intervals
        time.sleep(interval)
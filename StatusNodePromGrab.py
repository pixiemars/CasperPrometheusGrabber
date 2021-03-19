from prometheus_client import start_http_server, Info
import time
import requests

#change with your endpoint
endpoint_url = "http://localhost:8888/status"

#interval between api calls in seconds, dont set too fast to avoid issues
interval = 60

#function to get data from status endpoint with requests
def fetchStatusEndpoint(endpoint_url):
    r = requests.get(endpoint_url)
    return r.json()

#function to parse endpoint data into more condensed version
def parseEndpointData(data):
    if data['round_length'] == None:
        data['round_length'] = 'N/A'
    else:
        data['round_length'] = str(data['round_length'])
    parsed = {}
    parsed['general_info'] = {
        'api_version': data['api_version'],
        'chainspec_name': data['chainspec_name'],
        'starting_state_root_hash': data['starting_state_root_hash'],
        'round_length': data['round_length'],
        'build_version': data['build_version'],
        'peercount': str(len(data['peers']))
    }
    if data['next_upgrade'] == None:
        parsed['general_info']['next_upgrade_activation_point'] = 'N/A'
        parsed['general_info']['next_upgrade_protocol_version'] = 'N/A'
    else:
        parsed['general_info']['next_upgrade_activation_point'] = str(data['next_upgrade']['activation_point'])
        parsed['general_info']['next_upgrade_protocol_version'] = data['next_upgrade']['protocol_version']

    parsed['last_added_block_info'] = data['last_added_block_info']
    parsed['last_added_block_info']['era_id'] = str(parsed['last_added_block_info']['era_id'])
    parsed['last_added_block_info']['height'] = str(parsed['last_added_block_info']['height'])

    return parsed


#set up info metrics
gi = Info('general_info', 'General Information')
labi = Info('last_added_block_info', 'Last added block info')


#function to  update info metrics
def infoMetrics():
    data = fetchStatusEndpoint(endpoint_url)
    parsed_data = parseEndpointData(data)
    gi.info(parsed_data['general_info'])
    labi.info(parsed_data['last_added_block_info'])


if __name__ == '__main__':
    # Start up the server to expose the metrics.
    start_http_server(8000)
    # collect data every x seconds
    while True:
        infoMetrics()
        #change interval variable for different time intervals
        time.sleep(interval)
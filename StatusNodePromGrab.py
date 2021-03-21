from prometheus_client import start_http_server, Info, Gauge
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
        'build_version': data['build_version']
    }
    if data['next_upgrade'] == None:
        parsed['general_info']['next_upgrade_activation_point'] = 'N/A'
        parsed['general_info']['next_upgrade_protocol_version'] = 'N/A'
    else:
        parsed['general_info']['next_upgrade_activation_point'] = str(data['next_upgrade']['activation_point'])
        parsed['general_info']['next_upgrade_protocol_version'] = data['next_upgrade']['protocol_version']

    parsed['peer_count'] = len(data['peers'])
    parsed['era_id'] = data['last_added_block_info']['era_id']
    parsed['height'] = data['last_added_block_info']['height']

    #delete from last_added_block_info as they are now seperated for guages
    del data['last_added_block_info']['era_id']
    del data['last_added_block_info']['height']

    parsed['last_added_block_info'] = data['last_added_block_info']

    return parsed

#set up info metrics

api_version = Info('casper_exporter_api_version', 'Casper Node API Version')
build_version = Info('casper_exporter_build_version', 'Casper Node Build Version')
chainspec_name = Info('casper_exporter_chainspec_name', 'Casper Node Chainspec Name')
next_upgrade = Info('casper_exporter_next_upgrade', 'Casper Node Next Upgrade')
round_length = Info('casper_exporter_round_length', 'Casper node round length')
ssrh = Info('casper_exporter_starting_state_root_hash', ' Casper Node Starting State Root Hash')
labi = Info('casper_exporter_last_added_block_info', 'Casper node last added block info')
pc = Gauge('casper_exporter_peer_count', 'Casper Node Connected Peers')
eid = Gauge('casper_exporter_era_id', 'Casper Node Era ID')
h = Gauge('casper_exporter_height', 'Casper Node Block Height')


#function to  update info metrics
def infoMetrics():
    data = fetchStatusEndpoint(endpoint_url)
    parsed_data = parseEndpointData(data)
    api_version.info({'api_version': parsed_data['general_info']['api_version']})
    chainspec_name.info({'chainspec_name': parsed_data['general_info']['chainspec_name']})
    next_upgrade.info({
        'next_upgrade_activation_point': parsed_data['general_info']['next_upgrade_activation_point'],
        'next_upgrade_protocol_version': parsed_data['general_info']['next_upgrade_protocol_version']
    })
    round_length.info({'round_length': parsed_data['general_info']['round_length']})
    ssrh.info({'starting_state_root_hash': parsed_data['general_info']['starting_state_root_hash']})
    labi.info(parsed_data['last_added_block_info'])
    pc.set(parsed_data['peer_count'])
    eid.set(parsed_data['era_id'])
    h.set(parsed_data['height'])



if __name__ == '__main__':
    # Start up the server to expose the metrics.
    start_http_server(8123)
    # collect data every x seconds
    while True:
        infoMetrics()
        #change interval variable for different time intervals
        time.sleep(interval)
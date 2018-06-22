import sys
import json
from pprint import pprint
import os



OUTPUT_DIR = 'output/'


def generateConfig(config):
    with open(os.path.join(OUTPUT_DIR, config['fileName']), 'w') as config_file:
        for attr, val in config.items():
            config_file.write(attr + "=" + val + '\n')

def generateTopicMappings(config):
    with open(os.path.join(OUTPUT_DIR, config['fileName']), 'w') as config_file:
        for mapping in config['mappings']:
            config_file.write(mapping['srcTopics'] + " " + mapping['destTopic'] + '\n')
        
        

def main():
    # config = sys.argv[1]
    config = 'config/config.json'

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    with open(config) as f:
        data = json.load(f)
        for controller in data:
            workerConfigs = controller['workerConfig']
            generateConfig(workerConfigs['consumer'])
            generateConfig(workerConfigs['producer'])
            generateConfig(workerConfigs['helix'])
            generateTopicMappings(workerConfigs['topics'])
main()

import sys
import json
import os
from pprint import pprint


OUTPUT_DIR = 'output/'

def generateConfig(config):
    with open(os.path.join(OUTPUT_DIR, config['fileName']), 'w') as config_file:
        for attr, val in config.items():
            config_file.write(attr + "=" + val + '\n')

def generateTopicMappings(config):
    with open(os.path.join(OUTPUT_DIR, config['fileName']), 'w') as config_file:
        for mapping in config['mappings']:
            config_file.write(mapping['srcTopic'] + " " + mapping['destTopic'] + '\n')

def generateServerConfigs(config):

        
        

def main():
    # Configurations for helix controllers/workers
    controllerConfig = 'config/controllerConfig.json'
    # Configurations for zookeeper/kafka servers
    serverConfig = 'config/serverConfig.json'

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    # Generate Controller configurations
    with open(controllerConfig) as f:
        data = json.load(f)
        for controller in data:
            workerConfigs = controller['workerConfig']
            generateConfig(workerConfigs['consumer'])
            generateConfig(workerConfigs['producer'])
            generateConfig(workerConfigs['helix'])
            generateTopicMappings(workerConfigs['topics'])
    
 # Generate Server configurations
    with open(serverConfig) as f:
        data = json.load(f)
        for controller in data:
            workerConfigs = controller['workerConfig']
            generateConfig(workerConfigs['consumer'])
            generateConfig(workerConfigs['producer'])
            generateConfig(workerConfigs['helix'])
            generateTopicMappings(workerConfigs['topics'])
    
    
main()

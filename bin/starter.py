import sys
import json
import os
from pprint import pprint
from subprocess import call
import subprocess
import platform
import time


OUTPUT_DIR = 'output/'
KAFKA_LOGS = '/tmp/kafka-logs/'

def generateConfig(config):
    with open(os.path.join(OUTPUT_DIR, config['fileName']), 'w') as config_file:
        for attr, val in config.items():
            config_file.write(str(attr) + "=" + str(val) + '\n')

def generateTopicMappings(config):
    with open(os.path.join(OUTPUT_DIR, config['fileName']), 'w') as config_file:
        for mapping in config['mappings']:
            config_file.write(mapping['srcTopic'] + " " + mapping['destTopic'] + '\n')

# def generateServerConfigs(config):

    

def generate_config():
    # Configurations for helix controllers/workers
    controllerConfig = 'config/controllerConfig.json'
    # Configurations for zookeeper/kafka servers
    serverConfig = 'config/serverConfig.json'

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

     # Generate Server configurations
    with open(serverConfig) as f:
        data = json.load(f)
        for server in data:
            zoo_conf = server['zooConfig']
            ZOO_PATH = zoo_conf['clientPort'] + "_cluster"
            if not os.path.exists(OUTPUT_DIR + "/" + ZOO_PATH):
                os.makedirs(OUTPUT_DIR + "/" + ZOO_PATH)
            # Generate readable zookeeper filename
            zoo_conf['fileName'] = ZOO_PATH + "/" + "zoo_" + zoo_conf['clientPort'] + ".properties"
            # Generate zookeeper config
            generateConfig(zoo_conf)

            # Loop through each broker managed by zookeeper
            for broker in server['brokersConfig']:
                # Generate readable kafka broker filename
                broker['fileName'] = ZOO_PATH + "/" + str("broker_" + str(server['zooConfig']['clientPort']) + "_" + str(broker['broker.id']) + ".properties")

                # Add the corresponding zookeeper listener
                broker['zookeeper.connect']= "localhost:" + zoo_conf['clientPort']

                # Set path for logs
                broker['log.dirs'] = KAFKA_LOGS + ZOO_PATH + "_" + str(broker['broker.id'])
                # Generate broker config
                generateConfig(broker)

    # Generate Controller configurations
    with open(controllerConfig) as f:
        data = json.load(f)
        for controller in data:
            controller_id = controller['workerConfig']['consumer']['zookeeper.connect'].split(':')[1]
            ZOO_PATH = zoo_conf['clientPort'] + "_cluster"
            if not os.path.exists(OUTPUT_DIR + "/" + ZOO_PATH):
                print(OUTPUT_DIR + "/" + ZOO_PATH + "does not exist! Exiting")
                exit(1)

            if not os.path.exists(OUTPUT_DIR + ZOO_PATH + "/worker/"):
                os.makedirs(OUTPUT_DIR + ZOO_PATH + "/worker/")

            workerConfigs = controller['workerConfig']
           
            workerConfigs['consumer']['fileName'] = ZOO_PATH + '/worker/consumer.properties'
            workerConfigs['producer']['fileName'] = ZOO_PATH + '/worker/producer.properties'
            workerConfigs['helix']['fileName'] = ZOO_PATH + "/worker/helix.properties"
            workerConfigs['topics']['fileName'] = ZOO_PATH + "/worker/topic.mappings"

            generateConfig(workerConfigs['consumer'])
            generateConfig(workerConfigs['producer'])
            generateConfig(workerConfigs['helix'])
            generateTopicMappings(workerConfigs['topics'])
    

# TODO: GET THIS TO WORK
def terminate_clusters():
    call(['dos2unix', 'bin/stop_clusters.sh'])
    p = subprocess.Popen(['sh','bin/stop_clusters.sh'])
    time.sleep(2)
    p.kill()

# Go through output folder and run all clusters       
def run_clusters():
    cluster_dirs = next(os.walk('output'))[1]
    brokers = []
    for cluster in cluster_dirs:
        zoo_properties = ''
        sub_obj = os.listdir(OUTPUT_DIR + cluster)
        for item in sub_obj:
            f_type = item.split('_')[0]
            if f_type == 'broker':
                brokers.append(item)
            elif f_type == 'zoo':
                zoo_properties = item
        print("Running ZooKeeper On Port: " + zoo_properties.split('_')[1].split('.')[0])
        run_zoo(OUTPUT_DIR + cluster + '/' + zoo_properties)
    
    for broker in brokers:
        print("Running Broker under ZooKeeper: " + broker.split('_')[1] + " | broker id: " + broker.split('_')[2].split('.')[0])
        path_to_broker = OUTPUT_DIR + cluster + '/' + broker
        if platform.system() == 'Windows':
            bash_exe = "C:/cygwin64/bin/bash.exe" 
            call([bash_exe, './deploy/kafka/bin/kafka-server-start.sh', '-daemon', path_to_broker])
        else:
            call(['./deploy/kafka/bin/kafka-server-start.sh', '-daemon', path_to_broker])

    

def run_zoo(path_to_config):
    # call(['./deploy/kafka/bin/zookeeper-server-start.sh', '-daemon', path_to_config])
    if platform.system() == 'Windows':
        bash_exe = "C:/cygwin64/bin/bash.exe" 
        call([bash_exe, './deploy/kafka/bin/zookeeper-server-start.sh', '-daemon', path_to_config])
    else:
        call(['./deploy/kafka/bin/zookeeper-server-start.sh', '-daemon', path_to_config])

def main():
    generate_config()
    # terminate_clusters()
    run_clusters()
    

main()

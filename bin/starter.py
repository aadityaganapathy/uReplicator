import sys
import json
import os
from pprint import pprint
from subprocess import call
import subprocess
import platform
import time
import shutil


OUTPUT_DIR = 'output/'
KAFKA_LOGS = '/tmp/kafka-logs/'
sourceClusters = []

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

    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(OUTPUT_DIR)

     # Generate Server configurations
    with open(serverConfig) as f:
        data = json.load(f)
        for server in data:
            zoo_conf = server['zooConfig']
            ZOO_PATH = zoo_conf['clientPort'] + "_cluster"

            # If the directory for the cluster doesn't exist, create one
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
        for controller in data['controllers']:
            controller_id = controller['workerConfig']['consumer']['zookeeper.connect'].split(':')[1]
            srcPort = controller['srcZKPort'].split(':')[1]
            sourceClusters.append(srcPort)
            ZOO_PATH =  srcPort + "_cluster"
            if not os.path.exists(OUTPUT_DIR + "/" + ZOO_PATH):
                print(OUTPUT_DIR + "/" + ZOO_PATH + "does not exist! Exiting")
                exit(1)

            if not os.path.exists(OUTPUT_DIR + ZOO_PATH + "/controller/"):
                os.makedirs(OUTPUT_DIR + ZOO_PATH + "/controller/")

            workerConfigs = controller['workerConfig']
           
            workerConfigs['consumer']['fileName'] = ZOO_PATH + '/controller/consumer.properties'
            workerConfigs['producer']['fileName'] = ZOO_PATH + '/controller/producer.properties'
            workerConfigs['helix']['fileName'] = ZOO_PATH + "/controller/helix.properties"
            workerConfigs['topics']['fileName'] = ZOO_PATH + "/controller/topicmapping.properties"

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
    for cluster in cluster_dirs:
        brokers = []
        zoo_properties = ''
        sub_obj = os.listdir(OUTPUT_DIR + cluster)

        # Find the zookeeper file, and put all broker files in a list for later
        for item in sub_obj:
            f_type = item.split('_')[0]
            if f_type == 'broker':
                brokers.append(item)
            elif f_type == 'zoo':
                zoo_properties = item
        print("Running ZooKeeper On Port: " + zoo_properties.split('_')[1].split('.')[0])
        run_zoo(OUTPUT_DIR + cluster + '/' + zoo_properties)
  
    
        # Run all the brokers
        for broker in brokers:
            print("Running Broker under ZooKeeper: " + broker.split('_')[1] + " | broker id: " + broker.split('_')[2].split('.')[0])
            # print(broker)
            path_to_broker = OUTPUT_DIR + cluster + '/' + broker
            if platform.system() == 'Windows':
                bash_exe = "C:/cygwin64/bin/bash.exe" 
                call([bash_exe, './deploy/kafka/bin/kafka-server-start.sh', '-daemon', path_to_broker])
            else:
                # print('running', path_to_broker)
                subprocess.call('./deploy/kafka/bin/kafka-server-start.sh -daemon ' + path_to_broker, shell=True)

    

def run_zoo(path_to_config):
    if platform.system() == 'Windows':
        bash_exe = "C:/cygwin64/bin/bash.exe" 
        call([bash_exe, './deploy/kafka/bin/zookeeper-server-start.sh', '-daemon', path_to_config])
    else:
        return_code = subprocess.call("./deploy/kafka/bin/zookeeper-server-start.sh -daemon " + path_to_config, shell=True)

def run_controllers():
    # run controller
    print('Running Controller')
    subprocess.call("nohup ./bin/pkg/start-controller-example1.sh config/controllerConfig.json > /dev/null 2>&1 &", shell=True)

    # subprocess.call("./bin/pkg/start-worker-example1.sh 2183_cluster", shell=True)

def run_workers():
    print('Running Workers')
    for port in sourceClusters:
        print("PORT: " + port)
        cmd = "nohup ./bin/pkg/start-worker-example1.sh " + port + "_cluster"
        print(cmd)
        subprocess.call("nohup ./bin/pkg/start-worker-example1.sh " + port + "_cluster > /dev/null 2>&1 &", shell=True)

def init():
    subprocess.call("cp bin/start-controller-example1.sh bin/pkg", shell=True)
    subprocess.call("cp bin/start-worker-example1.sh bin/pkg", shell=True)

def terminate_clusters():
     subprocess.call("./bin/pkg/stop-all.sh", shell=True)

def main():
    init()
    terminate_clusters()
    generate_config()
    
    run_clusters()
    run_controllers()
    run_workers()

    

main()

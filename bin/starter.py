import sys
import json
import os
from pprint import pprint
from subprocess import call
import subprocess
import platform
import time
import shutil
from collections import OrderedDict


OUTPUT_DIR = 'output/'
KAFKA_LOGS = '/tmp/kafka-logs/'
sourceClusters = []

def generateConfig(config):
    with open(os.path.join(OUTPUT_DIR, config['fileName']), 'w') as config_file:
        for attr, val in config.items():
            config_file.write(f"{str(attr)}={str(val)}\n")

def generateTopicMappings(config):
    with open(os.path.join(OUTPUT_DIR, config['fileName']), 'w') as config_file:
        for mapping in config['mappings']:
            config_file.write(f"{mapping['srcTopic']} {mapping['destTopic']}\n")

def generate_config():
    # Configurations for helix controllers/workers
    controllerConfig = 'config/controllerConfig.json'
    # Configurations for zookeeper/kafka servers
    serverConfig = 'config/serverConfig.json'

    # Clear directory
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(OUTPUT_DIR)

    # Generate Server configurations
    with open(serverConfig) as f:
        data = json.load(f)
        for server in data:
            zoo_conf = server['zooConfig']
            ZOO_PATH = f"{zoo_conf['clientPort']}_cluster"
            # If the directory for the cluster doesn't exist, create one
            if not os.path.exists(f"{OUTPUT_DIR}{ZOO_PATH}"):
                os.makedirs(f"{OUTPUT_DIR}{ZOO_PATH}")
            # Generate readable zookeeper filename
            zoo_conf['fileName'] = f"{ZOO_PATH}/zoo_{zoo_conf['clientPort']}.properties"
            # Generate zookeeper config
            generateConfig(zoo_conf)

            # Loop through each broker managed by zookeeper
            for broker in server['brokersConfig']:
                # Generate readable kafka broker filename
                broker['fileName'] = f"{ZOO_PATH}/broker_{str(server['zooConfig']['clientPort'])}_{str(broker['broker.id'])}.properties"
                # Add the corresponding zookeeper listener
                broker['zookeeper.connect']= f"localhost:{zoo_conf['clientPort']}"
                # Set path for logs
                broker['log.dirs'] = f"{KAFKA_LOGS}{ZOO_PATH}_{str(broker['broker.id'])}"
                # Generate broker config
                generateConfig(broker)

    # Generate Controller configurations
    with open(controllerConfig) as f:
        data = json.load(f)
        for controller in data['controllers']:
            srcPort = controller['srcZKPort'].split(':')[1]
            sourceClusters.append(srcPort)
            generate_controller(controller)
    

# Go through output folder and run all clusters       
def run_clusters():
    cluster_dirs = next(os.walk('output'))[1]
    # count = 0;
    for cluster in cluster_dirs:
        brokers = []
        zoo_properties = ''
        sub_obj = os.listdir(f"{OUTPUT_DIR}{cluster}")

        # Find the zookeeper file, and put all broker files in a list for later
        for item in sub_obj:
            f_type = item.split('_')[0]
            if f_type == 'broker':
                brokers.append(item)
            elif f_type == 'zoo':
                zoo_properties = item
        print(f"Running ZooKeeper On Port: {zoo_properties.split('_')[1].split('.')[0]}")
        run_zoo(f"{OUTPUT_DIR}{cluster}/{zoo_properties}")

        # Run all the brokers
        for broker in brokers:
            print("Running Broker under ZooKeeper: " + broker.split('_')[1] + " | broker id: " + broker.split('_')[2].split('.')[0])
            # print(broker)
            path_to_broker = OUTPUT_DIR + cluster + '/' + broker
            if platform.system() == 'Windows':
                bash_exe = "C:/cygwin64/bin/bash.exe" 
                call([bash_exe, './deploy/kafka/bin/kafka-server-start.sh', '-daemon', path_to_broker])
            else:
                subprocess.call('./deploy/kafka/bin/kafka-server-start.sh -daemon ' + path_to_broker, shell=True)

def run_zoo(path_to_config):
    if platform.system() == 'Windows':
        bash_exe = "C:/cygwin64/bin/bash.exe" 
        call([bash_exe, './deploy/kafka/bin/zookeeper-server-start.sh', '-daemon', path_to_config])
    else:
        subprocess.call("./deploy/kafka/bin/zookeeper-server-start.sh -daemon " + path_to_config, shell=True)

def run_controllers():
    # run controller
    print('Running Controller')
    subprocess.call("nohup ./bin/pkg/start-controller-example1.sh config/controllerConfig.json > /dev/null 2>&1 &", shell=True)

def run_controller(port):
    print("Finding Controller on port: " + port)
    controllerConfig = 'config/controllerConfig.json'
    tempFile = 'config/controller_temp.json'
    with open(controllerConfig) as f:
        data = json.load(f)
        for controller in data['controllers']:
            if controller['controllerPort'] == port:
                print("Found controller!")
                file = open(tempFile, 'w+')
                data = {}
                data['controllers'] = []
                data['controllers'].append(controller)
                json.dump(data, file)

                generate_controller(controller)

                subprocess.call(f"nohup ./bin/pkg/start-controller-example1.sh {tempFile} > /dev/null 2>&1 &", shell=True)
                subprocess.call(f"nohup ./bin/pkg/start-worker-example1.sh {controller['srcZKPort'].split(':')[1]}_cluster > /dev/null 2>&1 &", shell=True)
                exit()
    print("Could not find specified controller")
                

def generate_controller(controller):
        controller_dir = '/controller'
        srcPort = controller['srcZKPort'].split(':')[1]
        
        ZOO_PATH =  srcPort + "_cluster"
        if not os.path.exists(f"{OUTPUT_DIR}{ZOO_PATH}"):
            os.makedirs(f"{OUTPUT_DIR}{ZOO_PATH}")

        path_to_controller = f"{OUTPUT_DIR}{ZOO_PATH}{controller_dir}"
        if not os.path.exists(path_to_controller):
            os.makedirs(path_to_controller)

        workerConfigs = controller['workerConfig']
        worker_base_path = f"{ZOO_PATH}{controller_dir}"

        workerConfigs['consumer']['fileName'] = f"{worker_base_path}/consumer.properties"
        workerConfigs['producer']['fileName'] = f"{worker_base_path}/producer.properties"
        workerConfigs['helix']['fileName'] = f"{worker_base_path}/helix.properties"
        workerConfigs['topics']['fileName'] = f"{worker_base_path}/topicmapping.properties"

        generateConfig(workerConfigs['consumer'])
        generateConfig(workerConfigs['producer'])
        generateConfig(workerConfigs['helix'])
        generateTopicMappings(workerConfigs['topics'])


def run_workers():
    print(f"Running Workers {sourceClusters}")
    for port in sourceClusters:
        subprocess.call(f"nohup ./bin/pkg/start-worker-example1.sh {port}_cluster > /dev/null 2>&1 &", shell=True)

def init():
    subprocess.call("cp bin/start-controller-example1.sh bin/pkg", shell=True)
    subprocess.call("cp bin/start-worker-example1.sh bin/pkg", shell=True)

def terminate_clusters():
     subprocess.call("./bin/pkg/stop-all.sh", shell=True)

def main():
    init()
    options = OrderedDict()
    options['generate_config'] = generate_config
    options['run_clusters'] = run_clusters
    options['run_controllers'] = run_controllers
    options['run_workers'] = run_workers

    if sys.argv[1] == "run_all":
       [value()  for key, value in options.items()]
    elif sys.argv[1] == "run_controller":
        run_controller(sys.argv[2])
    else:
        options[sys.argv[1]]()

main()

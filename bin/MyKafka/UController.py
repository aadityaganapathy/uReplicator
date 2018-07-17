import json
import requests
import glob
import os
from subprocess import call, Popen, PIPE
from MyKafka.ConfigCursor import ConfigCursor

# TODO: Create get_worker_configs function

class UController():
    def __init__(self, controller_configs, config_cursor):
        self.controller_configs = controller_configs
        self.config_cursor = config_cursor
        self.config_cursor.generate_controller_config(controller_configs)
    
    def connect_controllers(self, controllers=[], key=''):
        """Establish connection to all Helix controllers"""
        if len(controllers) > 0 and len(key) > 0:
            controller_configs = self.__get_controller_configs(controllers=controllers, key=key)
        self.__run_controllers(controller_configs)

    def whitelist_topics(self, topics, controllerPorts=[]):
        """Whitelist topics to be mirrored"""
        if(len(controllerPorts) == 0):
            controllerPorts = self.__get_all_controller_ports()
        response = {}
        for port in controllerPorts:
            response[port] = {'success': [], 'failed': []}
            for topic in topics:
                res = self.__whitelist_topic(topic, port, partitions=8)
                if res:
                    response[port]['success'].append(topic)
                else:
                    response[port]['failed'].append(topic)
        print(response)
        return response
        
    def blacklist_topics(self, topics, controllerPorts=[]):
        """Blacklist topics from being mirrored"""
        if(len(controllerPorts) == 0):
            controllerPorts = self.__get_all_controller_ports()
        for port in controllerPorts:
            for topic in topics:
                self.__blacklist_topic(topic, port)

    def run_workers(self, controllerPort, worker_count):
        """Run 'worker_count' number of workers"""
        self.remove_workers()
        self.__delete_worker_configs(controllerPort)
        self.__generate_worker_configs(controllerPort, worker_count, offset=0)
        self.__run_worker_instances(controllerPort)
        

    def add_workers(self, workers_count):
        print("")

    def remove_workers(self, workers_count=-1):
        """Remove specified number of workers, or all workers if workers_count is omitted"""
        worker_pids = self.get_worker_pids()
        if workers_count > 0:
            worker_pids = worker_pids[:workers_count]

        for pid in worker_pids:
            print(f"kill -9 {pid}")
            call(f"kill -9 {pid}")

    def get_worker_count(self):
        """Return the number of workers currently running"""
        return len(self.get_worker_pids())

    def get_worker_pids(self):
        """Return the pids of all workers"""
        proc1 = Popen("pgrep -f 'Dapp_name=uReplicator-Worker'", shell=True, stdout=PIPE)
        out = proc1.communicate()[0]
        out = out.decode("utf-8").split("\n")[:-2] # [:-2] because empty string and some non PID number is included in list
        return out

    def __run_worker_instances(self, controllerPort):
        helix_configs = self.__get_worker_configs(controllerPort)
        output_path = self.__get_controller_path(controllerPort)
        for helix_config in helix_configs:
            print(f"nohup ./bin/pkg/start-worker-example1.sh {output_path} {helix_config} > /dev/null 2>&1 &")
            call(f"nohup ./bin/pkg/start-worker-example1.sh {output_path} {helix_config} > /dev/null 2>&1 &", shell=True)

    def __get_worker_configs(self, controllerPort):
        controller_path = self.__get_controller_path(controllerPort)
        return glob.glob(f"{controller_path}/helix*")

    def __generate_worker_configs(self, controllerPort, worker_count, offset=0):
        controller_json = self.__get_controller_configs(controllers=[controllerPort], key="controllerPort")[0]
        output_path = self.__get_controller_path(controllerPort)
        for count in range(offset, worker_count + offset):
            with open(os.path.join(output_path, f"helix_{count}.properties"), 'w') as config_file:
                config_file.write(f"zkServer={controller_json['srcZKPort']}\n")
                config_file.write(f"instanceId=helixWorker_{count}\n")
                config_file.write(f"helixClusterName={controller_json['controllerName']}\n")

    def __delete_worker_configs(self, controllerPort):
        """Deletes all worker configs (helix.properties) for the specified controller"""
        controller_path = self.__get_controller_path(controllerPort)
        for filename in glob.glob(f"{controller_path}/helix*"):
            os.remove(filename) 

    def __get_all_controller_ports(self):
        controllers_json_list = self.__get_controller_configs()
        ports = list()
        for controller in controllers_json_list:
            ports.append(controller['controllerPort'])
        return ports

    def __whitelist_topic(self, topic, port, partitions=8):
        topic_data = {"topicName": topic, "numPartitions": partitions}
        print(f"CURL -d POST {json.dumps(topic_data)} http://localhost:{port}/topics")
        try:
            res = requests.post(f"http://localhost:{port}/topics", data=json.dumps(topic_data))
            print(res.status_code)
        except requests.exceptions.RequestException:
            print(f"Could not connect to controller on port {port}")
            res = None
        return res

    def __blacklist_topic(self, topic, port):
        print(f"CURL -X DELETE http://localhost:{port}/topics/{topic}")
        try:
            res = requests.delete(f"http://localhost:{port}/topics")
            print(res.status_code)
        except requests.exceptions.RequestException:
            print(f"Could not connect to controller on port {port}")
            res = None
        return res

    def __run_controllers(self, controllers):
        """Function to run all specified controllers"""
        for controller in controllers:
            src_cluster_port = controller['srcZKPort'].split(":")[-1]
            path = f"{self.__get_controller_path(controller['controllerPort'])}/controllerConfig.json"
            call(f"nohup ./bin/pkg/start-controller-example1.sh {path} {src_cluster_port} > /dev/null 2>&1 &", shell=True)

    def __get_controller_configs(self, controllers=[], key=""):
        """Returns list of controller configs as JSON"""
        controllers_json = list()
        with open(self.controller_configs) as f:
            data = json.load(f)
            for controller in data['controllers']:
                if len(controllers) == 0 or int(controller[key]) in controllers or str(controller[key]) in controllers:
                    controllers_json.append(controller)
        return controllers_json

    def __get_controller_path(self, controllerPort):
        controller_json = self.__get_controller_configs(controllers=[controllerPort], key='controllerPort')[0]
        src_cluster_port = controller_json['srcZKPort'].split(":")[-1]
        path = f"{self.config_cursor.get_output_config_path(src_cluster_port)}/controller"
        return path
        
            





    
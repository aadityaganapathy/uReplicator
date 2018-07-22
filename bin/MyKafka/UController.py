import json, requests, glob, os
import time
from subprocess import call, Popen, PIPE
from MyKafka.ConfigCursor import ConfigCursor
from MyKafka.ULogger import ULogger


class UController():
    def __init__(self, controller_configs, config_cursor):
        self.controller_configs = controller_configs
        self.config_cursor = config_cursor
        self.config_cursor.generate_controller_config(controller_configs)
        self.logger = ULogger()
    
    def connect_controllers(self, controllerPorts=None):
        """Establish connection to all Helix controllers"""
        if controllerPorts == None:
            controllerPorts = self.__get_all_controller_ports()

        # We only want the controller ports that are not currently running
        controllerPorts = self.get_offline_controllers(controllerPorts=controllerPorts)

        if len(controllerPorts) > 0:
            controller_configs = self.__get_controller_configs(controllerPorts=controllerPorts)
            self.__run_controllers(controller_configs)
            self.__poll_controllers(controllerPorts)
    
    def get_controllers(self):
        controllers = []
        ports = self.__get_all_controller_ports()
        for port in ports:
            controller = {}
            controller_json = self.__get_controller_configs(controllerPorts=[port])[0]
            controller['srcZKPort'] = controller_json['srcZKPort']
            controller['destZKPort'] = controller_json['destZKPort']
            controller['controllerName'] = controller_json['controllerName']
            controller['controllerPort'] = port
            controller['controllerActive'] = self.controller_running(port)
            controller['activeWorkers'] = self.get_worker_count(port)
            controller['topics'] = self.get_topics(port)
            controllers.append(controller)
        return controllers

    def get_topics(self, controllerPort):
        """Returns all whitelisted topics"""
        if self.controller_running(controllerPort):
            topics = requests.get(f"http://localhost:{controllerPort}/topics")
            # a little tricky since uReplicator returns a sentence (e.g 'currently serving topics [topic1, topic2]')
            # so do some manipulation to extract the list
            content = topics.content.decode("utf-8")
            list_string_form = content[content.index('['):content.index(']')+1]
            csv = list_string_form.strip('[]')
            return csv.split(',')
        else:
            self.logger.log_inactive_controller(controllerPort)

    def whitelist_topics(self, topics, controllerPort):
        """Whitelist topics to be mirrored"""
        if self.controller_running(controllerPort):
            for topic in topics:
                self.__whitelist_topic(topic, controllerPort, partitions=8)
        else:
            self.logger.log_inactive_controller(controllerPort)

    def blacklist_topics(self, topics, controllerPort):
        """Blacklist topics from being mirrored"""
        if self.controller_running(controllerPort):
            for topic in topics:
                self.__blacklist_topic(topic, controllerPort)
        else:
            self.logger.log_inactive_controller(controllerPort)

    def run_workers(self, controllerPort, worker_count):
        """Run worker_count number of workers"""
        self.remove_workers(controllerPort)
        self.__delete_worker_configs(controllerPort)
        self.__generate_worker_configs(controllerPort, worker_count, offset=0)
        self.__run_worker_instances(controllerPort)

    def add_workers(self, workers_count):
        print("")

    def remove_controller(self, controllerPort):
        """Shuts down the specified controller"""
        if self.controller_running(controllerPort):
            controller_pid = self.__get_controller_pid(controllerPort)
            call(f"kill -9 {controller_pid}", shell=True)
            print(f"INFO: Killed controller on port {controllerPort}")
            self.remove_workers(controllerPort)
        else:
            self.logger.log_inactive_controller(controllerPort, status="INFO")

    def remove_workers(self, controllerPort, workers_count=-1):
        """Removes specified number of workers, or all workers if workers_count is omitted"""
        worker_pids = self.__get_worker_pids(controllerPort)
        if workers_count > 0:
            worker_pids = worker_pids[:workers_count]
        elif workers_count > len(worker_pids):
            self.logger.log_invalid_worker_input_count(len(worker_pids), workers_count)
            return

        for pid in worker_pids:
            call(f"kill -9 {pid}", shell=True)
        print(f"INFO: Killed {len(worker_pids)} workers from controller on port {controllerPort}")

    def get_worker_count(self, controllerPort):
        """Returns the number of workers currently running"""
        return len(self.__get_worker_pids(controllerPort))

    def controller_running(self, port):
        """Returns true if the specified controller is running, false otherwise"""
        try:
            requests.get(f"http://localhost:{port}/topics") 
            return True
        except requests.exceptions.RequestException:
            return False

    def get_offline_controllers(self, controllerPorts=None):
        """Returns a list of inactive controllers"""
        if controllerPorts == None:
            controllerPorts == self.__get_all_controller_ports()
        for port in controllerPorts:
            if self.controller_running(port):
                self.logger.log_active_controller(port)
                controllerPorts.remove(port)
        return controllerPorts

    
    def __get_worker_pids(self, controllerPort):
        """Returns the pids of all workers"""
        proc1 = Popen(f"pgrep -f 'Dapp_name=uReplicator-Worker_{controllerPort}'", shell=True, stdout=PIPE)
        out = proc1.communicate()[0]
        out = out.decode("utf-8").split("\n")[:-2] # [:-2] because empty string and some non PID number is included in list
        return out

    def __get_controller_pid(self, controllerPort):
        """Returns the pids of all workers"""
        proc1 = Popen(f"pgrep -f 'Dapp_name=uReplicator-Controller_{controllerPort}'", shell=True, stdout=PIPE)
        out = proc1.communicate()[0]
        out = out.decode("utf-8").split('\n')[0]
        return out

    def __run_worker_instances(self, controllerPort):
        """Runs the workers attatched to a controller"""
        helix_configs = self.__get_worker_configs(controllerPort)
        output_path = self.__get_controller_path(controllerPort)
        for helix_config in helix_configs:
            print(f"nohup ./bin/pkg/start-worker-example1.sh {output_path} {helix_config} uReplicator-Worker_{controllerPort} > /dev/null 2>&1 &")
            call(f"nohup ./bin/pkg/start-worker-example1.sh {output_path} {helix_config} uReplicator-Worker_{controllerPort} > /dev/null 2>&1 &", shell=True)

    def __get_worker_configs(self, controllerPort):
        """Returns all helix_*.properties paths for a specified controller """
        controller_path = self.__get_controller_path(controllerPort)
        return glob.glob(f"{controller_path}/helix*")

    def __generate_worker_configs(self, controllerPort, worker_count, offset=0):
        """Generates the helix_*.properties files"""
        controller_json = self.__get_controller_configs(controllerPorts=[controllerPort])[0]
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
        """Returns a list of all controller ports"""
        controllers_json_list = self.__get_controller_configs()
        ports = list()
        for controller in controllers_json_list:
            ports.append(controller['controllerPort'])
        return ports

    def __whitelist_topic(self, topic, port, partitions=8):
        topic_data = {"topic": topic, "numPartitions": partitions}
        print(f"EXECUTING: curl -X POST -d '{json.dumps(topic_data)}' http://localhost:{port}/topics")
        try:
            response = requests.post(f"http://localhost:{port}/topics", data=json.dumps(topic_data))
        except requests.exceptions.RequestException:
            self.logger.log_failed_controller_connection(port)
            res = "failed"
        if response.status_code < 300:
            self.logger.log_whitelist_topic(topic)
            res = "success"
        else:
            if self.__topic_whitelisted:
                self.logger.log_repeat_whitelist_topic(topic)
            else:
                self.logger.log_failed_whitelist_topic(topic)
            res = "failed"
        return res

    def __topic_whitelisted(self, topic, port):
        topics = self.get_topics(port)
        if topic in topics:
            return True
        return False

    def __blacklist_topic(self, topic, port):
        print(f"DELETE http://localhost:{port}/topics/{topic}")
        try:
            res = requests.delete(f"http://localhost:{port}/topics/{topic}")
        except requests.exceptions.RequestException:
            self.logger.log_failed_controller_connection(port)
            res = None
        return res

    def __run_controllers(self, controllers):
        """Function to run all specified controllers"""
        for controller in controllers:
            path = f"{self.__get_controller_path(controller['controllerPort'])}/controllerConfig.json"
            call(f"nohup ./bin/pkg/start-controller-example1.sh {path} {controller['controllerPort']} > /dev/null 2>&1 &", shell=True)

    def __get_controller_configs(self, controllerPorts=[]):
        """Returns list of controller configs as JSON"""
        controllers_json = list()
        with open(self.controller_configs) as f:
            data = json.load(f)
            for controller in data['controllers']:
                if len(controllerPorts) == 0 or int(controller['controllerPort']) in controllerPorts or str(controller['controllerPort']) in controllerPorts:
                    controllers_json.append(controller)
        return controllers_json

    def __get_controller_path(self, controllerPort):
        controller_json = self.__get_controller_configs(controllerPorts=[controllerPort])[0]
        src_cluster_port = controller_json['srcZKPort'].split(":")[-1]
        path = f"{self.config_cursor.get_output_config_path(src_cluster_port)}/controller"
        return path

    def __poll_controllers(self, controllerPorts):
        retries = 3
        for controllerPort in controllerPorts:
            while self.controller_running(controllerPort) == False and retries >= 0:
                retries -= 1
                time.sleep(0.5)






    
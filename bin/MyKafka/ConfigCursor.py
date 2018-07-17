import os
import json

class ConfigCursor():
    def __init__(self, base_path):
        self.base_path = base_path
   
    def __get_config_file(self, dir, keyword): 
        """Function will find the specific config file (broker config or zookeeper config)"""  
        files = list()
        for config_file in os.listdir(f"{self.base_path}/{dir}"):
            f_type = config_file.split('_')[0]
            if f_type == keyword:
                files.append(f"{self.base_path}/{dir}/{config_file}")
        return files
    
    def __generate_config(self, config):
        """Function will take in json and output a properties file"""
        with open(config['fileName'], 'w') as config_file:
            for attr, val in config.items():
                config_file.write(f"{str(attr)}={str(val)}\n")

    def get_config_files(self, keyword):
        configs = dict()
        for dir in next(os.walk(self.base_path))[1]:
            key = dir.split("_")[0]
            if key not in configs:
                configs[key] = list()
            configs[key] = self.__get_config_file(dir, keyword)     
        return configs
        

    def generate_zoo_config(self, config_file):
        """Generate zookeeper file configurations"""
        with open(config_file) as f:
            data = json.load(f)
            for server in data:
                path_to_dir = self.get_output_config_path(server['zooConfig']['clientPort'])
                self.create_directory(path_to_dir)
                zoo_conf = server['zooConfig']
                zoo_conf['fileName'] = f"{path_to_dir}/zoo_{zoo_conf['clientPort']}.properties"
                self.__generate_config(zoo_conf)
    
    def generate_kafka_config(self, config_file):
        """Generate kafka file configurations"""
        with open(config_file) as f:
            data = json.load(f)
            for server in data:
                path_to_dir = self.get_output_config_path(server['zooConfig']['clientPort'])
                zoo_conf = server['zooConfig']
                for broker in server['brokersConfig']:
                    broker['fileName'] = f"{path_to_dir}/broker_{str(zoo_conf['clientPort'])}_{str(broker['broker.id'])}.properties"
                    broker['zookeeper.connect'] = f"localhost:{zoo_conf['clientPort']}"
                    broker['log.dirs'] = f"/tmp/kafka-logs/{path_to_dir.split('/')[1]}_{str(broker['broker.id'])}"
                    self.__generate_config(broker)

    def generate_controller_config(self, config_file):
        controller_paths = self.__place_controller_configs(config_file)
        self.__place_controller_contents(config_file)
        for controller_path in controller_paths:
            with open(f"{controller_path}/controllerConfig.json") as f:
                data = json.load(f)['controllers'][0]
                workerConfigs = data['workerConfig']
                workerConfigs['consumer']['fileName'] = f"{controller_path}/consumer.properties"
                workerConfigs['producer']['fileName'] = f"{controller_path}/producer.properties"
                workerConfigs['topics']['fileName'] = f"{controller_path}/topicmapping.properties"
                self.__generate_config(workerConfigs['consumer'])
                self.__generate_config(workerConfigs['producer'])
                self.generate_topic_mappings(workerConfigs['topics'])

    def generate_topic_mappings(self, config):
       with open(config['fileName'], 'w') as config_file:
            for mapping in config['mappings']:
                config_file.write(f"{mapping['srcTopic']} {mapping['destTopic']}\n")

    def __place_controller_configs(self, controllers):
        """Function put the controllers in their respective directories"""
        controller_paths = list()
        with open(controllers) as f:
            data = json.load(f)
            for controller in data['controllers']:
                src_cluster_port = controller['srcZKPort'].split(":")[-1]
                path = f"{self.get_output_config_path(src_cluster_port)}/controller"
                self.create_directory(path)
                f = open(f"{path}/controllerConfig.json","w+")
                controller_paths.append(path)
        return controller_paths

    def __place_controller_contents(self, controllers):
        """Function dump the controllers content into their respective files"""
        with open(controllers) as f:
            data = json.load(f)
            for controller in data['controllers']:
                src_cluster_port = controller['srcZKPort'].split(":")[-1]
                path = f"{self.get_output_config_path(src_cluster_port)}/controller"
                file_path = f"{path}/controllerConfig.json"
                file = open(file_path, 'w+')
                self.__dump_controller_data(file, controller)
    
    def __dump_controller_data(self, file, controller_data):
        json_data = {}
        json_data['controllers'] = []
        json_data['controllers'].append(controller_data)
        json.dump(json_data, file, indent=4, sort_keys=True)

    def create_directory(self, dir_path):
        """Function will create the specified directory if it does not exist"""
        if not os.path.exists(f"{dir_path}"):
            os.makedirs(f"{dir_path}")

    def get_output_config_path(self, zk_port):
        """Function will output the configuration directory path for a given zoo/broker config"""
        path = f"{self.base_path}/{zk_port}_cluster"
        return path

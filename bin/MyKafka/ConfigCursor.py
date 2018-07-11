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
                path_to_dir = self.__get_output_config_path(server)
                self.create_directory(path_to_dir)
                zoo_conf = server['zooConfig']
                zoo_conf['fileName'] = f"{path_to_dir}/zoo_{zoo_conf['clientPort']}.properties"
                self.__generate_config(zoo_conf)
    
    def generate_kafka_config(self, config_file):
        """Generate kafka file configurations"""
        with open(config_file) as f:
            data = json.load(f)
            for server in data:
                path_to_dir = self.__get_output_config_path(server)
                zoo_conf = server['zooConfig']
                for broker in server['brokersConfig']:
                    broker['fileName'] = f"{path_to_dir}/broker_{str(zoo_conf['clientPort'])}_{str(broker['broker.id'])}.properties"
                    broker['zookeeper.connect'] = f"localhost:{zoo_conf['clientPort']}"
                    broker['log.dirs'] = f"/tmp/kafka-logs/{path_to_dir.split('/')[1]}_{str(broker['broker.id'])}"
                    self.__generate_config(broker)

    def create_directory(self, dir_path):
        """Function will create the specified directory if it does not exist"""
        if not os.path.exists(f"{dir_path}"):
            os.makedirs(f"{dir_path}")

    def __get_output_config_path(self, config_json):
        """Function will output the configuration directory path for a given zoo/broker config"""
        zoo_conf = config_json['zooConfig']
        path = f"{self.base_path}/{zoo_conf['clientPort']}_cluster"
        return path

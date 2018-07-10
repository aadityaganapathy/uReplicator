import os
import json

class ConfigCursor():
    def __init__(self, base_path):
        self.base_path = base_path
   
    def __get_config_file(self, dir, keyword): 
        # Find the config files
        files = list()
        for config_file in os.listdir(f"{self.base_path}/{dir}"):
            f_type = config_file.split('_')[0]
            if f_type == keyword:
                files.append(f"{self.base_path}/{dir}/{config_file}")
        return files
    
    def __generate_config(self, config):
        with open(os.path.join(self.base_path, config['fileName']), 'w') as config_file:
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
        

    def generate_zoo_config(self, config):
        """Generate zookeeper file configurations"""
        with open(config) as f:
            data = json.load(f)
            for server in data:
                zoo_conf = server['zooConfig']
                ZOO_PATH = f"{zoo_conf['clientPort']}_cluster"
                # If the directory for the cluster doesn't exist, create one
                if not os.path.exists(f"{self.base_path}/{ZOO_PATH}"):
                    os.makedirs(f"{self.base_path}/{ZOO_PATH}")
                # Generate readable zookeeper filename
                zoo_conf['fileName'] = f"{ZOO_PATH}/zoo_{zoo_conf['clientPort']}.properties"
                # Generate zookeeper config
                self.__generate_config(zoo_conf)


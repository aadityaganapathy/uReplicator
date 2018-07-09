import os

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

    def get_config_files(self, keyword):
        configs = dict()
        for dir in next(os.walk('output'))[1]:
            key = dir.split("_")[0]
            if key not in configs:
                configs[key] = list()
            configs[key] = self.__get_config_file(dir, keyword)     
        return configs

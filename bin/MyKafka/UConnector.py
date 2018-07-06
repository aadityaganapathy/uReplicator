import os
from MyKafka.UZoo import UZoo


def get_config_file(base_path, dir): 
    # Find the zookeeper file
    for config_file in os.listdir(f"{base_path}/{dir}"):
        f_type = config_file.split('_')[0]
        if f_type == 'zoo':
            return f"{base_path}/{dir}/{config_file}"

def get_config_files(base_path):
    configs = list()
    for dir in next(os.walk('output'))[1]:
        configs.append(get_config_file(base_path, dir))       
    return configs


class UConnector():
    def __init__(self, path_to_config):
        """Intialize UConnector.
        Args:
            path_to_config (str): Relative path to where all of the cluster configurations are located
        """
        self.path_to_config = path_to_config

    # Spawn all zookeeper instances
    def connect_zoo(self):
        """Function to spawn all the zookeeper instances."""
        configs = get_config_files(self.path_to_config)
        self.u_zoo = UZoo(configs)
        self.u_zoo.start_zookeeper()


    # Spawn all Kafka broker instances
    def connect_kafka(self):
        print("connecting kafka")

    # Spwan all uReplicator helix controller instances
    def run_controllers(self):
        print("connecting controllers")

    # Spawn all uReplicator helix worker instances
    def run_worker(self):
        print("connecting zoo")
import os

from MyKafka.ConfigCursor import ConfigCursor
from MyKafka.UKafka import UKafka
from MyKafka.UZoo import UZoo


class UConnector():
    def __init__(self, path_to_config):
        """Intialize UConnector.
        Args:
            path_to_config (str): Relative path to where all of the cluster configurations are located
        """
        self.path_to_config = path_to_config
        self.config_cursor = ConfigCursor(path_to_config)

    def init_zoo(self):
        """Function to spawn all the zookeeper instances."""
        configs = self.config_cursor.get_config_files('zoo')
        self.u_zoo = UZoo(configs)

    def init_kafka(self):
        """Function to spawn all the kafka broker instances."""
        configs = self.config_cursor.get_config_files('broker')
        self.u_kafka = UKafka(configs)
 
    def run_controllers(self):
        """Spawn all uReplicator helix controller instances"""
        print("connecting controllers")

    def run_worker(self):
        """Spawn all uReplicator helix worker instances"""
        print("connecting zoo")

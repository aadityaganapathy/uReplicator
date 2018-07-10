from subprocess import call
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
        return self.u_zoo

    def init_kafka(self):
        """Function to spawn all the kafka broker instances."""
        configs = self.config_cursor.get_config_files('broker')
        self.u_kafka = UKafka(configs)
        return self.u_kafka
 
    def run_controllers(self):
        """Spawn all uReplicator helix controller instances"""
        print("connecting controllers")

    def run_worker(self):
        """Spawn all uReplicator helix worker instances"""
        print("connecting zoo")

    def start_all(self):
        """Start everything"""
        self.init_zoo()
        self.init_kafka()
        self.run_controllers()
        self.run_worker()

    def stop_all(self):
        """Stop all instances of zookeeper, kafka brokers and helix controllers/workers"""
        call("./bin/stop_clusters.sh && ./bin/pkg/stop-all.sh", shell=True)

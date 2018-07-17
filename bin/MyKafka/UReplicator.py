from subprocess import call
from MyKafka.ConfigCursor import ConfigCursor
from MyKafka.UKafka import UKafka
from MyKafka.UZoo import UZoo
from MyKafka.UController import UController


class UReplicator():
    def __init__(self, controller_configs='', config_json_path='', path_to_config=''):
        """Intialize UConnector.
        Args:
            config_json_path (str): Path the where the JSON file configuration is located
            path_to_config (str): Path to where all of the cluster configurations are located
        """
        if len(config_json_path) == 0 and len(path_to_config) == 0:
            print("Must pass in either JSON config file or config direcotry")
        elif len(config_json_path) > 0:
            self.generate_config(config_json_path, path_to_config)

        self.controller_configs = controller_configs
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
 
    def init_controllers(self):
        """Spawn all uReplicator helix controller instances"""
        self.u_controller = UController(self.controller_configs, self.config_cursor)
        return self.u_controller

    def stop_all(self):
        """Stop all instances of zookeeper, kafka brokers and helix controllers/workers"""
        call("./bin/stop_clusters.sh && ./bin/pkg/stop-all.sh", shell=True)

    def generate_config(self, config_json_path, output_path):
        if len(output_path) == 0:
            print("Invalid output directory path!")
        else:
            config_cursor = ConfigCursor(output_path)
            config_cursor.generate_zoo_config(config_json_path)
            config_cursor.generate_kafka_config(config_json_path)



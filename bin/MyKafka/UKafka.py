import socket
import time
from subprocess import call, Popen, PIPE
from configobj import ConfigObj as ConfigParser
from kafka import KafkaClient, BrokerConnection

class UKafka():
    def __init__(self, configs):
        """This class will maintain a all zookeeper instances

        Args:
            config (list of str): The locations of the <name>.properties files that contatins the broker configurations
        """
        self.configs = configs
        self.connections = dict()

    def start_kafka(self):
        """This function will start up brokers for all clusters"""
        for zoo_port, cluster_configs in self.configs.items():
            for config in cluster_configs:
                config_parser = ConfigParser(config)
                try:
                    listener = config_parser['listeners']
                    port = self.__get_port(listener)
                except KeyError:
                    raise Exception(f"Key 'listeners' does not exist in '{config}'")
                self.__run_kafka_instance(config)
            self.verify_conn(zoo_port, cluster_configs)

    def verify_conn(self, zoo_port, cluster_configs):
        """Function to ensure all brokers have run successfully (and retry connection for failure)
        Args:
            zoo_port (int): The port zookeeper is running on
            cluster_configs (list of str): The list of kafka broker configuration file paths
        """
        active_brokers = self.__poll_kafka_connections(zoo_port, len(cluster_configs), retries=3)
        self.retry_connections(cluster_configs, active_brokers)
        active_brokers = self.__poll_kafka_connections(zoo_port, len(cluster_configs), retries=3)
        if len(active_brokers) != len(cluster_configs):
            print(f"WARNING: {len(cluster_configs)-len(active_brokers)}/{len(cluster_configs)} broker(s) failed to connect")
        else:
            print(f"SUCCESS: {len(active_brokers)}/{len(cluster_configs)} broker(s) sucessfully connected!")

    def retry_connections(self, cluster_configs, active_brokers):
        """Function will attempt to reconnect any inactive brokers"""
        if len(active_brokers) == len(cluster_configs):
            return
        for config in cluster_configs:
            config_parser = ConfigParser(config)
            if str(config_parser['broker.id']) not in active_brokers:
                self.__run_kafka_instance(config)
        
    def get_active_brokers(self, zoo_port):
        """Get the active brokers"""
        cmd = f"echo dump | nc localhost {zoo_port} | grep brokers"
        proc1 = Popen(cmd, shell=True, stdout=PIPE)
        out, err = proc1.communicate()
        active_brokers = [broker.split("/")[-1] for broker in out.decode("utf-8").split("\n")[:-1]]
        return active_brokers

    def __poll_kafka_connections(self, zoo_port, target_connections, retries=2):
        """Poll to get active brokers"""
        active_brokers = list()
        brokers_len = -1
        while brokers_len != target_connections or retries == 0:
            active_brokers = self.get_active_brokers(zoo_port)
            brokers_len = len(active_brokers)
            if brokers_len == target_connections:
                break
            retries -= 1
            time.sleep(2)
        return active_brokers

    def __run_kafka_instance(self, config):
        call(f"./deploy/kafka/bin/kafka-server-start.sh -daemon {config}", shell=True)
    
    def __get_port(self, listener):
        try:
            port = int(listener.split(":")[-1])
        except ValueError:
            raise Exception(f"Listener '{listener}' is not in a correct format")
        return port


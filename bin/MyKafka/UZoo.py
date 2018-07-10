from kazoo.client import KazooClient, KazooState
from subprocess import call
from configobj import ConfigObj as ConfigParser

def zk_listener(state):
    if state == KazooState.LOST:
        # Register somewhere that the session was lost
        print("Connection Lost!")
    elif state == KazooState.SUSPENDED:
        # Handle being disconnected from Zookeeper
        print("Session Disconnected!")
    else:
        # Handle being connected/reconnected to Zookeeper
        print("Connected!")

class UZoo():
    def __init__(self, configs):
        """This class will maintain a all zookeeper instances

        Args:
            config (list of str): The locations of the <name>.properties files that contatins the zookeeper configurations
        """
        self.configs = configs

    def start_zookeeper(self):
        """Function will use the config files and start the zookeeper instances"""
        ports = list()
        for port, cluster_configs in self.configs.items():
            for config in cluster_configs:
                self.config_parser = ConfigParser(config)

                try:
                    port = self.config_parser['clientPort']
                except KeyError:
                    raise Exception(f"Key 'clientPort' does not exist in '{config}'")

                self.__run_zoo_instance(config)
                ports.append(f"127.0.0.1:{port}")
            self.__run_kazoo_instances(ports)
            self.zk.add_listener(zk_listener)

    def stop_zoo(self):
        self.zk.stop()

    def __run_zoo_instance(self, config):
        call(f"../deploy/kafka/bin/zookeeper-server-start.sh -daemon {config}", shell=True)

    def __run_kazoo_instances(self, ports):
        """Establish all kazoo client connections

        Args:
            ports (list of str): list of client ports to create connection to zookeeper
        """
        ports_csv = ','.join(ports)
        self.zk = KazooClient(hosts=f"{ports_csv}")
        self.zk.start()

from MyKafka.UReplicator import UReplicator
import time
import pprint

pp = pprint.PrettyPrinter(indent=4)

connector = UReplicator(
    controller_configs='config/controllerConfig.json', 
    config_json_path='config/serverConfig.json', 
    path_to_config='output'
)

# connector.generate_config()

u_zoo = connector.init_zoo()
u_zoo.start_zookeeper()
# # # time.sleep(1)
u_kafka = connector.init_kafka()
u_kafka.start_kafka()

u_controller = connector.init_controllers()
u_controller.connect_controllers(controllerPorts=["9000", "9001"])

u_controller.run_workers(9000, 10)
u_controller.run_workers(9001, 20)

u_controller.blacklist_topics(['testTopic', 'largeTopic'], 9000)
u_controller.whitelist_topics(['largeTopic'], 9000)

u_controller.blacklist_topics(['testTopic', 'largeTopic'], 9001)
u_controller.whitelist_topics(['largeTopic'], 9001)

pp.pprint(u_controller.get_controllers())

# time.sleep(2)

# u_controller.remove_controller(9000)
# u_controller.remove_controller(9001)

# pp.pprint(u_controller.get_controllers())


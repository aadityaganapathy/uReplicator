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

# # # # # connector.stop_all()
# u_zoo = connector.init_zoo()
# u_zoo.start_zookeeper()
# # # time.sleep(1)
# u_kafka = connector.init_kafka()
# u_kafka.start_kafka()

u_controller = connector.init_controllers()
print(len(u_controller.get_topics(9000)))
# u_controller.blacklist_topics(['testTopic'], 9000)
# u_controller.whitelist_topics(['testTopic'], 9000)

# u_controller.connect_controllers(controllerPorts=["9000", "9001"])
# u_controller.whitelist_topics(['testopic'], 9000)
# u_controller.run_workers(9000, 4)
# u_controller.run_workers(9001, 2)

# pp.pprint(u_controller.get_controllers())
# print(u_controller.controller_running(9000))
# print(u_controller.get_worker_count(9000))
# u_controller.remove_workers(9000)
# u_controller.remove_controller(9000)
# u_controller.remove_controller(9001)

# pp.pprint(u_controller.get_controllers())s



# u_controller.connect_controllers(controllerPorts=["9001"])
# u_controller.whitelist_topics(['testopic'], 9001)
# u_controller.run_workers(9001, 10)
# print(u_controller.controller_running(9001))
# print(u_controller.get_worker_count(9001))
# u_controller.remove_workers(9001)

from MyKafka.UReplicator import UReplicator
import time

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
# u_controller.connect_controllers(controllers=["9000"], key="controllerPort")
# u_controller.whitelist_topics(['testopic'])
# u_controller.run_workers(9000, 10)
print(u_controller.get_worker_count())
# # while True:
#     print(connector.u_zoo.zk.state)
#     time.sleep(1)

from MyKafka.UReplicator import UReplicator


connector = UReplicator(
    controller_configs='config/controllerConfig.json', 
    config_json_path='config/serverConfig.json', 
    path_to_config='output'
)

u_zoo = connector.init_zoo()
u_zoo.start_zookeeper()

u_kafka = connector.init_kafka()
u_kafka.start_kafka()


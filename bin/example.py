import pprint
import sys
from MyKafka.UReplicator import UReplicator

def shutdown_controllers(args, controller):
    controller_ids = args[2].split(',')
    for controller_id in controller_ids:
        controller.shutdown_controller(controller_id)

def describe_controller(args, controller):
    pp = pprint.PrettyPrinter(indent=4)
    controller_ids = sys.argv[2].split(",")
    pp.pprint(controller.get_controllers(controllerPorts=controller_ids))

def blacklist_topics(args, controller):
    controller_id, topics_to_blacklist = split_args(args)
    controller.blacklist_topics(topics_to_blacklist, controller_id)

def whitelist_topics(args, controller):
    controller_id, topics_to_whitelist = split_args(args)
    controller.whitelist_topics(topics_to_whitelist, controller_id)

def run_workers(args, controller):
    controller.run_workers(args[2], args[3])

def run_controllers(args, controller):
    controller_ids = args[2].split(',')
    controller.connect_controllers(controllerPorts=controller_ids)

def split_args(args):
    return [args[2], args[3].split(',')]

def main():
    connector = UReplicator(
        controller_configs='config/controllerConfig.json', 
        config_json_path='config/serverConfig.json', 
        path_to_config='output'
    )
    u_controller = connector.init_controllers()

    commands = {
        "run_controllers": run_controllers,
        "run_workers": run_workers,
        "whitelist_topics": whitelist_topics,
        "blacklist_topics": blacklist_topics,
        "describe_controller": describe_controller,
        "shutdown_controllers": shutdown_controllers
    }
    cmd = sys.argv[1]
    commands[cmd](sys.argv, u_controller)

if __name__ == "__main__": 
    main()
    


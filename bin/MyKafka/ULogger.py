class ULogger():

    def __init__(self, logging_on=True):
        actions = {True: self.__log, False: self.__nothing}
        self.action = actions[logging_on]

    def log_inactive_controller(self, controllerPort, status="ERROR"):
        self.action(f"[{status}]: Controller on port {controllerPort} is inactive")

    def log_active_controller(self, controllerPort):
        self.action(f"[INFO]: Controller on port {controllerPort} is already running")

    def log_failed_controller_connection(self, controllerPort):
        self.action(f"[ERROR]: Failed to connect to controller on port {controllerPort}")

    def log_successful_controller_connection(self, controllerPort):
        self.action(f"[SUCCESS]: Connected to controller on port {controllerPort}")

    def log_invalid_worker_input_count(self, requested_count, actual_count):
        self.action(f"[ERROR]: Cannot remove {requested_count} workers => only {actual_count} available")

    def log_whitelist_topic(self, topic):
        self.action(f"[SUCCESS]: Whitelisted {topic}")
    
    def log_repeat_whitelist_topic(self, topic):
        self.action(f"[INFO]: {topic} is already whitelisted")

    def log_failed_whitelist_topic(self, topic):
        self.action(f"[INFO]: Unable to whitelist topic '{topic}'")

    def __log(self, val):
        print(val)

    def __nothing(self, val):
        return
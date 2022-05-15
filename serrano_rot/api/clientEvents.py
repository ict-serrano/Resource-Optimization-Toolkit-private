class EventBase(object):

    def __init__(self):
        super(EventBase, self).__init__()


class ControllerResponse(EventBase):

    def __init__(self, response):
        super(ControllerResponse, self).__init__()
        self.response = response


class EventEnginesChanged(EventBase):

    def __init__(self):
        super(EventEnginesChanged, self).__init__()


class EventExecutionCompleted(EventBase):

    def __init__(self, response_params):
        super(EventExecutionCompleted, self).__init__()
        self.execution_uuid = response_params["uuid"]
        self.status = response_params["status"]
        self.results = response_params["results"]


class EventExecutionError(EventBase):

    def __init__(self, response_params):
        super(EventExecutionError, self).__init__()
        self.execution_uuid = response_params["uuid"]
        self.status = response_params["status"]
        self.reason = response_params["reason"]

import pika
import json
import logging
import threading

import serrano_rot.utils.constants as constants

from multiprocessing import Lock, Queue, queues

from PyQt5.QtCore import QThread
from PyQt5.QtCore import pyqtSignal

logger = logging.getLogger("SERRANO.ROT.DataBrokerInterface")


class SyncQueue(queues.Queue):

    def __init__(self):
        self.q = Queue()
        self.lock = Lock()

    def add(self, item):
        self.lock.acquire()
        self.q.put(item)
        self.lock.release()

    def get(self):
        return self.q.get()


# Implements the Exchange 1 async interface (ROT results to clients)
def ExecutionResponseHander(config, internal_fwd_queue):
    connection_parameters = pika.ConnectionParameters(host=config["address"],
                                                      virtual_host=config["virtual_host"],
                                                      credentials=pika.PlainCredentials(config["username"],
                                                                                        config["password"]),
                                                      blocked_connection_timeout=5,
                                                      socket_timeout=None,
                                                      heartbeat=0)

    connection = pika.BlockingConnection(connection_parameters)
    channel = connection.channel()

    channel.exchange_declare(exchange=constants.DISPATCHER_RESULTS_EXCHANGE, exchange_type='direct')

    while True:
        message = internal_fwd_queue.get()
        logger.debug("Forward execution response '%s' to client '%s'" % (message["uuid"], message["client_uuid"]))
        channel.basic_publish(exchange=constants.DISPATCHER_RESULTS_EXCHANGE,
                              routing_key=message["client_uuid"],
                              body=json.dumps(message))


# Implements the Exchange 4 async interface (Dispatcher events to external services)
def DispatcherEventHandler(rabbitmq_config, internal_fwd_queue):
    connection_parameters = pika.ConnectionParameters(host=rabbitmq_config["address"],
                                                      virtual_host=rabbitmq_config["virtual_host"],
                                                      credentials=pika.PlainCredentials(rabbitmq_config["username"],
                                                                                        rabbitmq_config["password"]),
                                                      blocked_connection_timeout=5,
                                                      socket_timeout=None,
                                                      heartbeat=0)

    connection = pika.BlockingConnection(connection_parameters)
    channel = connection.channel()
    channel.exchange_declare(exchange=constants.DISPATCHER_EVENTS_EXCHANGE, exchange_type='fanout')

    while True:
        message = internal_fwd_queue.get()
        channel.basic_publish(exchange=constants.DISPATCHER_EVENTS_EXCHANGE,
                              routing_key='',
                              body=json.dumps(message))


# Implements the Exchange 3 async interface that Dispatcher uses to send requests to a specific engine
def EngineRequestHandler(rabbitmq_config, internal_fwd_queue):
    connection_parameters = pika.ConnectionParameters(host=rabbitmq_config["address"],
                                                      virtual_host=rabbitmq_config["virtual_host"],
                                                      credentials=pika.PlainCredentials(rabbitmq_config["username"],
                                                                                        rabbitmq_config["password"]),
                                                      blocked_connection_timeout=5,
                                                      socket_timeout=None,
                                                      heartbeat=0)

    connection = pika.BlockingConnection(connection_parameters)
    channel = connection.channel()
    channel.exchange_declare(exchange=constants.DISPATCHER_REQUESTS_EXCHANGE, exchange_type='direct')

    while True:
        message = internal_fwd_queue.get()
        print(message)
        engine_id = message["engine_id"]
        request = message["request"]
        channel.basic_publish(exchange=constants.DISPATCHER_REQUESTS_EXCHANGE, routing_key=engine_id,
                              body=json.dumps(request))


class EngineResponseInterface(QThread):
    engineResponse = pyqtSignal(object)

    def __init__(self, config):
        QThread.__init__(self)

        connection_parameters = pika.ConnectionParameters(host=config["address"],
                                                          virtual_host=config["virtual_host"],
                                                          credentials=pika.PlainCredentials(config["username"],
                                                                                            config["password"]),
                                                          blocked_connection_timeout=5,
                                                          socket_timeout=None,
                                                          heartbeat=0)

        connection = pika.BlockingConnection(connection_parameters)
        self.channel = connection.channel()
        self.channel.queue_declare(queue=constants.ENGINE_RESPONSE_QUEUE)

        logger.info("EngineResponseInterface is read. Waiting for responses ...")

    def __del__(self):
        self.wait()

    def run(self):
        logger.info("RequestInterface is running ...")

        def callback(ch, method, properties, body):
            self.engineResponse.emit(body.decode("utf-8"))

        self.channel.basic_consume(queue=constants.ENGINE_RESPONSE_QUEUE, on_message_callback=callback, auto_ack=True)
        self.channel.start_consuming()


class DataBrokerInterface(QThread):
    engineResponse = pyqtSignal(object)

    def __init__(self, config):
        QThread.__init__(self)

        self.config = config
        self.dispatcher_events_fwd_queue = SyncQueue()
        self.engine_requests_fwd_queue = SyncQueue()
        self.execution_responses_fwd_queue = SyncQueue()

        self.dispatcher_events_worker = threading.Thread(name='Dispatcher Events Forwarder',
                                                         target=DispatcherEventHandler,
                                                         args=(config, self.dispatcher_events_fwd_queue,))

        self.engine_requests_worker = threading.Thread(name='Engine Requests Forwarder', target=EngineRequestHandler,
                                                       args=(config, self.engine_requests_fwd_queue,))

        self.execution_responses_worker = threading.Thread(name='Execution Responses Forwarder',
                                                           target=ExecutionResponseHander,
                                                           args=(config, self.execution_responses_fwd_queue,))

        self.responseInterface = EngineResponseInterface(config)
        self.responseInterface.engineResponse.connect(self.handle_engine_response)
        self.responseInterface.start()

        logger.info("DataBrokerInterface is ready ...")

    def handle_engine_response(self, data):
        self.engineResponse.emit(data)

    def __del__(self):
        self.wait()

    def forward_dispatcher_evt_message(self, msg):
        logger.debug("Forward Dispatcher event message: %s" % msg)
        self.dispatcher_events_fwd_queue.add(msg)

    def forward_dispatcher_request(self, request):
        logger.debug("Forward at engine '%s' Dispatcher request: %s" % (request["engine_id"], request))
        self.engine_requests_fwd_queue.add({"engine_id": request["engine_id"], "request": request})

    def forward_execution_request_response(self, response):
        logger.debug("Forward response for execution '%s' at client '%s'" % (response["uuid"],
                                                                             response["client_uuid"]))
        self.execution_responses_fwd_queue.add(response)

    def run(self):
        logger.info("DataBrokerInterface is running ...")
        self.dispatcher_events_worker.start()
        self.engine_requests_worker.start()
        self.execution_responses_worker.start()

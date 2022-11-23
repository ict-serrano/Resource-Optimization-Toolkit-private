import pika
import logging

import serrano_rot.utils.constants as constants

from PyQt5.QtCore import QThread
from PyQt5.QtCore import pyqtSignal

logger = logging.getLogger("SERRANO.ROT.RequestInterface")


class RequestInterface(QThread):

    dispatcherRequest = pyqtSignal(object)

    def __init__(self, engine_id, config):

        QThread.__init__(self)

        self.engine_id = engine_id

        connection_parameters = pika.ConnectionParameters(host=config["address"],
                                                          virtual_host=config["virtual_host"],
                                                          credentials=pika.PlainCredentials(config["username"],
                                                                                            config["password"]),
                                                          blocked_connection_timeout=5,
                                                          socket_timeout=None,
                                                          heartbeat=0)
        
        connection = pika.BlockingConnection(connection_parameters)
        self.channel = connection.channel()
        self.channel.exchange_declare(exchange=constants.DISPATCHER_REQUESTS_EXCHANGE, exchange_type='direct')
        result = self.channel.queue_declare(queue='', exclusive=True)
        self.queue_name = result.method.queue
        self.channel.queue_bind(exchange=constants.DISPATCHER_REQUESTS_EXCHANGE, queue=self.queue_name, routing_key=self.engine_id)

        logger.info("RequestInterface is read. Waiting for requests ...")

    def __del__(self):
        return""
        #self.wait()

    def run(self):

        logger.info("RequestInterface is running ...")

        def callback(ch, method, properties, body):
            self.dispatcherRequest.emit(body.decode("utf-8"))

        self.channel.basic_consume(queue=self.queue_name, on_message_callback=callback, auto_ack=True)
        self.channel.start_consuming()
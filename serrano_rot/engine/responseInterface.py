import pika
import logging

import serrano_rot.utils.constants as constants

from PyQt5.QtCore import QObject

logger = logging.getLogger("SERRANO.ROT.ResponseInterface")


class ResponseInterface(QObject):

    def __init__(self, config):
        super(QObject, self).__init__()

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

        logger.info("ResponseInterface is ready ...")

    def forward_response_to_controller(self, data):
        logger.debug("Forward response to controller: %s" % data)
        self.channel.basic_publish(exchange="", routing_key=constants.ENGINE_RESPONSE_QUEUE, body=data)
import pika
from rabbitparams import RabbitParams

class RabbitConnection:
    def __init__(self,params,logger,widget,message_view):
        self.logger = logger
        self.server = params.server
        self.port = params.port
        self.user = params.user
        self.password = params.password
        self.exchange = params.exchange
        self.routing_key = params.routing_key
        self.queue_name = params.queue_name
        self.consuming = False
        self._connection = None
        self._channel = None
        self._closing = False
        self._consumer_tag = None
        self.queue_bound = False
        self.widget = widget
        self.message_view = message_view
        self._url = params.get_url()

    def isConnected(self):
        if self._connection == None:
            return False
        else:
            return True

    def connect(self):
        self.logger.warning('Connecting to %s' % self._url)
        return pika.SelectConnection(pika.URLParameters(self._url),
                                     self.on_connection_open,
                                     stop_ioloop_on_close=False)

    def on_connection_open(self, unused_connection):
        self.logger.warning('Connection opened')
        #self.add_on_connection_close_callback()
        self.logger.warning('Creating a new channel')
        self._connection.channel(on_open_callback=self.on_channel_open)

    def on_channel_open(self, channel):
        self.logger.warning('Channel opened')
        self._channel = channel
        self.widget.set_active(True)
        return True
        #self.add_on_channel_close_callback()
        #self.setup_exchange(self.EXCHANGE)

    def run(self):
        self._connection = self.connect()
        self._connection.ioloop.start()
        #return True

    def close_connection(self):
        """This method closes the connection to RabbitMQ."""
        self.logger.warning('Closing connection')
        self._connection.close()
        self._connection = None
        self.queue_bound = False
        self.widget.set_active(False)

    def start_consuming(self):
        self.consuming = True
        if self.queue_bound:
            self.add_on_cancel_callback()
            self._consumer_tag = self._channel.basic_consume(self.on_message,
                                                             self.queue_name)
        else:
            self.logger.warning("Queue is not set, first setup_queue")
            self.setup_queue()

    def add_on_cancel_callback(self):
        self._channel.add_on_cancel_callback(self.on_consumer_cancelled)

    def on_consumer_cancelled(self, method_frame):
        if self._channel:
            self._channel.close()

    def acknowledge_message(self, delivery_tag):
        self._channel.basic_ack(delivery_tag)

    def isConsuming(self):
        return self.consuming

    def stop_consuming(self):
        if self._channel:
            self.logger.warning('Sending a Basic.Cancel RPC command to RabbitMQ')
            self._channel.basic_cancel(self.on_cancelok, self._consumer_tag)

    def on_cancelok(self,unused_frame):
        self._channel.close()
        self.consuming = False

    def setup_queue(self):
        self.logger.warning('Declaring queue %s' % self.queue_name)
        self._channel.queue_declare(self.on_queue_declareok, self.queue_name,auto_delete=True)

    def on_queue_declareok(self, method_frame):
        self.logger.warning('Binding %s to %s with %s' %
                            (self.exchange, self.queue_name, self.routing_key))
        self._channel.queue_bind(self.on_bindok, self.queue_name,
                                 self.exchange, self.routing_key)

    def on_bindok(self, unused_frame):
        self.logger.warning('Queue bound')
        self.queue_bound = True
        if self.consuming:
            self.start_consuming()

    def on_message(self, unused_channel, basic_deliver, properties, body):
        self.logger.warning('Received message # %s from %s: %s' %
                    (basic_deliver.delivery_tag, properties.app_id, body))
        buffer=self.message_view.get_buffer()
        end_text = buffer.get_end_iter()
        buffer.insert(end_text,"\n"+body)
        self.acknowledge_message(basic_deliver.delivery_tag)

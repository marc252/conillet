

class RabbitParams:
    def __init__(self,valors_dict):
        self.server = valors_dict['server']
        self.port = valors_dict['port']
        self.user = valors_dict['user']
        self.password = valors_dict['pass']
        self.exchange = valors_dict['exchange']
        self.routing_key = valors_dict['routing_key']
        self.queue_name = valors_dict['queue_name']

    def get_url(self):
        return 'amqp://'+self.user+':'+self.password+'@'+self.server+':'+self.port+'/%2F'

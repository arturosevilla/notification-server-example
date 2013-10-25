import zmq
from zmq.core.error import ZMQError
import errno
import logging
import json
from uuid import UUID

__all__ = ['send_notification']
logger = logging.getLogger(__name__)


def create_zmq_context():
    return zmq.Context()

def create_zmq_socket(context, type_):
    sock = context.socket(type_)
    sock.setsockopt(zmq.LINGER, 2000) # 2 secs of linger
    return sock

def log_debug_instance(instance, msg):
    logger.debug('[' + instance.__class__.__name__ + '] ' + msg)

def send_notification(router_address, notification, recipient):
    try:
        context = create_zmq_context()
        router = create_zmq_socket(context, zmq.REQ)
        router.connect(router_address)
        router.send(
            json.dumps({
                notification: notification,
                recipient: recipient
            }).encode('utf-8')
        )
    except:
        pass
    finally:
        router.close()
        context.term()

class QueueRouter(object):
    
    def __init__(self, context, queue_config, queue_push_config):
        log_debug_instance(self, 'Establishing  the queue router')
        self.router = create_zmq_socket(context, zmq.ROUTER)
        self.router.bind(queue_config)

        self.pusher = create_zmq_socket(context, zmq.PUSH)
        self.pusher.bind(queue_push_config)

    def close(self):
        log_debug_instance(self, 'Shutting down')
        self.router.close()
        self.pusher.close()

    def handle(self):
        # Message envelope that comes with zmq.ROUTER:
        #   - First address
        #   - Then empty data
        #   - Then the actual data

        # off with their heads!
        # first we chop off the address
        log_debug_instance(self, 'Handling a message through the queue')
        message = self.router.recv()
        more = self.router.getsockopt(zmq.RCVMORE)
        if more:
            # then we chop off the empty data
            self.router.recv()
            # and finally we get the data
            message = self.router.recv()
        
        self.pusher.send(message)


class PublisherRecords(object):

    def __init__(self, context, pub_notifier_config, req_config):
        log_debug_instance(self, 'Establishing the publisher records')
        self.pub_notifier = create_zmq_socket(context, zmq.PUB)
        self.pub_notifier.bind(pub_notifier_config)
        self.req_notifier = create_zmq_socket(context, zmq.REP)
        self.req_notifier.bind(req_config)
        self.publishers = []

    def close(self):
        log_debug_instance(self, 'Shutting down')
        self.pub_notifier.close()
        self.req_notifier.close()
        
    def handle(self):
        log_debug_instance(self, 'Received request for publishers')
        message = self.req_notifier.recv()
        try:
            message = json.loads(message)
        except:
            log_debug_instance(self, 'Invalid request for publishers')
            raise ValueError('message is not json')

        type_ = message.get('type')

        if type_ == 'add-publisher':
            log_debug_instance(self, 'Adding a publisher')
            self.publishers.append(message['address'])
            serialized_pubs = json.dumps(self.publishers)
            self.req_notifier.send(serialized_pubs)
            self.pub_notifier.send(serialized_pubs)
        elif type_ == 'get-publishers':
            log_debug_instance(self, 'Sending list of publishers')
            self.req_notifier.send(json.dumps(self.publishers))
        else:
            log_debug_instance(self, 'Unknown request: ' + str(type_))


def start_queue_and_router(
    queue_config,
    queue_push_config,
    pub_notifier_config,
    req_notifier_config
):
    context = create_zmq_context()
    router = QueueRouter(context, queue_config, queue_push_config)
    publishers = PublisherRecords(
        context,
        pub_notifier_config,
        req_notifier_config
    )

    poller = zmq.Poller()
    poller.register(router.router, zmq.POLLIN)
    poller.register(publishers.req_notifier, zmq.POLLIN)

    try:
        while True:
            available = dict(poller.poll())

            if available.get(router.router) == zmq.POLLIN:
                router.handle()

            if available.get(publishers.req_notifier) == zmq.POLLIN:
                try:
                    publishers.handle()
                except ValueError:
                    continue

    except KeyboardInterrupt:
        # killing it
        pass

    except ZMQError, e:
        if e.errno != errno.EINTR:
            # we are probably being terminated, or unhandled signal, anyways
            # killing the process
            # Warn about other stuff
            raise


class QueueWorker(object):

    def __init__(
        self,
        queue_config,
        pub_host,
        pub_port,
        req_notifier_config
    ):
        self.publisher_number = pub_port
        self.log_worker('Registering a queue worker')
        context = create_zmq_context()
        self.puller = create_zmq_socket(context, zmq.PULL)
        self.puller.connect(queue_config)

        self.publisher = create_zmq_socket(context, zmq.PUB)
        address = 'tcp://' + pub_host + ':' + str(pub_port)
        self.publisher.bind(address)

        self.poller = zmq.Poller()
        self.poller.register(self.puller, zmq.POLLIN)

        report_worker = create_zmq_socket(context, zmq.REQ)
        report_worker.connect(req_notifier_config)

        report_worker.send(json.dumps({
            'type': 'add-publisher',
            'address': address
        }))

        # Verify we got ourselves registered
        publishers = json.loads(report_worker.recv())
        if address in publishers:
            self.log_worker('Successful registration of queue worker')

        report_worker.close()

    def log_worker(self, message):
        log_debug_instance(
            self, 
            '[' + str(self.publisher_number) + '] ' + message
        )

    def close(self):
        self.log_worker('Shutting down')
        self.publisher.close()
        self.puller.close()

    def _extract_message(self, message):
        # we require the userid so that ZeroMQ consumers can filter the
        # messages through zmq.SUBSCRIBE
        
        try:
            decoded = json.loads(message)
        except:
            return None
        
        return decoded['notification'], decoded['recipient']

    def handle(self):
        self.log_worker('Working with a notification')
        message = self.puller.recv()
        more = self.puller.getsockopt(zmq.RCVMORE)

        # do the actual work
        decoded = self._extract_message(message)
        if decoded is None:
            self.log_worker('Invalid message: ' + message)
            return

        # in a real system we should do some work here
        # self.do_work(decoded)

        message_to_send, user_id = decoded

        self.log_worker(
            'Sending notification to the publisher for user: ' + user_id
        )
        
        if more:
            self.publisher.send(user_id + '|' + message_to_send, zmq.SNDMORE)
        else:
            self.publisher.send(user_id + '|' + message_to_send)

    def work(self):
        try:
            while True:
                available = dict(self.poller.poll())

                if available.get(self.puller) == zmq.POLLIN:
                    self.handle()
        except KeyboardInterrupt:
            # killing it
            pass
        except ZMQError, e:
            if e.errno != errno.EINTR:
                raise


def start_single_worker(queue_config, pub_host, pub_port, req_notifier_config):
    worker = QueueWorker(
        queue_config,
        pub_host,
        pub_port,
        req_notifier_config
    )
    worker.work()


#!/usr/bin/env python

from queue import start_queue_and_router, start_single_worker
from config import get_config
from multiprocessing import Process

def queue_process(config):
    def _init(config):
        start_queue_and_router(
            config['notification.queue.router'],
            config['notification.queue.pusher'],
            config['notification.queue.worker.notifier.pub'],
            config['notification.queue.worker.notifier.req']
        )
    process = Process(target=_init, args=[config])
    process.start()
    return process


def worker_process(config, port):
    def _init(config):
        start_single_worker(
            config['notification.queue.pusher'],
            config['notification.queue.worker.host'],
            port,
            config['notification.queue.worker.notifier.req']
        )
    process = Process(target=_init, args=[config])
    process.start()
    return process

if __name__ == '__main__':
    import sys
    if len(sys.argv) == 1:
        print('Required configuration file!')
        sys.exit(1)
    config = get_config(sys.argv[1])
    if config is None:
        print('File not found or incorrect format for INI file')
        sys.exit(1)
    num_workers = int(config['notification.queue.worker.num_workers'])
    base_port = int(config['notification.queue.worker.init_port'])
    processes = [queue_process(config)]
    for i in range(num_workers):
        processes.append(worker_process(config, base_port + i))
    for p in processes:
        p.join()


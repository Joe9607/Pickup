# coding: utf-8

import os
import logging
import socket
import json
from logging.handlers import TimedRotatingFileHandler
from tornado.options import options, define
from tornado.ioloop import IOLoop, PeriodicCallback
import zmq


CRITICAL = 60
FATAL = 50
ERROR = 40
WARNING = 30
WARN = WARNING
INFO = 20
DEBUG = 10
NOTSET = 0

level_names = {
    CRITICAL: 'CRITICAL',
    ERROR: 'ERROR',
    WARNING: 'WARNING',
    INFO: 'INFO',
    DEBUG: 'DEBUG',
    NOTSET: 'NOTSET',
    FATAL: 'FATAL',
    'CRITICAL': CRITICAL,
    'ERROR': ERROR,
    'WARN': WARNING,
    'WARNING': WARNING,
    'INFO': INFO,
    'DEBUG': DEBUG,
    'NOTSET': NOTSET,
    'FATAL': FATAL,
}

host = socket.gethostbyname(socket.gethostname())
context = zmq.Context()
# tcp_url = "tcp://127.0.0.1:{0}".format(options.logger_port)


class LogRotate(object):
    def __init__(self):
        from settings import log_dir
        self.logger = logging.getLogger("mahjong")
        self.logger.setLevel(logging.DEBUG)
        file_handler = TimedRotatingFileHandler(os.path.join(log_dir, "mahjong.log"), when='d')
        file_handler.setLevel(logging.DEBUG)
        file_handler.formatter = logging.Formatter('%(levelname)s %(message)s')
        self.logger.addHandler(file_handler)

        self.level_router = {
            DEBUG: self.logger.debug,
            "DEBUG": self.logger.debug,
            INFO: self.logger.info,
            "INFO": self.logger.info,
            WARN: self.logger.warn,
            "WARN": self.logger.warn,
            WARNING: self.logger.warning,
            "WARNING": self.logger.warning,
            FATAL: self.logger.fatal,
            "FATAL": self.logger.fatal,
            CRITICAL: self.logger.critical,
            "CRITICAL": self.logger.critical,
        }

        self.mq = context.socket(zmq.PULL)
        self.mq.bind("tcp://127.0.0.1:{0}".format(options.logger_port))

    def consumer(self):
        while True:
            try:
                log = self.mq.recv(flags=zmq.NOBLOCK)
                msg = json.loads(log)
                level = level_names[msg["level"]]
                self.level_router[level](log)
            except zmq.ZMQError:
                break


def run():
    log_rotate = LogRotate()
    PeriodicCallback(log_rotate.consumer, 1000).start()
    IOLoop.instance().start()

if __name__ == '__main__':
    define("logger_port", 8047, type=int)
    #define("redis_host", "192.168.36.77", type=str)
    define("redis_host", "127.0.0.1", type=str)
    define("redis_port", 6379, type=int)
    define("redis_password", None, type=str)
    define("redis_db", 1, type=int)
    options.parse_command_line()
    run()

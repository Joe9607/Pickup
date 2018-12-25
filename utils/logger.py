# coding: utf-8

import os
import sys
import json
import socket
import weakref

try:
    syslog = __import__("syslog")
except ImportError:
    syslog = None

import zmq
from tornado.options import options
from settings import log_dir


__all__ = ["Logger", "LogRotate"]


# noinspection PyBroadException
def frame():
    try:
        raise Exception
    except:
        return sys.exc_info()[2].tb_frame.f_back


if hasattr(sys, '_getframe'):
    # noinspection PyProtectedMember
    frame = lambda: sys._getframe(3)

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
_srcfile = os.path.normcase(frame.__code__.co_filename).capitalize()
host = socket.gethostbyname(socket.gethostname())
context = zmq.Context()
tcp_url = "tcp://127.0.0.1:{0}".format(options.logger_port)

zmq_socket = context.socket(zmq.PUSH)
zmq_socket.connect(tcp_url)


class Logger(object):
    """
    玩家座位号
    玩家UUID
    玩家事件
    玩家状态
    桌子状态
    桌子事件
    当前局数
    """

    def __init__(self, room_id):
        self.pid = os.getpid()
        self.host = host
        self.room_id = room_id
        self.level = None
        self.line = None
        self.msg = None

        # self.socket = weakref.proxy(zmq_socket)

    def file_descriptor(self):
        """
        Find the stack frame of the caller so that we can note the source
        file name, line number and function name.
        """
        f = frame()
        # On some versions of IronPython, currentframe() returns None if
        # IronPython isn't run with -X:Frames.
        if f is not None:
            f = f.f_back

        rv = "(unknown file)", 0, "(unknown function)"
        while hasattr(f, "f_code"):
            co = f.f_code
            filename = os.path.normcase(co.co_filename).capitalize()
            if filename == _srcfile:
                f = f.f_back
                continue
            rv = (co.co_filename, f.f_lineno, co.co_name)
            break
        self.line = "{0}:{2}[{1}]".format(*rv)

    def debug(self, msg):
        self.level = DEBUG
        self.msg = msg
        self.record()

    def info(self, msg):
        self.level = INFO
        self.msg = msg
        self.record()

    def warn(self, msg):
        self.level = WARN
        self.msg = msg
        self.record()

    def fatal(self, msg):
        self.level = FATAL
        self.msg = msg
        self.record()

    def critical(self, msg):
        self.level = CRITICAL
        self.msg = msg
        self.record()

    def record(self):
        self.file_descriptor()
        # for player in self.table.player_dict.values():
        #     self.player_state[player.seat] = player.state
        record_format = json.dumps({
            "level": level_names[self.level],
            "room_id": self.room_id,
            "line": self.line,
            "msg": self.msg,
            # "pid": self.pid,
            # "host": self.host,
            # "time": time.time(),
            # "table_state": self.table.state,
            # "player_state": self.player_state,
        })
        # if self.level > level_names["INFO"]:
        #     print record_format
        self.producer(record_format)
        self.reset()

    def reset(self):
        self.level = None
        self.line = None
        self.msg = None

    @staticmethod
    def local(record):
        with open(os.path.join(log_dir, "mahjong.log"), 'a+') as fp:
            fp.write(record + '\n')

    @staticmethod
    def rsyslog(record):
        if not syslog:
            return
        syslog.openlog(logoption=syslog.LOG_PID, facility=syslog.LOG_MAIL)
        syslog.syslog(record)

    def producer(self, record):
        # self.socket.send(record)
        zmq_socket.send(record)

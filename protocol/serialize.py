# coding: utf-8

import struct
from tornado.websocket import WebSocketClosedError


def send(cmd, proto, session):
    # 有可能掉线
    if not session:
        return
    result = proto.SerializeToString()
    fmt = ">ii{0}s".format(len(result))
    data = struct.pack(fmt, len(result)+8, cmd, result)
    try:
        session.write_message(data, True)
    except (WebSocketClosedError, AttributeError) as e:
        print e

#!/usr/bin/env python
# -*- coding:utf-8 -*-
# from tornado import escape
from tornado import gen
from tornado import httpclient
from tornado import ioloop
from tornado import websocket
from protocol import game_pb2
import struct
from protocol.commands import *
from time import sleep


class TestWebSocketClient(object):
    def __init__(self):
        self.cards = []
        self.count = 0
        self.uuid = 'zxy001'

    def connect(self, url):
        request = httpclient.HTTPRequest(url=url)
        ws_conn = websocket.WebSocketClientConnection(request)
        ws_conn.connect_future.add_done_callback(self._connect_callback)

    def send(self, proto, cmd):
        result = proto.SerializeToString()
        fmt = ">ii{0}s".format(len(result))
        data = struct.pack(fmt, len(result) + 8, cmd, result)
        if not self._ws_connection:
            raise RuntimeError('Web socket connection is closed.')
        print 'send', cmd
        self._ws_connection.write_message(data, True)

    def close(self):
        if not self._ws_connection:
            raise RuntimeError('Web socket connection is already closed.')
        self._ws_connection.close()

    def _connect_callback(self, future):
        if future.exception() is None:
            self._ws_connection = future.result()
            self._on_connection_success()
            self._read_messages()
        else:
            self._on_connection_error(future.exception())

    @gen.coroutine
    def _read_messages(self):
        while True:
            msg = yield self._ws_connection.read_message()
            # print 'message:', msg
            if msg is None:
                self.close()
                break
            self._on_message(msg)

    def _on_message(self, msg):
        cmd, size, string = self.receive(msg)
        print 'cmd:', cmd
        print 'string:', string
        if cmd == ENTER_ROOM:
            sleep(10)
            proto = game_pb2.ReadyRequest()
            self.send(proto, READY)
            print '准备'
        elif cmd == READY:
            print '以上玩家准备'
        # elif cmd == POKER_DEAL:
        #     proto = game_pb2.CockDealResponse()
        #     proto.ParseFromString(string)
        #     self.cards = []
        #     for a in proto.cards_in_hand:
        #         self.cards.append(a.card)
        #     print '发牌'

        elif cmd == ENTER_ROOM_OTHER:
            print '其他玩家进入房间'
        else:
            print 'else cmd'

    def _on_connection_success(self):
        print('Connected!')
        proto = game_pb2.EnterRoomRequest()
        proto.room_id = 12361
        proto.player = self.uuid
        proto.info = '1'
        self.send(proto, ENTER_ROOM)
        # print('success')

    def _on_connection_error(self, exception):
        print('Connection error: %s', exception)

    def receive(self, message):
        cmd, = struct.unpack('>i', message[4:8])
        size, = struct.unpack('>i', message[:4])
        string, = struct.unpack('>{0}s'.format(size - 8), message[8:size])
        print 'unpack success'
        return cmd, size, string


def main():
    client = TestWebSocketClient()
    client.connect('ws://127.0.0.1:9052/ws')
    try:
        ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        client.close()


if __name__ == '__main__':
    main()

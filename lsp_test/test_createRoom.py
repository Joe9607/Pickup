#!/usr/bin/env python
# -*- coding:utf-8 -*-
from protocol import game_pb2
import json
from tornado.httpclient import HTTPClient


class request(object):

    def createRoom(self, roomid, owner):
        proto = game_pb2.CreateRoomRequest()
        proto.room_id = roomid
        proto.owner = owner
        proto.room_uuid = '7a6e7a155c0c4928accd5eaef3625e6e'
        # proto.app_id = 9
        proto.kwargs = json.dumps({})
        print roomid, owner, proto.room_uuid
        request = HTTPClient()
        request.fetch('http://127.0.0.1:9052/web/create_room', method="POST", body=proto.SerializeToString())
        print 'success'


if __name__ == '__main__':
    request().createRoom(12361, 'lsp001')

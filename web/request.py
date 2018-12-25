# coding: utf-8

import os
import re
import traceback
from StringIO import StringIO
import json
import hashlib
from ConfigParser import ConfigParser

from tornado.gen import coroutine
from tornado.httpclient import AsyncHTTPClient
from tornado.options import options

from settings import redis, root
from protocol import game_pb2
from utils.logger import Logger, host

name_web_retry = "web:retry"
# pattern = re.compile(
#     r'^http://'
#     r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
#     r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
#     r'(?::\d+)?', re.IGNORECASE)
pattern = re.compile(r'.*(?=/[^/]*/[^/]*)', re.IGNORECASE)


class WebRequest(object):
    def __init__(self, room_id, room_uuid, game_type, app_id, owner):
        self.room_id = room_id
        self.room_uuid = room_uuid
        self.game_type = game_type
        self.app_id = app_id
        self.owner = owner
        self.logger = Logger(room_id)
        self.web_alloc_url = None
        self.web_record_url = None
        self.reload_web_url()

    def reload_web_url(self):
        conf_web = ConfigParser()
        conf_web.read(os.path.join(os.path.join(root, "confs"), "web.conf"))
        self.web_alloc_url = conf_web.get("url", "alloc")
        self.web_record_url = conf_web.get("url", "record")

    @staticmethod
    def is_web_alloc(url):
        for i in ("/room/enter", "/room/exit", "/room/dismiss", "/room/load_plus", "/room/load_minus"):
            if i in url:
                return True
        return False

    @staticmethod
    def is_web_record(url):
        for i in ("/room/refund", "/settle_for_round", "/settle_for_room"):
            if i in url:
                return True
        return False

    # noinspection PyBroadException
    @coroutine
    def post(self, url, body, retry=False):
        key = hashlib.md5(url + body).hexdigest()
        if retry:
            self.reload_web_url()
        try:
            request = AsyncHTTPClient()
            response = yield request.fetch(url, method="POST", body=body)
            self.logger.info("url: {0} code: {1} body {2}".format(url, response.code, response))

            for key, value in redis.hgetall(name_web_retry).items():
                # print key, value
                redis.hdel(name_web_retry, key)
                i, j = value.split("|", 1)
                m = re.findall(pattern, i)
                if self.is_web_alloc(i):
                    i = i.replace(m[0], self.web_alloc_url)
                else:
                    i = i.replace(m[0], self.web_record_url)
                self.post(i, j, True)
        except Exception:
            fp = StringIO()
            traceback.print_exc(file=fp)
            self.logger.fatal("url: {0} error: {1}".format(url, fp.getvalue()))
            redis.hsetnx(name_web_retry, key, "{0}|{1}".format(url, body))

    @coroutine
    def enter_room(self, player):
        proto_web = game_pb2.EnterRoomWebResponse()
        proto_web.code = 1
        proto_web.room_id = self.room_id
        proto_web.player = player
        proto_web.game_type = self.game_type
        proto_web.app_id = self.app_id
        url = self.web_alloc_url + "/room/enter"
        body = proto_web.SerializeToString()
        self.post(url, body)

    @coroutine
    def exit_room(self, player):
        proto_web = game_pb2.ExitRoomWebResponse()
        proto_web.player = player
        proto_web.code = 1
        proto_web.room_id = self.room_id
        proto_web.game_type = self.game_type
        proto_web.app_id = self.app_id
        url = self.web_alloc_url + "/room/exit"
        body = proto_web.SerializeToString()
        self.post(url, body)

    @coroutine
    def dismiss_room(self, table):
        # print 'enter dismiss room'
        if table.conf.is_aa():
            if table.total_round <= 1:
                for p in table.player_dict.values():
                    self.aa_refund(p.uuid, 0)
                    # elif table.total_round < table.conf.max_rounds:
                    #     for p in table.player_dict.values():
                    #         self.aa_refund(p.uuid, 2)
        else:
            if table.total_round <= 1:
                self.refund()

        proto_web = game_pb2.DismissRoomWebResponse()
        proto_web.room_id = self.room_id
        proto_web.code = 1
        proto_web.game_type = self.game_type
        proto_web.app_id = self.app_id
        proto_web.owner = self.owner
        url = self.web_alloc_url + "/room/dismiss"
        body = proto_web.SerializeToString()
        self.post(url, body)

    @coroutine
    def aa_refund(self, userid, refund_type):
        proto_web = game_pb2.AvgRefundRequest()
        proto_web.app_id = self.app_id
        proto_web.room_uuid = self.room_uuid
        proto_web.user_id = userid
        proto_web.refund_type = refund_type
        url = self.web_record_url + "/aa/refund"
        body = proto_web.SerializeToString()
        # print 'aa userid:', userid, ',refund_type:', refund_type
        self.post(url, body)

    @coroutine
    def refund(self):
        proto_web = game_pb2.RefundWebResponse()
        proto_web.room_id = self.room_id
        proto_web.code = 1
        proto_web.game_type = self.game_type
        proto_web.app_id = self.app_id
        proto_web.owner = self.owner
        proto_web.room_uuid = self.room_uuid
        url = self.web_record_url + "/room/refund"
        body = proto_web.SerializeToString()
        self.post(url, body)

    @coroutine
    def settle_for_round(self, data):
        url = self.web_record_url + "/settle_for_round/{0}".format(self.game_type)
        body = json.dumps(data)
        self.post(url, body)

    @coroutine
    def settle_for_room(self, data):
        url = self.web_record_url + "/settle_for_room/{0}".format(self.game_type)
        body = json.dumps(data)
        self.post(url, body)

    @coroutine
    def load_plus(self):
        proto_web = game_pb2.LoadPlusWebResponse()
        proto_web.addr = host
        proto_web.port = options.server_port
        proto_web.app_id = self.app_id
        proto_web.room_uuid = self.room_uuid
        url = self.web_alloc_url + "/room/load_plus"
        body = proto_web.SerializeToString()
        self.post(url, body)

    @coroutine
    def load_minus(self):
        proto_web = game_pb2.LoadPlusWebResponse()
        proto_web.addr = host
        proto_web.port = options.server_port
        proto_web.app_id = self.app_id
        proto_web.room_uuid = self.room_uuid
        url = self.web_alloc_url + "/room/load_minus"
        body = proto_web.SerializeToString()
        self.post(url, body)

    @coroutine
    def aa_cons(self, userid):
        proto_web = game_pb2.GameConsRequest()
        proto_web.app_id = self.app_id
        proto_web.room_uuid = self.room_uuid
        proto_web.user_id = userid
        proto_web.cons_type = 1
        # print 'aa userid:', userid, ',aa_cons'
        url = self.web_record_url + "/aa/cons"
        body = proto_web.SerializeToString()
        self.post(url, body)

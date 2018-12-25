# coding: utf-8

import traceback
from StringIO import StringIO
from protocol import game_pb2
from tornado.web import RequestHandler
from logic.table_manager import TableMgr
from logic.session_manager import SessionMgr
import json

# noinspection PyArgumentList,PyAbstractClass
class CreateRoomHandler(RequestHandler):
    def post(self):
        proto = game_pb2.CreateRoomRequest()
        proto.ParseFromString(self.request.body)
        TableMgr().create(proto.room_id, proto.room_uuid, proto.owner, proto.kwargs)
        proto = game_pb2.CreateRoomResponse()
        proto.code = 1
        self.write(proto.SerializeToString())

    def get(self, *args, **kwargs):
        self.write("create room ok")


# noinspection PyAbstractClass
class MaintenanceHandler(RequestHandler):
    def post(self, *args, **kwargs):
        pass


# noinspection PyAbstractClass
class DismissRoomHandler(RequestHandler):
    def post(self, *args, **kwargs):
        proto = game_pb2.DismissRoomWebRequest()
        proto.ParseFromString(self.request.body)
        table = TableMgr().room_dict.get(proto.room_id)
        if table:
            assert table.room_id == proto.room_id
            assert table.conf.game_type == proto.game_type
            assert table.conf.app_id == proto.app_id
            assert table.owner == proto.owner
            assert table.room_uuid == proto.room_uuid
            table.dismiss_state = True
            # noinspection PyBroadException
            try:
                table.dismiss_room(False)
            except Exception:
                fp = StringIO()
                traceback.print_exc(file=fp)
                table.logger.critical(fp.getvalue())
                table.delete()
                TableMgr().dismiss(proto.room_id)
        proto_back = game_pb2.DismissRoomWebResponse()
        proto_back.code = 0
        proto_back.room_id = proto.room_id
        proto_back.game_type = proto.game_type
        proto_back.app_id = proto.app_id
        proto_back.owner = proto.owner
        self.write(proto.SerializeToString())


# noinspection PyAbstractClass
class LoadBalanceHandler(RequestHandler):
    def post(self, *args, **kwargs):
        proto = game_pb2.LoadBalanceWebResponse()
        for room_id, table in TableMgr().room_dict.items():
            if not table:
                TableMgr().dismiss(room_id)
                continue
            unit = proto.unit.add()
            unit.room_id = table.room_id
            unit.room_status = 0 if table.state == "InitState" else 1
            unit.room_uuid = table.room_uuid
            unit.owner = table.owner
            unit.game_type = table.conf.game_type
            unit.app_id = table.conf.app_id
            unit.st = int(table.st)
            for player in table.player_dict.keys():
                unit.player.append(player)
        self.write(proto.SerializeToString())


# noinspection PyAbstractClass
class ExistRoomHandler(RequestHandler):
    def post(self, *args, **kwargs):
        proto = game_pb2.ExistRoomWebRequest()
        proto.ParseFromString(self.request.body)
        table = TableMgr().room_dict.get(proto.room_id)
        if table:
            flag = True
        else:
            flag = False
        proto = game_pb2.ExistRoomWebResponse()
        proto.flag = flag
        self.write(proto.SerializeToString())


# noinspection PyAbstractClass
class RunningHandler(RequestHandler):
    def post(self, *args, **kwargs):
        proto = game_pb2.RunningWebReponse()
        tables_initial = 0
        tables_playing = 0
        for room_id, table in TableMgr().room_dict.items():
            if not table:
                TableMgr().dismiss(room_id)
                continue
            if table.state == "InitState":
                tables_initial += 1
            else:
                tables_playing += 1
        proto.sessions = len(SessionMgr().session_set)
        proto.players = len(SessionMgr().player_dict)
        proto.tables_initial = tables_initial
        proto.tables_playing = tables_playing
        self.write(proto.SerializeToString())


class BroadcastHandler(RequestHandler):
    def post(self, *args, **kwargs):
        # proto = game_pb2.BroadcastWebRequest()
        # proto.ParseFromString(self.request.body)       
        # message = proto.message
        # ext_info = proto.ext_info
        body = json.loads(self.request.body)
        message = body.get('message')
        ext_info = body.get('ext_info')

        table_mgr = TableMgr()
        table_mgr.broadcast = [message]

        for room_id, table in table_mgr.room_dict.items():
            if not table:
                TableMgr().dismiss(room_id)
                continue                   
            try:
                table.broadcast_all(message)
            except Exception:
                fp = StringIO()
                traceback.print_exc(file=fp)
                table.logger.critical(fp.getvalue())

    def get(self, *args, **kwargs):
        self.write("ok")


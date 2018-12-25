# coding: utf-8

from tornado.options import options

from protocol import game_pb2
from protocol.commands import ENTER_ROOM
from protocol.serialize import send
from utils.singleton import Singleton
from logic.table import Table
from logic.table_conf import TableConf
from logic.session_manager import SessionMgr
from settings import redis
from logic.backup import loads_table
from web.request import WebRequest


class TableMgr(object):
    __metaclass__ = Singleton

    def __init__(self):
        self.room_dict = {}
        self.name = "table:mgr:{0}".format(options.server_port)
        self.broadcast = [] # [start_time, message]
        
    def create(self, room_id, room_uuid, owner, kwargs):
        table = Table(room_id, room_uuid, owner, kwargs)
        table.conf = TableConf(table.kwargs)
        table.chairs = table.conf.chairs
        table.request = WebRequest(room_id, room_uuid, table.conf.game_type, table.conf.app_id, owner)
        table.cards_total = 136

        from state.table_state.init import InitState as TableInitState
        table.machine.trigger(TableInitState())
        self.room_dict[room_id] = table
        redis.sadd(self.name, room_id)

    def dismiss(self, room_id):
        try:
            del self.room_dict[room_id]
        except KeyError:
            print "room id ", room_id, "not in table mgr"
        redis.srem(self.name, room_id)

    def reload(self):
        room_list = redis.smembers(self.name)
        for room in room_list:
            room_id = int(room)
            try:
                table = loads_table(room_id)
                self.room_dict[room_id] = table
                print room_id, "load success"
            except Exception as e:
                print room_id, "load failed"
                print e
                import traceback
                traceback.print_exc()

    def enter(self, room_id, player_id, info, session):
        #print "player {0} enter room {1}, session {2}".format(player_id, room_id, session.uuid)
        table = self.room_dict.get(room_id)
        #if not table:
            #self.create(room_id,'asdfasdfsaf', player_id,
                        #'{"game_type":163,"max_rounds":6,"play_type":100,"has_zhong":0,"app_id":47,"has_niao":0,"chips":null,"options":604005382,"ren_shu":4,"qiang_gang":0,"bao_gang":0,"hu_pai":1,"create_type":2,"aa":0}')
            #table = self.room_dict.get(room_id)
        if not table:
            # 给前端返回房间不存在的错误
            proto = game_pb2.EnterRoomResponse()
            proto.code = 5001
            send(ENTER_ROOM, proto, session)
            print("room {0} not exist, player {1} enter failed".format(room_id, player_id))
            return
        if table.room_id != room_id:
            self.room_dict[table.room_id] = table
            del self.room_dict[room_id]
            proto = game_pb2.EnterRoomResponse()
            proto.code = 5001
            send(ENTER_ROOM, proto, session)
            table.logger.fatal("room id map error: proto {0} actually {1}".format(room_id, table.room_id))
            return
        player = table.player_dict.get(player_id)
        if player:
            # 服务重启后player没有session
            if player.session:
                player.table.logger.info("player {0} cancel old session {1}".format(player_id, player.session.uuid))
                # SessionMgr().cancel(player.session)
                player.session.close()
            SessionMgr().register(player, session)
            player.table.logger.info("player {0} register new session {1}".format(player_id, player.session.uuid))
            player.reconnect()
            player.online_status(True)
        else:
            table.enter_room(player_id, info, session)

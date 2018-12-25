# coding: utf-8

from protocol import game_pb2
from protocol.commands import READY
from protocol.serialize import send
from state.player_state.base import PlayerStateBase


class ReadyState(PlayerStateBase):
    def enter(self, owner):
        super(ReadyState, self).enter(owner)
        # 广播其他玩家
        for k, v in owner.table.player_dict.items():
            proto = game_pb2.ReadyResponse()
            proto.player = owner.uuid
            proto.cur_circle = owner.table.cur_real_round
            proto.cur_round = owner.table.cur_round
            send(READY, proto, v.session)
        owner.table.is_all_ready()
        owner.dumps()

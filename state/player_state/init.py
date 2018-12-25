# coding: utf-8

from state.player_state.base import PlayerStateBase
from logic.player_action import *


class InitState(PlayerStateBase):

    def execute(self, owner, event, proto=None):
        super(InitState, self).execute(owner, event, proto)
        if event == "ready":
            owner.ready()
        else:
            owner.table.logger.warn("player {0} event {1} not register".format(owner.seat, event))
            proto_re = game_pb2.CommonNotify()
            proto_re.messageId = PLAYER_MSG_RECONNECT
            send(NOTIFY_MSG, proto_re, owner.session)
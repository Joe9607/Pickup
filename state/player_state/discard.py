# coding: utf-8
from protocol import game_pb2
from protocol.commands import NOTIFY_MSG
from protocol.serialize import send
from rules.define import PLAYER_MSG_RECONNECT
from state.player_state.base import PlayerStateBase
from logic.player_action import discard
from state.player_state.wait import WaitState


class DiscardState(PlayerStateBase):
    def enter(self, owner):
        super(DiscardState, self).enter(owner)
        # 海底状态直接返回，防止前端自动出牌
        if owner.table.state == "HaiDiState":
            return
        # 防止前端未发 pass
        owner.table.clear_prompt()
        owner.table.clear_actions()

    def execute(self, owner, event, proto=None):
        super(DiscardState, self).execute(owner, event, proto)
        if event == "discard":
            discard(owner, proto)
        else:
            owner.table.logger.warn("player {0} event {1} not register".format(owner.seat, event))
            proto_re = game_pb2.CommonNotify()
            proto_re.messageId = PLAYER_MSG_RECONNECT
            send(NOTIFY_MSG, proto_re, owner.session)

    def exit(self, owner):
        super(DiscardState, self).exit(owner)

    def next_state(self, owner):
        # 要先将自己切换为等待状态 否则流局这种情况在切换到SettleState后又切回来了
        owner.machine.trigger(WaitState())
        owner.table.machine.cur_state.execute(owner.table, "step")

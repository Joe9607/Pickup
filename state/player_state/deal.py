# coding: utf-8

from state.player_state.base import PlayerStateBase
from state.player_state.wait import WaitState
from rules.player_rules.manager import PlayerRulesManager
from rules.define import *


class DealState(PlayerStateBase):
    def __init__(self):
        super(DealState, self).__init__()

    def enter(self, owner):
        super(DealState, self).enter(owner)
        PlayerRulesManager().condition(owner, PLAYER_RULE_DEAL)
        owner.dumps()

    def next_state(self, owner):
        owner.proto.send()
        owner.ready_hand()      # 检测自己能碰和胡的牌
        owner.machine.trigger(WaitState())
        owner.table.machine.cur_state.execute(owner.table, "prompt_deal")

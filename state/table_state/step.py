# coding: utf-8


from state.table_state.base import TableStateBase
from rules.table_rules.manager import TableRulesManager
from state.player_state.draw import DrawState
from rules.define import *


class StepState(TableStateBase):
    def __init__(self):
        super(StepState, self).__init__()

    def enter(self, owner):
        super(StepState, self).enter(owner)
        # if owner.conf.is_fan_hu("HDLY"):
        #     TableRulesManager().condition(owner, TABLE_RULE_STEP_WITH_HAIDI)
        # else:
        TableRulesManager().condition(owner, TABLE_RULE_STEP)

    def next_state(self, owner):
        if owner.active_seat >= 0:
            active_player = owner.seat_dict[owner.active_seat]
            owner.active_seat = active_player.next_seat
        else:
            owner.active_seat = owner.dealer_seat
        active_player = owner.seat_dict[owner.active_seat]

        from state.table_state.wait import WaitState
        owner.machine.trigger(WaitState())
        active_player.machine.trigger(DrawState())

# coding: utf-8


from state.table_state.base import TableStateBase
from rules.table_rules.manager import TableRulesManager
from rules.define import *
from state.table_state.deal import DealState


class ReadyState(TableStateBase):
    def enter(self, owner):
        super(ReadyState, self).enter(owner)
        for k, v in owner.seat_dict.items():
            next_seat = k + 1
            if next_seat == owner.chairs:
                next_seat = 0
            v.next_seat = next_seat
            prev_seat = k - 1
            if prev_seat == -1:
                prev_seat = owner.chairs - 1
            v.prev_seat = prev_seat
        owner.logger.info("table ready")
        owner.dumps()
        TableRulesManager().condition(owner, TABLE_RULE_READY)

    def next_state(self, owner):
        owner.machine.trigger(DealState())


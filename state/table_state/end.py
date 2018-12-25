# coding: utf-8


from state.table_state.base import TableStateBase
from rules.table_rules.manager import TableRulesManager
from rules.define import *
from state.table_state.settle_for_round import SettleForRoundState


class EndState(TableStateBase):
    def enter(self, owner):
        super(EndState, self).enter(owner)
        TableRulesManager().condition(owner, TABLE_RULE_END)

    def next_state(self, owner):
        owner.machine.trigger(SettleForRoundState())

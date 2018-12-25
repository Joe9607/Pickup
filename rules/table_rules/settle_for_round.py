# coding: utf-8

from rules.table_rules.base import TableRulesBase


# from state.table_state.settle_for_room import SettleForRoomState


class SettleForRoundRule(TableRulesBase):
    def condition(self, table):
        if table.conf.is_round:        
            res = table.total_round > table.conf.max_rounds
        else:
            res = (table.cur_round - 1)>= table.conf.circle * table.chairs
        if res:
            return True
        else:
            return False

    def action(self, table):
        # return
        # table.machine.trigger(SettleForRoomState())
        table.dismiss_room()

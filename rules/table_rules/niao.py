# coding: utf-8

from rules.table_rules.base import TableRulesBase
from rules.table_rule_states.niao import NiaoState


class NiaoRule(TableRulesBase):
    def condition(self, table):
        if table.conf.is_niao() and table.win_type > 0:
            return True
        else:
            return False

    def action(self, table):
        table.machine.trigger(NiaoState())

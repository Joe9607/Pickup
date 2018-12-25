# coding: utf-8
from rules.player_rules.manager import PlayerRulesManager
from state.player_state.base import PlayerStateBase
from rules.define import *
from state.table_state.step import StepState


class AfterKongState(PlayerStateBase):

    def enter(self, owner):
        super(AfterKongState, self).enter(owner)
        owner.table.clear_prompt()
        owner.table.clear_actions()
        for i in owner.table.player_dict.values():
            PlayerRulesManager().condition(i, PLAYER_RULE_KG_AFTER)
        if not owner.table.player_prompts:
            owner.table.machine.trigger(StepState())

# coding: utf-8

from state.player_state.base import PlayerStateBase
from rules.player_rules.base import PlayerRulesBase
from rules.define import *


class SmallWinRuleState(PlayerRulesBase):
    def condition(self, player):
        pass
        # if True:
        #     PlayerRulesBase.add_prompt(player, {}, PLAYER_WEIGHT_DEAL)

    def action(self, player):
        pass


class SmallWinRule(PlayerStateBase):
    def enter(self, owner):
        pass

    def exit(self, owner):
        pass

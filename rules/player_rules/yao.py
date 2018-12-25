# coding: utf-8
from rules.player_rule_states.ting import TingState
from rules.player_rules.base import PlayerRulesBase
from rules.define import *
from behavior_tree.forest import is_ready_hand
from rules.player_rule_states.yao import YaoState


class YaoRule(PlayerRulesBase):
    def __init__(self):
        super(YaoRule, self).__init__()
        self.ruleState = YaoState()

    def condition(self, player):
        #is_ready_hand(player).keys()
        if len(player.cards_ready_hand) > 0:
            self.add_prompt(player, PLAYER_ACTION_TYPE_YAO_GANG, 0)
            return True
        return False
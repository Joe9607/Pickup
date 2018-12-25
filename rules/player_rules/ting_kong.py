# coding: utf-8
from rules.player_rule_states.ting_kong import TingKongState
from rules.player_rules.base import PlayerRulesBase
from rules.define import *
import datetime
from behavior_tree.forest import is_ready_hand
from logic.player_action import *


class TingKongRule(PlayerRulesBase):
    def __init__(self):
        super(TingKongRule, self).__init__()
        self.ruleState = TingKongState()

    def condition(self, player):
        # player.had_check_ting_kong = True
        flag = False
        if player.isTing:
            return False
        cards = []
        cards_ready_hand = is_ready_hand(player)
        for k in cards_ready_hand.keys():
            cards.append(k)
        if cards:
            self.add_prompt(player, PLAYER_ACTION_TYPE_TING, 0, cards)
            flag = True
        return flag
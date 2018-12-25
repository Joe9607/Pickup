# coding: utf-8
from rules.player_rule_states.ting import TingState
from rules.player_rules.base import PlayerRulesBase
from rules.define import *
import datetime
from behavior_tree.forest import is_ready_hand
from logic.player_action import *


class TingRule(PlayerRulesBase):
    def __init__(self):
        super(TingRule, self).__init__()
        self.ruleState = TingState()

    def condition(self, player):
        cards_test = set(player.cards_in_hand)
        flag = False
        if player.isTing:
            return False
        for i in cards_test:
            player.cards_in_hand.remove(i)
            cards = []
            cards_ready_hand = is_ready_hand(player)
            for k in cards_ready_hand.keys():
                cards.append(k)
            player.cards_in_hand.append(i)
            if cards:
                self.add_prompt(player, PLAYER_ACTION_TYPE_TING, i, cards)
                flag = True
        return flag
# coding: utf-8

from collections import Counter

from logic.player_action import try_kong
from rules.player_rule_states.draw_concealed_kong_kg import DrawConcealedKongKGState
from rules.player_rules.base import PlayerRulesBase
from rules.define import *
from behavior_tree.forest import is_ready_hand


#暗杠
class DrawConcealedKongKGRule(PlayerRulesBase):
    def __init__(self):
        super(DrawConcealedKongKGRule, self).__init__()
        self.ruleState = DrawConcealedKongKGState()

    def condition(self, player):
        flag = False
        rest = player.table.conf.niao_num + 1
        if len(player.table.cards_on_desk) < rest:
            return False
        if player.seat != player.table.active_seat:
            return False
        c = Counter(player.cards_in_hand)

        for e, cnt in c.most_common():
            # if cnt == 4 and try_kong(player, [e] * 4, False):
            if cnt == 4 and try_kong(player, [e] * 4):
                flag = True
                self.add_prompt(player, PLAYER_ACTION_TYPE_KONG_CONCEALED_KG, e, [e] * 4)
        return flag

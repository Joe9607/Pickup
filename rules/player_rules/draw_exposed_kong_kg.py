# coding: utf-8
from logic.player_action import try_kong
from rules.player_rule_states.draw_exposed_kong_kg import DrawExposedKongKGState
from rules.player_rules.base import PlayerRulesBase
from rules.define import *
from behavior_tree.forest import is_ready_hand


#明杠
class DrawExposedKongKGRule(PlayerRulesBase):
    def __init__(self):
        super(DrawExposedKongKGRule, self).__init__()
        self.ruleState = DrawExposedKongKGState()

    def condition(self, player):
        flag = False
        rest = player.table.conf.niao_num + 1
        if len(player.table.cards_on_desk) < rest:
            return False
        if player.seat != player.table.active_seat:
            return False
        #if player.re
        for e in set(player.cards_in_hand):
            # if e in set(player.cards_pong) and try_kong(player, [e], False):
            if e in set(player.cards_pong) and try_kong(player, [e]):#碰杠
                self.add_prompt(player, PLAYER_ACTION_TYPE_KONG_PONG_KG, e, [e])
                flag = True

        return flag

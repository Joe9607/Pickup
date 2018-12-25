# coding: utf-8
# from behavior_tree.forest import is_ready_hand
from logic.player_action import try_kong
from rules.player_rule_states.discard_exposed_kong_kg import DiscardExposedKongKGState
from rules.player_rules.base import PlayerRulesBase
from rules.define import *


#放杠
class DiscardExposedKongKGRule(PlayerRulesBase):
    def __init__(self):
        super(DiscardExposedKongKGRule, self).__init__()
        self.ruleState = DiscardExposedKongKGState()

    def condition(self, player):
        active_card = player.table.active_card
        rest = player.table.conf.niao_num + 1
        if len(player.table.cards_on_desk) < rest:
            return False
        if player.seat == player.table.active_seat:
            return False

        # if try_kong(player, [active_card] * 3, False):
        if try_kong(player, [active_card] * 3):
            self.add_prompt(player, PLAYER_ACTION_TYPE_KONG_EXPOSED_KG, active_card, [active_card] * 3)
            return True
        else:
            return False

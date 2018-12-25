# coding: utf-8

from rules.player_rule_states.pong import PongState
from rules.player_rules.base import PlayerRulesBase
from rules.define import *
from behavior_tree.base import *


class PongRule(PlayerRulesBase):
    def __init__(self):
        super(PongRule, self).__init__()
        self.ruleState = PongState()

    def condition(self, player):
        if player.isTing:
            return False
        # if not player.table.conf.can_hu_with_one() and len(player.cards_in_hand) == 4:
        #     if player.cards_chow:
        #         return False
        #     if not player.table.conf.is_fan_hu("PIAOHU"):
        #         return False
        # if len(player.table.cards_on_desk) < (player.table.conf.chairs+player.table.reserved_cards):
        #     return False
        active_card = player.table.active_card
        can_pong_zfb = player.table.conf.can_pong_on_zfb()
        if active_card in [ZHONG,FA,BAI] and not can_pong_zfb:
            return False
        if player.cards_in_hand.count(active_card) >= 2:
            self.add_prompt(player, PLAYER_ACTION_TYPE_PONG, active_card, [active_card]*2)
            return True
        return False

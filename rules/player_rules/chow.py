# coding: utf-8

from rules.player_rule_states.chow import ChowState
from rules.player_rules.base import PlayerRulesBase
from rules.define import *


class ChowRule(PlayerRulesBase):
    def __init__(self):
        super(ChowRule, self).__init__()
        self.ruleState = ChowState()

    def condition(self, player):
        if not player.table.can_chow:
            return False
        if player.isTing:
            return False
        if len(player.table.cards_on_desk) < (player.table.conf.chairs+player.table.reserved_cards):
            return False
        if not player.table.conf.can_hu_with_one() and len(player.cards_in_hand) == 4:
            return False
        if player.table.active_seat != player.prev_seat:
            return False
        card = player.table.active_card
        tiles = player.cards_in_hand

        flag = False
        if card + 1 in tiles and card + 2 in tiles and card >= 0x11 and card + 2 <= 0x39:
            self.add_prompt(player, PLAYER_ACTION_TYPE_CHOW, card, [card + 1, card + 2])
            flag = True
        if card - 1 in tiles and card + 1 in tiles and card - 1 >= 0x11 and card + 1 <= 0x39:
            self.add_prompt(player, PLAYER_ACTION_TYPE_CHOW, card, [card - 1, card + 1])
            flag = True
        if card - 2 in tiles and card - 1 in tiles and card - 2 >= 0x11 and card <= 0x39:
            self.add_prompt(player, PLAYER_ACTION_TYPE_CHOW, card, [card - 2, card - 1])
            flag = True
        return flag

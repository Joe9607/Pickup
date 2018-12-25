# coding: utf-8

from collections import Counter
from rules.player_rule_states.draw_concealed_kong import DrawConcealedKongState
from rules.player_rules.base import PlayerRulesBase
from rules.define import *


class DrawConcealedKongRule(PlayerRulesBase):
    def __init__(self):
        super(DrawConcealedKongRule, self).__init__()
        self.ruleState = DrawConcealedKongState()

    def can_kong(self, player, card):
        if not player.isTing:
            return True
        flag = True
        for card_groups in player.has_win_cards.values():
            for group in card_groups:
                if card in group and len(group) == 3 and group[0] != group[2]:
                    flag = False
                if len(group) == 2 and group[0] == card:
                    flag = False
        return flag






    def condition(self, player):
        flag = False
        active_card = player.table.active_card
        if len(player.table.cards_on_desk) < player.table.reserved_cards:
            return False
        c = Counter(player.cards_in_hand)
        for e, cnt in c.most_common():
            if cnt == 4:
                # 杠牌是否影响听牌
                if self.can_kong(player, e):
                    self.add_prompt(player, PLAYER_ACTION_TYPE_KONG_CONCEALED, e, [e]*4)
                    flag = True
        return flag

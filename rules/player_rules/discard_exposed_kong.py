# coding: utf-8

from rules.player_rule_states.discard_exposed_kong import DiscardExposedKongState
from rules.player_rules.base import PlayerRulesBase
from rules.define import *


class DiscardExposedKongRule(PlayerRulesBase):
    def __init__(self):
        super(DiscardExposedKongRule, self).__init__()
        self.ruleState = DiscardExposedKongState()

    def can_kong(self, player, card):
        if len(player.table.cards_on_desk) < player.table.reserved_cards:
            return False
        if not player.isTing:
            return True
        # if not player.table.conf.can_hu_with_one() and len(player.cards_in_hand) == 4:
        #     if player.cards_chow:
        #         return False
        #     if not player.table.conf.is_fan_hu("PIAOHU"):
        #         return False
        # for card_group in player.win_card_group.values():
        #     for group in card_group:
        #         if len(group) == 2 and group[0] == card:
        #             return False
        #         if card in group and len(group) == 3 and group[0] != group[2]:  # 与其他牌组成顺子
        #             return False
        # return True
        # 要杠的牌在已经胡过得牌的values 中以顺子存在,或者以对子存在则不能杠
        flag = True
        for card_groups in player.has_win_cards.values():
            for group in card_groups:
                if card in group and len(group) == 3 and group[0] != group[2]:
                    flag = False
                if len(group) == 2 and group[0] == card:
                    flag = False
        return flag

    def condition(self, player):
        active_card = player.table.active_card
        #杠牌是否影响听牌
        if len(player.table.cards_on_desk) < player.table.reserved_cards:
            return False
        if player.cards_in_hand.count(active_card) == 3:
            if self.can_kong(player, active_card):
                self.add_prompt(player, PLAYER_ACTION_TYPE_KONG_EXPOSED, active_card, [active_card]*3)
                return True
        return False

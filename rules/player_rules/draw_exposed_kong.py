# coding: utf-8

from rules.player_rule_states.draw_exposed_kong import DrawExposedKongState
from rules.player_rules.base import PlayerRulesBase
from rules.define import *


class DrawExposedKongRule(PlayerRulesBase):
    def __init__(self):
        super(DrawExposedKongRule, self).__init__()
        self.ruleState = DrawExposedKongState()

    def can_kong(self, player, card):
        if not player.isTing:
            return True
        # if not player.table.conf.can_hu_with_one() and len(player.cards_in_hand) == 4:
        # if len(player.cards_in_hand) <= 1:
        #     return False
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
                print "===============group"
                if card in group and len(group) == 3 and group[0] != group[2]:
                    flag = False
                if len(group) == 2 and group[0] == card:
                    flag = False
        return flag

    def condition(self, player):
        flag = False
        if len(player.table.cards_on_desk) < player.table.reserved_cards:
            return False

        for e in player.cards_in_hand:
            if e in player.cards_pong:
                # if player.is_yao_fail and e in player.miss_gang_cards:
                #     return False
                if self.can_kong(player, e):
                    self.add_prompt(player, PLAYER_ACTION_TYPE_KONG_PONG, player.draw_card, [e])
                    flag = True
        return flag

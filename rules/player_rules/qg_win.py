# coding: utf-8

from rules.player_rules.base import PlayerRulesBase
from rules.define import *
from rules.player_rule_states.qg_win import QGWinState

"""
单纯的屁胡不能胡
需要判断 是否为抢杠胡，番数是否大于一（是否亮倒）
"""


class QGWinRule(PlayerRulesBase):
    def __init__(self):
        super(QGWinRule, self).__init__()
        self.ruleState = QGWinState()

    def condition(self, player):
        if not player.table.conf.is_qg():
            return False
        if not player.table.conf.is_pao():
            return False
        if player.table.conf.is_zimo():
            return False
        active_card = player.table.active_card
        # if active_card in player.miss_win_cards:
        #     player.table.logger.info("{0} in miss list {1}".format(active_card, player.miss_win_cards))
        #     return False
        # if active_card in player.cards_ready_hand:
            # player.miss_win_cards.append(active_card)
            # player.table.win_seat_prompt.append(player.seat)
            # self.add_prompt(player, PLAYER_ACTION_TYPE_WIN_DISCARD, active_card, player.cards_in_hand)
            # return True
        if active_card in player.cards_ready_hand:
            flag = False
            if player.isJia:
                if "JIAHU" in player.cards_ready_hand[active_card][1]:
                    flag = True
                if player.table.conf.bian_hu_jia():
                    if "BIANHU" in player.cards_ready_hand[active_card][1]:
                        flag = True
            else:
                flag = True
            if flag:
                player.table.win_seat_prompt.append(player.seat)
                self.add_prompt(player, PLAYER_ACTION_TYPE_WIN_DISCARD, active_card, player.cards_in_hand)
            return flag

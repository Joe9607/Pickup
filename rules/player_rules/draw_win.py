# coding: utf-8

from rules.player_rules.base import PlayerRulesBase
from rules.define import *
from rules.player_rule_states.draw_win import DrawWinState
from win_algorithm.base import WinAlgorithm
from behavior_tree.base import *

"""
单纯的屁胡不能胡
需要判断 是否为抢杠胡，番数是否大于一（是否亮倒）
"""


class DrawWinRule(PlayerRulesBase):
    def __init__(self):
        super(DrawWinRule, self).__init__()
        self.ruleState = DrawWinState()

    def can_tian_hu(self, player):
        win_alm = WinAlgorithm(True)
        if player.table.conf.can_hu_on_ready() and player.table.step == 0:
            self.card_group = win_alm.start(player.cards_in_hand)
            return bool(self.card_group)
        else:
            return False

    def condition(self, player):
        active_card = player.draw_card
        # 必须听牌才能胡
        if not (player.table.conf.can_hu_on_ready() and player.table.step == 0):
            if not player.isTing:
                return False
        elif self.can_tian_hu(player):
            player.table.win_seat_prompt.append(player.seat)
            self.add_prompt(player, PLAYER_ACTION_TYPE_WIN_DRAW, active_card, player.cards_in_hand)
            return True
        if active_card in player.cards_ready_hand:
            player.table.win_seat_prompt.append(player.seat)
            self.add_prompt(player, PLAYER_ACTION_TYPE_WIN_DRAW, active_card, player.cards_in_hand)
            return True

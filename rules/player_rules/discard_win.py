# coding: utf-8

from rules.player_rules.base import PlayerRulesBase
from rules.define import *
from rules.player_rule_states.discard_win import DiscardWinState

class DiscardWinRule(PlayerRulesBase):
    def __init__(self):
        super(DiscardWinRule, self).__init__()
        self.ruleState = DiscardWinState()

    def condition(self, player):
        if len(player.table.cards_on_desk) < (player.table.conf.chairs+player.table.reserved_cards):
            return False
        # 暂时用下面这个控制死
        if not player.table.conf.is_pao():
            return False
        if player.table.conf.is_zimo():
            return False
        active_card = player.table.active_card
        if not player.isTing:
            return False
        # tmp_ready_cards = []
        # for card in player.cards_ready_hand.keys():
        #     tmp_ready_cards.append(int(card))
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

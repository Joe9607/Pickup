# coding: utf-8

from rules.player_rules.base import PlayerRulesBase
from rules.define import *
from rules.player_rule_states.win import WinState


class WinRule(PlayerRulesBase):
    def __init__(self):
        super(WinRule, self).__init__()
        self.ruleState = WinState()

    def condition(self, player):
        win_type = None

        if player.state == "DrawState":
            active_card = player.draw_card
            win_type = PLAYER_ACTION_TYPE_WIN_DRAW
        else:
            active_card = player.table.active_card
            if player.table.conf.is_pao() and active_card not in player.miss_win_cards:
                win_type = PLAYER_ACTION_TYPE_WIN_DISCARD

        if win_type and active_card in player.cards_ready_hand:
            #player.miss_win_cards.append(active_card)
            self.add_prompt(player, win_type, active_card, player.cards_in_hand)
            return True

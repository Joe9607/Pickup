# coding: utf-8
from rules.define import *
from state.player_state.prompt_discard import PromptDiscardState
from state.player_state.prompt_draw import PromptDrawState
from state.player_state.prompt_ting_kong import PromptTingKongState

from utils.singleton import Singleton
from rules.table_rules.niao import NiaoRule
from rules.table_rule_states.niao import NiaoState


# from state.player_state.prompt import PromptState


class PlayerRulesManager(object):
    __metaclass__ = Singleton

    def __init__(self):
        from rules.player_rules.discard_exposed_kong import DiscardExposedKongRule
        from rules.player_rules.draw_concealed_kong import DrawConcealedKongRule
        from rules.player_rules.draw_exposed_kong import DrawExposedKongRule
        from rules.player_rules.discard_win import DiscardWinRule
        from rules.player_rules.draw_win import DrawWinRule
        from rules.player_rules.qg_win import QGWinRule
        from rules.player_rules.pong import PongRule
        from rules.player_rules.ting import TingRule
        from rules.player_rules.chow import ChowRule
        from rules.player_rules.ting_kong import TingKongRule
        self.rules = {
            PLAYER_RULE_READY: [],
            PLAYER_RULE_DRAW: [DrawConcealedKongRule(), DrawExposedKongRule(), TingRule(), DrawWinRule()],
            PLAYER_RULE_DISCARD: [DiscardExposedKongRule(), PongRule()],
            PLAYER_RULE_DEAL: [],
            PLAYER_RULE_CHOW: [TingRule(),DrawConcealedKongRule(), DrawExposedKongRule()],
            PLAYER_RULE_PONG: [TingRule(),DrawConcealedKongRule(), DrawExposedKongRule()],
            PLAYER_RULE_KONG: [],
            PLAYER_RULE_WIN: [],
            PLAYER_RULE_NIAO: [],
            PLAYER_RULE_YAO: [],
            PLAYER_RULE_MOON:[DrawWinRule()],
            PLAYER_RULE_TING_KONG:[TingKongRule()],
        }

    def condition(self, player, rule):
        if rule not in self.rules.keys():
            player.table.logger.warn("player {0} rule {1} not exist".format(player.seat, rule))
            return
        flag = False
        for r in self.rules[rule]:
            if r.condition(player):
                flag = True
        if flag:
            # player.machine.trigger(PromptState())
            if rule in (PLAYER_RULE_DISCARD,PLAYER_RULE_KONG):
                player.machine.trigger(PromptDiscardState())
            elif rule in (PLAYER_RULE_TING_KONG,):
                player.machine.trigger(PromptTingKongState())
            else:
                player.machine.trigger(PromptDrawState())
        else:
            player.machine.cur_state.next_state(player)

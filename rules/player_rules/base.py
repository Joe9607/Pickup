# coding: utf-8

from utils.singleton import Singleton


class PlayerRulesBase(object):
    __metaclass__ = Singleton

    def __init__(self):
        self.name = self.__class__.__name__
        self.ruleState = None

    def condition(self, player):
        pass

    def action(self, player):
        player.machine.trigger(self.ruleState)

    def add_prompt(self, player, prompt, op_card, ref_cards=None):
        player.add_prompt(prompt, self.name, op_card, ref_cards)

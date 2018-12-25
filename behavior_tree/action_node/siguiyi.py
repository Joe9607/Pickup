# coding: utf-8

from behavior_tree.base import *
from win_algorithm.base import WinAlgorithm
from copy import copy


class SGY(NodeBase):
    def __init__(self, weight=1):
        super(SGY, self).__init__(weight)

    def condition(self, player):
        super(SGY, self).condition(player)
        cards = copy(player.cards_in_hand)
        tfs = WinAlgorithm()
        if tfs.start(cards) and player.draw_card in set(player.cards_pong):
            return True
        else:
            return False

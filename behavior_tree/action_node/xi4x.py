# coding: utf-8

from collections import Counter
from behavior_tree.base import *


class XI4X(NodeBase):
    def __init__(self, weight=1):
        super(XI4X, self).__init__(weight)

    def condition(self, player):
        super(XI4X, self).condition(player)
        cards = []
        for k, v in Counter(player.cards_in_hand).items():
            if v == 4:
                cards.extend([k]*v)
        if cards:
            player.cards_unfold.extend(cards)
            return True
        else:
            return False

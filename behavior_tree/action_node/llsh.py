# coding: utf-8

from collections import Counter
from behavior_tree.base import *


class LLSH(NodeBase):
    def __init__(self, weight=1):
        super(LLSH, self).__init__(weight)

    def condition(self, player):
        super(LLSH, self).condition(player)
        flag = 0
        cards = []
        for k, v in Counter(player.cards_in_hand).items():
            if v >= 3:
                flag += 1
                cards.extend([k]*v)
        if flag >= 2:
            player.cards_unfold.extend(cards)
            return True
        else:
            return False

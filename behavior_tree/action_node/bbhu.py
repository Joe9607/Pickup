# coding: utf-8

from copy import copy
from behavior_tree.base import *


class BBHU(NodeBase):
    def __init__(self):
        super(BBHU, self).__init__(1)

    def condition(self, player):
        super(BBHU, self).condition(player)
        flag = len(filter(lambda x: x % 16 not in (2, 5, 8), player.cards_in_hand)) == len(player.cards_in_hand)
        flag = flag and (len(player.cards_in_hand) == 14)
        if flag:
            player.cards_unfold = copy(player.cards_in_hand)
        return flag

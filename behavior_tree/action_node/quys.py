# coding: utf-8

from copy import copy
from behavior_tree.base import *


class QUYS(NodeBase):
    def __init__(self):
        super(QUYS, self).__init__(1)

    def condition(self, player):
        super(QUYS, self).condition(player)
        wan, tiao, tong = 0, 0, 0
        for i in player.cards_in_hand:
            if i in WAN:
                wan += 1
            if i in TIAO:
                tiao += 1
            if i in TONG:
                tong += 1
        if not(wan and tiao and tong):
            player.cards_unfold = copy(player.cards_in_hand)
            return True
        else:
            return False

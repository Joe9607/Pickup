# coding: utf-8

from copy import copy
from behavior_tree.base import *


class QIYS(NodeBase):
    def __init__(self, weight=1):
        super(QIYS, self).__init__(weight)

    def condition(self, player):
        super(QIYS, self).condition(player)
        cards = copy(player.cards_in_hand)
        cards.extend(player.cards_group)
        cards.sort()
        flag = False
        if 0x11 <= cards[0] <= cards[-1] <= 0x19:
            flag = True
        if 0x21 <= cards[0] <= cards[-1] <= 0x29:
            flag = True
        if 0x31 <= cards[0] <= cards[-1] <= 0x39:
            flag = True
        if flag:
            self.append(player)
        return flag

    def execute(self, player):
        if not self.condition(player):
            return False
        if "QIYS" in FANS_ZHUANG.keys() and "QIYS" not in player.router:
            player.router.append("QIYS")
        for child in self.children:
            child.execute(player)

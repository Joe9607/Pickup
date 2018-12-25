# coding: utf-8

from behavior_tree.base import *
from behavior_tree.action_node.qiys import QIYS


class XIQD(NodeBase):
    def __init__(self, weight=1):
        super(XIQD, self).__init__(weight)
        self.children = [QIYS()]

    def condition(self, player):
        super(XIQD, self).condition(player)
        cards = copy(player.cards_in_hand)
        if player.table.conf.is_zhong():

            while ZHONG in cards:
                cards.remove(ZHONG)
            if len(set(cards)) == 7:
                return True
        else:

            if len(set(cards)) == 7:
                return True
        return False

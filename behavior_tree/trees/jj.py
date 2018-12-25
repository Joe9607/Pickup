# coding: utf-8

from behavior_tree.base import *


class TreeJJ(NodeBase):
    def __init__(self):
        super(TreeJJ, self).__init__(1)

    def condition(self, player):
        if not player.table.conf.is_dahu("JJHU"):
            return False
        cards = copy(player.cards_in_hand)
        while ZHONG in cards:
            cards.remove(ZHONG)
        cards.extend(player.cards_group)
        return len(filter(lambda x: x % 16 in (2, 5, 8), cards)) == len(cards)

    def execute(self, player):
        if not self.condition(player):
            return False
        player.router.append("JJHU")
        #if len(player.cards_in_hand) == 2 and len(set(player.cards_in_hand)) == 2:
            #player.router.append("QQRN")

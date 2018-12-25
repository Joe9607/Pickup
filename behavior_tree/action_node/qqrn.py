# coding: utf-8

from behavior_tree.base import NodeBase


class QQRN(NodeBase):

    def condition(self, player):
        super(QQRN, self).condition(player)
        if len(set(player.cards_in_hand)) == 1 and len(player.cards_in_hand) == 2:
            return True
        else:
            return False

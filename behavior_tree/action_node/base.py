# coding: utf-8

from behavior_tree.base import *


class BASE(NodeBase):

    def condition(self, player):
        super(BASE, self).condition(player)
        tfs = TFS()
        return bool(tfs.start(player.cards_in_hand))

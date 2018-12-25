# coding: utf-8

from behavior_tree.base import *
from behavior_tree.action_node.qiys import QIYS
from behavior_tree.action_node.qqrn import QQRN
from behavior_tree.action_node.pphu import PPHU
from behavior_tree.action_node.long import LONG


class TreeSpecial(NodeBase):
    def __init__(self):
        super(TreeSpecial, self).__init__(1)
        self.add_child(QIYS())
        self.add_child(QQRN())
        self.add_child(PPHU())

    def condition(self, player):
        tfs = TFS()
        return bool(tfs.start(player.cards_in_hand))

    def execute(self, player):
        if not self.condition(player):
            return False
        for child in self.children:
            child.execute(player)

# coding: utf-8

from behavior_tree.base import *
from behavior_tree.action_node.bbhu import BBHU


class TreeFirst(NodeBase):
    def __init__(self):
        super(TreeFirst, self).__init__(1)
        self.add_child(BBHU())

    def execute(self, player):
        player.router = []
        for child in self.children:
            child.execute(player)
        return player.router

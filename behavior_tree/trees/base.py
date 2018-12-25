# coding: utf-8
from behavior_tree.base import *
from win_algorithm.base import WinAlgorithm
from behavior_tree.action_node.qiys import QIYS
from behavior_tree.action_node.bianhu import BIANHU



class TreeBase(NodeBase):

    def __init__(self):
        super(TreeBase, self).__init__(1)
        self.card_group = {}
        self.add_child(QIYS())

    def condition(self, player):
        win_alm = WinAlgorithm(True)
        self.card_group = win_alm.start(player.cards_in_hand)
        player.win_card_group[player.tmpTingCard] = self.card_group
        return bool(self.card_group)

    def execute(self, player):
        if not self.condition(player):
            return False
        if "BASE" in FANS_ZHUANG.keys() and "BASE" not in player.router:
            player.router.append("BASE")
        for child in self.children:
            child.execute(player)

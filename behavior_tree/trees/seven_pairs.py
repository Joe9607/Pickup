# coding: utf-8
from behavior_tree.base import *
from win_algorithm.base import WinAlgorithmSevenPairs
from behavior_tree.action_node.qiys import QIYS
from behavior_tree.action_node.haqd import HAQD


class TreeSevenPairs(NodeBase):

    def __init__(self):
        super(TreeSevenPairs, self).__init__(1)
        self.card_group2 = {}
        # 在base里会检测一次清一色，这种情况没法通过base检测所以在这也得检测一次
        self.add_child(QIYS())
        self.add_child(HAQD())

    def condition(self, player):
        # if player.table.conf.huang == 2:
        #     return False
        win_alm = WinAlgorithmSevenPairs(True)
        self.card_group2 = win_alm.start(player.cards_in_hand)
        if self.card_group2:
            player.win_card_group[player.tmpTingCard] = self.card_group2
        return bool(self.card_group2)


    def execute(self, player):
        if not self.condition(player):
            return False
        if "TSP" in FANS_ZHUANG.keys() and "TSP" not in player.router:
            player.router.append("TSP")

        for child in self.children:
            child.execute(player)

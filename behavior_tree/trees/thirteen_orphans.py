# coding: utf-8
from behavior_tree.base import *
from win_algorithm.base import WinThirteenOrphans
from behavior_tree.action_node.qiys import QIYS

class TreeThirteenOrphans(NodeBase):

    def __init__(self):
        super(TreeThirteenOrphans, self).__init__(1)
        self.card_group3 = {}
        # 在base里会检测一次清一色，这种情况没法通过base检测所以在这也得检测一次
        self.add_child(QIYS())

    def condition(self, player):
        win_alm = WinThirteenOrphans(True)
        self.card_group3 = win_alm.start(player.cards_in_hand)
        if self.card_group3:
            player.win_card_group[player.tmpTingCard] = self.card_group3
        return bool(self.card_group3)


    def execute(self, player):
        if not self.condition(player):
            return False
        if "TTO" in FANS_ZHUANG.keys() and "TTO" not in player.router:
            player.router.append("TTO")

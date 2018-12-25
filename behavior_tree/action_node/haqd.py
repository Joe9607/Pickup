# coding: utf-8
from behavior_tree.action_node.qiys import QIYS
from behavior_tree.base import *


class HAQD(NodeBase):
    def __init__(self, weight=1):
        super(HAQD, self).__init__(weight)
        self.children = [QIYS()]
        self.count = 0
        # 直接在这计算豪七对所有类型
        self.routes_list = ["HHHQ","HHQ","HAQD"]

    def condition(self, player):
        super(HAQD, self).condition(player)
        cards = copy(player.cards_in_hand)
        if len(set(cards)) < 7:
            return True
        return False
    def execute(self, player):
        if not self.condition(player):
            return False
        cards_t = copy(player.cards_in_hand)
        pairs = len(set(cards_t))
        kind = self.routes_list[pairs-4]
        if kind in FANS_ZHUANG.keys() and kind not in player.router:
            player.router.append(kind)
            # 豪七对和普通七对不同时出现
            if  "TSP" in player.router:
                player.router.remove("TSP")
        for child in self.children:
            child.execute(player)
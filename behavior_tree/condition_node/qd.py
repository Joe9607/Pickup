# coding: utf-8

from copy import copy
from behavior_tree.base import *
from win_algorithm.huaihua import WinAlgorithmSevenPairsHuaiHua
from win_algorithm.base import WinAlgorithmSevenPairs


class QD(NodeBase):
    def __init__(self, weight=1):
        super(QD, self).__init__(weight)

    def condition(self, player):
        # super(QD, self).condition(player)
        if player.table.conf.is_zhong():
            laizi_qd = WinAlgorithmSevenPairsHuaiHua(ZHONG)
            if len(laizi_qd.start(player.cards_in_hand)) > 0:
                return True
            return False
        else:
            qd = WinAlgorithmSevenPairs()
            if len(qd.start(player.cards_in_hand)) > 0:
                return True
            return False

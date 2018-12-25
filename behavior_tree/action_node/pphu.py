# coding: utf-8

from collections import Counter
from behavior_tree.base import *
from win_algorithm.huaihua import WinAlgorithmTriplet


class PPHU(NodeBase):
    def __init__(self, weight=1):
        super(PPHU, self).__init__(weight)

    def condition(self, player):
        super(PPHU, self).condition(player)
        if player.cards_chow:
            return False
        pairs = 0
        triplets = 0
        four_cards = 0
        rest_cards = []
        for k, v in Counter(player.cards_in_hand).items():
            if v == 3:
                triplets += 1
            elif v == 4:
                four_cards += 1
            elif v == 2:
                pairs += 1
            else:
                rest_cards.append(k)
        if not rest_cards and pairs == 1:
            return True
        else:
            return False

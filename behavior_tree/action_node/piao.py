# coding: utf-8

from behavior_tree.control_node.selector import SelectorNode
from behavior_tree.base import NodeBase
from collections import Counter
from behavior_tree.base import *
from win_algorithm.base import WinAlgorithm


class PIAOHU(NodeBase):
    def __init__(self, weight = 1):
        super(PIAOHU, self).__init__(weight)
        self.card_group = {}

    def condition(self, player):
        super(PIAOHU, self).condition(player)
        if not player.table.conf.is_fan_hu("PIAOHU"):
            return False
        if player.cards_chow:
            return False
        if player.table.conf.is_color_all():
            if not player.is_color_all():
                return False
        if player.table.conf.is_open_door():
            if not player.is_open_door():
                return False
        win_alm = WinAlgorithm(True)
        self.card_group = win_alm.start(player.cards_in_hand)
        if not self.card_group:
            return False
        if player.table.conf.is_19():
            if not self.is_19(player):
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
            player.win_card_group[player.tmpTingCard] = self.card_group
            return True
        else:
            return False

    def is_19(self, player):
        card_except = [ZHONG, WEST, EAST, SOUTH, NORTH, FA, BAI]
        for card_group in self.card_group:
            for card in card_group:
                if card in card_except:
                    return True
                elif card & 0xf == 1 or card & 0xf == 9:
                    return True
        for card in player.cards_group:
            if card in card_except:
                return True
            elif card & 0xf == 1 or card & 0xf == 9:
                return True
        if player.tmpTingCard & 0xf == 1 or player.tmpTingCard & 0xf == 9:
            return True
        return False
# coding: utf-8

from behavior_tree.base import *
from copy import copy
from win_algorithm.huaihua import WinAlgorithmHuaiHua


class LONG(NodeBase):
    def __init__(self, weight=1):
        super(LONG, self).__init__(weight)

    def condition(self, player):
        super(LONG, self).condition(player)
        if not player.table.conf.is_dahu("LONG"):
            return False
        if len(player.cards_in_hand) < 11:
            return False

        wan_cards, tong_cards, tiao_cards = [], [], []

        for i in player.cards_in_hand:
            if i & 0xF0 == 0x10 and i & 0x0F > 0:
                wan_cards.append(i)
            if i & 0xF0 == 0x20:
                tong_cards.append(i)
            if i & 0xF0 == 0x30:
                tiao_cards.append(i)

        max_suit = max([len(set(wan_cards)), len(set(tong_cards)), len(set(tiao_cards))])

        def win(suit_cards):
            cards = copy(player.cards_in_hand)
            for e in set(suit_cards):
                cards.remove(e)
            for _ in range(9 - max_suit):
                cards.remove(ZHONG)
            w = WinAlgorithmHuaiHua(ZHONG)
            if w.start(cards):
                return True
            return False

        if player.table.conf.is_zhong():
            if max_suit + player.cards_in_hand.count(ZHONG) < 9:
                return False

            if len(set(wan_cards)) == max_suit and win(wan_cards):
                return True
            if len(set(tong_cards)) == max_suit and win(tong_cards):
                return True
            if len(set(tiao_cards)) == max_suit and win(tiao_cards):
                return True
        else:
            if max_suit == 9:
                return True
        return False






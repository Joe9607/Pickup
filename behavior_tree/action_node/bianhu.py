# coding: utf-8

from behavior_tree.base import *
from copy import copy
from win_algorithm.huaihua import WinAlgorithmHuaiHua


class BIANHU(NodeBase):
    def __init__(self, weight=1):
        super(BIANHU, self).__init__(weight)

    def condition(self, player):
        super(BIANHU, self).condition(player)
        hu_cards = []
        if not player.table.conf.bian_hu_jia():
            return False
        for item in self.parent.card_group:
            for card in item:
                hu_cards.append(card)
        hu_cards.sort()
        player.cards_in_hand.sort()
        idx = 0
        target_card = player.tmpTingCard
        # while idx < len(hu_cards):
        #     if player.cards_in_hand[idx] != hu_cards[idx]:
        #         target_card = hu_cards[idx]
        #         break
        #     idx += 1
        mask_target = target_card & 0x0f
        if mask_target == 0x07 or mask_target == 0x03:
            for item in self.parent.card_group:
                if len(item) == 2:
                    # if target_card in item:
                    #     return False
                    continue
                mask_cards = [0x0f & item[0], 0x0f & item[1], 0x0f & item[2]]
                if mask_cards[2] == mask_cards[0] + 2:
                    if (mask_cards[2] == 3 and target_card == item[2]) or (mask_cards[0] == 7 and target_card == item[0]):
                        return True
        return False






# coding: utf-8

from behavior_tree.base import *
from copy import copy
from win_algorithm.huaihua import WinAlgorithmHuaiHua


class JIAHU(NodeBase):
    def __init__(self, weight=1):
        super(JIAHU, self).__init__(weight)

    def condition(self, player):
        super(JIAHU, self).condition(player)
        if len(self.parent.card_group) > 0:
            hu_cards = []
            for item in self.parent.card_group:
                for card in item:
                    hu_cards.append(card)
            hu_cards.sort()
            player.cards_in_hand.sort()
            #mask_target = player.tmpTingCard&0x0f
            #if mask_target == 0x07 or mask_target == 0x03:
                #return False
            for item in self.parent.card_group:
                if len(item) == 2:
                    # if player.tmpTingCard in item:
                        # return False
                    continue
                mask_cards = [0x0f&item[0], 0x0f&item[1], 0x0f&item[2]]
                #print mask_cards, mask_target
                if mask_cards[2] == mask_cards[0]+2 and player.tmpTingCard == item[1]:
                    return True
        return False






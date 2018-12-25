# coding: utf-8

from copy import copy

from card_define import NUMBER,WIND, DRAGON, ALL_19


class WinAlgorithm(object):
    """普通胡牌算法 3N + 2"""

    def __init__(self, raw=False):
        self.stack = []  # 牌组栈
        self.cards = []  # 剩余手牌
        self.pairs = 0  # 将对个数
        self.raw = raw  # 是否直接返牌组栈

    def start(self, cards):
        self.cards = copy(cards)
        self.cards.sort()

        if self.try_win():
            if self.raw:
                # 直接返回牌组栈
                return self.stack
            else:
                # 返回胡牌的排列
                win_cards = []
                for i in self.stack:
                    win_cards.extend(i)
                return win_cards
        else:
            return []

    def push(self, group):
        # 将牌组压栈
        self.stack.append(group)

    def roll_back(self):
        # 牌组出栈
        group = self.stack.pop()
        self.cards.extend(group)
        self.cards.sort()

    def try_triplets(self, card):
        # 尝试组成一个刻子，如果可以的话则将此组牌压栈
        if self.cards.count(card) >= 3:
            self.cards.remove(card)
            self.cards.remove(card)
            self.cards.remove(card)
            self.push([card, card, card])
            return True
        else:
            return False

    def try_sequence(self, card):
        if card not in NUMBER:
            return False
        # 尝试组成一个顺子，如果可以的话则将此组牌压栈
        if card in self.cards and card + 1 in self.cards and card + 2 in self.cards:
            self.cards.remove(card)
            self.cards.remove(card + 1)
            self.cards.remove(card + 2)
            self.push([card, card + 1, card + 2])
            return True
        else:
            return False

    def try_pair(self, card):
        # 尝试组成一个对子，对子只能有一个
        if self.pairs == 1:
            return False
        if self.cards.count(card) >= 2:
            self.cards.remove(card)
            self.cards.remove(card)
            self.push([card, card])
            self.pairs = 1
            return True
        else:
            return False

    def try_win(self):
        # 回溯尝试组成顺子刻子对子
        if not self.cards:
            if self.pairs == 1:
                return True
            else:
                return False

        active_card = self.cards[0]

        if self.try_triplets(active_card):
            if not self.try_win():
                self.roll_back()
            else:
                return True

        if self.try_pair(active_card):
            if not self.try_win():
                self.roll_back()
                self.pairs = 0
            else:
                return True

        if self.try_sequence(active_card):
            if not self.try_win():
                self.roll_back()
            else:
                return True

        return False


class WinAlgorithmSevenPairs(WinAlgorithm):
    """七对的胡牌算法"""
    def start(self, cards):
        if len(cards) != 14:
            return []
        self.cards = copy(cards)
        self.cards.sort()

        if self.try_win():
            if self.raw:
                # 直接返回牌组栈
                return self.stack
            else:
                # 返回胡牌的排列
                win_cards = []
                for i in self.stack:
                    win_cards.extend(i)
                return win_cards
        else:
            return []

    def try_pair(self, card):
        if self.cards.count(card) >= 2:
            self.cards.remove(card)
            self.cards.remove(card)
            self.push([card, card])
            self.pairs += 1
            return True
        else:
            return False

    def try_win(self):
        if not self.cards and self.pairs == 7:
            return True

        if not self.cards:
            if self.pairs == 7:
                return True
            else:
                return False

        active_card = self.cards[0]

        if self.try_pair(active_card):
            if not self.try_win():
                self.roll_back()
                self.pairs -= 1
            else:
                return True
        return False

class WinAlgorithmQH(object):
    """穷胡胡牌算法 3N + 2"""

    def __init__(self, raw=False):
        self.stack = []  # 牌组栈
        self.cards = []  # 剩余手牌
        self.pairs = 0  # 将对个数
        self.raw = raw  # 是否直接返牌组栈
        self.target_card = 0
        self.prior_sequence = False

    def start(self, cards, target_card,is_bianhu = False, prior_sequence = False):
        self.cards = copy(cards)
        self.cards.sort()
        self.target_card = target_card
        self.prior_sequence = prior_sequence
        self.is_bianhu = is_bianhu
        if self.try_jia_sequence():
            result = self.get_win_cards()
            if result:
                return result

            self.roll_back()
        # else:
        # if self.stack:
        #     self.roll_back()
        return self.get_win_cards()

    def get_win_cards(self):
        if self.try_win():
            if self.raw:
                # 直接返回牌组栈
                return self.stack
            else:
                # 返回胡牌的排列
                win_cards = []
                for i in self.stack:
                    win_cards.extend(i)
                return win_cards
        else:
            return []

    def push(self, group):
        # 将牌组压栈
        self.stack.append(group)

    def roll_back(self):
        # 牌组出栈
        group = self.stack.pop()
        self.cards.extend(group)
        self.cards.sort()

    def try_triplets(self, card):
        # 尝试组成一个刻子，如果可以的话则将此组牌压栈
        if self.cards.count(card) >= 3:
            self.cards.remove(card)
            self.cards.remove(card)
            self.cards.remove(card)
            self.push([card, card, card])
            return True
        else:
            return False

    def try_sequence(self, card):
        if card not in NUMBER:
            return False
        # 尝试组成一个顺子，如果可以的话则将此组牌压栈
        if card in self.cards and card + 1 in self.cards and card + 2 in self.cards:
            self.cards.remove(card)
            self.cards.remove(card + 1)
            self.cards.remove(card + 2)
            self.push([card, card + 1, card + 2])
            return True
        else:
            return False

    def try_jia_sequence(self):
        card = self.target_card
        if card not in NUMBER:
            return False
        if card == 0x11:
            return False
        if card & 0x0F == 3 and self.is_bianhu:
            if card in self.cards and card - 1 in self.cards and card - 2 in self.cards:
                self.cards.remove(card)
                self.cards.remove(card - 1)
                self.cards.remove(card - 2)
                self.push([card-2, card - 1, card ])
                return True
        elif card & 0x0F == 7 and self.is_bianhu:
            if card in self.cards and card + 1 in self.cards and card + 2 in self.cards:
                self.cards.remove(card)
                self.cards.remove(card + 1)
                self.cards.remove(card + 2)
                self.push([card, card + 1, card + 2])
                return True

        if card in self.cards and card - 1 in self.cards and card + 1 in self.cards:
            self.cards.remove(card)
            self.cards.remove(card - 1)
            self.cards.remove(card + 1)
            self.push([card - 1, card, card + 1])
            return True
        return False

    def try_pair(self, card):
        # 尝试组成一个对子，对子只能有一个
        if self.pairs == 1:
            return False
        if self.cards.count(card) >= 2:
            self.cards.remove(card)
            self.cards.remove(card)
            self.push([card, card])
            self.pairs = 1
            return True
        else:
            return False

    def try_win(self):
        # 回溯尝试组成顺子刻子对子
        if not self.cards:
            if self.pairs == 1:
                return True
            else:
                return False

        active_card = self.cards[0]
        if self.prior_sequence:
            if self.try_triplets(active_card):
                if not self.try_win():
                    self.roll_back()
                else:
                    return True

            if self.try_pair(active_card):
                if not self.try_win():
                    self.roll_back()
                    self.pairs = 0
                else:
                    return True

            if self.try_sequence(active_card):
                if not self.try_win():
                    self.roll_back()
                else:
                    return True
        else:
            if self.try_sequence(active_card):
                if not self.try_win():
                    self.roll_back()
                else:
                    return True

            if self.try_pair(active_card):
                if not self.try_win():
                    self.roll_back()
                    self.pairs = 0
                else:
                    return True

            if self.try_triplets(active_card):
                if not self.try_win():
                    self.roll_back()
                else:
                    return True
        return False

class WinThirteenOrphans(WinAlgorithm):
    """ 十三幺胡牌算法
    """
    def __init__(self, raw=False):
        super(WinThirteenOrphans, self).__init__(raw)
        self.template = WIND + DRAGON + ALL_19


    def try_match(self, card):
        if card in self.template:
            self.cards.remove(card)
            self.push([card])
            return True
        return False

    def try_template_pair(self, card):
        if self.cards.count(card) >= 2 and card in self.template:
            self.cards.remove(card)
            self.cards.remove(card)
            self.push([card, card])
            self.pairs += 1
            return True
        else:
            return False

    def try_win(self):
        if not self.stack and len(set(self.cards)) != 13:
            return False
        if not self.cards:
            if self.pairs == 1:
                return True
            return False

        active_card = self.cards[0]

        if self.try_template_pair(active_card):
            if not self.try_win():
                self.roll_back()
                self.pairs -= 1
            else:
                return True

        if self.try_match(active_card):
            if not self.try_win():
                self.roll_back()
            else:
                return True

        return False



if __name__ == '__main__':
    # import time
    # t = time.time()
    # for _ in range(1000):
    #     test_one()
    # print(time.time() - t)
    # cards = [0x15,0x16,0x17,0x25,0x25,0x25,0x31,0x31,0x31,0x35,0x35]
    cards = [0x14,0x14,0x14,0x14,0x21,0x21,0x31,0x31,0x34,0x34,0x35,0x35,0x36,0x36]
    # cards = [0x15,0x16,0x17,0x25,0x25,0x25,0x31,0x31,0x31,0x35,0x13,0x14,0x15,0x16]
    wa = WinAlgorithmSevenPairs(True)
    print wa.start(cards)


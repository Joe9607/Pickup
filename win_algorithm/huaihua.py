# coding: utf-8

from copy import copy

from win_algorithm.base import WinAlgorithm


class WinAlgorithmHuaiHua(WinAlgorithm):
    """3N + 2 牌型"""

    def __init__(self, joker):
        super(WinAlgorithmHuaiHua, self).__init__(True)
        self.compose_types = []

        self.joker_card = joker  # 癞子（混）
        self.joker_list = []  # 癞子（混）数量

    def roll_back(self):
        # 牌组出栈
        if not self.stack:
            return
        group = self.stack.pop()
        for i in group:
            if i == self.joker_card:
                self.joker_list.append(i)
            else:
                self.cards.append(i)
        self.cards.sort()

    def try_compose_triplet_with_one(self, card):
        # 尝试用一个癞子与其他牌组成一个刻子
        if len(self.joker_list) >= 1 and self.cards.count(card) >= 2:
            self.cards.remove(card)
            self.cards.remove(card)
            self.push([card, card, self.joker_card])
            self.joker_list.pop()
            return True
        else:
            return False

    def try_compose_triplet_with_two(self, card):
        # 尝试用两个癞子与其他牌组成一个刻子
        if len(self.joker_list) >= 2:
            self.cards.remove(card)
            self.push([card, self.joker_card, self.joker_card])
            self.joker_list.pop()
            self.joker_list.pop()
            return True
        else:
            return False

    def try_compose_sequence_with_one(self, card):
        # 尝试用一个癞子与其他牌组成一个顺子
        if len(self.joker_list) < 1:
            return False
        if card + 1 in self.cards:
            self.cards.remove(card)
            self.cards.remove(card + 1)
            self.push([card, card + 1, self.joker_card])
            self.joker_list.pop()
            return True
        if card + 2 in self.cards:
            self.cards.remove(card)
            self.cards.remove(card + 2)
            self.push([card, self.joker_card, card + 2])
            self.joker_list.pop()
            return True
        else:
            return False

    def try_compose_pair_with_one(self, card):
        # 尝试用一个癞子与其他牌组成一个对子
        if self.pairs == 1:
            return False
        if len(self.joker_list) < 1:
            return False
        self.joker_list.pop()
        self.pairs = 1
        self.cards.remove(card)
        self.push([card, self.joker_card])
        return True

    def try_compose_pair_with_two(self):
        # 尝试用两个癞子与其他牌组成一个对子
        if self.pairs == 1:
            return False
        if len(self.joker_list) < 2:
            return False
        self.joker_list.pop()
        self.joker_list.pop()
        self.pairs = 1
        self.push([self.joker_card, self.joker_card])
        return True

    def try_compose_triplet_with_three(self):
        # 尝试用三个癞子组成一个刻子
        if len(self.joker_list) >= 3:
            self.push([self.joker_card, self.joker_card, self.joker_card])
            self.joker_list.pop()
            self.joker_list.pop()
            self.joker_list.pop()
            return True
        else:
            return False

    def save(self):
        cards = copy(self.stack)
        if len(self.joker_list) > 0:
            cards.append(copy(self.joker_list))
        self.compose_types.append(cards)
        self.roll_back()

    def start(self, cards):
        self.cards = copy(cards)
        self.cards.sort()
        # 先将癞子（混）从牌里面剔除
        while self.joker_card in self.cards:
            self.cards.remove(self.joker_card)
            self.joker_list.append(self.joker_card)

        self.try_win()
        return self.stack

    def try_win(self):
        if not self.cards and self.pairs == 1:
            return True
        if not self.cards and self.pairs == 0:
            return self.try_compose_pair_with_two()

        active_card = self.cards[0]
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

        if self.try_triplets(active_card):
            if not self.try_win():
                self.roll_back()
            else:
                return True

        if self.try_compose_pair_with_one(active_card):
            if not self.try_win():
                self.roll_back()
                self.pairs = 0
            else:
                return True

        if self.try_compose_pair_with_two():
            if not self.try_win():
                self.roll_back()
                self.pairs = 0
            else:
                return True

        if self.try_compose_sequence_with_one(active_card):
            if not self.try_win():
                self.roll_back()
            else:
                return True

        if self.try_compose_triplet_with_one(active_card):
            if not self.try_win():
                self.roll_back()
            else:
                return True

        if self.try_compose_triplet_with_two(active_card):
            if not self.try_win():
                self.roll_back()
            else:
                return True

        if self.try_compose_triplet_with_three():
            if not self.try_win():
                self.roll_back()
            else:
                return True
        return False


class WinAlgorithmSevenPairsHuaiHua(WinAlgorithmHuaiHua):
    """7 * N"""

    def save(self):
        cards = copy(self.stack)
        if len(self.joker_list) > 0:
            cards.append(copy(self.joker_list))
        self.compose_types.append(cards)
        self.roll_back()

    def roll_back(self):
        super(WinAlgorithmSevenPairsHuaiHua, self).roll_back()
        self.pairs -= 1

    def try_pair(self, card):
        if self.cards.count(card) >= 2:
            self.cards.remove(card)
            self.cards.remove(card)
            self.push([card, card])
            self.pairs += 1
            return True
        else:
            return False

    def try_compose_pair_with_one(self, card):
        if len(self.joker_list) < 1:
            return False
        self.pairs += 1
        self.cards.remove(card)
        self.push([card, self.joker_list.pop()])
        return True

    def try_compose_pair_with_two(self):
        if len(self.joker_list) < 2:
            return False
        self.pairs += 1
        self.push([self.joker_list.pop(), self.joker_list.pop()])
        return True

    def try_win(self):
        if not self.cards:
            if self.pairs == 7 or self.pairs + len(self.joker_list) / 2 == 7:
                return True

        if not self.cards and self.pairs == 6:
            return self.try_compose_pair_with_two()

        active_card = self.cards[0]

        if self.try_pair(active_card):
            if not self.try_win():
                self.roll_back()
            else:
                return True

        if self.try_compose_pair_with_one(active_card):
            if not self.try_win():
                self.roll_back()
            else:
                return True

        if self.try_compose_pair_with_two():
            if not self.try_win():
                self.roll_back()
            else:
                return True

        return False


class WinAlgorithmTriplet(WinAlgorithmHuaiHua):
    """碰碰胡判断"""

    def try_win(self):
        if not self.cards and self.pairs == 1:
            return True

        if not self.cards and self.pairs == 0:
            return self.try_compose_pair_with_two()

        active_card = self.cards[0]
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

        if self.try_compose_pair_with_one(active_card):
            if not self.try_win():
                self.roll_back()
                self.pairs = 0
            else:
                return True

        if self.try_compose_pair_with_two():
            if not self.try_win():
                self.roll_back()
                self.pairs = 0
            else:
                return True

        if self.try_compose_triplet_with_one(active_card):
            if not self.try_win():
                self.roll_back()
            else:
                return True

        if self.try_compose_triplet_with_two(active_card):
            if not self.try_win():
                self.roll_back()
            else:
                return True

        if self.try_compose_triplet_with_three():
            if not self.try_win():
                self.roll_back()
            else:
                return True
        return False


def test_batch():
    cards = [
        [0x21, 0x21, 0x21, 0x22, 0x22, 0x10, 0x10, 0x10, 0x10, 0x24, 0x24, 0x24, 0x25, 0x25],
        [0x21, 0x21, 0x21, 0x10, 0x10, 0x23, 0x24, 0x24, 0x25, 0x25, 0x26, 0x26, 0x27, 0x27],
        [0x11, 0x12, 0x13, 0x14, 0x10, 0x16, 0x10, 0x18, 0x19, 0x21, 0x22, 0x23, 0x11, 0x11],
        [0x11, 0x12, 0x13, 0x14, 0x15, 0x16, 0x17, 0x18, 0x19, 0x19, 0x10, 0x10, 0x10, 0x10],
    ]


def test_one():
    # cards = [0x21, 0x21, 0x21, 0x22, 0x22, 0x10, 0x10, 0x10, 0x10, 0x24, 0x24, 0x24, 0x25, 0x25]
    # cards = [0x11, 0x12, 0x13, 0x14, 0x10, 0x16, 0x10, 0x18, 0x19, 0x21, 0x22, 0x23, 0x11, 0x11]
    # cards = [0x11, 0x12, 0x13, 0x14, 0x15, 0x16, 0x17, 0x18, 0x19, 0x19, 0x11, 0x10, 0x10, 0x10]
    cards = [16, 17, 17, 17, 19, 19, 21, 21, 21, 25, 25]
    w = WinAlgorithmTriplet(0x10)
    #w = WinAlgorithmHuaiHua(0x10)
    # w.start(cards)
    for i in w.start(cards):
        print(i)


def test_seven():
    cards = []
    w = WinAlgorithmSevenPairsHuaiHua(0x10)
    for i in w.start(cards):
        print(i)


if __name__ == '__main__':
    # import time
    # t = time.time()
    # for _ in range(1000):
    #     test_one()
    # print(time.time() - t)
    test_one()

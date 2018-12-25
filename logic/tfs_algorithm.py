# coding: utf-8

from copy import copy
from collections import Counter

ZHONG = 0x10


class TFS(object):
    def __init__(self):
        self.stack = []
        self.cards = []
        self.zhong = 0
        self.pairs = 0

    def start(self, cards):
        self.cards = copy(cards)
        self.cards.sort()
        self.zhong = self.cards.count(ZHONG)
        i = 0
        while i < self.zhong:
            i += 1
            self.cards.remove(ZHONG)
        if self.zhong == 4:
            i = 0
            while i < self.zhong:
                i += 1
                self.cards.append(ZHONG)
            return self.cards
        if self.try_win():
            if self.zhong > 0:
                self.stack.append([ZHONG]*self.zhong)
            win_cards = []
            for i in self.stack:
                win_cards.extend(i)
            return win_cards
        else:
            return []

    def push(self, group):
        self.stack.append(group)

    def roll_back(self):
        group = self.stack.pop()
        zhong = group.count(ZHONG)
        i = 0
        while i < zhong:
            i += 1
            group.remove(ZHONG)
        self.cards.extend(group)
        self.cards.sort()

    def try_triplets(self, card):
        if self.cards.count(card) >= 3:
            self.cards.remove(card)
            self.cards.remove(card)
            self.cards.remove(card)
            self.push([card, card, card])
            return True
        else:
            return False

    def try_sequence(self, card):
        if card in self.cards and card + 1 in self.cards and card + 2 in self.cards:
            self.cards.remove(card)
            self.cards.remove(card + 1)
            self.cards.remove(card + 2)
            self.push([card, card + 1, card + 2])
            return True
        else:
            return False

    def try_pair(self, card):
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

    def try_compose_triplet_with_one(self, card):
        if self.zhong >= 1 and self.cards.count(card) == 2:
            self.cards.remove(card)
            self.cards.remove(card)
            self.push([card, card, ZHONG])
            self.zhong -= 1
            return True
        else:
            return False

    def try_compose_triplet_with_two(self, card):
        if self.zhong >= 2 and self.cards.count(card) == 1:
            self.cards.remove(card)
            self.push([card, ZHONG, ZHONG])
            self.zhong -= 2
            return True
        else:
            return False

    def try_compose_sequence_with_one(self, card):
        if self.zhong < 1:
            return False
        if card + 1 in self.cards:
            self.cards.remove(card)
            self.cards.remove(card + 1)
            self.push([card, card + 1, ZHONG])
            self.zhong -= 1
            return True
        if card + 2 in self.cards:
            self.cards.remove(card)
            self.cards.remove(card + 2)
            self.push([card, card + 2, ZHONG])
            self.zhong -= 1
            return True
        else:
            return False

    def try_compose_pair_with_one(self, card):
        if self.pairs == 1:
            return False
        if self.zhong < 1:
            return False
        self.zhong -= 1
        self.pairs = 1
        self.cards.remove(card)
        self.push([card, ZHONG])
        return True

    def try_compose_pair_with_two(self):
        if self.pairs == 1:
            return False
        if self.zhong < 2:
            return False
        self.zhong -= 2
        self.pairs = 1
        self.push([ZHONG, ZHONG])
        return True

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
                self.zhong += 1
            else:
                return True

        if self.try_compose_sequence_with_one(active_card):
            if not self.try_win():
                self.roll_back()
                self.zhong += 1
            else:
                return True

        if self.try_compose_triplet_with_one(active_card):
            if not self.try_win():
                self.roll_back()
                self.zhong += 1
            else:
                return True

        if self.try_compose_triplet_with_two(active_card):
            if not self.try_win():
                self.roll_back()
                self.zhong += 2
            else:
                return True
        return False


def try_compose_seven_pairs(tiles):
    if len(tiles) != 14:
        return False
    cards = copy(tiles)
    zhong = cards.count(ZHONG)
    i = 0
    while i < zhong:
        i += 1
        cards.remove(ZHONG)

    pairs = []
    ones = []
    for k, v in Counter(cards).items():
        if v == 1:
            ones.append(k)
        if v == 2:
            pairs.append(k)
        if v == 3:
            pairs.append(k)
            ones.append(k)
        if v == 4:
            pairs.extend([k]*2)
    if zhong < len(ones):
        return False
    zhong -= len(ones)
    pairs.extend(ones)
    if len(pairs) + zhong/2 == 7:
        return True
    else:
        return False


def is_ready_hand(tiles, is_zhong=True, is_qxd=True):
    cards_test = list(filter(lambda e: 0 < (e % 16) < 10, range(0x11, 0x3A)))
    if is_zhong:
        cards_test.append(ZHONG)

    success = []
    for i in cards_test:
        cards = copy(tiles)
        cards.append(i)
        if is_qxd and try_compose_seven_pairs(cards):
            success.append(i)
        tfs = TFS()
        if tfs.start(cards):
            success.append(i)
        cards.remove(i)
    return success


def test_win():
    cards = [
        # 三个红中
        [ZHONG, ZHONG, ZHONG, 0x11, 0x12, 0x13, 0x14, 0x14, 0x15, 0x15, 0x15, 0x15, 0x16, 0x17],
        [ZHONG, 0x11, ZHONG, 0x21, 0x21, ZHONG, 0x32, 0x33, 0x14, 0x15, 0x16, 0x15, 0x16, 0x17],
        [0x11, 0x11, 0x22, 0x23, ZHONG, ZHONG, ZHONG, 0x17, 0x32, 0x32, 0x32, 0x23, 0x23, 0x23],
        [ZHONG, ZHONG, ZHONG, 0x12, 0x13, 0x32, 0x33, 0x34, 0x14, 0x15, 0x16, 0x15, 0x16, 0x17],
        # 两个红中
        [ZHONG, ZHONG, 0x12, 0x13, 0x14, 0x32, 0x33, 0x34, 0x14, 0x15, 0x16, 0x15, 0x16, 0x17],
        [ZHONG, 0x32, 0x33, ZHONG, 0x12, 0x13, 0x14, 0x14, 0x14, 0x15, 0x16, 0x15, 0x16, 0x17],
        [ZHONG, ZHONG, 0x33, 0x11, 0x12, 0x13, 0x14, 0x14, 0x14, 0x15, 0x15, 0x15, 0x16, 0x17],
        # 一个红中
        [ZHONG, 0x33, 0x11, 0x12, 0x13, 0x14, 0x14, 0x14, 0x15, 0x15, 0x15, 0x16, 0x17, 0x15],
        [0x33, 0x33, ZHONG, 0x12, 0x13, 0x14, 0x14, 0x14, 0x15, 0x15, 0x15, 0x16, 0x17, 0x15],
        [0x10, 0x17, 0x17, 0x18, 0x19, 0x19, 0x25, 0x26, 0x27, 0x32, 0x32],
        [35, 22, 19, 34, 22, 36, 21, 16, 18, 21, 21],
        [0x32, 0x32, 0x32, 0x10, 0x35, 0x36, 0x39, 0x39],
        [ZHONG, 0x12, 0x13, 0x14, 0x21, 0x22, 0x35, 0x35, 0x35, 0x36, 0x37],
        [ZHONG, ZHONG, 0x15, 0x15, 0x15],
        [0x11, 0x12, 0x13, 0x14, 0x15, 0x16, 0x16, 0x17, 0x18, 0x18, 0x18, 0x18, 0x19, 0x19],
        [ZHONG, 0x12, 0x13, 0x14, 0x21, 0x22, 0x35, 0x35, 0x35, 0x36, 0x37],
        [ZHONG, ZHONG, 0x22, 0x23, 0x24, 0x26, 0x36, 0x37, 0x38, 0x38, 0x39],
        [ZHONG, ZHONG, 0x13, 0x24, 0x25, 0x26, 0x27, 0x27, 0x27, 0x38, 0x39],
        [16, 16, 51, 17, 18, 19, 20, 20, 20, 21, 21, 21, 22, 23],
        [16, 16, 17, 18, 19, 20, 20, 20, 21, 21, 21, 22, 23, 25],
        [ZHONG, 0x15, 0x17, 0x22, 0x22],
        [ZHONG, 0x11, 0x13, 0x14, 0x15, 0x16, 0x22, 0x22],
        [ZHONG, 0x11, 0x13, 0x14, ZHONG, 0x16, 0x22, 0x22],
        [0x13, 0x14, 0x15, 0x17, 0x17, 0x39, 0x39, 0x39],
        [ZHONG, 0x16, 0x17, 0x32, 0x32, 0x34, 0x35, 0x36],
        [ZHONG, ZHONG, ZHONG, 0x11, 0x11, 0x13, 0x14, 0x15, 0x16, 0x17, 0x18, 0x23, 0x24, 0x28],
        [ZHONG, ZHONG, 0x14, 0x14, 0x16, 0x17, 0x18, 0x38],
        [ZHONG, 0x17, 0x18, 0x19, 0x22, 0x23, 0x24, 0x26, 0x26, 0x27, 0x27],
        [ZHONG, ZHONG, ZHONG, 0x14, 0x16, 0x17, 0x17, 0x32, 0x32, 0x36, 0x36],
        [ZHONG, ZHONG, 0x11, 0x12, 0x13, 0x34, 0x34, 0x35, 0x36, 0x36, 0x37],
        [ZHONG, ZHONG, 0x15, 0x15, 0x23, 0x24, 0x22, 0x26, 0x26, 0x36, 0x37, 0x38, 0x39, 0x39],
        [ZHONG, 0x14, 0x14, 0x15, 0x16, 0x17, 0x22, 0x22, 0x22, 0x23, 0x23, 0x25, 0x26, 0x27],
        [ZHONG, 0x13, 0x13, 0x14, 0x15, 0x16, 0x17, 0x17, 0x26, 0x27, 0x28],
        [ZHONG, ZHONG, 0x15, 0x16, 0x17, 0x25, 0x27, 0x29, 0x36, 0x37, 0x38],
        [ZHONG, ZHONG, 0x15, 0x15, 0x16, 0x18, 0x19, 0x19, 0x25, 0x26, 0x27, 0x32, 0x33, 0x34],
        [ZHONG, ZHONG],
        [0x16, 0x17, 0x18, 0x19, 0x19, 0x19, 0x24, 0x25, 0x26, 0x34, 0x35, 0x36, 0x39, 0x39],
        [ZHONG, ZHONG, 0x17, 0x18, 0x19, 0x22, 0x22, 0x26, 0x26, 0x27, 0x28, 0x29, 0x37, 0x39],
    ]

    import time

    for i in cards:
        st = time.time()
        #print i
        tfs = TFS()
        #print tfs.start(i)
        #print("-" * 60, time.time() - st)


def test_seven_pairs():
    cards = [
        [0x11, 0x11, 0x12, 0x12, 0x13, 0x13, 0x14, 0x14, 0x15, 0x15, 0x16, ZHONG, ZHONG, ZHONG],
        [0x11, 0x11, 0x12, 0x12, 0x13, 0x13, 0x14, 0x14, 0x15, 0x16, 0x17, ZHONG, ZHONG, ZHONG],
        [0x11, 0x11, 0x12, 0x12, 0x13, 0x13, 0x14, 0x14, 0x15, 0x15, 0x16, 0x17, ZHONG, ZHONG],
        [0x11, 0x11, 0x12, 0x12, 0x13, 0x13, 0x14, 0x14, 0x15, 0x15, 0x16, 0x16, ZHONG, ZHONG],
        [0x11, 0x11, 0x12, 0x12, 0x13, 0x13, 0x14, 0x14, 0x15, 0x15, 0x16, 0x16, 0x17, ZHONG],
        [ZHONG, ZHONG, 0x14, 0x14, 0x19, 0x19, 0x23, 0x23, 0x24, 0x24, 0x24, 0x26, 0x26, 0x27],
    ]
    for i in cards:
        print try_compose_seven_pairs(i)


if __name__ == '__main__':
    test_win()
    # test_seven_pairs()
    # try_compose_seven_pairs([ZHONG, ZHONG, 0x17, 0x18, 0x19, 0x22, 0x22, 0x26, 0x26, 0x27, 0x28, 0x29, 0x37, 0x39])
    # print is_ready_hand([ZHONG, ZHONG, 0x14, 0x14, 0x19, 0x19, 0x23, 0x23, 0x24, 0x24, 0x24, 0x26, 0x26])

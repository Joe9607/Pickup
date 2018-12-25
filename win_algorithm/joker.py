# coding: utf-8

from copy import copy

from win_algorithm.base import WinAlgorithm


class WinAlgorithmWithJoker(WinAlgorithm):
    """带癞子（宝牌）的胡牌算法 3N + 2"""

    def __init__(self, joker):
        super(WinAlgorithmWithJoker, self).__init__()
        self.joker = joker  # 癞子（宝牌）
        self.joker_cnt = 0  # 癞子（宝牌）数量

    def try_compose_triplet_with_one(self, card):
        # 尝试用一个癞子与其他牌组成一个刻子
        if self.joker_cnt >= 1 and self.cards.count(card) == 2:
            self.cards.remove(card)
            self.cards.remove(card)
            self.push([card, card, self.joker])
            self.joker_cnt -= 1
            return True
        else:
            return False

    def try_compose_triplet_with_two(self, card):
        # 尝试用两个癞子与其他牌组成一个刻子
        if self.joker_cnt >= 2 and self.cards.count(card) == 1:
            self.cards.remove(card)
            self.push([card, self.joker, self.joker])
            self.joker_cnt -= 2
            return True
        else:
            return False

    def try_compose_sequence_with_one(self, card):
        # 尝试用一个癞子与其他牌组成一个顺子
        if self.joker_cnt < 1:
            return False
        if card + 1 in self.cards:
            self.cards.remove(card)
            self.cards.remove(card + 1)
            self.push([card, card + 1, self.joker])
            self.joker_cnt -= 1
            return True
        if card + 2 in self.cards:
            self.cards.remove(card)
            self.cards.remove(card + 2)
            self.push([card, card + 2, self.joker])
            self.joker_cnt -= 1
            return True
        else:
            return False

    def try_compose_pair_with_one(self, card):
        # 尝试用一个癞子与其他牌组成一个对子
        if self.pairs == 1:
            return False
        if self.joker_cnt < 1:
            return False
        self.joker_cnt -= 1
        self.pairs = 1
        self.cards.remove(card)
        self.push([card, self.joker])
        return True

    def try_compose_pair_with_two(self):
        # 尝试用两个癞子组成一个对子
        if self.pairs == 1:
            return False
        if self.joker_cnt < 2:
            return False
        self.joker_cnt -= 2
        self.pairs = 1
        self.push([self.joker, self.joker])
        return True

    def start(self, cards):
        self.cards = copy(cards)
        self.cards.sort()
        self.joker_cnt = self.cards.count(self.joker)
        # 先将癞子（混）从牌里面剔除
        i = 0
        while i < self.joker_cnt:
            i += 1
            self.cards.remove(self.joker)
        # 如果癞子（混）等于四个则直接胡牌
        if self.joker_cnt == 4:
            i = 0
            while i < self.joker_cnt:
                i += 1
                self.cards.append(self.joker)
            return self.cards
        if self.try_win():
            if self.joker_cnt > 0:
                self.stack.append([self.joker] * self.joker_cnt)
            win_cards = []
            for i in self.stack:
                win_cards.extend(i)
            return win_cards
        else:
            return []

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
                self.joker_cnt += 1
            else:
                return True

        if self.try_compose_sequence_with_one(active_card):
            if not self.try_win():
                self.roll_back()
                self.joker_cnt += 1
            else:
                return True

        if self.try_compose_triplet_with_one(active_card):
            if not self.try_win():
                self.roll_back()
                self.joker_cnt += 1
            else:
                return True

        if self.try_compose_triplet_with_two(active_card):
            if not self.try_win():
                self.roll_back()
                self.joker_cnt += 2
            else:
                return True
        return False


class WinAlgorithmSevenPairsWithJoker(WinAlgorithmWithJoker):
    """带癞子（混）的七对胡牌算法"""

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
        if self.joker_cnt < 1:
            return False
        self.joker_cnt -= 1
        self.pairs += 1
        self.cards.remove(card)
        self.push([card, self.joker])
        return True

    def try_compose_pair_with_two(self):
        if self.joker_cnt < 2:
            return False
        self.joker_cnt -= 2
        self.pairs += 1
        self.push([self.joker, self.joker])
        return True

    def try_win(self):
        if not self.cards and self.pairs + self.joker_cnt // 2 == 7:
            return True

        active_card = self.cards[0]

        if self.try_pair(active_card):
            if not self.try_win():
                self.roll_back()
                self.pairs -= 1
            else:
                return True

        if self.try_compose_pair_with_one(active_card):
            if not self.try_win():
                self.roll_back()
                self.pairs -= 1
                self.joker_cnt += 1
            else:
                return True

        if self.try_compose_pair_with_two():
            if not self.try_win():
                self.roll_back()
                self.pairs -= 1
                self.joker_cnt += 1
            else:
                return True

        return False

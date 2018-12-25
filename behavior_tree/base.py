# coding: utf-8

from copy import copy

FA = 0x8
BAI = 0x9
ZHONG = 0x10
WAN = [0x11, 0x12, 0x13, 0x14, 0x15, 0x16, 0x17, 0x18, 0x19]
TONG = [0x21, 0x22, 0x23, 0x24, 0x25, 0x26, 0x27, 0x28, 0x29]
TIAO = [0x31, 0x32, 0x33, 0x34, 0x35, 0x36, 0x37, 0x38, 0x39]
EAST=0x42
SOUTH=0x43
WEST=0x44
NORTH=0x45

FANS_XIAN = {
    "BASE":1,
    "TSP": 3,
    "TTO":9,
    "HAQD":9,
    "QIYS":2,
}

FANS_ZHUANG = {
    # 自摸胡
    "BASE":1,
    # 七对
    "TSP": 3,
    # 十三幺
    "TTO":9,
    # 豪七对,11,22,33,44,55,666
    "HAQD":9,
    # 清一色
    "QIYS":2,
    # 吃干榨尽
    "CGZJ":2,
    # 豪豪七，11,22,33,4444,555
    "HHQ":18,
    # 豪豪豪七 11,2222,3333,444
    "HHHQ": 36

}

ZUI_LUAN = {
    # (自摸胡) 2嘴
    "BASE": 2,
    # 无宝 2嘴
    "WUBAO": 2,
    # 独子 2嘴（可以有宝牌 但是宝牌不能是独子中的两张，可以有红中。如果卡的那张是宝牌，宝牌当本身)
    "DUZI": 2,
    # 缺门 2嘴
    "QUEMENG": 2,
    # 断幺 2嘴（无字牌，无1、9）（不能有红中，可以有宝牌）
    "DUANYAO": 2,
    # 幺头 2嘴（字牌或1、9做将牌，不可以用宝替代1、9、字）
    "YAOTOU": 2,
    # 坎 1嘴（每3张一样的牌算1坎，1坎1嘴，碰不算，三张中有宝不算）
    "KAN": 1,
    # 亲三对 2嘴（即一色二顺，例：112233）
    "QINGSANDUI": 2,
    # 门清 2嘴
    "MENQING": 2,
    # 单吊宝 4嘴（单吊一张宝牌，抓任意一张牌都可以胡）
    "DANDIAOBAO": 4,
    # 双吊宝 8嘴（听牌后手上有一对宝是独立出来的，任意抓张牌都可以胡）
    "SUANDIAOBAO": 8,
    # 无宝独子 5嘴（牌形含无宝、独子（胡边卡，即只听一张牌））（可以有红中）
    "WUBAODUZI": 5,
    # 混一色 8嘴
    "HUNYISE": 8,
    # 七对 8嘴（11223344556677）
    "TSP": 8,
    # 杠后花 10嘴（杠后自摸胡牌）
    "GANGHOUHUA": 10,
    # 十三烂 10嘴(手中十四张牌中，序数牌间隔大于2 ，字牌没有重复所组成的牌型。)
    "SHISANLAN": 10,
    # 七风全15嘴（十三滥的基础上，东南西北中白发全，宝牌不可以当某张风牌）
    "QIFENGQUAN": 15,
    # 清一色 10嘴
    "QIYS": 10,
    # 通天 10嘴（万筒条其中一种花色的1-9,某种花色有且只有1-9的顺子）
    "TONGTIAN": 10,
    # 四宝 20嘴（要成牌形)
    "SIBAO": 20,
    # 天胡、地胡 20嘴(天胡：庄家起牌即胡，地胡：闲家第一轮)
    "TIANHU": 20,
    "DIHU": 20,
}


class NodeBase(object):
    def __init__(self, weight=1):
        self.weight = weight
        self.children = []
        self.node = self.__class__.__name__
        self.parent = None

    def add_child(self, node):
        self.children.append(node)
        node.parent = self

    def condition(self, player):
        pass

    def append(self, player):
        if self.node in FANS_ZHUANG.keys() and self.node not in player.router:
            player.router.append(self.node)

    def execute(self, player):
        if not self.condition(player):
            return False
        self.append(player)
        if not self.children:
            return True
        self.children.sort(key=lambda x: x.weight, reverse=True)
        for child in self.children:
            if child.execute(player):
                return True
        return False


class TFS(object):
    def __init__(self, pair258=False):
        self.stack = []
        self.cards = []
        self.pairs = 0
        self.pair258 = pair258

    def start(self, cards):
        self.cards = copy(cards)
        self.cards.sort()

        if self.try_win():
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
        if card in self.cards and card + 1 in self.cards and card + 2 in self.cards and card > 0x10:#红中赖子
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
        if self.cards.count(card) >= 2 and (self.pair258 and card % 16 in (2, 5, 8) or not self.pair258):
            self.cards.remove(card)
            self.cards.remove(card)
            self.push([card, card])
            self.pairs = 1
            return True
        else:
            return False

    def try_win(self):
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


def test():
    cards = [22, 22, 22, 20, 20, 20, 19, 19, 19, 17, 17, 17, 17]
    tfs = TFS()
    #print tfs.start(cards)


if __name__ == '__main__':
    test()

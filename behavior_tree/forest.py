# coding: utf-8
from utils.singleton import Singleton
from behavior_tree.base import *
from behavior_tree.trees.base import TreeBase
from behavior_tree.trees.thirteen_orphans import TreeThirteenOrphans
from behavior_tree.trees.seven_pairs import TreeSevenPairs


class Forest(object):
    __metaclass__ = Singleton

    def __init__(self):
        # 将所有树都放进来
        self.trees = [TreeBase(),TreeThirteenOrphans(),TreeSevenPairs()]

    def walk(self, player):
        player.router = []
        for tree in self.trees:
            tree.execute(player)
        # 要是有大胡就不算自摸得分
        # 吃干榨尽，不和自摸同时存在，在draw_win里处理
        if not (not (player.router != {"BASE"}) or not ("BASE" in player.router)):
            player.router.remove("BASE")
        # points = []
        # 算番数（reduce函数反复计算累加）
        points = reduce(lambda x, y: x+y, [FANS_ZHUANG[i] for i in player.router]) if player.router else 0
        return points, player.router


class Conf(object):
    def __init__(self):
        self.top = 8

    def can_hu_without_sequence(self):
        return False
    def is_qg(self):
        return True
    def is_fan_hu(self, hu_type):
        return True
    def is_color_all(self):
        return True
    def is_open_door(self):
        return True
    def is_19(self):
        return True
    def bian_hu_jia(self):
        return True

class Table(object):
    def __init__(self):
        self.conf = Conf()
        self.points = FANS_XIAN
        self.dealer_seat = 0


class Player(object):
    def __init__(self):
        # self.cards_in_hand = [8, 8, 34, 34, 38, 38, 49, 49, 50, 50, 51, 57, 57]
        # self.cards_in_hand = [17, 17, 17, 17, 20, 18, 18, 18, 18, 20, 19, 19, 19, 19]
        self.cards_in_hand = []
        self.cards_group = []
        self.cards_pong = []
        self.cards_chow = []
        self.cards_kong_concealed = []
        self.cards_kong_exposed = []
        self.router = []
        self.win_card = 0
        self.pair258 = False
        self.table = Table()
        self.seat = 0
        self.win_card_group = {}

    def is_color_all(self):
        return True

    def is_open_door(self):
        return True

def is_ready_hand(player):
    cards_test = copy(WAN)
    cards_test.extend(TONG)
    cards_test.extend(TIAO)
    cards_test.append(ZHONG)
    cards_test.append(EAST)
    cards_test.append(WEST)
    cards_test.append(NORTH)
    cards_test.append(SOUTH)
    cards_test.append(FA)
    cards_test.append(BAI)
    win_card_list = {}
    cards_in_hand = player.cards_in_hand + player.cards_group
    for i in cards_test:
        player.win_card = i
        player.cards_in_hand.append(i)
        player.tmpTingCard = i                           # 用于临时存储听牌判断中的添加牌
        points, win_types = Forest().walk(player)
        player.cards_in_hand.remove(i)
        player.tmpTingCard = 0
        player.win_card = 0
        #print 'wintypes:', win_types
        if win_types:
            win_card_list[i] = points, win_types
    return win_card_list


def test_is_ready_hand():
    player = Player()
    #print is_ready_hand(player)


def test_win():
    player = Player()
    points, win_types = Forest().walk(player)
    #print points, win_types

if __name__ == '__main__':
    # test_win()
    #test_is_ready_hand()
    player = Player()
    #player.cpg_group = [[BAI, BAI, BAI, BAI]]
    # player.cards_group = []
    # #player.cards_kong_concealed = [0x22, 0x22, 0x22, 0x22, 0x21, 0x21, 0x21,0x21, 0x23,0x23,0x23,0x23]
    # #player.cards_kong_exposed = [BAI, BAI, BAI, BAI]
    # player.tmpTingCard = 0x12
    # player.cards_in_hand = [0x12,0x12, 0x16,0x16, 0x29,0x29,0x29, 0x29]
    # points, win_types = Forest().walk(player)
    # print win_types
    # print 'tmpTingCard',player.tmpTingCard
    # print player.cards_in_hand


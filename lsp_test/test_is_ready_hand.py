#coding=utf-8
from behavior_tree.forest import is_ready_hand
from behavior_tree.base import *
import random

# cards_test = copy(WAN)
# cards_test.extend(TONG)
# cards_test.extend(TIAO)
# cards_test.append(ZHONG)
# cards_test.append(EAST)
# cards_test.append(WEST)
# cards_test.append(NORTH)
# cards_test.append(SOUTH)
# cards_test.append(FA)
# cards_test.append(BAI)

dealer = random.randint(0, 3)

cards_rest = list(filter(lambda e: 0 < (e % 16) < 10, range(0x11, 0x3A))) * 4  # 108 张数字牌
cards_rest.extend([ZHONG, FA, BAI, EAST, SOUTH, WEST, NORTH] * 4)
random.shuffle(cards_rest)
print "洗牌:", cards_rest
tile_list = []
seat = 0
while seat < 4:
    tile = []
    rounds = 0
    if seat < 3:
        while rounds < 13:
            tile.append(cards_rest.pop())
            rounds += 1
    else:
        while rounds < 14:
            tile.append(cards_rest.pop())
            rounds += 1
    tile_list.append(tile)
    seat += 1

print "发牌后剩余的牌：", cards_rest

if dealer != 3:
    tile_list[dealer], tile_list[3] = tile_list[3], tile_list[dealer]
else:
    tile_list[dealer] = tile_list[3]

dice_3 = random.randint(1, 6)
dice_4 = random.randint(1, 6)
dice_bao = dice_3 + dice_4        # 色子点数相加来确定宝牌
bao_appoint = cards_rest[-dice_bao]
if bao_appoint == 0x19:
    bao_card = 0x11
if bao_appoint == 0x29:
    bao_card = 0x21
if bao_appoint == 0x39:
    bao_card = 0x31
if bao_appoint == 0x45:
    bao_card = 0x42
if bao_appoint == 0x10:
    bao_card = 0x8
if bao_appoint == 0x8:
    bao_card = 0x9
if bao_appoint == 0x9:
    bao_card = 0x10

if bao_appoint in WAN and bao_appoint != 0x19:
    bao_card = bao_appoint + 1
elif bao_appoint in TONG and bao_appoint != 0x29:
    bao_card = bao_appoint + 1
elif bao_appoint in TIAO and bao_appoint != 0x23:
    bao_card = bao_appoint + 1
elif bao_appoint in [0x42, 0x43, 0x44]:
    bao_card = bao_appoint + 1
cards_on_desk = cards_rest[:-dice_bao:]
print "可以抓的牌", cards_on_desk
print "宝牌色子：", dice_bao
print "指定牌：", bao_appoint
print "宝牌：", bao_card


for k, v in enumerate(tile_list):
    print "玩家:", k, "牌型:", v, "牌数:",len(v)
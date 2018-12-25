# coding: utf-8

import random
from copy import copy

from logic.table_action import *
from protocol import game_pb2
from protocol.commands import DEAL
from settings import redis
from state.player_state.deal import DealState as PlayerDealState
from state.table_state.base import TableStateBase
from state.table_state.step import StepState
from behavior_tree.base import *


class DealState(TableStateBase):
    def __init__(self):
        super(DealState, self).__init__()

    def enter(self, owner):
        super(DealState, self).enter(owner)
        owner.active_seat = -1

        cards_rest = list(filter(lambda e: 0 < (e % 16) < 10, range(0x11, 0x3A))) * 4       # 108 张数字牌
        cards_rest.extend([ZHONG, FA, BAI, EAST, SOUTH, WEST, NORTH] * 4)
        random.shuffle(cards_rest)

        if owner.cur_round == 1 and owner.dealer_seat == -1:
            dealer = random.randint(0, owner.chairs-1)       # 随机挑选一个为庄家
            owner.dealer_seat = dealer
        else:
            dealer = owner.dealer_seat                # 非流局换庄为本局庄家下一位，荒庄或庄家赢连庄

        dice_1 = random.randint(1, 6)
        dice_2 = random.randint(1, 6)
        dice_3 = random.randint(1, 6)
        dice_4 = random.randint(1, 6)

        owner.dice_1 = dice_1
        owner.dice_2 = dice_2

        dice_bao = dice_3 + dice_4        # 色子点数相加来确定宝牌
        owner.dice_bao = dice_bao

        log = {
            "dice_1": dice_1,
            "dice_2": dice_2,
            "dice_bao": dice_bao,
            "dealer": dealer,
        }


        cheat =False
        if cheat:
            #dealer = owner.dealer_seat = 0
            name = "mahjong:huahuai:card:cheat:{0}"
            tile_list = []
            seat = 0
            # tile_list.append( [0x15, 0x16, 0x17, 0x25, 0x25, 0x25, 0x31, 0x31, 0x31, 0x35, 0x23,0x23,0x15])
            # tile_list.append( [0x12, 0x12, 0x12, 0x14, 0x17, 0x17, 0x17, 0x22, 0x23, 0x24, 0x39, 0x39,0x39])

            # tile_list.append([0x21,0x23,0x11,0x12,0x13,0x31,0x31,0x31,0x17, 0x17,0x31,0x32,0x33])
            # tile_list.append([0x21, 0x21, 0x21, 0x32, 0x33, 0x34, 0x11, 0x12, 0x13, 0x35, 0x35, 0x36, 0x36])
            # tile_list.append([0x11,0x11,0x12,0x13,0x21,0x21,0x24,0x22,0x31,0x32, 0x33,0x34,0x14])
            # tile_list.append([0x15,0x16,0x25,0x25,0x24,0x24,0x26,0x26,0x26,0x37,0x38,0x39,0x33])
            # tile_list.append([0x15, 0x16, 0x29, 0x29, 0x22, 0x22, 0x28, 0x28, 0x28, 0x37, 0x38, 0x39, 0x33])
            # cards_rest_tmp = []

            # for tmpList in tile_list:
            #     for card in tmpList:
            #         if card not in cards_rest:
            #             print 'card error:', card
            #         cards_rest.remove(card)

            # while len(tile_list) < owner.conf.chairs:
            #     a = []
            #     for i in range(12):
            #         a.append(cards_rest.pop())
            #     tile_list.append(a)
            #     tile_list.append(cards_rest.pop(0x45))

            # cards_rest[0] = 0x25
            # cards_rest[1] = 0x25
            # cards_rest[-1] = 0x25
            # cards_rest[-6] = 0x25
            # cards_rest[-7] = 0x25
            # cards_rest[-8] = 0x25
            # cards_rest[-9] = 0x25
            # cards_rest[-6] = 0x28
            # cards_rest[8] = 0x24
            while seat < owner.chairs:
                tile_list.append([int(i) for i in redis.lrange(name.format(seat), 0, -1)])
                seat += 1
            cards_rest = [int(i) for i in redis.lrange(name.format("rest"), 0, -1)]
        else:
            tile_list = []
            seat = 0
            while seat < owner.chairs:
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

        # tile_list 进行交换（地主位置能够对应14张牌）
        if dealer != 3:
            tile_list[dealer], tile_list[3] = tile_list[3], tile_list[dealer]
        else:
            tile_list[dealer] = tile_list[3]

        owner.card_odd = cards_rest   # 桌面上总共剩余下来的牌
        # 确定宝牌
        bao_appoint = cards_rest[-dice_bao]
        owner.bao_appoint = bao_appoint       # 确定宝牌的指定牌
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

        owner.bao_card = bao_card

        # 桌面剩下玩家能抓的牌
        owner.cards_on_desk = cards_rest[:-dice_bao:]
        owner.replay = {
            "room_id": owner.room_id,
            "round": owner.cur_real_round,
            "conf": owner.conf.settings,
            "dealer": dealer,
            "user": {},
            "deal": {},
            "procedure": [],
            'cards_rest_num': len(cards_rest)
        }

        owner.reset_proto(DEAL)
        for k, v in enumerate(tile_list):
            log[str(k)] = v
            player = owner.seat_dict[k]
            player.cards_in_hand = sorted(v)
            proto = game_pb2.DealResponse()
            proto.dealer_uuid = owner.seat_dict[dealer].uuid
            proto.dice.dice1 = dice_1
            proto.dice.dice2 = dice_2
            proto.dice.dice_bao = dice_bao
            proto.bao_card = bao_card
            for c in v:
                card = proto.cards_in_hand.add()
                card.card = c
            player.proto.p = proto
            owner.replay["user"][k] = (player.uuid, player.info)
            owner.replay["deal"][k] = copy(v)
            player.machine.trigger(PlayerDealState())
        # 将最后一张牌设置为last_card,手牌是栈0是最后一张1是倒数第二张
        owner.last_card = owner.cards_on_desk[0]
        owner.kong_temp_index = 0
        # 第一次要检测并换一次最后一张牌
        owner.change_kong_card(True)
        log["bao_card"] = bao_card
        log["cards_odd"] = owner.card_odd
        log["cards_on_desk"] = owner.cards_on_desk
        owner.logger.info(log)
        owner.dumps()

    def next_state(self, owner):
        owner.machine.trigger(StepState())

    def execute(self, owner, event):
        super(DealState, self).execute(owner, event)
        if event == "prompt_deal":
            prompt_deal(owner)

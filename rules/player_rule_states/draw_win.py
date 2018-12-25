# coding: utf-8

from protocol import game_pb2
from protocol.commands import *
from protocol.serialize import send
from rules.define import *
from state.player_state.base import PlayerStateBase
from logic.player_action import calculate_final_score
from state.player_state.wait import WaitState


class DrawWinState(PlayerStateBase):
    def enter(self, owner):
        super(DrawWinState, self).enter(owner)
        # 广播玩家胡牌
        owner.table.liuju = False
        proto = game_pb2.ActionResponse()
        proto.player = owner.uuid
        owner.win_total_cnt += 1
        proto.trigger_seat = owner.seat
        proto.active_type = PLAYER_ACTION_TYPE_WIN_DRAW
        owner.win_type = PLAYER_WIN_TYPE_DRAW
        owner.win_draw_cnt += 1
        owner.win_card = owner.draw_card
        owner.table.winner_list = [owner.seat]
        # 需要将胡的牌进行效验整理
        flags1 = []
        owner.cards_win = sorted(owner.cards_in_hand)
        owner.cards_in_hand.remove(owner.draw_card)

        owner.has_win = 1
        if owner.table.conf.can_hu_on_ready() and owner.table.step == 0:
            owner.win_flags.append("TNHU")
            win_score = 32
            for p in owner.table.player_dict.values():
                if p.uuid == owner.uuid:
                    continue
                calculate_final_score(p, owner, win_score)
        else:
            flags1 = []
            point = 0
            if owner.win_card != 0 and owner.win_card in owner.cards_ready_hand:
                point, flags1 = owner.cards_ready_hand[owner.win_card]
                # 存储已经胡过得牌和牌组
                owner.has_win_cards[owner.draw_card] = owner.win_card_group[owner.draw_card]
            # 算分
            if point:
                # 处理下吃干榨尽,不和自摸同时存在
                if len(owner.cards_in_hand) == 1:
                    if "BASE" in flags1:
                        point = 2
                    else:
                        point += 2
                # 倍数 = 连杠次数+流局倍数
                mul_liuju = 1 if owner.table.liuju_times > 0 else 0
                times = owner.kong_times+mul_liuju
                # 将番数相加*2^倍数
                owner.temp_total_score += point*(2**times)

        # 需要将胡的牌单独拿出来
        if owner.win_card in owner.cards_win:
            owner.cards_win.remove(owner.win_card)
            owner.has_win_cards_list.append(owner.win_card)
        proto.active_card.card = owner.win_card
        cards = proto.card.add()
        cards.card = 0
        # for card in owner.cards_win:
            # cards = proto.card.add()
            # cards.card = card
            # 胡牌不显示所有手牌
            # TODO
            # cards.card = 0
        owner.dumps()
        for player in owner.table.player_dict.values():
            send(ACTION, proto, player.session)
        owner.table.win_type = TABLE_WIN_TYPE_DISCARD_DRAW


        owner.table.logger.info("player {0} win {1} type {2} score {3}".format(owner.seat, owner.win_card, owner.win_type,owner.temp_total_score))
        owner.machine.trigger(WaitState())

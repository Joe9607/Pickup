# coding: utf-8
from datetime import datetime
from state.player_state.settle import SettleState
from state.table_state.base import TableStateBase
from state.table_state.restart import RestartState
from rules.table_rules.manager import TableRulesManager
from rules.define import *
from protocol import game_pb2
from protocol.commands import *
from protocol.serialize import send


class SettleForRoundState(TableStateBase):
    def enter(self, owner):
        super(SettleForRoundState, self).enter(owner)
        # 将所有玩家至于结算状态
        for player in owner.player_dict.values():
            player.machine.trigger(SettleState())

        # 广播小结算数据
        log = {"uuid": owner.room_uuid, "current_round": owner.total_round, "replay": owner.replay,
               "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
               "win_type": owner.win_type, "draw_niao_list": owner.draw_niao_list, "player_data": []}
        proto = game_pb2.SettleForRoundResponse()
        proto.bao_card.card = 0
        proto.win_type = owner.win_type

        liuju = owner.liuju

        # 不流局就换庄并且将当前局数加一,将流局次数减一
        if not liuju:
            if owner.liuju_times > 0:
                owner.liuju_times -= 1
            #     下局庄家换成当前庄家的下一个座位
            owner.dealer_seat = owner.seat_dict[owner.dealer_seat].next_seat
            # 圈
            if not owner.conf.is_round:
                owner.cur_round += 1
                if (owner.cur_round % owner.chairs) == 1:
                    owner.cur_circle += 1

        if owner.conf.is_round:
            if owner.total_round >= owner.conf.max_rounds:
                proto.cur_circle = owner.total_round + 1
            else:
                proto.cur_circle = owner.total_round
        else:
            if (owner.cur_round-1) >= owner.conf.circle * owner.chairs:
                proto.cur_circle = owner.cur_circle + 1
            else:
                proto.cur_circle = owner.cur_circle
            
        if not liuju:
            for k,v in owner.seat_dict.items():
                v.score = v.temp_total_score
                v.total += v.temp_total_score

        for seat in sorted(owner.seat_dict.keys()):
            i = owner.seat_dict[seat]
            p = proto.player_data.add()
            p.player = i.uuid
            for c in i.cards_chow:
                card = p.cards_group_chow.add()
                card.card = c
            for c in i.cards_pong:
                card = p.cards_group_pong.add()
                card.card = c
            for c in i.cards_kong_exposed:
                card = p.cards_group_kong.add()
                card.card = c
            for c in i.cards_kong_concealed:
                card = p.cards_group_kong.add()
                card.card = c

            # if i.win_type > 0:
            #     p.win_card.card = i.win_card
            #     for c in i.cards_in_hand:
            #         card = p.cards_in_hand.add()
            #         card.card = c
            # else:
            win_cards = list(set(i.has_win_cards_list))
            # test = [0x11,0x12,0x13,0x14,0x15,0x16]
            for tc_win_card in win_cards:
                w_card = p.cards_win.add()
                w_card.card = tc_win_card

            p.win_card.card = 0
            for c in sorted(i.cards_in_hand):
                card = p.cards_in_hand.add()
                card.card = c

            if liuju:
                owner.liuju_times += 1
                i.score = 0

            p.hu_score = i.score
            p.kong_score = 0
            p.score = i.score
            p.total = i.total
            p.win_type = i.win_type
            p.kong_exposed_cnt = i.kong_exposed_cnt
            p.kong_concealed_cnt = i.kong_concealed_cnt
            p.kong_discard_cnt = i.kong_discard_cnt
            p.kong_pong_cnt = i.kong_pong_cnt
            for c in i.win_flags:
                flag = p.win_flag.add()
                flag.flag = c

            log["player_data"].append({
                "player": i.uuid,
                "cards_group": i.cards_group,
                "cards_in_hand": i.cards_in_hand,
                "cards_draw_niao": i.cards_draw_niao,
                "win_card": i.win_card,
                "score": i.score + i.gang_score,
                "total": i.total,
                "win_type": i.win_type,
                "kong_exposed_cnt": i.kong_exposed_cnt,
                "kong_concealed_cnt": i.kong_concealed_cnt,
                "kong_discard_cnt": i.kong_discard_cnt,
                "kong_pong_cnt": i.kong_pong_cnt,
            })
            i.kong_total += i.kong_exposed_cnt + i.kong_concealed_cnt + i.kong_pong_cnt
        owner.logger.info(log)
        for i in owner.player_dict.values():
            send(SETTLEMENT_FOR_ROUND, proto, i.session)
        owner.request.settle_for_round(log)
        #owner.cur_round += 1
        owner.total_round += 1
        # 清空本局数据
        for player in owner.player_dict.values():
            player.clear_for_round()
        owner.winner_list = []
        owner.loser_list = []
        owner.draw_niao_list = []
        owner.replay = {}
        owner.win_seat_prompt = []
        owner.win_seat_action = []
        owner.last_oper_seat = -1
        owner.yao_card = -1
        owner.dumps()
        owner.step = 0
        owner.animation_count = 0
        owner.first_ting = -1
        owner.disable_show = False
        owner.last_card = 0
        owner.kong_temp_index = 0
        owner.liuju = True
        # 检测规则是否进入大结算
        TableRulesManager().condition(owner, TABLE_RULE_SETTLE_FOR_ROUND)

    def exit(self, owner):
        # 清空玩家的当局数据
        super(SettleForRoundState, self).exit(owner)

    def next_state(self, owner):
        owner.win_type = 0
        owner.machine.trigger(RestartState())


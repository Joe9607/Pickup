# coding: utf-8

import time
from state.table_state.base import TableStateBase
from protocol import game_pb2
from protocol.commands import *
from protocol.serialize import send


class SettleForRoomState(TableStateBase):

    def enter(self, owner):
        super(SettleForRoomState, self).enter(owner)
        # 广播大结算数据并解散房间
        owner.et = time.time()
        proto = game_pb2.SettleForRoomResponse()
        proto.end_time = time.strftime('%Y-%m-%d %X', time.localtime())
        proto.room_id = owner.room_id
        dismiss_flag = 0 if owner.dismiss_state else 1
        if owner.dismiss_flag == 2:
            dismiss_flag = 2        
        proto.flag = dismiss_flag
        log = {"flag": proto.flag, "uuid": owner.room_uuid, "owner": owner.owner, "max_rounds": owner.conf.max_rounds,
               "st": owner.st, "et": owner.et, "room_id": owner.room_id, "player_data": []}
        scores = []
        for p in owner.player_dict.values():
            scores.append(p.total)
        top_score = max(scores)
        for p in owner.player_dict.values():
            i = proto.player_data.add()
            i.player = p.uuid
            i.seat = p.seat
            i.total_score = p.total
            i.top_score = top_score
            i.win_total_cnt = p.win_total_cnt
            i.win_draw_cnt = p.win_draw_cnt
            i.win_discard_cnt = p.win_discard_cnt
            i.pao_cnt = p.pao_cnt
            i.is_owner = 1 if p.uuid == owner.owner else 0
            i.kong_total_cnt = p.kong_total
            i.total_chong_bao = p.total_chong_bao
            log["player_data"].append({
                "player": p.uuid,
                "seat": p.seat,
                "total": p.total,
                "top_score": top_score,
                "win_total_cnt": p.win_total_cnt,
                "win_draw_cnt": p.win_draw_cnt,
                "win_discard_cnt": p.win_discard_cnt,
                "pao_cnt": p.pao_cnt,
                "is_owner": i.is_owner,
                "kong_total_cnt": i.kong_total_cnt,
                "total_chong_bao":i.total_chong_bao,
            })
        owner.logger.info(log)
        owner.dumps()
        for p in owner.player_dict.values():
            send(SETTLEMENT_FOR_ROOM, proto, p.session)
        owner.request.settle_for_room(log)
        # owner.bao_card = 0
        # owner.bao_card_idx = 0
        owner.dismiss_flag = 1
        # if owner.conf.is_aa() and owner.cur_round >= owner.conf.max_rounds:
        #     for p in owner.player_dict.values():
        #         owner.request.aa_refund(p.uuid, 1)

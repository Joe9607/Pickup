# coding: utf-8
from state.player_state.wait import WaitState
from state.table_state.base import TableStateBase
from rules.define import *
from protocol import game_pb2
from protocol.commands import *
from protocol.serialize import send


class SettleForCardState(TableStateBase):
    def enter(self, owner):
        super(SettleForCardState, self).enter(owner)
        # 将所有玩家至于结算状态
        for player in owner.player_dict.values():
            player.machine.trigger(WaitState())

        # 广播胡牌数据
        proto = game_pb2.SendScoreResponse()

        for seat in sorted(owner.seat_dict.keys()):
            i = owner.seat_dict[seat]
            p = proto.player_data.add()
            p.player = i.uuid
            # 胡牌的人需要特殊处理
            if i.has_win > 0:
                p.win_card = i.win_card
                # 添加回放
                owner.replay["procedure"].append({"hu_card": [i.seat, i.win_card]})
            else:
                p.win_card = 0

            p.win_type = i.win_type
            p.hu_score = i.cards_score + i.gang_score

        for i in owner.player_dict.values():
                send(SEND_SCORE, proto, i.session)

        # 清空本次胡牌数据
        for player in owner.player_dict.values():
            player.cards_score = 0
            player.has_win = 0
            player.win_card = 0
        owner.win_seat_prompt = []
        owner.win_seat_action = []
        from state.table_state.step import StepState
        owner.machine.trigger(StepState())
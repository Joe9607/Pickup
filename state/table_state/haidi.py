# coding: utf-8


from protocol.serialize import send
from state.table_state.base import TableStateBase
from rules.define import *
from state.table_state.end import EndState
from protocol.commands import HAIDI
from protocol import game_pb2
from behavior_tree.forest import is_ready_hand


class HaiDiState(TableStateBase):
    def enter(self, owner):
        super(HaiDiState, self).enter(owner)
        # TableRulesManager().condition(owner, TABLE_RULE_END)
        owner.haidi_pre_seat = owner.active_seat
        owner.reset_proto(HAIDI)
        # 按顺序发牌
        for i in range(owner.chairs):
            active_player = owner.seat_dict[owner.active_seat]
            owner.active_seat = active_player.next_seat
            player = owner.seat_dict[owner.active_seat]
            proto = game_pb2.QH_HaiDiResponse()
            proto.cards_rest_num = 0
            card = owner.cards_on_desk.pop()
            player.draw_card = card
            player.cards_ready_hand = is_ready_hand(player)
            player.cards_in_hand.append(card)
            # player.proto.p = copy(proto)
            proto.card.card= card
            send(HAIDI,proto,player.session)
            player.dumps()
            cards_rest_num = len(owner.cards_on_desk)
            owner.replay["procedure"].append({"draw": [player.seat, card, cards_rest_num]})
        for player in owner.player_dict.values():
            from rules.player_rules.manager import PlayerRulesManager
            PlayerRulesManager().condition(player, PLAYER_RULE_MOON)
        if not owner.player_prompts :
            # 没有提示
            owner.machine.trigger(EndState())

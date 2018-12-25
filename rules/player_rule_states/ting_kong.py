# coding: utf-8
from state.player_state.draw_after_kong import DrawAfterKongState
from state.player_state.base import PlayerStateBase
from rules.player_rule_states.draw_win import DrawWinState
from logic.player_action import *


class TingKongState(PlayerStateBase):
    def enter(self, owner):
        super(TingKongState, self).enter(owner)
        # 广播听牌
        proto = game_pb2.ActionResponse()
        for card in owner.action_ref_cards:
            cards = proto.card.add()
            cards.card = card
        proto.active_card.card = 0
        proto.trigger_seat = owner.seat
        proto.player = owner.uuid
        if owner.last_gang_card != 0:
            owner.gang_pao_card = owner.last_gang_card
        else:
            owner.gang_pao_card = 0
        owner.ready_hand(True)
        owner.isTing = True
        proto.active_type = PLAYER_ACTION_TYPE_TING
        owner.table.reset_proto(ACTION)
        for player in owner.table.player_dict.values():
            if player.uuid == owner.uuid:
                continue
            player.proto.p = copy(proto)
            player.proto.send()
        #发送看宝
        owner.table.logger.info("player {0} enter ting".format(owner.seat))
        owner.table.reset_proto(ACTION)
        self.next_state(owner)



    def next_state(self, owner):
        owner.machine.trigger(DrawAfterKongState())

    def exit(self, owner):
        super(TingKongState, self).exit(owner)

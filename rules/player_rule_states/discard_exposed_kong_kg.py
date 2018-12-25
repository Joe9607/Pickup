# coding: utf-8
from protocol import game_pb2
from protocol.commands import *
from protocol.serialize import send
from rules.define import *
from state.player_state.base import PlayerStateBase
from state.player_state.wait import WaitState
from logic.player_action import calculate_final_score


class DiscardExposedKongKGState(PlayerStateBase):

    def enter(self, owner):
        super(DiscardExposedKongKGState, self).enter(owner)

        for card in owner.action_ref_cards:
            owner.cards_in_hand.remove(card)

        active_card = owner.action_op_card
        action_cards = [active_card] * 4
        owner.cards_kong_exposed.extend(action_cards)
        owner.cards_group.extend(action_cards)
        owner.add_gang_num(1, 0, 0, 0)
        trigger_seat = owner.table.active_seat
        trigger_player = owner.table.seat_dict[trigger_seat]
        calculate_final_score(trigger_player, owner, owner.get_fang_gang_score())
        trigger_player.add_gang_num(0,0,0,1)
        trigger_player.cards_discard.remove(active_card)
        trigger_player.machine.trigger(WaitState())
        owner.table.active_seat = owner.seat

        proto = game_pb2.ActionCSResponse()
        for card in owner.action_ref_cards:
            cards = proto.ref_card.add()
            cards.card = card
        proto.active_card.card = active_card
        proto.trigger_seat = trigger_seat
        proto.active_type = PLAYER_ACTION_TYPE_KONG_EXPOSED_KG
        proto.player = owner.uuid
        for player in owner.table.player_dict.values():
            send(ACTION_CS, proto, player.session)
        owner.table.logger.info("player {0} kong {1}".format(owner.seat, active_card))
        owner.table.discard_seat = -1

        #owner.table.machine.trigger(KongState())

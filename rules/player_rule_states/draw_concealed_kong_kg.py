# coding: utf-8
from protocol import game_pb2
from protocol.commands import *
from protocol.serialize import send
from rules.define import *
from state.player_state.base import PlayerStateBase
from logic.player_action import calculate_final_score


class DrawConcealedKongKGState(PlayerStateBase):

    def enter(self, owner):
        super(DrawConcealedKongKGState, self).enter(owner)
        #print self.name, owner.action_ref_cards, owner.cards_in_hand
        for card in owner.action_ref_cards:
            owner.cards_in_hand.remove(card)
        owner.cards_kong_concealed.extend(owner.action_ref_cards)
        owner.cards_group.extend(owner.action_ref_cards)
        owner.table.active_seat = owner.seat
        owner.add_gang_num(0, 0, 1, 0)
        proto = game_pb2.ActionCSResponse()
        for card in owner.action_ref_cards:
            cards = proto.ref_card.add()
            cards.card = card
        proto.active_type = PLAYER_ACTION_TYPE_KONG_CONCEALED_KG
        proto.player = owner.uuid
        proto.trigger_seat = owner.seat
        proto.active_card.card = 0
        for player in owner.table.player_dict.values():
            send(ACTION_CS, proto, player.session)
            if player == owner:
                continue
            else:
                calculate_final_score(player, owner, SCORE_AN_GANG)
        owner.table.logger.info("player {0} kong {1}".format(owner.seat, owner.action_ref_cards))
        owner.table.discard_seat = -1

        #owner.table.machine.trigger(KongState())

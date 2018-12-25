# coding: utf-8
from copy import copy

from protocol import game_pb2
from protocol.commands import *
from protocol.serialize import send
from rules.player_rules.manager import PlayerRulesManager
from state.player_state.base import PlayerStateBase

from rules.define import *

from logic.player_action import calculate_final_score


class DrawExposedKongKGState(PlayerStateBase):

    def enter(self, owner):
        super(DrawExposedKongKGState, self).enter(owner)

        active_card = owner.action_op_card
        #print self.name, owner.action_ref_cards, owner.cards_in_hand

        owner.cards_in_hand.remove(active_card)
        owner.cards_kong_exposed.extend([active_card] * 4)
        owner.cards_pong.remove(active_card)
        owner.cards_pong.remove(active_card)
        owner.cards_pong.remove(active_card)
        insert_index = owner.cards_group.index(active_card)
        owner.cards_group.insert(insert_index, active_card)
        owner.table.active_seat = owner.seat
        owner.table.active_card = active_card
        owner.add_gang_num(0, 1, 0, 0)
        proto = game_pb2.ActionCSResponse()
        for card in owner.action_ref_cards:
            cards = proto.ref_card.add()
            cards.card = card
        proto.active_type = PLAYER_ACTION_TYPE_KONG_PONG_KG
        proto.player = owner.uuid
        proto.trigger_seat = owner.seat
        proto.active_card.card = 0
        owner.table.reset_proto(ACTION_CS)

        owner.table.clear_prompt()
        owner.table.clear_actions()

        for player in owner.table.player_dict.values():
            # send(ACTION_CS, proto, player.session)
            player.proto.p = copy(proto)
            if player.uuid != owner.uuid:
                PlayerRulesManager().condition(player, PLAYER_RULE_KONG)
                calculate_final_score(player, owner, SCORE_MING_GANG)
            player.proto.send()
        owner.table.discard_seat = -1
        owner.table.logger.info("player {0} kong {1}".format(owner.seat, active_card))
        owner.table.logger.debug("clear all prompt and action at DrawExposedKongKGState state")

        if owner.table.player_prompts:
            #print "when pong kong ", owner.table.player_prompts
            return

        #owner.table.machine.trigger(KongState())

    def next_state(self, owner):
        owner.table.machine.trigger(KongState())

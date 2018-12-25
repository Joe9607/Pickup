# coding: utf-8
from copy import copy

from protocol import game_pb2
from protocol.commands import *
from protocol.serialize import send
from rules.define import *
from rules.player_rules.manager import PlayerRulesManager
from state.player_state.base import PlayerStateBase
from state.player_state.discard import DiscardState
from state.player_state.wait import WaitState


class ChowState(PlayerStateBase):
    def __init__(self):
        super(PlayerStateBase, self).__init__()

    def enter(self, owner):
        super(ChowState, self).enter(owner)

        for card in owner.action_ref_cards:
            owner.cards_in_hand.remove(card)
        active_card = owner.table.active_card
        action_cards = owner.action_ref_cards
        action_cards.append(active_card)
        owner.cards_chow.extend(action_cards)
        owner.cards_group.extend(action_cards)

        trigger_seat = owner.table.active_seat
        trigger_player = owner.table.seat_dict[trigger_seat]
        trigger_player.cards_discard.remove(active_card)
        trigger_player.machine.trigger(WaitState())
        owner.table.active_seat = owner.seat

        proto = game_pb2.ActionResponse()
        for card in owner.action_ref_cards:
            cards = proto.card.add()
            cards.card = card
        proto.active_card.card = active_card
        proto.trigger_seat = trigger_seat
        proto.active_type = PLAYER_ACTION_TYPE_CHOW
        proto.player = owner.uuid
        # for player in owner.table.player_dict.values():
        #     send(ACTION, proto, player.session)
        owner.table.reset_proto(ACTION)
        for player in owner.table.player_dict.values():
            player.proto.p = copy(proto)
            if player.uuid == owner.uuid:
                PlayerRulesManager().condition(owner, PLAYER_RULE_CHOW)
            player.proto.send()
        owner.table.logger.info("player {0} chow {1}".format(owner.seat, active_card))
        # 吃完后检测杠
        owner.table.discard_seat = -1
        # owner.table.check_bao_change()
        owner.dumps()
        # PlayerRulesManager().condition(owner, PLAYER_RULE_CHOW)

    def exit(self, owner):
        super(ChowState, self).exit(owner)

    def next_state(self, owner):
        owner.machine.trigger(DiscardState())

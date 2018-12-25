# coding: utf-8
from protocol import game_pb2
from protocol.commands import *
from protocol.serialize import send
from rules.define import *
from state.player_state.base import PlayerStateBase
from state.player_state.draw_after_kong import DrawAfterKongState
from state.player_state.wait import WaitState
from rules.player_rules.manager import PlayerRulesManager


class DiscardExposedKongState(PlayerStateBase):
    def __init__(self):
        super(DiscardExposedKongState, self).__init__()

    def enter(self, owner):
        super(DiscardExposedKongState, self).enter(owner)
        for card in owner.action_ref_cards:
            owner.cards_in_hand.remove(card)

        active_card = owner.table.active_card
        action_cards = [active_card] * 4
        owner.cards_kong_exposed.extend(action_cards)
        owner.cards_group.extend(action_cards)

        trigger_seat = owner.table.active_seat
        trigger_player = owner.table.seat_dict[trigger_seat]
        trigger_player.cards_discard.remove(active_card)
        trigger_player.machine.trigger(WaitState())
        owner.table.active_seat = owner.seat
        trigger_player.add_gang_num(0, 0, 0, 1)
        owner.add_gang_num(1, 0, 0, 0)

        proto = game_pb2.ActionResponse()
        for card in owner.action_ref_cards:
            cards = proto.card.add()
            cards.card = card
        proto.active_card.card = active_card
        proto.trigger_seat = trigger_seat
        proto.active_type = PLAYER_ACTION_TYPE_KONG_EXPOSED
        proto.player = owner.uuid
        for player in owner.table.player_dict.values():
            send(ACTION, proto, player.session)
        owner.last_gang_card = active_card
        owner.table.logger.info("player {0} kong {1}".format(owner.seat, active_card))
        owner.table.discard_seat = -1
        from rules.player_rules.manager import PlayerRulesManager
        from rules.define import PLAYER_RULE_TING_KONG
        owner.table.reset_proto(PROMPT)
        PlayerRulesManager().condition(owner,PLAYER_RULE_TING_KONG)
        # owner.machine.next_state()
        # owner.table.check_bao_change()

    def exit(self, owner):
        super(DiscardExposedKongState, self).exit(owner)

    def next_state(self, owner):
        owner.ready_hand()
        owner.machine.trigger(DrawAfterKongState())

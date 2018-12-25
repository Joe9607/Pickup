    # coding: utf-8
from protocol import game_pb2
from protocol.commands import *
from protocol.serialize import send
from state.player_state.base import PlayerStateBase
from state.player_state.draw_after_kong import DrawAfterKongState
from rules.define import *
from rules.player_rules.manager import PlayerRulesManager


class DrawConcealedKongState(PlayerStateBase):

    def enter(self, owner):
        super(DrawConcealedKongState, self).enter(owner)
        #print "cards_kong_concealed", owner.action_ref_cards, owner.cards_in_hand
        for card in owner.action_ref_cards:
            owner.cards_in_hand.remove(card)
        owner.cards_kong_concealed.extend(owner.action_ref_cards)
        owner.cards_group.extend(owner.action_ref_cards)
        owner.table.active_seat = owner.seat

        proto = game_pb2.ActionResponse()
        for card in owner.action_ref_cards:
            cards = proto.card.add()
            cards.card = card
        proto.active_type = PLAYER_ACTION_TYPE_KONG_CONCEALED
        proto.player = owner.uuid
        proto.trigger_seat = owner.seat
        proto.active_card.card = 0
        for player in owner.table.player_dict.values():
            send(ACTION, proto, player.session)
        owner.table.logger.info("player {0} kong {1}".format(owner.seat, owner.action_ref_cards))
        # 修改杠上开花
        owner.last_gang_card = owner.table.active_card
        owner.add_gang_num(0, 0, 1, 0)
        owner.table.discard_seat = -1
        # owner.table.check_bao_change()
        from rules.player_rules.manager import PlayerRulesManager
        from rules.define import PLAYER_RULE_TING_KONG
        owner.table.reset_proto(PROMPT)
        PlayerRulesManager().condition(owner,PLAYER_RULE_TING_KONG)
        # owner.machine.next_state()

    def exit(self, owner):
        super(DrawConcealedKongState, self).exit(owner)

    def next_state(self, owner):
        owner.ready_hand()
        owner.machine.trigger(DrawAfterKongState())

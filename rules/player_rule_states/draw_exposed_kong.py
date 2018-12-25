# coding: utf-8
from copy import copy

from protocol import game_pb2
from protocol.commands import *
from rules.define import *
from state.player_state.base import PlayerStateBase
from state.player_state.draw_after_kong import DrawAfterKongState
from state.player_state.pause import PauseState
from rules.player_rules.manager import PlayerRulesManager


class DrawExposedKongState(PlayerStateBase):

    def enter(self, owner):
        super(DrawExposedKongState, self).enter(owner)

        active_card = owner.action_ref_cards[0]
        owner.draw_kong_exposed_card = active_card
        #print "cards_draw_kong_exposed", owner.action_ref_cards, owner.cards_in_hand

        owner.cards_in_hand.remove(active_card)
        owner.cards_kong_exposed.extend([active_card] * 4)
        owner.cards_pong.remove(active_card)
        owner.cards_pong.remove(active_card)
        owner.cards_pong.remove(active_card)
        owner.add_gang_num(0, 1, 0, 0)
        insert_index = owner.cards_group.index(active_card)
        owner.cards_group.insert(insert_index, active_card)
        owner.table.active_seat = owner.seat
        owner.table.last_oper_seat = owner.seat
        owner.table.active_card = active_card
        proto = game_pb2.ActionResponse()
        for card in owner.action_ref_cards:
            cards = proto.card.add()
            cards.card = card
        proto.active_type = PLAYER_ACTION_TYPE_KONG_PONG
        proto.player = owner.uuid
        proto.trigger_seat = owner.seat
        proto.active_card.card = 0
        owner.table.discard_seat = owner.seat
        owner.table.logger.info("player {0} kong {1}".format(owner.seat, active_card))
        #owner.table.reset_proto(ACTION)
        # 修改杠上开花
        owner.last_gang_card = owner.table.active_card
        if owner.table.conf.is_qg():
            owner.table.reset_proto(ACTION)
            owner.table.clear_prompt()
            owner.table.clear_actions()
            for player in owner.table.player_dict.values():
                player.proto.p = copy(proto)
                if player.uuid != owner.uuid:
                    player.machine.cur_state.execute(player, "other_kong")
                player.proto.send()

            if owner.table.player_prompts:
                #print "when pong kong ", owner.table.player_prompts
                owner.machine.trigger(PauseState())
                return
        else:
            owner.table.reset_proto(ACTION)
            for player in owner.table.player_dict.values():
                player.proto.p = copy(proto)
                player.proto.send()
        # for player in owner.table.player_dict.values():
        #     player.proto.p = copy(proto)
        #     player.proto.send()
        from rules.player_rules.manager import PlayerRulesManager
        from rules.define import PLAYER_RULE_TING_KONG
        owner.table.reset_proto(PROMPT)
        PlayerRulesManager().condition(owner,PLAYER_RULE_TING_KONG)
        # owner.machine.next_state()

    def exit(self, owner):
        super(DrawExposedKongState, self).exit(owner)

    def next_state(self, owner):
        owner.ready_hand()
        owner.machine.trigger(DrawAfterKongState())

# coding: utf-8
from state.player_state.wait import WaitState
from state.player_state.base import PlayerStateBase
from rules.player_rule_states.draw_win import DrawWinState
from logic.player_action import *


class TingState(PlayerStateBase):
    def enter(self, owner):
        super(TingState, self).enter(owner)
        #print 'ready hand len:', len(owner.cards_ready_hand)

        # 广播听牌
        proto = game_pb2.ActionResponse()
        for card in owner.action_ref_cards:
            cards = proto.card.add()
            cards.card = card

        proto.active_card.card = owner.action_op_card
        proto.trigger_seat = owner.seat
        proto.player = owner.uuid
        owner.cards_in_hand.remove(owner.action_op_card)
        if owner.last_gang_card != 0:
            owner.gang_pao_card = owner.last_gang_card
        else:
            owner.gang_pao_card = 0
        owner.last_gang_card = 0
        if owner.action_weight == PLAYER_ACTION_TYPE_JIA:
            owner.isJia = True
        owner.ready_hand(True)
        owner.isTing = True
        proto.active_type = PLAYER_ACTION_TYPE_TING
        # for player in owner.table.player_dict.values():
        #     send(ACTION, proto, player.session)
        owner.table.reset_proto(ACTION)
        for player in owner.table.player_dict.values():
            if player.uuid == owner.uuid:
                continue
            player.proto.p = copy(proto)
            player.proto.send()
        #发送看宝
        owner.table.logger.info("player {0} enter ting".format(owner.seat))
        # 出牌相关
        owner.table.discard_seat = owner.seat
        owner.table.last_oper_seat = owner.seat
        owner.last_gang_card = 0
        owner.cards_discard.append(owner.action_op_card)


        owner.table.logger.info("player {0} ting discard {1}".format(owner.seat, owner.action_op_card))
        owner.table.step += 1
        owner.table.active_card = owner.action_op_card
        owner.miss_win_cards = []
        owner.draw_card = 0
        owner.table.replay["procedure"].append({"discard": [owner.seat, owner.action_op_card]})
        owner.can_look_bao = owner.table.conf.look_bao_on_ting()
        owner.table.reset_proto(ACTION)
        for i in owner.table.player_dict.values():
            if i.uuid == owner.uuid:
                continue
            i.machine.cur_state.execute(i, "other_discard")
        if owner.table.player_prompts:
            owner.machine.trigger(PauseState())
        else:
            self.next_state(owner)


    def next_state(self, owner):
        owner.machine.trigger(WaitState())
        owner.table.machine.cur_state.execute(owner.table, "step")

    def exit(self, owner):
        super(TingState, self).exit(owner)

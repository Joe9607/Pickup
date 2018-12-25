# coding: utf-8
from state.player_state.wait import WaitState
import random
from copy import copy
from state.player_state.base import PlayerStateBase
from protocol import game_pb2
from protocol.commands import *
from state.player_state.prompt_draw import PromptDrawState
from protocol.serialize import send
from state.player_state.discard import DiscardState
from rules.player_rule_states.draw_win import DrawWinState
from rules.player_rules.manager import PlayerRulesManager
from rules.define import *


class YaoState(PlayerStateBase):
    def enter(self, owner):
        super(YaoState, self).enter(owner)
        from rules.player_rules.draw_concealed_kong import DrawConcealedKongRule
        from rules.player_rules.draw_exposed_kong import DrawExposedKongRule
        from rules.player_rules.draw_win import DrawWinRule
        from rules.player_rules.ting import TingRule
        owner.miss_win_cards = []
        owner.miss_pong_cards = []
        owner.table.clear_prompt()
        owner.table.clear_actions()
        draw_rules = [DrawConcealedKongRule(), DrawExposedKongRule(), TingRule(), DrawWinRule()]
        card = owner.table.cards_on_desk.pop()
        owner.draw_card = card
        # owner.dealer_seat = owner.seat
        owner.cards_in_hand.append(card)
        dice_1 = random.randint(1, 6)
        dice_2 = random.randint(1, 6)
        owner.table.reset_proto(DRAW)
        proto = game_pb2.DrawResponse()
        proto.player = owner.uuid
        proto.card.card = card + (dice_1 << 12) + (dice_2 << 8)
        #print 'card val:', proto.card.card
        owner.table.last_draw = owner.seat
        owner.draw_cnt += 1
        player = owner.table.player_dict[owner.uuid]
        # owner.dumps()
        player.proto.p = proto
        player.is_yao_fail = True
        # owner.dumps()
        # player.add_prompt(PLAYER_ACTION_TYPE_WIN_DRAW, "DrawWinRule", card, player.cards_in_hand)
        owner.table.yao_card = card
        if card in owner.cards_ready_hand:
            # 添加胡牌提示
            owner.last_yao_card = card
            player.is_yao_fail = False
        flag = False
        for r in draw_rules:
            if r.condition(player):
                flag = True
        if flag:
            owner.table.player_prompts.append(owner.uuid)
        player.proto.send()
        # owner.table.clear_actions()
        owner.table.logger.info("player {0} yao card {1}".format(owner.seat, card))
        owner.table.reset_proto(DRAW)
        owner.dumps()
        owner.table.replay["procedure"].append({"yao": [owner.seat, card]})

    def next_state(self, owner):
        owner.machine.trigger(DiscardState())
        return

    def execute(self, owner, event, proto=None):
        super(YaoState, self).execute(owner, event, proto)
        from logic.player_action import action, discard
        if event == "action":
            action(owner, proto)
        elif event == "discard":
            discard(owner, proto)
        else:
            owner.table.logger.warn("player {0} event {1} not register".format(owner.seat, event))

    def exit(self, owner):
        return

    # def execute(self, owner, event, proto=None):
    #     if event == "action":
    #         if owner.last_yao_card != 0:
    #             owner.machine.trigger(DrawWinState())



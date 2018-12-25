# coding: utf-8
from copy import copy

from protocol import game_pb2
from protocol.commands import *
from rules.define import PLAYER_RULE_DRAW
from behavior_tree.forest import is_ready_hand
from state.player_state.base import PlayerStateBase
from state.player_state.discard import DiscardState


class DrawAfterKongState(PlayerStateBase):
    def __init__(self):
        super(DrawAfterKongState, self).__init__()

    def enter(self, owner):
        super(DrawAfterKongState, self).enter(owner)

        # 清除桌子提示和动作
        owner.miss_win_cards = []
        owner.miss_pong_cards = []
        owner.table.clear_prompt()
        owner.table.clear_actions()
        # 重新更新听牌提示，在上家打牌点过后这个需要重新计算
        # 杠次数加一
        owner.kong_times += 1
        card = owner.table.cards_on_desk.pop(0)
        # 换显示的杠牌
        owner.table.change_kong_card()
        owner.draw_card = card
        owner.cards_ready_hand = is_ready_hand(owner)
        owner.cards_in_hand.append(card)
        # 增加剩余可抓牌
        cards_rest_num = len(owner.table.cards_on_desk)
        owner.table.replay["procedure"].append({"draw": [owner.seat, card, cards_rest_num]})
        proto = game_pb2.DrawResponse()
        proto.player = owner.uuid

        proto.cards_rest_num = cards_rest_num
        # print cards_rest_num
        owner.table.reset_proto(DRAW)
        owner.table.last_draw = owner.seat
        owner.draw_cnt += 1
        for player in owner.table.player_dict.values():
            player.proto.p = copy(proto)
            if player.uuid == owner.uuid:
                player.proto.p.card.card = card
                from rules.player_rules.manager import PlayerRulesManager
                PlayerRulesManager().condition(owner, PLAYER_RULE_DRAW)
            else:
                player.proto.p.card.card = 0
            player.proto.send()
        owner.table.logger.info("player {0} draw card {1}".format(owner.seat, card))
        owner.dumps()
        owner.table.logger.info("draw after dumps")

    def next_state(self, owner):
        owner.machine.trigger(DiscardState())


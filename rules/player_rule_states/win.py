# coding: utf-8

from protocol import game_pb2
from protocol.commands import *
from protocol.serialize import send
from rules.define import *
from state.player_state.base import PlayerStateBase
from logic.tfs_algorithm import TFS, try_compose_seven_pairs


class WinState(PlayerStateBase):
    def enter(self, owner):
        super(WinState, self).enter(owner)
        # 广播玩家胡牌

        proto = game_pb2.ActionResponse()
        proto.player = owner.uuid

        owner.win_total_cnt += 1
        if owner.table.active_seat == owner.seat:
            proto.trigger_seat = owner.seat
            proto.active_type = PLAYER_ACTION_TYPE_WIN_DRAW
            owner.win_type = PLAYER_WIN_TYPE_DRAW
            owner.win_draw_cnt += 1
            owner.win_card = owner.draw_card
            owner.table.winner_list = [owner.seat]
            # 需要将胡的牌进行效验整理
            tfs = TFS()
            owner.cards_win = tfs.start(owner.cards_in_hand)
            if owner.table.conf.is_qxd() and try_compose_seven_pairs(owner.cards_in_hand):
                owner.cards_win = sorted(owner.cards_in_hand)

            for player in owner.table.player_dict.values():
                if player.uuid == owner.uuid:
                    owner.score += 6
                    owner.total += 6
                else:
                    player.score -= 2
                    player.total -= 2
                    owner.table.loser_list.append(player.seat)

        else:
            active_card = owner.action_op_card
            proto.trigger_seat = owner.table.active_seat
            trigger_player = owner.table.seat_dict[owner.table.active_seat]
            trigger_player.win_type = PLAYER_WIN_PAO

            # 如果触发玩家上一个状态是自摸明杠则需要从他的手牌中删除此牌, 不重复删除
            if trigger_player.machine.last_state.name == "DrawExposedKongState" \
                    and active_card in trigger_player.cards_kong_exposed:
                trigger_player.kong_pong_cnt -= 1
                trigger_player.cards_pong.extend([active_card]*3)
                trigger_player.cards_kong_exposed.remove(active_card)
                trigger_player.cards_kong_exposed.remove(active_card)
                trigger_player.cards_kong_exposed.remove(active_card)
                trigger_player.cards_kong_exposed.remove(active_card)
                trigger_player.cards_group.remove(active_card)

            proto.active_type = PLAYER_ACTION_TYPE_WIN_DISCARD
            owner.win_type = PLAYER_WIN_TYPE_DISCARD
            owner.win_card = active_card
            owner.win_discard_cnt += 1
            owner.table.winner_list.append(owner.seat)
            owner.table.loser_list = [trigger_player.seat]

            cards_win = owner.cards_in_hand
            cards_win.append(active_card)
            tfs = TFS()
            owner.cards_win = tfs.start(cards_win)
            if owner.table.conf.is_qxd() and try_compose_seven_pairs(cards_win):
                owner.cards_win = sorted(cards_win)

            trigger_player.score -= 1
            trigger_player.total -= 1
            owner.score += 1
            owner.total += 1
            trigger_player.dumps()

        # 需要将胡的牌单独拿出来
        owner.cards_win.remove(owner.win_card)
        proto.active_card.card = owner.win_card
        for card in owner.cards_win:
            cards = proto.card.add()
            cards.card = card
        owner.dumps()
        for player in owner.table.player_dict.values():
            send(ACTION, proto, player.session)
        owner.table.logger.info("player {0} win {1} type {2}".format(owner.seat, owner.win_card, owner.win_type))

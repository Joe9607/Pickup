# coding: utf-8

from protocol import game_pb2
from protocol.commands import *
from protocol.serialize import send
from rules.define import *
from state.player_state.base import PlayerStateBase
from state.table_state.end import EndState
from logic.player_action import calculate_final_score
from behavior_tree.base import *


class QGWinState(PlayerStateBase):
    def enter(self, owner):
        super(QGWinState, self).enter(owner)
        # 广播玩家胡牌

        proto = game_pb2.ActionResponse()
        proto.player = owner.uuid

        owner.win_total_cnt += 1
        active_card = owner.action_op_card
        proto.trigger_seat = owner.table.active_seat
        trigger_player = owner.table.seat_dict[owner.table.active_seat]
        trigger_player.win_type = PLAYER_WIN_PAO

        # 如果触发玩家上一个状态是自摸明杠则需要从他的手牌中删除此牌, 不重复删除
        if active_card in trigger_player.cards_kong_exposed:
            trigger_player.cards_pong.extend([active_card]*3)
            trigger_player.cards_kong_exposed.remove(active_card)
            trigger_player.cards_kong_exposed.remove(active_card)
            trigger_player.cards_kong_exposed.remove(active_card)
            trigger_player.cards_kong_exposed.remove(active_card)
            trigger_player.kong_pong_cnt -= 1
            trigger_player.cards_group.remove(active_card)
        proto.active_type = PLAYER_ACTION_TYPE_WIN_DISCARD
        owner.win_type = PLAYER_WIN_TYPE_DISCARD
        owner.win_card = active_card
        owner.win_discard_cnt += 1
        owner.table.winner_list.append(owner.seat)
        owner.table.loser_list = [trigger_player.seat]

        owner.cards_win = owner.cards_in_hand
        owner.cards_win.append(active_card)
        owner.cards_win.sort()

        _, flags = owner.cards_ready_hand[owner.win_card]
        #print 'player seat:', owner.seat, ', uuid:', owner.uuid, 'win flags:', flags
        flags.append('QGH')
        owner.win_flags.extend(flags)
        if "JIAHU" in owner.win_flags and not owner.isJia:
            owner.win_flags.remove("JIAHU")
        # 需要将胡的牌单独拿出来
        owner.cards_win.remove(owner.win_card)
        proto.active_card.card = owner.win_card
        for card in owner.cards_win:
            cards = proto.card.add()
            cards.card = card
        owner.dumps()
        if owner.isJia:
            if owner.table.conf.bian_hu_jia() and "BIANHU" in owner.win_flags:
                owner.win_flags.remove("BIANHU")
                owner.win_flags.append("JIAHU")
        base_score = WIN_DISCARD
        if owner.table.dealer_seat == owner.seat:
            base_score = base_score * 2
        if len(trigger_player.cards_group) == 0:#门清
            base_score = base_score * 2
        if owner.isJia:
            base_score = base_score * 2
        if trigger_player.seat == owner.table.dealer_seat:
            base_score = base_score * 2
        if owner.table.conf.is_fan_hu('PIAOHU') and 'PIAOHU' in owner.win_flags:
            base_score *= 4
        base_score *= 2#抢杠

        if owner.table.conf.pao_score_self():
            calculate_final_score(trigger_player, owner, base_score)
        if owner.table.conf.pao_score_pay_all():
            b_score = 0
            for k, v in owner.table.seat_dict.items():
                if k == owner.seat:
                    continue
                b_score += self.calc_score(v, owner)
            calculate_final_score(trigger_player, owner, b_score)
        if owner.table.conf.pao_score_all_pay():
            for k, v in owner.table.seat_dict.items():
                if  k == owner.seat:
                    continue
                if k == trigger_player.seat:
                    calculate_final_score(trigger_player, owner, base_score)
                else:
                    pay_score = self.calc_score(v, owner)
                    calculate_final_score(v, owner, pay_score)
        trigger_player.dumps()
        for player in owner.table.player_dict.values():
            send(ACTION, proto, player.session)

        if owner.table.dealer_seat != owner.seat:
            owner.table.dealer_seat = owner.table.seat_dict[owner.table.dealer_seat].next_seat
            # 圈
            if not owner.table.conf.is_round:
                owner.table.cur_round += 1
                if (owner.table.cur_round % owner.table.chairs) == 1:
                    owner.table.cur_circle += 1
   
        #owner.table.dealer_seat = owner.seat
        owner.table.logger.info("player {0} win {1} type {2}".format(owner.seat, owner.win_card, owner.win_type))
        owner.table.machine.trigger(EndState())

    def calc_score(self,player, owner):
        base_score = WIN_BASE#抢杠翻
        if player.seat == player.table.dealer_seat:
            base_score *= 2
        if len(player.cards_group) == 0:
            base_score *= 2
        if owner.isJia:
            base_score *= 2
        if owner.seat == player.table.dealer_seat:
            base_score *= 2
        if owner.table.conf.is_fan_hu('PIAOHU') and "PIAOHU" in owner.win_flags:
            base_score = base_score * 2
        if player.seat == player.table.active_seat:#点炮者加倍
            base_score *= 2
        return base_score
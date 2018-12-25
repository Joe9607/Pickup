# coding: utf-8

from protocol import game_pb2
from protocol.commands import *
from protocol.serialize import send
from rules.define import *
from state.player_state.base import PlayerStateBase
from state.table_state.end import EndState
from logic.player_action import calculate_final_score


class DiscardWinState(PlayerStateBase):
    def enter(self, owner):
        super(DiscardWinState, self).enter(owner)
        # 广播玩家胡牌
        proto = game_pb2.ActionResponse()
        proto.player = owner.uuid
        owner.win_total_cnt += 1
        active_card = owner.action_op_card
        proto.trigger_seat = owner.table.active_seat
        trigger_player = owner.table.seat_dict[owner.table.active_seat]
        trigger_player.win_type = PLAYER_WIN_PAO
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
        trigger_player.dumps()
        owner.win_flags.extend(flags)
        if "JIAHU" in owner.win_flags and not owner.isJia:
            owner.win_flags.remove("JIAHU")
        #owner.table.dealer_seat = owner.seat
        # 需要将胡的牌单独拿出来
        owner.cards_win.remove(owner.win_card)
        proto.active_card.card = owner.win_card
        for card in owner.cards_win:
            cards = proto.card.add()
            cards.card = card
        owner.dumps()
        #穷胡计分
        base_score = WIN_DISCARD
        if trigger_player.gang_pao_card != 0 and owner.table.conf.is_fan_hu('GSDP'):
            owner.win_flags.append('GSDP')
            base_score = base_score * 2
        if owner.table.dealer_seat == owner.seat:
            owner.win_flags.append('ZHHU')
            base_score = base_score * 2
        if len(trigger_player.cards_group) == 0:#门清
            base_score = base_score * 2
        if owner.isJia:
            base_score = base_score * 2
            if owner.table.conf.bian_hu_jia() and "BIANHU" in owner.win_flags:
                owner.win_flags.remove("BIANHU")
                if "JIAHU" not in owner.win_flags:
                    owner.win_flags.append("JIAHU")
        # 删除普通胡显示边胡
        if not owner.isJia and "BIANHU" in owner.win_flags:
            owner.win_flags.remove("BIANHU")
        if trigger_player.seat == owner.table.dealer_seat:
            base_score = base_score * 2
        if owner.table.conf.is_fan_hu('PIAOHU') and "PIAOHU" in owner.win_flags:
            base_score = base_score * 4
        # 不加下面这行会不会崩溃？
        all_close_door = False
        if owner.table.chairs > 2:
            all_close_door = True
            for k, v in owner.table.seat_dict.items():
                if k != owner.seat and v.is_open_door():
                    all_close_door = False
            if all_close_door:
                owner.win_flags.append('SJMQ')
                base_score = base_score * 2
        #if len(owner.cards_ready_hand) == 1 and
        #base_score += (owner.kong_exposed_cnt + owner.kong_pong_cnt) * SCORE_BASE# + owner.kong_concealed_cnt * 2 * SCORE_BASE
        if owner.table.conf.pao_score_self():
            calculate_final_score(trigger_player, owner, base_score)
        if owner.table.conf.pao_score_pay_all():
            b_score = 0
            for k,v in owner.table.seat_dict.items():
                if k == owner.seat:
                    continue
                b_score += self.calc_score(v, owner, all_close_door)
            calculate_final_score(trigger_player, owner, b_score)
        if owner.table.conf.pao_score_all_pay():
            for k,v in owner.table.seat_dict.items():
                if k == owner.seat:
                    continue
                pay_score = self.calc_score(v,owner,all_close_door)
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
            
        owner.table.logger.info("player {0} win {1} type {2}".format(owner.seat, owner.win_card, owner.win_type))
        owner.table.machine.trigger(EndState())

    def calc_score(self,player, owner, all_close_door):
        base_score = SCORE_BASE
        if player.seat == player.table.dealer_seat:
            base_score *= 2
        if len(player.cards_group) == 0:
            base_score *= 2
        if owner.isJia:
            base_score *= 2
        if owner.seat == player.table.dealer_seat:
            base_score *= 2
        if owner.table.conf.is_fan_hu('PIAOHU') and "PIAOHU" in owner.win_flags:
            base_score = base_score * 4
        if all_close_door:
            base_score = base_score * 2
        if player.seat == player.table.active_seat:#点炮者加倍
            base_score *= 2
        return base_score

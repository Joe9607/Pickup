# coding: utf-8
from copy import copy

import random
from protocol import game_pb2
from protocol.commands import *
from protocol.serialize import send
from rules.define import *
from state.player_state.pause import PauseState
from behavior_tree.forest import is_ready_hand
from logic.tfs_algorithm import ZHONG


def discard(player, proto):
    card = proto.card.card
    if player.has_win_cards:
        # 胡牌不能再更换手牌
        if card != player.draw_card:
            proto = game_pb2.SynchroniseCardsResponse()
            for i in player.cards_in_hand:
                c = proto.card.add()
                c.card = i
            send(SYNCHRONISE_CARDS, proto, player.session)
            player.table.logger.warn("player {0} has already played,can not discard {1} in hand".format(player.seat, card))
            return
    if card not in player.cards_in_hand:
        # 出不存在的牌的时候同步手牌
        proto = game_pb2.SynchroniseCardsResponse()
        for i in player.cards_in_hand:
            c = proto.card.add()
            c.card = i
        send(SYNCHRONISE_CARDS, proto, player.session)
        player.table.logger.warn("player {0} discard {1} not exist in hand".format(player.seat, card))
        return
    player.table.replay["procedure"].append({"discard": [player.seat, card]})
    # 当玩家处于自摸提示状态下直接出牌
    # if player.state == "PromptState" and player.machine.last_state.name == "DrawState":
    if player.state == "PromptDrawState":
        player.del_prompt()
        player.table.clear_prompt()
        player.machine.next_state()
        proto_re = game_pb2.CommonNotify()
        proto_re.messageId = PLAYER_MSG_RECONNECT
        send(NOTIFY_MSG, proto_re, player.session)
        player.table.logger.fatal("{0} client send discard event without pass".format(player.uuid))

    # 将出牌玩家至于当前玩家
    player.table.discard_seat = player.seat
    player.table.last_oper_seat = player.seat       # 最后操作玩家
    if player.last_gang_card != 0:
        player.gang_pao_card = player.last_gang_card
    else:
        player.gang_pao_card = 0
    player.last_gang_card = 0
    player.cards_in_hand.remove(card)
    player.cards_discard.append(card)
    player.table.logger.info("player {0} discard {1}".format(player.seat, card))
    player.table.active_card = card
    player.miss_win_cards = []
    player.draw_card = 0

    proto = game_pb2.DiscardResponse()
    proto.card.card = card
    proto.player = player.uuid

    player.table.reset_proto(DISCARD)
    for i in player.table.player_dict.values():
        if i.uuid == player.uuid:
            continue
        i.proto.p = copy(proto)
        i.machine.cur_state.execute(i, "other_discard")
        i.proto.send()
    #player.ready_hand()
    player.table.step += 1
    # player.table.check_bao_change()
    if player.table.player_prompts:
        player.machine.trigger(PauseState())
    else:
        player.machine.next_state()


def other_discard(player):
    from rules.player_rules.manager import PlayerRulesManager
    PlayerRulesManager().condition(player, PLAYER_RULE_DISCARD)


def other_kong(player):
    from rules.player_rules.manager import PlayerRulesManager
    PlayerRulesManager().condition(player, PLAYER_RULE_KONG)


def action(player, proto):
    player.table.logger.debug(("when player do action", "prompts", player.table.player_prompts, "proto.action_id", proto.action_id))
    state = player.state
    if proto.action_id:
        # 判断是否在提示列表中
        if proto.action_id in player.action_dict.keys():
            # 判断是否在提示列表中
            player.table.logger.info("player {0} do {1} action {2} {3} {4} {5}".format(
                player.seat, proto.action_id, player.action_dict[proto.action_id], PLAYER_ACTION_TYPE_WIN_DISCARD, PLAYER_ACTION_TYPE_WIN_DRAW, player.action_dict[proto.action_id]["prompt"], player.table.win_seat_prompt))
            if player.seat in player.table.win_seat_prompt and player.action_dict[proto.action_id]["prompt"]\
                    in [PLAYER_ACTION_TYPE_WIN_DISCARD, PLAYER_ACTION_TYPE_WIN_DRAW]:

                player.table.win_seat_action.append(player.seat)
                
            player.action(proto.action_id)
        else:
            proto_re = game_pb2.CommonNotify()
            proto_re.messageId = PLAYER_MSG_RECONNECT
            send(NOTIFY_MSG, proto_re, player.session)
            player.table.logger.warn("player {0} do {1} not illegal".format(player.seat, proto.action_id))
            return
    else:
        player.table.logger.info("player {0} pass".format(player.seat))
        # 只要点过则未更换手牌之前不能胡任何牌, 如果提示操作里面没有胡则不清除胡牌提示
        #if PLAYER_ACTION_TYPE_WIN_DRAW <= max([i["prompt"] for i in player.action_dict.values()]):
            #player.cards_ready_hand = []
        player.del_prompt()
        if player.seat in player.table.win_seat_prompt:
            player.table.win_seat_prompt.remove(player.seat)
        # from state.player_state.wait import WaitState
        # 海底捞月特殊
        if player.table.state != "HaiDiState":
            # 杠之后有上听提示但是选择过，这里不要走next_state会在is_all_players_do_action走，
            # 也不能像自摸点过直接清除提示，因为之后的抓牌可能有新的提示，如果清理则又出现问题
            if state !="PromptTingKongState":
                player.machine.next_state()

    if state == 'PromptDrawState' and not proto.action_id and player.table.state != "HaiDiState" :
    # if player.state == "DiscardState":
    #     玩家处于自摸点过出牌状态
        player.table.clear_prompt()
    else:
        # 玩家处于其他玩家出牌提示状态
        player.table.player_actions.append(player.uuid)
        # 将低优先级的玩家直接过掉
        for player_id in player.table.player_prompts:
            if player_id == player.uuid:
                continue
            p = player.table.player_dict[player_id]
            # 只有在其他玩家没做出选择才可以直接pass， 但是不能重复pass
            if p.highest_prompt_weight() < player.action_weight and p.action_id == 0 and \
                            p.uuid not in player.table.player_actions:
                player.table.logger.info("player {0} auto pass".format(p.seat))
                p.del_prompt()
                if p.table.state != "HaiDiState":
                    p.machine.next_state()
                player.table.player_actions.append(p.uuid)
            next_seat = player.next_seat
            if player.action_weight == PLAYER_ACTION_TYPE_WIN_DISCARD and p.uuid not in player.table.player_actions:
                # print player.table.discard_seat
                count = 0
                while next_seat != player.table.discard_seat:
                    next_p = player.table.seat_dict[next_seat]
                    if next_p.highest_prompt_weight() == PLAYER_ACTION_TYPE_WIN_DISCARD:
                        next_p.del_prompt()
                        if next_p.uuid not in player.table.player_actions:
                            player.table.player_actions.append(next_p.uuid)
                    next_seat = next_p.next_seat
                    count += 1
                    if count >= 10:
                        break
        # 单独为海底捞月添加
        if player.action_weight == PLAYER_ACTION_TYPE_WIN_DRAW and len(player.table.player_prompts)>1:
            def seat_order(seat):
                return (seat - player.table.seat_dict[player.table.haidi_pre_seat].next_seat + player.table.conf.chairs) % player.table.conf.chairs

            for p in player.table.seat_dict.values():
                if p.uuid not in player.table.player_prompts:
                    continue
                if p.uuid in player.table.player_actions:
                    continue
                if seat_order(p.seat) > seat_order(player.seat):
                    p.del_prompt()
                    # p.machine.next_state()
                    player.table.player_actions.append(p.uuid)
        if len(player.table.player_actions) != len(player.table.player_prompts):
            return
        player.table.is_all_players_do_action()


def calculate_final_score(dest, src, score):
    #print 'score change, dest: ', dest.seat, ",src:", src.seat, ", score:", score
    if dest.table.conf.max_double and score > dest.table.conf.max_double:
        score = dest.table.conf.max_double
    dest.score -= score
    src.score += score


def kg(player):
    dice_1 = random.randint(1, 6)
    dice_2 = random.randint(1, 6)
    proto = game_pb2.KGResponse()
    proto.player = player.uuid
    proto.dice.dice1 = dice_1
    proto.dice.dice2 = dice_2

    log = {
        "dice_1": dice_1,
        "dice_2": dice_2,
        "player": player.seat,
        "card": [],
    }

    i = 0
    while i < 2:
        i += 1
        try:
            card = player.table.cards_on_desk.pop()
            if not player.table.cards_on_desk:
                player.table.haidi_card = card
        except IndexError:
            card = player.table.haidi_card
        body = proto.cards.add()
        body.card = card
        log["card"].append(card)
    for i in player.table.player_dict.values():
        send(KG, proto, i.session)
    player.table.logger.info(log)
    player.table.cards_kg = log["card"]
    player.cards_discard.extend(log["card"])


def try_kong(player, cards):
    if ZHONG in cards:#红中不允许杠
        return False
    if player.cards_in_hand.count(cards[0]) < len(cards):
        return False

    flag = False
    #player.pair258 = player.table.conf.is_pair258()

    for e in cards:
        player.cards_in_hand.remove(e)
    player.cards_group.extend(cards)
    if len(cards) == 3:
        player.cards_group.append(cards[0])

    if is_ready_hand(player).keys():
        flag = True

    player.cards_in_hand.extend(cards)
    for e in cards:
        player.cards_group.remove(e)
    if len(cards) == 3:
        player.cards_group.remove(cards[0])

    #player.pair258 = False

    return flag


def try_bz(player, cards):
    if ZHONG in cards:#红中不允许杠
        return False
    if player.cards_in_hand.count(cards[0]) < len(cards):
        return False

    flag = False
    if player.frozen:
       # player.pair258 = player.table.conf.is_pair258()
        for e in cards:
            player.cards_in_hand.remove(e)
        player.cards_group.extend(cards)
        if len(cards) == 3:
            player.cards_group.append(cards[0])

        if is_ready_hand(player).keys():
            flag = True

        player.cards_in_hand.extend(cards)
        for e in cards:
            player.cards_group.remove(e)
        if len(cards) == 3:
            player.cards_group.remove(cards[0])
        #player.pair258 = False
    else:
        flag = True

    return flag

def draw_after_animation(player):
    from state.player_state.draw import DrawState
    player.machine.trigger(DrawState())
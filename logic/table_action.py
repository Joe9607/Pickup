# coding: utf-8
from logic.tfs_algorithm import ZHONG
from protocol import game_pb2
from protocol.commands import NIAO
from protocol.serialize import send
from rules.define import TABLE_WIN_TYPE_DISCARD_ONE, TABLE_WIN_TYPE_DISCARD_MORE, TABLE_WIN_TYPE_DISCARD_DRAW,TABLE_WIN_TYPE_DISCARD_GSP
from state.table_state.step import StepState
from state.table_state.end import EndState
from logic.player_action import calculate_final_score


def step(table):
    table.machine.trigger(StepState())


def prompt_deal(table):
    for player in table.player_dict.values():
        if player.state != "WaitState":
            return
    table.machine.trigger(StepState())


def end(table):
    if not table.all_prompt_list and table.win_type:
        table.machine.trigger(EndState())


def draw_niao_normal(table):
    proto = game_pb2.DrawNiaoResponse()
    i = 0
    while i < table.conf.niao_num:
        i += 1
        try:
            card = table.cards_on_desk.pop()
        except IndexError:
            break
        table.draw_niao_list.append(card)

        if table.win_type == TABLE_WIN_TYPE_DISCARD_ONE:
            winner, loser = table.winner_list[0], table.loser_list[0]
            pos = (card % table.chairs + winner - 1) % table.chairs
            body = proto.niao.add()
            if pos in (loser, winner) or card == ZHONG:
                if pos == winner or card == ZHONG:
                    body.seat = winner
                    table.seat_dict[winner].cards_draw_niao.append(card)
                else:
                    body.seat = loser
                    table.seat_dict[loser].cards_draw_niao.append(card)

                table.seat_dict[winner].score += 1
                table.seat_dict[winner].total += 1
                table.seat_dict[loser].score -= 1
                table.seat_dict[loser].total -= 1
            else:
                body.seat = -1
            body.card.card = card

        # 对于一炮多响的情况
        if table.win_type == TABLE_WIN_TYPE_DISCARD_MORE:
            winner, loser = table.winner_list, table.loser_list[0]

            zhong_cnt = 0
            for seat in winner:
                pos = (card % table.chairs + seat - 1) % table.chairs

                if pos in (loser, seat) or card == ZHONG:
                    zhong_cnt += 1
                    body = proto.niao.add()
                    if pos == seat or card == ZHONG:
                        body.seat = seat
                        table.seat_dict[seat].cards_draw_niao.append(card)
                    else:
                        body.seat = loser
                        table.seat_dict[loser].cards_draw_niao.append(card)
                    table.seat_dict[seat].score += 1
                    table.seat_dict[seat].total += 1
                    table.seat_dict[loser].score -= 1
                    table.seat_dict[loser].total -= 1

                    body.card.card = card

            # 如果没人中鸟则加上一次
            if not zhong_cnt:
                body = proto.niao.add()
                body.seat = -1
                body.card.card = card

        if table.win_type == TABLE_WIN_TYPE_DISCARD_DRAW:
            winner, loser = table.winner_list[0], table.loser_list
            body = proto.niao.add()
            pos = (card % table.chairs + winner - 1) % table.chairs
            if pos == winner or card == ZHONG:
                body.seat = winner
                table.seat_dict[winner].score += 3
                table.seat_dict[winner].total += 3
                table.seat_dict[winner].cards_draw_niao.append(card)
                for seat in loser:
                    table.seat_dict[seat].score -= 1
                    table.seat_dict[seat].total -= 1
            else:
                body.seat = pos
                table.seat_dict[winner].score += 1
                table.seat_dict[winner].total += 1
                table.seat_dict[pos].score -= 1
                table.seat_dict[pos].total -= 1
                table.seat_dict[pos].cards_draw_niao.append(card)
            body.card.card = card

    for player in table.player_dict.values():
        send(NIAO, proto, player.session)


def draw_niao_hard(table):
    # 只中159其他不中
    proto = game_pb2.DrawNiaoResponse()
    i = 0
    winner, loser = table.winner_list[0], table.loser_list[0]
    niao_score = -1
    #print 'wintype:', table.win_type
    if table.win_type == TABLE_WIN_TYPE_DISCARD_ONE or table.win_type == TABLE_WIN_TYPE_DISCARD_GSP:
        niao_score = table.seat_dict[winner].score
    elif table.win_type == TABLE_WIN_TYPE_DISCARD_DRAW:
        niao_score = table.seat_dict[winner].score / 3
    draw_zha = []
    rest_cards_len = len(table.cards_on_desk)
    last_draw_player = table.seat_dict[table.last_draw]
    last_draw_card = last_draw_player.draw_card
    niao_num1 = table.conf.niao_num
    #print 'rest,',rest_cards_len,'niao num,',niao_num1,',i:',i
    if rest_cards_len < niao_num1:
        niao_num1 = 1
        if rest_cards_len == 0:
            table.cards_on_desk.append(last_draw_card)
    while i < niao_num1:
        i += 1
        try:
            card = table.cards_on_desk.pop()
        except IndexError:
            break
        table.draw_niao_list.append(card)
        cardVal = (card & 0x0F) - 1
        if card == ZHONG:
            cardVal = 0
        if table.win_type == TABLE_WIN_TYPE_DISCARD_ONE or table.win_type == TABLE_WIN_TYPE_DISCARD_GSP:
            winner, loser = table.winner_list[0], table.loser_list[0]
            body = proto.niao.add()
            targetIdx = (cardVal + winner) % 4
            table.seat_dict[targetIdx].cards_draw_niao.append(card)
            niao_num = len(table.seat_dict[targetIdx].cards_draw_niao)
            if targetIdx == winner or targetIdx == loser:
                draw_zha.append(loser)
                body.seat = targetIdx
                calculate_final_score(table.seat_dict[loser], table.seat_dict[winner],
                                      niao_score * (2 ** (len(draw_zha) - 1)))
            else:
                body.seat = targetIdx
            body.card.card = card
        if table.win_type == TABLE_WIN_TYPE_DISCARD_DRAW:
            winner, loser = table.winner_list[0], table.loser_list
            body = proto.niao.add()
            targetIdx = (cardVal + winner) % 4
            table.seat_dict[targetIdx].cards_draw_niao.append(card)
            niao_num = len(table.seat_dict[targetIdx].cards_draw_niao)
            if targetIdx == winner:
                body.seat = winner
                for seat in loser:
                    if seat in draw_zha:
                        calculate_final_score(table.seat_dict[seat], table.seat_dict[winner],
                                              niao_score * 2)
                    else:
                        calculate_final_score(table.seat_dict[seat], table.seat_dict[winner],
                                              niao_score)
                    draw_zha.append(seat)
            else:
                body.seat = targetIdx
                if targetIdx in draw_zha:
                    calculate_final_score(table.seat_dict[targetIdx], table.seat_dict[winner],
                                          niao_score * 2)
                else:
                    calculate_final_score(table.seat_dict[targetIdx], table.seat_dict[winner],
                                          niao_score)
                draw_zha.append(targetIdx)
            body.card.card = card

    for player in table.player_dict.values():
        send(NIAO, proto, player.session)


def draw_niao_159(table):
    # assert table.win_type == TABLE_WIN_TYPE_DISCARD_DRAW
    niao_cnt = 0

    proto = game_pb2.DrawNiaoResponse()
    i = 0
    while i < 2:
        i += 1
        try:
            card = table.cards_on_desk.pop()
        except IndexError:
            break
        table.draw_niao_list.append(card)

        for seat in table.winner_list:
            table.seat_dict[seat].cards_draw_niao.append(card)

        body = proto.niao.add()
        body.card.card = card
        if card == ZHONG or card % 4 == 1:
            niao_cnt += 1
            body.seat = table.winner_list[0]
        else:
            body.seat = -1

    niao_score = pow(2, niao_cnt + 1) - 2

    if niao_score > 0:
        if table.win_type == TABLE_WIN_TYPE_DISCARD_DRAW:
            winner, loser = table.winner_list[0], table.loser_list
            table.seat_dict[winner].score += 3 * niao_score
            table.seat_dict[winner].total += 3 * niao_score
            for seat in loser:
                table.seat_dict[seat].score -= niao_score
                table.seat_dict[seat].total -= niao_score

        if table.win_type == TABLE_WIN_TYPE_DISCARD_MORE:
            winner, loser = table.winner_list, table.loser_list[0]
            for seat in winner:
                table.seat_dict[seat].score += 3 * niao_score
                table.seat_dict[seat].total += 3 * niao_score
                table.seat_dict[loser].score -= 3 * niao_score
                table.seat_dict[loser].total -= 3 * niao_score

        if table.win_type == TABLE_WIN_TYPE_DISCARD_ONE:
            winner, loser = table.winner_list[0], table.loser_list[0]
            table.seat_dict[winner].score += 3 * niao_score
            table.seat_dict[winner].total += 3 * niao_score
            table.seat_dict[loser].score -= 3 * niao_score
            table.seat_dict[loser].total -= 3 * niao_score

    for player in table.player_dict.values():
        send(NIAO, proto, player.session)


def draw_niao_all(table):
    # assert table.win_type == TABLE_WIN_TYPE_DISCARD_DRAW

    proto = game_pb2.DrawNiaoResponse()
    i = 0
    while i < 1:
        i += 1
        try:
            card = table.cards_on_desk.pop()
        except IndexError:
            break
        table.draw_niao_list.append(card)
        if card == ZHONG:
            score = 1
        else:
            score = card % 16
        for seat in table.winner_list:
            table.seat_dict[seat].cards_draw_niao.append(card)
        body = proto.niao.add()
        body.card.card = card
        body.seat = table.winner_list[0]

        if table.win_type == TABLE_WIN_TYPE_DISCARD_DRAW:
            winner, loser = table.winner_list[0], table.loser_list
            table.seat_dict[winner].score += 3 * score
            table.seat_dict[winner].total += 3 * score
            for seat in loser:
                table.seat_dict[seat].score -= score
                table.seat_dict[seat].total -= score

        if table.win_type == TABLE_WIN_TYPE_DISCARD_ONE:
            winner, loser = table.winner_list[0], table.loser_list[0]
            table.seat_dict[winner].score += 3 * score
            table.seat_dict[winner].total += 3 * score
            table.seat_dict[loser].score -= 3 * score
            table.seat_dict[loser].total -= 3 * score

    for player in table.player_dict.values():
        send(NIAO, proto, player.session)

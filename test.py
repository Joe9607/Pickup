# coding: utf-8

from protocol import game_pb2


def test():
    proto = game_pb2.LoadBalanceWebResponse()
    unit = proto.unit.add()
    unit.room_id = 123456
    unit.room_status = 0
    for player in ["test1"]:
        unit.player.append(player)
    proto_string = proto.SerializeToString()
    proto = game_pb2.LoadBalanceWebResponse()
    proto.ParseFromString(proto_string)
    for unit in proto.unit:
        print unit.room_id, unit.room_status
        for player in unit.player:
            print player


stack = []


def push_stack(card_group):
    stack.append(card_group)


def roll_back(tiles):
    card_group = stack.pop()
    for i in range(card_group.count(ZHONG)):
        card_group.remove(ZHONG)
    tiles.extend(card_group)
    tiles.sort()


def try_sequence(card, tiles):
    if card + 1 in tiles and card + 2 in tiles:
        tiles.remove(card)
        tiles.remove(card + 1)
        tiles.remove(card + 2)
        push_stack([card, card + 1, card + 2])
        return True
    else:
        return False


def try_triplets(card, tiles):
    if tiles.count(card) == 3:
        tiles.remove(card)
        tiles.remove(card)
        tiles.remove(card)
        push_stack([card, card, card])
        return True
    else:
        return False


def try_pair(card, tiles, param):
    if param["pair_count"] == 1:
        return False
    if tiles.count(card) == 2:
        tiles.remove(card)
        tiles.remove(card)
        push_stack([card, card])
        param["pair_count"] = 1
        return True
    else:
        return False


def try_zhong_1_triplets(card, tiles, param):
    if param["zhong_count"] >= 1 and tiles.count(card) == 2:
        tiles.remove(card)
        tiles.remove(card)
        push_stack([card, card, ZHONG])
        param["zhong_count"] -= 1
        return True
    else:
        return False


def try_zhong_2_triplets(card, tiles, param):
    if param["zhong_count"] >= 2 and tiles.count(card) == 1:
        tiles.remove(card)
        push_stack([card, ZHONG, ZHONG])
        param["zhong_count"] -= 2
        return True
    else:
        return False


def try_zhong_1_sequence(card, tiles, param):
    if param["zhong_count"] < 1:
        return False
    if card + 1 in tiles:
        tiles.remove(card)
        tiles.remove(card + 1)
        push_stack([card, card + 1, ZHONG])
        param["zhong_count"] -= 1
        return True
    if card + 2 in tiles:
        tiles.remove(card)
        tiles.remove(card + 2)
        push_stack([card, card + 2, ZHONG])
        param["zhong_count"] -= 1
        return True
    else:
        return False


def try_zhong_1_pair(card, tiles, param):
    if param["pair_count"] == 1:
        return False
    if param["zhong_count"] < 1:
        return False
    param["zhong_count"] -= 1
    param["pair_count"] = 1
    tiles.remove(card)
    push_stack([card, ZHONG])
    return True


def try_zhong_2_pair(param):
    if param["pair_count"] == 1:
        return False
    if param["zhong_count"] < 2:
        return False
    param["zhong_count"] -= 2
    param["pair_count"] = 1
    push_stack([ZHONG, ZHONG])
    return True


def try_win(cards, param):
    if len(cards) == 0 and param["pair_count"] == 1:
        return True

    if len(cards) == 0 and param["pair_count"] == 0:
        return try_zhong_2_pair(param)

    active_card = cards[0]
    if try_pair(active_card, cards, param):
        if not try_win(cards, param):
            roll_back(cards)
            param["pair_count"] = 0
        else:
            return True

    if try_sequence(active_card, cards):
        if not try_win(cards, param):
            roll_back(cards)
        else:
            return True

    if try_triplets(active_card, cards):
        if not try_win(cards, param):
            roll_back(cards)
        else:
            return True

    if try_zhong_1_pair(active_card, cards, param):
        if not try_win(cards, param):
            roll_back(cards)
            param["pair_count"] = 0
            param["zhong_count"] += 1
        else:
            return True

    if try_zhong_1_sequence(active_card, cards, param):
        if not try_win(cards, param):
            roll_back(cards)
            param["zhong_count"] += 1
        else:
            return True

    if try_zhong_1_triplets(active_card, cards, param):
        if not try_win(cards, param):
            roll_back(cards)
            param["zhong_count"] += 1
        else:
            return True

    if try_zhong_2_triplets(active_card, cards, param):
        if not try_win(cards, param):
            roll_back(cards)
            param["zhong_count"] += 2
        else:
            return True
    return False


ZHONG = 0x10


def test_win():
    cards = [
        # 三个红中
        [ZHONG, ZHONG, ZHONG, 0x11, 0x12, 0x13, 0x14, 0x14, 0x15, 0x15, 0x15, 0x15, 0x16, 0x17],
        [ZHONG, 0x11, ZHONG, 0x21, 0x21, ZHONG, 0x32, 0x33, 0x14, 0x15, 0x16, 0x15, 0x16, 0x17],
        [0x11, 0x11, 0x22, 0x23, ZHONG, ZHONG, ZHONG, 0x17, 0x32, 0x32, 0x32, 0x23, 0x23, 0x23],
        [ZHONG, ZHONG, ZHONG, 0x12, 0x13, 0x32, 0x33, 0x34, 0x14, 0x15, 0x16, 0x15, 0x16, 0x17],
        # 两个红中
        [ZHONG, ZHONG, 0x12, 0x13, 0x14, 0x32, 0x33, 0x34, 0x14, 0x15, 0x16, 0x15, 0x16, 0x17],
        [ZHONG, 0x32, 0x33, ZHONG, 0x12, 0x13, 0x14, 0x14, 0x14, 0x15, 0x16, 0x15, 0x16, 0x17],
        [ZHONG, ZHONG, 0x33, 0x11, 0x12, 0x13, 0x14, 0x14, 0x14, 0x15, 0x15, 0x15, 0x16, 0x17],
        # 一个红中
        [ZHONG, 0x33, 0x11, 0x12, 0x13, 0x14, 0x14, 0x14, 0x15, 0x15, 0x15, 0x16, 0x17, 0x15],
        [0x33, 0x33, ZHONG, 0x12, 0x13, 0x14, 0x14, 0x14, 0x15, 0x15, 0x15, 0x16, 0x17, 0x15],
        [0x10, 0x17, 0x17, 0x18, 0x19, 0x19, 0x25, 0x26, 0x27, 0x32, 0x32],
        [35, 22, 19, 34, 22, 36, 21, 16, 18, 21, 21],
        [0x32, 0x32, 0x32, 0x10, 0x35, 0x36, 0x39, 0x39],
        [ZHONG, 0x12, 0x13, 0x14, 0x21, 0x22, 0x35, 0x35, 0x35, 0x36, 0x37],
        [ZHONG, ZHONG, 0x15, 0x15, 0x15],
        [0x11, 0x12, 0x13, 0x14, 0x15, 0x16, 0x16, 0x17, 0x18, 0x18, 0x18, 0x18, 0x19, 0x19],
        [ZHONG, 0x12, 0x13, 0x14, 0x21, 0x22, 0x35, 0x35, 0x35, 0x36, 0x37],
        [ZHONG, ZHONG, 0x22, 0x23, 0x24, 0x26, 0x36, 0x37, 0x38, 0x38, 0x39],
        [ZHONG, ZHONG, 0x13, 0x24, 0x25, 0x26, 0x27, 0x27, 0x27, 0x38, 0x39],
        [16, 16, 51, 17, 18, 19, 20, 20, 20, 21, 21, 21, 22, 23],
        [16, 16, 17, 18, 19, 20, 20, 20, 21, 21, 21, 22, 23, 25],
        [ZHONG, 0x15, 0x17, 0x22, 0x22],
        [ZHONG, 0x11, 0x13, 0x14, 0x15, 0x16, 0x22, 0x22],
        [ZHONG, 0x11, 0x13, 0x14, ZHONG, 0x16, 0x22, 0x22],
        [0x13, 0x14, 0x15, 0x17, 0x17, 0x39, 0x39, 0x39],
        [ZHONG, 0x16, 0x17, 0x32, 0x32, 0x34, 0x35, 0x36],
        [ZHONG, ZHONG, ZHONG, 0x11, 0x11, 0x13, 0x14, 0x15, 0x16, 0x17, 0x18, 0x23, 0x24, 0x28],
        [ZHONG, ZHONG, 0x14, 0x14, 0x16, 0x17, 0x18, 0x38],
        [ZHONG, 0x17, 0x18, 0x19, 0x22, 0x23, 0x24, 0x26, 0x26, 0x27, 0x27],
        [ZHONG, ZHONG, ZHONG, 0x14, 0x16, 0x17, 0x17, 0x32, 0x32, 0x36, 0x36],
        [ZHONG, ZHONG, 0x11, 0x12, 0x13, 0x34, 0x34, 0x35, 0x36, 0x36, 0x37],
        [ZHONG, ZHONG, 0x15, 0x15, 0x23, 0x24, 0x22, 0x26, 0x26, 0x36, 0x37, 0x38, 0x39, 0x39],
        [ZHONG, 0x14, 0x14, 0x15, 0x16, 0x17, 0x22, 0x22, 0x22, 0x23, 0x23, 0x25, 0x26, 0x27],
        [ZHONG, 0x13, 0x13, 0x14, 0x15, 0x16, 0x17, 0x17, 0x26, 0x27, 0x28],
        [ZHONG, ZHONG, 0x15, 0x16, 0x17, 0x25, 0x27, 0x29, 0x36, 0x37, 0x38],
        [ZHONG, ZHONG, 0x15, 0x15, 0x16, 0x18, 0x19, 0x19, 0x25, 0x26, 0x27, 0x32, 0x33, 0x34],
    ]

    import time
    from copy import copy
    global stack

    for i in cards:
        st = time.time()
        cards = copy(i)
        cnt = i.count(ZHONG)
        for j in range(cnt):
            cards.remove(ZHONG)
        cards.sort()
        stack = []
        print i
        param = {"zhong_count": cnt, "pair_count": 0}
        if not try_win(cards, param):
            print "-->", i, cards
        else:
            print stack, param
        print("-" * 60, time.time() - st)


if __name__ == '__main__':
    # [16, 51, 17, 18, 19, 20, 20, 20, 21, 21, 21, 22, 23, 21]
    # [35, 22, 19, 34, 22, 36, 21, 16, 18, 21, 21]
    test_win()

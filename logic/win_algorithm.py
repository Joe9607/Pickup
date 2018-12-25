# coding: utf-8

from copy import copy

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
    ]
    for i in cards:
        # print(i)
        # win_algorithm(i)
        win_algorithm_new(i)
        # print("-" * 60)


def is_win(tiles):
    cards = sorted(tiles)
    pairs = []

    for i in set(cards):
        if cards.count(i) >= 2:
            pairs.extend([i] * 2)
    if not pairs:
        return False

    for i in set(pairs):
        cards_copy = copy(cards)
        cards_copy.remove(i)
        cards_copy.remove(i)
        if not cards_copy:
            return False

        triplets = []
        sequences = []

        j = 0
        size = len(cards_copy)
        while j < size:
            # print(i, j, cards_copy)
            c = cards_copy[j]
            if cards_copy.count(c) == 3:
                cards_copy.remove(c)
                cards_copy.remove(c)
                cards_copy.remove(c)
                triplets.extend([c] * 3)
                j = 0
                size -= 3
            elif j + 2 < size and c in cards_copy and c + 1 in cards_copy and c + 2 in cards_copy:
                sequences.extend([c, c + 1, c + 2])
                cards_copy.remove(c)
                cards_copy.remove(c + 1)
                cards_copy.remove(c + 2)
                j = 0
                size -= 3
            else:
                j += 1
            if not cards_copy:
                return True
    else:
        return False


def is_pair(tiles):
    if len(tiles) == 2 and tiles[0] == tiles[1]:
        return True
    else:
        return False


def is_sequence(tiles):
    if len(tiles) == 3 and tiles[0] == tiles[1] - 1 == tiles[2] - 2:
        return True
    else:
        return False


def is_triplet(tiles):
    if len(tiles) == 3 and tiles[0] == tiles[1] == tiles[2]:
        return True
    else:
        return False


def split_groups(tiles):
    cards_copy = sorted(tiles)
    pairs = []
    triplets = []
    sequences = []

    j = 0
    size = len(cards_copy)
    while j < size:
        c = cards_copy[j]
        if cards_copy.count(c) >= 3:
            cards_copy.remove(c)
            cards_copy.remove(c)
            cards_copy.remove(c)
            triplets.extend([c] * 3)
            j = 0
            size -= 3
        elif j + 2 < size and c in cards_copy and c + 1 in cards_copy and c + 2 in cards_copy:
            sequences.extend([c, c + 1, c + 2])
            cards_copy.remove(c)
            cards_copy.remove(c + 1)
            cards_copy.remove(c + 2)
            j = 0
            size -= 3
        elif cards_copy.count(c) == 2:
            cards_copy.remove(c)
            cards_copy.remove(c)
            pairs.extend([c] * 2)
            j = 0
            size -= 2
        else:
            j += 1

    return pairs, triplets, sequences, cards_copy


def insert(dest, src):
    if not src:
        return dest
    if not dest:
        dest = copy(src)
        return dest
    i = 0
    for i in dest:
        if i >= src[-1]:
            break
    index = i - len(dest)
    for i in src:
        dest.insert(index, i)
    return dest


def merge(group):
    # group = [[0, 1], [1, 2], [2, 3], [4, 5]]
    final_groups = []
    while len(group) > 1:
        if group[0][-1] == group[1][0]:
            unit = copy(group[0])
            unit.append(group[1][1])
            group.insert(0, unit)
            group.remove(group[1])
            group.remove(group[1])
        else:
            final_groups.append(group[0])
            group.remove(group[0])
    if group:
        final_groups.append(group[0])
    return final_groups


def xor(a, b):
    _a, _b = bool(a), bool(b)
    return ((not _a) and _b) or (_a and (not _b))


def win_algorithm(tiles):
    # print tiles
    zhong_cnt = tiles.count(ZHONG)
    if zhong_cnt == 4:
        return tiles
    # if is_qixiaodui(tiles):
    #     return sorted(tiles)
    zhong_rest = copy(zhong_cnt)
    replace_cards = []
    cards = sorted(tiles)
    i = 0
    while i < zhong_cnt:
        cards.remove(ZHONG)
        i += 1
    unit = [cards[0]]
    groups = []

    for i in range(1, len(cards)):
        if cards[i - 1] == cards[i] or cards[i - 1] + 1 == cards[i]:
            unit.append(cards[i])
        else:
            groups.append(unit)
            unit = [cards[i]]
    if unit:
        groups.append(unit)

    merge_index = []
    for i in range(1, len(groups)):
        # 对跳牌的连牌进行合并，如果两组牌都不能自成对子顺子刻子或者胡牌则进行合并
        if groups[i - 1][-1] == groups[i][0] - 2:
            if is_pair(groups[i - 1]) or is_sequence(groups[i - 1]) or is_triplet(groups[i - 1]) or is_win(
                    groups[i - 1]):
                continue
            if is_pair(groups[i]) or is_sequence(groups[i]) or is_triplet(groups[i]) or is_win(groups[i]):
                continue
            merge_index.append([i - 1, i])

    if merge_index:
        merge_index = merge(merge_index)
        final_group = []
        for i in merge_index:
            unit = []
            # 算出接缝点和消耗的红中数
            for c in i[:-1]:
                replace_cards.append(groups[c][-1] + 1)
                zhong_rest -= 1
                unit.append(groups[c][-1] + 1)
            # 将分组合并
            for c in i:
                unit.extend(groups[c])
            final_group.append(unit)

        # 合并分组，保留剩下未合并的分组
        for i in merge_index:
            for c in i:
                groups[c] = []
        for i in groups:
            if i:
                final_group.append(i)
        groups = final_group

    wins = []
    wins_cnt = 0
    pairs = []
    triplets = []
    sequences = []
    left_1 = []
    left_2 = []

    for i in groups:
        if len(i) % 3 == 2 and is_win(i):
            wins.extend(i)
            wins_cnt += 1

        elif is_pair(i):
            pairs.extend(i)

        elif is_sequence(i):
            sequences.extend(i)

        elif is_triplet(i):
            triplets.extend(i)

        else:
            p, t, s, c = split_groups(i)
            if p:
                pairs.extend(p)
            if t:
                triplets.extend(t)
            if s:
                sequences.extend(s)
            if len(c) == 1:
                left_1.extend(c)
            # 存在剩余截断牌型
            else:
                left_2.extend(c)

    # print "left 1: ", left_1, zhong_rest
    while left_1:
        c = left_1[0]
        # print "1: ", c, left_1, zhong_rest
        if c + 2 in left_1:
            sequences.extend([c, ZHONG, c + 2])
            left_1.remove(c + 2)
        else:
            pairs.extend([c, ZHONG])
        left_1.remove(c)
        zhong_rest -= 1

    # print "left 2: ", left_2, zhong_rest
    while left_2:
        c = left_2[0]
        # print "2: ", c, left_2, zhong_rest
        if left_2.count(c) == 2:
            pairs.extend([c] * 2)
            left_2.remove(c)

        elif c + 1 in left_2:
            sequences.extend([c, c + 1, ZHONG])
            left_2.remove(c + 1)
            zhong_rest -= 1
        elif c + 2 in left_2:
            sequences.extend([c, ZHONG, c + 2])
            left_2.remove(c + 2)
            zhong_rest -= 1
        else:
            pairs.extend([c, ZHONG])
            zhong_rest -= 1
        left_2.remove(c)

    flag = False
    if wins_cnt > 1:
        wins.append(ZHONG)
        zhong_rest -= 1
    # 有一个对子异或者有胡牌则表示可以胡牌
    # if len(pairs) != len(wins) and len(pairs) in (0, 2):
    if xor(pairs, wins) and len(pairs) in (0, 2):
        flag = True
    # 没有对子并且没有胡牌但是有一对红中则也可以胡牌
    if len(pairs) == 0 and len(wins) == 0 and zhong_rest == 2:
        flag = True
        pairs = [ZHONG] * 2
        zhong_rest = 0
    # 有一个对子并且有胡牌并且剩余红中为一也可以胡牌
    if len(pairs) == 2 and len(wins) > 0 and zhong_rest == 1:
        flag = True
        pairs.append(ZHONG)
        zhong_rest = 0
    # 对子的多余数目等于红中的多余数目
    if len(pairs) > 2:
        pairs_rest = len(pairs) / 2
        if not wins:
            pairs_rest -= 1
        if zhong_rest == pairs_rest:
            flag = True
            pairs.extend([ZHONG] * zhong_rest)
            zhong_rest = 0
    if zhong_rest == 3:
        flag = True
        triplets.extend([ZHONG] * zhong_rest)
        zhong_rest = 0

    if zhong_rest == 0 and flag:
        win_cards = []
        win_cards = insert(win_cards, pairs)
        win_cards = insert(win_cards, sequences)
        win_cards = insert(win_cards, triplets)
        win_cards = insert(win_cards, wins)

        for i in replace_cards:
            index = win_cards.index(i)
            win_cards[index] = ZHONG

        if sorted(win_cards) == sorted(tiles):
            return win_cards
        else:
            return []
    else:
        return []


def is_qixiaodui(tiles):
    cards = sorted(tiles)
    zhong_cnt = cards.count(ZHONG)
    for i in range(zhong_cnt):
        cards.remove(ZHONG)
    pairs = []
    for i in set(cards):
        if cards.count(i) in (2, 3):
            cards.remove(i)
            cards.remove(i)
            pairs.append(i)
        if cards.count(i) == 4:
            cards.remove(i)
            cards.remove(i)
            pairs.append(i)
            pairs.append(i)
    if len(pairs) + zhong_cnt == 7:
        return sorted(tiles)
    else:
        return []


def is_ready_hand(tiles, is_zhong=True, is_qxd=True):
    cards_test = list(filter(lambda e: 0 < (e % 16) < 10, range(0x11, 0x3A)))
    zhong_cnt = tiles.count(ZHONG)
    if zhong_cnt == 4:
        return cards_test

    win_card_list = []
    for c in cards_test:
        cards = copy(tiles)
        cards.append(c)
        win_cards = win_algorithm(cards)
        if win_cards:
            win_card_list.append(c)
        if is_qxd and is_qixiaodui(cards):
            win_card_list.append(c)
        cards.remove(c)
    if is_zhong and win_card_list:
        win_card_list.append(ZHONG)
    # if win_card_list:
    #     print "win_card_list", win_card_list
    return win_card_list


def easy_win_algorithm(tiles):
    zhong_cnt = tiles.count(ZHONG)
    if zhong_cnt == 4:
        return tiles
    cards_replace = list(filter(lambda e: 0 < (e % 16) < 10, range(0x11, 0x3A)))
    win_cards = []

    def replace_zhong(cards):
        try:
            index = cards.index(ZHONG)
        except ValueError:
            if is_win(cards):
                win_cards.append(cards)
            return
        c = copy(cards)
        for i in cards_replace:
            c[index] = i
            replace_zhong(c)

    replace_zhong(tiles)
    # print len(win_cards)


def win_algorithm_new(tiles):
    tiles.sort()
    match = copy(tiles)
    #print len(match)
    for i in range(1, len(tiles)):
        k = tiles[i] - tiles[i-1] - 1
        while k > 0:
            k -= 1
            match.insert(match.index(tiles[i]), 0)
    #print tiles
    #print match


if __name__ == '__main__':
    # print is_ready_hand([ZHONG, 0x13, 0x13, 0x14, 0x15, 0x16, 0x17, 0x17, 0x27, 0x28])
    # win_algorithm_new([ZHONG, 0x13, 0x13, 0x14, 0x15, 0x16, 0x17, 0x17, 0x26, 0x27, 0x28])
    # win_algorithm_new([ZHONG, ZHONG, 0x15, 0x16, 0x17, 0x25, 0x27, 0x29, 0x36, 0x37, 0x38])
    test_win()

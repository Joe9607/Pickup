# coding: utf-8

CARD = {
    "spring": 0x1,              # 春
    "summer": 0x2,              # 夏
    "autumn": 0x3,              # 秋
    "winter": 0x4,              # 冬
    "plum": 0x5,                # 梅
    "orchid": 0x6,              # 兰
    "bamboo": 0x7,              # 竹
    "chrysanthemum": 0x40,       # 菊
    "joker": 0x41,               # 百搭
    "east": 0x42,               # 东风
    "south": 0x43,              # 南风
    "west": 0x44,               # 西风
    "north": 0x45,              # 北风
    "red": 0x10,                # 红中
    "green": 0x8,              # 发财
    "white": 0x9,              # 白板
    "character_1": 0x11,        # 一万
    "character_2": 0x12,        # 二万
    "character_3": 0x13,        # 三万
    "character_4": 0x14,        # 四万
    "character_5": 0x15,        # 五万
    "character_6": 0x16,        # 六万
    "character_7": 0x17,        # 七万
    "character_8": 0x18,        # 八万
    "character_9": 0x19,        # 九万
    "dot_1": 0x21,              # 一筒
    "dot_2": 0x22,              # 二筒
    "dot_3": 0x23,              # 三筒
    "dot_4": 0x24,              # 四筒
    "dot_5": 0x25,              # 五筒
    "dot_6": 0x26,              # 六筒
    "dot_7": 0x27,              # 七筒
    "dot_8": 0x28,              # 八筒
    "dot_9": 0x29,              # 九筒
    "bamboo_1": 0x31,           # 一条
    "bamboo_2": 0x32,           # 二条
    "bamboo_3": 0x33,           # 三条
    "bamboo_4": 0x34,           # 四条
    "bamboo_5": 0x35,           # 五条
    "bamboo_6": 0x36,           # 六条
    "bamboo_7": 0x37,           # 七条
    "bamboo_8": 0x38,           # 八条
    "bamboo_9": 0x39,           # 九条
}

CHARACTER = [CARD["character_{0}".format(i)] for i in range(1, 10)]             # 万牌
DOT = [CARD["dot_{0}".format(i)] for i in range(1, 10)]                         # 筒牌
BAMBOO = [CARD["bamboo_{0}".format(i)] for i in range(1, 10)]                   # 条牌
WIND = [CARD["east"], CARD["south"], CARD["west"], CARD["north"]]               # 风牌（东，西，南，北）
DRAGON = [CARD["red"], CARD["green"], CARD["white"]]                            # 箭牌 （红中，发财，白板）
FLOWER = [CARD["spring"], CARD["summer"], CARD["autumn"], CARD["winter"],       # 花牌（春，夏，秋，冬，梅，兰，竹，菊）
          CARD["plum"], CARD["orchid"], CARD["bamboo"], CARD["chrysanthemum"]]
ALL_19 = [CARD['character_9'], CARD['character_1'], CARD['dot_1'], CARD['dot_9'], CARD['bamboo_1'], CARD['bamboo_9']]

CARDS_TYPE = {
    0b000001: CHARACTER,    # 万
    0b000010: DOT,          # 筒
    0b000100: BAMBOO,       # 条
    0b001000: WIND,         # 风牌 东南西北
    0b010000: DRAGON,       # 箭牌 中发白
    0b100000: FLOWER,       # 花牌 春夏秋冬梅兰竹菊
}

NUMBER = CHARACTER + DOT + BAMBOO
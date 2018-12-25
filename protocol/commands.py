# coding: utf-8

""" 通用麻将命令 0x0001 ~ 0x0FFF """
ENTER_ROOM = 0x0001                   # 进入房间 原命令号（0x1005）
ENTER_ROOM_OTHER = 0x0002             # 其他玩家进入房间 原命令号（0x1015）
EXIT_ROOM = 0x0003                    # 退出房间 原命令号（0x1007）
DISMISS_ROOM = 0x0004                 # 解散房间 原命令号（0x1006）
SPONSOR_VOTE = 0x0005                 # 发起投票解散 原命令号（0x1009）
VOTE = 0x0007                         # 玩家选择投票 原命令号（0x1037）
ONLINE_STATUS = 0x0008                # 在线状态广播 原命令号（0x1016）
SPEAKER = 0x0009                      # 超级广播命令 原命令号（0x1002）
READY = 0x000A                        # 准备 原命令号（0x1012）
DEAL = 0x000B                         # 起手发牌 原命令号（0x2005）
DRAW = 0x000C                         # 摸牌 原命令号（0x1024）
DISCARD = 0x000D                      # 出牌 原命令号（0x1021）
SYNCHRONISE_CARDS = 0x000E            # 服务端主动同步手牌 原命令号（0x1011）
HEARTBEAT = 0x000F            		  # 服务端主动检测心跳
HAIDI = 0x0010                        # 海底捞月

""" 塔城 0x1000 ~ 0x101F """
RECONNECT = 0x1000                    # 玩家断线重连 原命令号（0x1014）
PROMPT = 0x1001                       # 操作提示 原命令号（0x2007）
ACTION = 0x1002                       # 玩家根据提示列表选择动作 原命令号（0x1022）
READY_HAND = 0x1003                   # 听牌提示 原命令号（0x1033）
NIAO = 0x1004                         # 抓鸟 原命令号（0x1026）
SETTLEMENT_FOR_ROUND = 0x1005         # 小结算 原命令号（0x2004）
SETTLEMENT_FOR_ROOM = 0x1006          # 大结算 原命令号（0x2006）
NOTIFY_MSG = 0x1007
SHOW_ANIMATION = 0x1008               # 显示宝之前的动画
# ILLEGAL = 0x1009               # 客户端非法
SHOW_LAST_CARD = 0x100A          # 显示最后一张牌(杠牌之后要抓的牌)

""" 长沙麻将 0x1020 ~ 0x103F """
KG = 0x1020                           # 开杠
HD_NOTICE = 0x1021                    # 通知海底
HD_SELECT = 0x1022                    # 玩家回复是否要海底
ACTION_CS = 0x1023                    # 玩家动作
FOLD = 0x1024                         # 小胡收牌
SETTLEMENT_FOR_ROUND_CS = 0x1025      # 小结算
SETTLEMENT_FOR_ROOM_CS = 0x1026       # 大结算
HD_BROADCAST = 0x1027                 # 广播海底牌
PROMPT_CS = 0x1028                    # 提示
FROZEN_CS = 0x1029                    # 表示已经开杠 只能摸牌打牌或者胡牌
DRAW_CS = 0x102A					  # 合并后的摸牌命令
DISCARD_CS = 0x102B					  # 合并后的出牌命令
DEAL_CS = 0x102C					  # 发牌

""" 卡五星 0x1040 ~ 0x105F """
PIAO_SELECTOR = 0x1040                # 广播选漂
PIAO = 0x1041                         # 玩家选漂
ACTION_K5X = 0x1042                   # 玩家动作
PROMPT_K5X = 0x1043                   # 卡五星提示
RECONNECT_K5X = 0x1044                # 卡五星重连
POINTS_MAP = 0x1045                   # 卡五星牌型番数对照
SETTLEMENT_FOR_ROUND_K5X = 0x1046     # 小结算
SETTLEMENT_FOR_ROOM_K5X = 0x1047      # 大结算
MAIMA = 0x1048                        # 买码
SYNC_KONG_SCORE = 0x1049              # 实时同步杠的分数

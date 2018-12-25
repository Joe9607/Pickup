# coding: utf-8

from copy import copy
import json
import time
from behavior_tree.base import *
from tornado.ioloop import IOLoop

from logic.player import Player
from logic.session_manager import SessionMgr
from protocol import game_pb2
from protocol.commands import *
from protocol.serialize import send
from rules.define import *
from settings import redis
from state.machine import Machine
from state.status import player_state_code_map
from state.table_state.ready import ReadyState
from utils.logger import Logger


class Table(object):
    def __init__(self, room_id, room_uuid, owner, kwargs):
        super(Table, self).__init__()
        self.room_id = room_id
        self.room_uuid = room_uuid
        self.owner = owner
        self.owner_info = None
        self.kwargs = str(kwargs)
        self.chairs = 4
        self.player_dict = {}
        self.seat_dict = {}
        self.machine = None
        self.state = None
        self.dismiss_state = False
        self.dismiss_sponsor = None
        self.dismiss_time = 0
        self.dismiss_flag = 1
        self.logger = Logger(room_id)
        self.request = None
        self.dealer_seat = -1   # 庄家座位
        self.active_seat = -1
        self.active_card = 0
        self.discard_seat = -1
        self.event = None
        self.cards_total = 0
        self.win_seat_prompt = []
        self.win_seat_action = []
        self.last_oper_seat = -1
        self.yao_card = -1
        self.bao_card_idx = 0

        self.player_prompts = []
        self.player_actions = []
        self.conf = None
        self.step = 0

        self.st = time.time()
        self.et = 0
        self.replay = {}
        self.cards_on_desk = []         # 桌上玩家能抓的剩余牌（最后一张牌是宝牌指定牌的前一张牌）
        self.dice_1 = 0
        self.dice_2 = 0
        # 胡牌类型：流局，自摸胡，点炮胡，一炮多响
        self.win_type = 0
        self.cur_round = 1
        self.draw_niao_list = []
        self.winner_list = []
        self.loser_list = []
        self.last_draw_seat = 0
        # 总局数
        self.total_round = 1
        # 当前圈
        self.cur_circle = 1
        # 预留牌(最后一张牌不让杠)
        self.reserved_cards = 1
        # 海底捞月前最后摸牌人座位号（类似点炮人的座位号,用于判断谁胡）
        self.haidi_pre_seat = -1
        # 播放动画计数器
        self.animation_count = 0
        # 第一个听牌人
        self.first_ting = -1
        # 播放动画定时器
        # self.animation_timer = None
        # 是否能吃牌
        self.can_chow = False
        self.disable_show = False
        # 最后一张牌用于杠摸牌
        self.last_card = 0
        # 杠摸牌在桌上牌的原来的号，用于第一次检测做交换
        self.kong_temp_index = 0
        # 流局之后底分翻倍,记录流局次数
        self.liuju_times = 0
        self.liuju = True
        self.logger.info("room created")

        # 六安麻将额外参数
        self.dice_bao = 0
        self.bao_appoint = 0    # 确定宝牌的指定牌
        self.bao_card = 0  # 宝牌（百搭牌）
        self.card_odd = []   # 桌面总共剩余下来的牌
        Machine(self)

    def dumps(self):
        data = {}
        for key, value in self.__dict__.items():
            if key in ("logger", "conf", "request", "animation_timer"):
                continue
            elif key == "player_dict":
                data[key] = value.keys()
            elif key == "seat_dict":
                data[key] = {k: v.uuid for k, v in value.items()}
            elif key == "machine":
                data[key] = [None, None]
                if value.cur_state:
                    data[key][1] = value.cur_state.name
                if value.last_state:
                    data[key][0] = value.last_state.name
            else:
                data[key] = value
                # print "table dumps", data
        redis.set("table:{0}".format(self.room_id), json.dumps(data))

    def delete(self):
        self.player_dict = {}
        self.seat_dict = {}
        redis.delete("table:{0}".format(self.room_id))

    def enter_room(self, player_id, info, session):
        if not self.owner_info and player_id == self.owner:
            self.owner_info = info
        proto = game_pb2.EnterRoomResponse()
        proto.room_id = self.room_id
        proto.owner = self.owner

        if len(self.player_dict.keys()) >= self.chairs:
            proto.code = 5002
            send(ENTER_ROOM, proto, session)
            if self.conf.is_aa():
                self.request.aa_refund(player_id, 0)
            self.logger.warn("room {0} is full, player {1} enter failed".format(self.room_id, player_id))
            return

        player = Player(player_id, info, session, self)
        from state.player_state.init import InitState
        player.machine.trigger(InitState())
        seat = -1
        for seat in range(self.chairs):
            if seat in self.seat_dict.keys():
                continue
            break
        player.seat = seat
        self.player_dict[player_id] = player
        self.seat_dict[seat] = player
        proto.code = 1
        proto.kwargs = self.kwargs
        proto.rest_cards = self.cards_total
        for k, v in self.seat_dict.items():
            p = proto.player.add()
            p.seat = k
            p.player = v.uuid
            p.info = v.info
            p.status = player_state_code_map[v.state]
            p.is_online = v.is_online
            p.total_score = v.total
        SessionMgr().register(player, session)

        send(ENTER_ROOM, proto, session)
        # print 'player cnt:', len(self.player_dict.keys())
        proto = game_pb2.EnterRoomOtherResponse()
        proto.code = 1
        proto.player = player_id
        player = self.player_dict[player_id]
        proto.info = player.info
        proto.seat = player.seat

        for i in self.player_dict.values():
            if i.uuid == player_id:
                continue
            send(ENTER_ROOM_OTHER, proto, i.session)
        player.dumps()
        self.dumps()
        self.request.enter_room(player_id)
        self.logger.info("player {0} enter room".format(player_id))
        if self.conf.is_aa():
            self.request.aa_cons(player_id)

    def dismiss_room(self, vote=True):
        # 如果是投票解散房间则进入大结算，否则直接推送房主解散命令
        def _dismiss():
            from state.table_state.settle_for_room import SettleForRoomState
            self.machine.trigger(SettleForRoomState())
            self.request.load_minus()

        if vote and self.state != "InitState":
            _dismiss()
        else:
            proto = game_pb2.DismissRoomResponse()
            proto.code = 1
            # 0-没开始解散 1-投票 2-游戏内解散
            vote_flag = 2
            if vote:
                vote_flag = 1
            else:
                if self.state == "InitState":
                    vote_flag = 0
            proto.flag = vote_flag
            for k, v in self.player_dict.items():
                send(DISMISS_ROOM, proto, v.session)

            if self.state != "InitState":
                self.dismiss_flag = 2
                _dismiss()

        self.logger.info("room {0} dismiss".format(self.room_id))
        from logic.table_manager import TableMgr
        self.request.dismiss_room(self)
        TableMgr().dismiss(self.room_id)
        for player in self.player_dict.values():
            try:
                player.session.close()
            except Exception:
                pass
            player.delete()

        self.delete()

    def check_bao_change(self):
        isChange = False
        while self.bao_card_idx < len(self.cards_on_desk):
            bao_cnt = 0
            for player in self.player_dict.values():
                bao_cnt += player.cards_discard.count(self.bao_card)
                bao_cnt += player.cards_group.count(self.bao_card)
            if bao_cnt >= 3:
                self.bao_card_idx += 1
                self.bao_card = self.cards_on_desk[self.bao_card_idx - 1]
                # print 'bao:',self.bao_card
                isChange = True
            else:
                break
        if isChange:
            self.broadcast_change_bao()
        return isChange

    def broadcast_change_bao(self):
        if not self.conf.allow_view_bao():
            return False
        # 第一次动画不让发
        if self.disable_show:
            self.disable_show = False
            return False
        proto = game_pb2.CommonNotify()
        proto.messageId = PLAYER_MSG_KANBAO
        if self.bao_card == 0:
            return
        proto.idata = (self.bao_card | (self.bao_card_idx << 8))
        proto.sdata = ''
        proto.seat = 0
        for player in self.player_dict.values():
            if player.isTing and player.can_look_bao:
                proto.seat = player.seat
                send(NOTIFY_MSG, proto, player.session)
        self.replay["procedure"].append({"bao": self.bao_card})

    def is_all_ready(self):
        if len(self.player_dict) != self.chairs:        # 凑齐4人开始游戏
            return
        for player in self.player_dict.values():
            if player.state != "ReadyState":
                return
        self.machine.trigger(ReadyState())
        if self.total_round == 1:
            self.request.load_plus()

    def is_all_players_do_action(self):
        self.dumps()
        self.logger.debug(("during player do actions", "prompts", self.player_prompts, "actions", self.player_actions))
        if len(self.player_actions) != len(self.player_prompts):
            return
        self.logger.debug(("after player do actions", "prompts", self.player_prompts, "actions", self.player_actions))
        # 没有提示
        if not self.player_prompts:
            self.seat_dict[self.active_seat].machine.next_state()
        self.clear_prompt()
        self.logger.debug(("after player do actions1", "prompts", self.player_prompts, "actions", self.player_actions))
        max_weight, max_weight_player = self.get_highest_weight_action_player()

        # 有提示但是都选择过
        if not max_weight:
            # 海底点过直接结束
            if self.state == "HaiDiState":
                from state.table_state.end import EndState
                self.machine.trigger(EndState())
            # 冲杠点过直接发牌
            # elif self.seat_dict[self.active_seat].had_check_kong:
            #     from state.player_state.draw import DrawState
            #     self.seat_dict[self.active_seat].machine.trigger(DrawState())
            else:
                self.seat_dict[self.active_seat].machine.next_state()
            return
        self.logger.debug(("after player do actions3", "prompts", self.player_prompts, "actions", self.player_actions))
        if max_weight in (PLAYER_ACTION_TYPE_WIN_DRAW, PLAYER_ACTION_TYPE_WIN_DISCARD):
            if max_weight == PLAYER_ACTION_TYPE_WIN_DRAW:
                # assert len(max_weight_player) == 1
                # 海底捞月
                if len(max_weight_player) > 1:
                    target = self.win_seat_action[0]
                    loser = self.haidi_pre_seat
                    if len(self.win_seat_action) > 1:
                        for i in self.win_seat_action:
                            # 当是最后的玩家直接剔除
                            if i == loser:
                                continue
                            t = (loser - i + self.conf.chairs) % self.conf.chairs
                            r = (loser - target + self.conf.chairs) % self.conf.chairs
                            if t > r:
                                target = i
                        self.win_seat_action[0] = target
                self.win_type = TABLE_WIN_TYPE_DISCARD_DRAW
            else:
                self.logger.fatal(("discard_win R U KIDDING ME?????????"))

        from rules.rules_map import rules_dict

        for player in max_weight_player:
            rule = rules_dict[player.action_rule]
            if player.action_rule in ("DiscardWinRule", "QGWinRule", "DrawWinRule"):
                if self.win_seat_action[0] == player.seat:
                    self.logger.debug(
                        ("procedure", "prompts", self.player_prompts, "actions", self.player_actions, "rules",
                         player.action_rule, "ref_cards", player.action_ref_cards))
                    self.replay["procedure"].append(
                        [{"action": {"rule": player.action_rule, "op_card": player.action_op_card,
                                     "ref_cards": player.action_ref_cards,
                                     "prompt": player.action_weight},
                          "seat": player.seat}])
                    rule.action(player)
            else:
                self.logger.debug(("procedure", "prompts", self.player_prompts, "actions", self.player_actions, "rules",
                                   player.action_rule, "ref_cards", player.action_ref_cards))
                self.replay["procedure"].append(
                    [{"action": {"rule": player.action_rule, "op_card": player.action_op_card,
                                 "ref_cards": player.action_ref_cards,
                                 "prompt": player.action_weight},
                      "seat": player.seat}])
                rule.action(player)
        self.clear_actions()
        self.dumps()
        self.logger.debug(("after player do actions2", "prompts", self.player_prompts, "actions", self.player_actions))
        # 如果有人胡牌
        if max_weight in (PLAYER_ACTION_TYPE_WIN_DRAW,):
            # win_seat_action清空，否则第二个人胡牌就GG
            self.win_seat_action = []
            # 新抓的牌置空否则胡完之后重连出错
            self.seat_dict[self.active_seat].draw_card = 0
            self.machine.cur_state.execute(self, "step")
            # from state.table_state.settle_for_card import SettleForCardState
            # self.machine.trigger(SettleForCardState())

    def clear_prompt(self):
        self.player_prompts = []
        for player in self.player_dict.values():
            player.del_prompt()

    def clear_actions(self):
        self.player_actions = []
        self.logger.debug("clear actions")
        for player in self.player_dict.values():
            player.del_action()

    def get_highest_weight_action_player(self):
        self.logger.debug(("get_highest_weight_action_player ", self.player_actions))
        max_weight = 0
        for player_id in self.player_actions:
            player = self.player_dict[player_id]
            weight = player.action_weight
            if weight > max_weight:
                max_weight = weight
        max_weight_player = []
        for player_id in self.player_actions:
            player = self.player_dict[player_id]
            if player.action_weight == max_weight:
                max_weight_player.append(player)
            else:
                if player.table.state != "HaiDiState":
                    player.machine.next_state()
        return max_weight, max_weight_player

    def reset_proto(self, cmd):
        for player in self.player_dict.values():
            player.proto.require()
            player.proto.c = cmd

    @property
    def cur_real_round(self):
        return self.total_round if self.conf.is_round else self.cur_circle

    def show_bao_blocking(self, player):
        self.animation_count += 1
        if self.animation_count == 1:
            # from state.player_state.animation import AnimationState
            # player.machine.trigger(AnimationState())
            # 播放动画发包先换宝
            self.check_bao_change()
            import random
            dice_1 = random.randint(1, 6)
            dice_2 = random.randint(1, 6)
            proto = game_pb2.ShowAnimationResponse()
            proto.dice.dice1 = dice_1
            proto.dice.dice2 = dice_2
            for every_player in self.player_dict.values():
                proto.bao_card.card = 0
                if self.conf.allow_view_bao() and every_player.seat == player.seat:
                    proto.bao_card.card = self.bao_card
                send(SHOW_ANIMATION, proto, every_player.session)
            # now = time.time()
            # self.animation_timer = IOLoop().instance().add_timeout(
            #         now + 5, self.draw_after_animation)

    def draw_after_animation(self):
        IOLoop.instance().remove_timeout(self.animation_timer)
        self.animation_timer = None
        active_player = self.seat_dict[self.active_seat]
        if active_player.state == "AnimationState":
            active_player.machine.cur_state.execute(active_player, "get_bao")

    def broadcast_all(self, message):
        """ 系统广播
        """
        proto = game_pb2.CommonNotify()
        proto.messageId = 4
        proto.sdata = message

        for player in self.player_dict.values():
            send(NOTIFY_MSG, proto, player.session)

    def change_kong_card(self, is_first=False):
        # 换杠牌，需要将杠牌显示出来，类似宝牌，第一次不能是19或者风
        if is_first:
            if self.is_wind_19(self.last_card):
                # 有可能是逻辑错误死循环先做预防最多41次循环
                if self.kong_temp_index > 41:
                    self.logger.fatal('table.kong_temp_index larger than 40')
                    return
                # 第一次是风或者19，将最后一张牌换一下再进行一次迭代
                self.kong_temp_index += 1
                self.cards_on_desk[0], self.cards_on_desk[self.kong_temp_index] = self.cards_on_desk[
                                                                                      self.kong_temp_index], \
                                                                                  self.cards_on_desk[0]
                self.last_card = self.cards_on_desk[0]
                self.change_kong_card(True)
                return
        self.last_card = self.cards_on_desk[0]
        self.replay["procedure"].append({"bao": self.last_card})
        self.send_last_card()

    def is_wind_19(self, card):
        card_except = [ZHONG, WEST, EAST, SOUTH, NORTH, FA, BAI]
        if card in card_except:
            return True
        elif card & 0xf == 1 or card & 0xf == 9:
            return True

    def send_last_card(self):
        # 将最后一张牌发送给客户端,按照宝牌发送
        # proto_slc = game_pb2.ShowLastCardResponse()
        # proto_slc.last_card.card = self.last_card
        # for player in self.player_dict.values():
        #     send(SHOW_LAST_CARD,proto_slc,player.session)
        if 0 == self.last_card:
            return
        proto = game_pb2.CommonNotify()
        proto.messageId = PLAYER_MSG_KANBAO
        proto.idata = self.last_card
        proto.sdata = ''
        proto.seat = 0
        for player in self.player_dict.values():
            proto.seat = player.seat
            send(NOTIFY_MSG, proto, player.session)

        # print self.last_card

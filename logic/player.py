# coding: utf-8

import json
import time
import types
import weakref

from tornado.ioloop import IOLoop

from logic.player_proto_mgr import PlayerProtoMgr
from behavior_tree.forest import is_ready_hand
from protocol import game_pb2
from protocol.commands import *
from protocol.serialize import send
from settings import redis, dismiss_delay
from state.machine import Machine
from state.player_state.ready import ReadyState
from state.status import table_state_code_map, player_state_code_map
from rules.define import *
from behavior_tree.base import *


class Player(object):
    def __init__(self, uuid, info, session, table):
        super(Player, self).__init__()
        self.uuid = uuid
        self.table = weakref.proxy(table)
        self.info = info
        self.seat = None
        self.prev_seat = None
        self.next_seat = None
        self.session = session
        self.is_online = True
        self.state = None
        self.vote_state = None
        self.vote_timer = None
        self.status = 0
        self.event = None
        self.isTing = False
        self.can_look_bao = False
        self.isJia = False
        self.tmpTingCard = 0 #用于临时存储听牌判断中的添加牌
        self.win_card_group = {}


        self.machine = None
        Machine(self)

        self.score = 0
        self.total = 0
        self.kong_total = 0
        self.win_total_cnt = 0
        self.total_chong_bao = 0
        self.win_draw_cnt = 0
        self.win_discard_cnt = 0
        self.big_win_draw_cnt = 0
        self.big_win_discard_cnt = 0
        self.small_win_draw_cnt = 0
        self.small_win_discard_cnt = 0
        self.pao_cnt = 0
        self.is_owner = 0
        self.is_yao_fail = False
        self.last_yao_card = 0
        self.last_gang_card = 0

        self.cards_in_hand = []
        self.cards_group = []
        self.cards_discard = []
        self.cards_chow = []
        self.cards_pong = []
        self.cards_kong_exposed = []                    # 明杠牌
        self.cards_kong_concealed = []                  # 暗杠牌
        self.cards_ready_hand = []
        self.cards_draw_niao = []
        self.cards_win = []
        self.kong_exposed_cnt = 0   # 放杠，我杠别人
        self.gang_pao_card = 0
        self.kong_concealed_cnt = 0     # 暗杠
        self.kong_discard_cnt = 0    # 明杠，别人杠我
        self.kong_pong_cnt = 0  # 明杠
        self.draw_cnt = 0   # 抓牌数量
        self.gang_score = 0
        self.last_discard_kong = None

        # 漏胡的牌
        self.miss_win_cards = []
        self.miss_pong_cards = []
        self.miss_gang_cards = []
        self.draw_card = 0
        self.draw_kong_exposed_card = 0
        # 胡的牌
        self.win_card = 0
        # 胡牌类型：点炮 自摸
        self.win_type = 0
        # 胡牌牌型：将将胡 | 碰碰胡 | 七小对 | 。。。
        self.win_flags = []
        self.offline_cmd_stack = []

        self.prompts = 0
        # 提示ID
        self.prompt_id = 0
        # 动作
        self.action_dict = {}
        self.action_id = 0
        self.action_weight = 0
        self.action_rule = None
        self.action_ref_cards = None
        self.action_op_card = None
        # self.had_check_kong = False
        # self.had_check_ting_kong = False
        # 已经胡的牌，以及拆出来的牌组
        self.has_win_cards = {}
        # 杠的次数
        self.kong_times = 0
        #每局累积分，因为在最后才更改得分所以用这个来缓存
        self.temp_total_score = 0
        # 已经胡的牌组，可以用来显示
        self.has_win_cards_list = []
        self.proto = PlayerProtoMgr(self)

    def dumps(self):
        data = {}
        for key, value in self.__dict__.items():
            if key == "table":
                data[key] = value.room_id
            elif key in ("session", "vote_timer"):
                continue
            elif key == "machine":
                data[key] = [None, None]
                if value.last_state:
                    data[key][0] = value.last_state.name
                if value.cur_state:
                    data[key][1] = value.cur_state.name
            elif key == "proto":
                val = self.proto.dump()
                if type(val) is types.StringType:
                    data[key] = unicode(val, errors='ignore')
                else:
                    data[key] = val
            else:
                if type(value) is types.StringType:
                    data[key] = unicode(value, errors='ignore')
                else:
                    data[key] = value
        # print "player", data
        redis.set("player:{0}".format(self.uuid), json.dumps(data))
        self.table.dumps()

    def delete(self):
        redis.delete("player:{0}".format(self.uuid))

    def add_prompt(self, prompt, rule, op_card, ref_cards=None):
        """
        提示包含以下字段信息
        规则（服务端自己持有）
        提示ID（客户端选择完后返回给服务器的ID， 这个字段是唯一的）
        提示类型
        操作牌（每一个提示都唯一对应一张操作牌， 由于关联牌的多样性，操作牌是可以重复的）
        关联牌（操作牌影响的相关牌，比如吃操作有N种吃法则，会有同一个操作牌对应N组关联牌）
        """
        if ref_cards is None:
            ref_cards = []
        self.prompts |= prompt
        self.prompt_id += 1
        self.action_dict[self.prompt_id] = {"rule": rule, "op_card": op_card, "ref_cards": ref_cards, "prompt": prompt}
        #print 'add prompt:',prompt, "ref_cards",ref_cards

    def del_prompt(self):
        self.prompts = 0
        self.action_dict = {}
        self.prompt_id = 0

    # noinspection PyTypeChecker
    def highest_prompt_weight(self):
        max_weight = 0
        for i in self.action_dict.values():
            if i["prompt"] > max_weight:
                max_weight = i["prompt"]
        return max_weight

    def del_action(self):
        self.action_id = 0
        self.action_weight = 0
        self.action_rule = None
        self.action_ref_cards = None
        self.action_op_card = None

    def action(self, action_id):
        self.action_id = action_id
        action = self.action_dict[self.action_id]
        self.action_rule = action["rule"]
        self.action_weight = action["prompt"]
        self.action_ref_cards = action["ref_cards"]
        self.action_op_card = action["op_card"]
        # self.table.replay["procedure"].append([{"action": action, "seat": self.seat}])
        self.del_prompt()

    def is_color_all(self):
        mask_color = []
        card_expt = [ZHONG, WEST, EAST, SOUTH, NORTH, FA, BAI]
        for card in self.cards_in_hand:
            if card not in card_expt:
                mask_color.append(card&0xf0)
        for card in self.cards_group:
            if card not in card_expt:
                mask_color.append(card&0xf0)
        if len(set(mask_color)) == 3:
            return True
        return False

    def is_open_door(self):
        #if len(self.cards_group) > 0:
        if len(self.cards_group) == self.kong_concealed_cnt * 4:
            return False
        return True

    def ready_hand(self, isTing = False):
        if self.isTing:
            return
        if not isTing:
            return
        cards = is_ready_hand(self)
        # cards,键：牌，值：（分，[类型])
        self.cards_ready_hand = cards
        if not cards:
            return
        # 删除win_card_group不胡的牌
        for temp_keys in self.win_card_group.keys():
            if temp_keys not in self.cards_ready_hand.keys():
                self.win_card_group.pop(temp_keys)
        proto = game_pb2.ReadyHandResponse()
        for i in cards:
            flag = True
            if flag:
                c = proto.card.add()
                c.card = i
        if isTing:
            proto.ting_tag = 1
        send(READY_HAND, proto, self.session)
        self.table.logger.info("player {0} ready hand cards {1}".format(self.seat, cards))

    def clear_for_round(self):
        self.del_prompt()
        self.del_action()
        self.score = 0
        self.gang_pao_card = 0
        self.can_look_bao = False
        self.cards_in_hand = []
        self.cards_group = []
        self.cards_discard = []
        self.cards_chow = []
        self.cards_pong = []
        self.cards_kong_exposed = []
        self.cards_kong_concealed = []
        self.cards_ready_hand = []
        self.cards_draw_niao = []
        self.cards_win = []
        self.last_gang_card = 0

        self.kong_exposed_cnt = 0
        self.kong_concealed_cnt = 0
        self.kong_discard_cnt = 0
        self.kong_pong_cnt = 0
        self.miss_win_cards = []
        self.miss_pong_cards = []
        self.miss_gang_cards = []#
        self.draw_card = 0
        self.kong_pong_cnt = 0
        self.draw_cnt = 0
        self.gang_score = 0
        self.last_discard_kong = None
        self.is_yao_fail = False
        self.last_yao_card = 0
        self.isTing = False
        self.isJia = False
        self.tmpTingCard = 0  # 用于临时存储听牌判断中的添加牌
        self.win_card_group = {}
        # 胡的牌
        self.win_card = 0
        # 胡牌类型：点炮 自摸
        self.win_type = 0
        self.miss_gang_cards = []
        # 胡牌牌型：将将胡 | 碰碰胡 | 七小对 | 。。。
        self.win_flags = []
        self.offline_cmd_stack = []
        # self.had_check_kong = False
        # self.had_check_ting_kong = False
        # 已经胡的牌
        self.has_win_cards = {}
        self.kong_times = 0
        self.temp_total_score = 0
        self.has_win_cards_list = []
        self.dumps()

    def clear_for_room(self):
        self.clear_for_round()
        self.total = 0
        self.miss_gang_cards = []
        self.miss_win_cards = []#
        self.miss_pong_cards = []##
        self.kong_total = 0
        self.win_total_cnt = 0
        self.win_draw_cnt = 0
        self.win_discard_cnt = 0
        self.pao_cnt = 0
        self.is_owner = 0
        self.total_chong_bao = 0
        self.big_win_draw_cnt = 0
        self.big_win_discard_cnt = 0
        self.small_win_draw_cnt = 0
        self.small_win_discard_cnt = 0
        self.is_yao_fail = False
        self.isTing = False
        self.isJia = False
        self.tmpTingCard = 0  # 用于临时存储听牌判断中的添加牌
        self.win_card_group = {}

    def online_status(self, status):
        self.is_online = status
        proto = game_pb2.OnlineStatusResponse()
        proto.player = self.uuid
        proto.status = self.is_online
        self.table.logger.info("player {0} toggle online status {1}".format(self.seat, status))
        for i in self.table.player_dict.values():
            if i.uuid == self.uuid:
                continue
            send(ONLINE_STATUS, proto, i.session)

    def reconnect(self):
        proto = game_pb2.ReconnectResponse()
        proto.room_id = self.table.room_id
        proto.kwargs = self.table.kwargs
        proto.owner = self.table.owner
        proto.room_status = table_state_code_map[self.table.state]
        proto.current_round = self.table.cur_real_round
        proto.dealer = self.table.dealer_seat
        active_seat = self.table.active_seat
        #print 'active seat:', active_seat,self.table.seat_dict[active_seat].state
        # 对于前端只有活动玩家处于出牌状态才发送指示灯
        if active_seat >= 0 and \
                (self.table.seat_dict[active_seat].state == "DiscardState" or self.table.seat_dict[active_seat].state == "PromptDrawState"
                 or self.table.seat_dict[active_seat].state == "PromptDiscardState"):
            proto.active_seat = self.table.active_seat
        else:
            proto.active_seat = -1
        #print 'active seat:', proto.active_seat, 'self.table.active_seat', self.table.active_seat
        proto.discard_seat = self.table.discard_seat
        proto.rest_cards = self.table.cards_total if self.table.state == "InitState" else len(self.table.cards_on_desk)
        proto.code = 1
        last_draw = 0
        if len(self.cards_in_hand) % 3 == 2 and self.draw_card in self.cards_in_hand:
            last_draw = self.draw_card

        proto.extra = json.dumps({'last_draw':last_draw})

        log = {
            "description": "reconnect",
            "room_id": self.table.room_id,
            "kwargs": self.table.kwargs,
            "owner": self.table.owner,
            "owner_info": self.table.owner_info,
            "cur_round": self.table.cur_real_round,
            "room_status": table_state_code_map[self.table.state],
            "dealer": self.table.dealer_seat,
            "active_seat": self.table.active_seat,
            "discard_seat": self.table.discard_seat,
            "rest_cards": len(self.table.cards_on_desk),
            "code": 1,
            "players": [],
            "last_draw" : last_draw,
        }

        for i in self.table.player_dict.values():
            player = proto.player.add()
            player.seat = i.seat
            player.player = i.uuid
            player.info = i.info
            player.status = player_state_code_map[i.state]
            player.is_online = i.is_online
            player.total_score = i.total
            player.is_ting = i.isTing
            player.is_jia = i.isJia
            player.last_draw_card = self.draw_card
            if i.is_yao_fail:
                player.is_yao_fail = 1
            else:
                player.is_yao_fail = 0

            for c in i.cards_in_hand:
                cards = player.cards_in_hand.add()
                if i.uuid == self.uuid:
                    cards.card = c
                else:
                    cards.card = 0
            for c in i.cards_discard:
                cards = player.cards_discard.add()
                cards.card = c
            for c in i.cards_kong_exposed:
                cards = player.cards_kong_exposed.add()
                cards.card = c
            for c in i.cards_kong_concealed:
                cards = player.cards_kong_concealed.add()
                cards.card = c
            for c in i.cards_pong:
                cards = player.cards_pong.add()
                cards.card = c
            for c in i.cards_chow:
                cards = player.cards_chow.add()
                cards.card = c

            log["players"].append({
                "seat": i.seat,
                "player": i.uuid,
                "info": i.info,
                "status": player_state_code_map[i.state],
                "is_online": i.is_online,
                "total": i.total,

                "cards_in_hand": i.cards_in_hand,
                "cards_discard": i.cards_discard,
                "cards_Kong_exposed": i.cards_kong_exposed,
                "cards_Kong_concealed": i.cards_kong_concealed,
                "cards_pong": i.cards_pong,
                "cards_chow": i.cards_chow,
            })
        send(RECONNECT, proto, self.session)
        self.table.logger.info(log)
        # 必须屏蔽掉以下代码否则重连之前点过然后重连之后又出现提示
        # 此时再点听则无任何效果客户端显示为卡住
        # from rules.player_rules.ting import TingRule
        # if not self.isTing:
        #     r = TingRule()
        #     r.condition(self)
            # 发送操作提示
        if self.action_dict:
            self.send_prompts()

        #print 'player id:', self.seat, self.uuid, ',isting:', self.isTing, 'ready len:', len(self.cards_ready_hand)
        # 发送听牌提示
        if self.isTing and self.cards_ready_hand:
            proto = game_pb2.ReadyHandResponse()
            proto.ting_tag = 1
            tmp_ready_hand = {}
            for i in self.cards_ready_hand:
                flag = False
                if self.isJia:
                    if "JIAHU" in self.cards_ready_hand[i][1]:
                        flag = True
                        proto.ting_tag = 2
                    elif self.table.conf.bian_hu_jia() and "BIANHU" in self.cards_ready_hand[i][1]:
                        flag = True
                        proto.ting_tag = 2
                    else:
                        flag = False
                else:
                    flag = True
                if flag:
                    c = proto.card.add()
                    if type(i) is types.IntType:
                        c.card = i
                    else:
                        c.card = int(i)
                    tmp_ready_hand[int(i)] = self.cards_ready_hand[i]
            self.cards_ready_hand = tmp_ready_hand
            send(READY_HAND, proto, self.session)
            #self.table.broadcast_change_bao()
        if self.table.dismiss_state:
            # 先弹出投票界面
            expire_seconds = int(dismiss_delay + self.table.dismiss_time - time.time())
            if expire_seconds <= 0:
                self.table.dismiss_room()
                return
            proto = game_pb2.SponsorVoteResponse()
            proto.room_id = self.table.room_id
            proto.sponsor = self.table.dismiss_sponsor
            proto.expire_seconds = expire_seconds
            send(SPONSOR_VOTE, proto, self.session)
            # 生成定时器
            if not self.vote_timer and self.uuid != self.table.dismiss_sponsor and not self.vote_state:
                proto_vote = game_pb2.PlayerVoteRequest()
                proto_vote.flag = True
                self.vote_timer = IOLoop().instance().add_timeout(
                    self.table.dismiss_time + dismiss_delay, self.vote, proto_vote)
            # 遍历所有人的投票状态
            for player in self.table.player_dict.values():
                proto_back = game_pb2.PlayerVoteResponse()
                proto_back.player = player.uuid
                if player.vote_state is not None:
                    proto_back.flag = player.vote_state
                    send(VOTE, proto_back, self.session)
        self.table.send_last_card()

    def send_prompts(self):
        proto = game_pb2.PromptResponse()
        for k, v in self.action_dict.items():
            prompt = proto.prompt.add()
            prompt.action_id = k
            prompt.prompt = v["prompt"]
            prompt.op_card.card = v["op_card"]
            for c in v["ref_cards"]:
                ref_card = prompt.ref_card.add()
                ref_card.card = c
        send(PROMPT, proto, self.session)
        self.table.logger.info(self.action_dict)

    def exit_room(self):
        if self.table.state == 'InitState':
            if self.table.conf.is_aa():
                #if self.table.cur_round <= 1:
                if self.table.total_round <= 1:
                    if self.uuid == self.table.owner:
                        self.dismiss_room()
                    else:
                        self.table.request.aa_refund(self.uuid, 0)
            self.table.request.exit_room(self.uuid)

            proto = game_pb2.ExitRoomResponse()
            proto.player = self.uuid
            proto.code = 1
            for player in self.table.player_dict.values():
                send(EXIT_ROOM, proto, player.session)

            self.table.logger.info("player {0} exit room".format(self.uuid))

            self.delete()
            try:
                self.session.close()
            except Exception:
                pass
            del self.table.seat_dict[self.seat]
            del self.table.player_dict[self.uuid]
            self.table.dumps()
            self.table = None
        else:
            self.table.logger.info("player {0} exit room failed".format(self.uuid))

    def dismiss_room(self):
        # 解散房间不重复响应
        if self.table.dismiss_state:
            return
        if self.table.state == "InitState":
            # 房间未开局直接由房主解散
            if self.uuid == self.table.owner:
                self.table.dismiss_room(False)
            else:
                proto = game_pb2.DismissRoomResponse()
                proto.code = 5003
                send(DISMISS_ROOM, proto, self.session)
        else:
            # 如果是房主则直接解散
            if self.uuid == self.table.owner:
                self.table.dismiss_room(False)
                return            
            # 房间已开局则直接发起投票
            self.table.dismiss_state = True
            self.table.dismiss_sponsor = self.uuid
            self.table.dismiss_time = time.time()
            self.vote_state = True
            self.dumps()
            proto = game_pb2.SponsorVoteResponse()
            proto.room_id = self.table.room_id
            proto.sponsor = self.table.dismiss_sponsor
            proto.expire_seconds = dismiss_delay
            for player in self.table.player_dict.values():
                send(SPONSOR_VOTE, proto, player.session)
                if player.uuid == self.uuid:
                    continue
                proto_vote = game_pb2.PlayerVoteRequest()
                proto_vote.flag = True
                player.vote_timer = IOLoop().instance().add_timeout(
                    self.table.dismiss_time+dismiss_delay, player.vote, proto_vote)
            self.table.logger.info("player {0} sponsor dismiss room".format(self.uuid))

    def vote(self, proto):
        IOLoop().instance().remove_timeout(self.vote_timer)
        self.dumps()
        self.vote_state = proto.flag
        self.table.logger.info("player {0} vote {1}".format(self.uuid, self.vote_state))

        self.vote_timer = None
        proto_back = game_pb2.PlayerVoteResponse()
        proto_back.player = self.uuid
        proto_back.flag = proto.flag
        for k, v in self.table.player_dict.items():
            send(VOTE, proto_back, v.session)

        if proto.flag:
            for player in self.table.player_dict.values():
                if not player.vote_state:
                    return
            self.table.dismiss_room()
        else:
            # 只要有一人拒绝则不能解散房间
            self.table.dismiss_state = False
            self.table.dismiss_sponsor = None
            self.table.dismiss_time = 0
            for player in self.table.player_dict.values():
                player.vote_state = None
                if player.vote_timer:
                    IOLoop.instance().remove_timeout(player.vote_timer)
                    player.vote_timer = None

    def ready(self):
        self.machine.trigger(ReadyState())

    def add_gang_num(self, fang, ming, an, discard_kong):
        self.kong_exposed_cnt += fang
        self.kong_pong_cnt += ming
        self.kong_concealed_cnt += an
        self.kong_discard_cnt += discard_kong

    def get_fang_gang_score(self):
        return 1

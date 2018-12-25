# coding: utf-8
import json
import operator
import rules.define
DAHU = ['GSKH','QD', 'PPHU','QIYS']
DAHU_OPTION = ['TNHU', 'DIHU', 'BBHU', 'LONG', 'SGY',  'HAQD', 'JJHU']
FANHU_OPTION = ['HDLY', 'GSKH','QGH','PIAOHU','GSDP']
ConfigDetail = {}
ConfigDetail['JuShu'] = 0
ConfigDetail['Chairs'] = 1
ConfigDetail['HuType'] = 2
ConfigDetail['BaoCard'] = 3

ConfigDetail['DIAN_PAO'] = 4

ConfigDetail['ZFB_PONG'] = 5
ConfigDetail['BIAN_JIA'] = 6
ConfigDetail['HUPAI_GANG'] = 7
ConfigDetail['MOBAO_TYPE'] = 8
ConfigDetail['CHONG_GANG'] = 9
ConfigDetail['HDLY'] = 10
ConfigDetail['GSKH'] = 11
ConfigDetail['QGH'] = 12
ConfigDetail['PIAOHU'] = 13
ConfigDetail['GSDP'] = 14

class TableConf(object):
    def __init__(self, kwargs):
        self.hu_type = ""
        self.kwargs = kwargs
        self.settings = json.loads(kwargs)
        self.chairs = self.settings.get("chairs", 4)
        self.hu_type = str(self.settings.get("hu_type"))
        self.max_rounds = int(self.settings.get("max_rounds", 10))
        self.game_type = self.settings.get("game_type")
        self.app_id = self.settings.get("app_id")
        self.options = self.settings.get("options")
        self.chips = self.settings.get("chips")
        self.aa = self.settings.get("aa")
        # max圈
        self.circle = self.settings.get('max_rounds', 1)
        self.is_round = int(self.settings.get('is_round', 1))
        # print self.hu_type

    def is_aa(self):
        return self.aa

    # def is_pao(self):
    #     # return True#self.play_type == 0 or self.play_type == 2
    #     return False
    # def is_zimo(self):
    #     # return self.hu_type[ConfigDetail['HuType']] == '3'
    #    # return False#self.play_type == 1
    #     return True
    #
    # def is_jia(self):
    #     #return self.play_type == 2
    #     # return self.hu_type[ConfigDetail['HuType']] == '2'
    #     return False
    #
    def can_hu_on_ready(self):
        return False
    #
    # def can_hu_without_sequence(self):
    #     return False#bool(self.options & 0x00000800 != 0)
    #
    # def is_color_all(self):
    #     return True#bool(self.options & 0x00000100 == 0)
    #     #return True
    #
    # def can_hu_with_one(self):1
    #     return False
    #
    # def is_19(self):
    #     return True#bool(self.options & 0x00000200 == 0)
    #     #return True
    #
    # def is_open_door(self):
    #     return True#bool(self.options & 0x00000400 == 0)
    #     #return True
    #
    # def bian_hu_jia(self):
    #     #return bool(self.options & 0x00001000 == 0)
    #     return self.hu_type[ConfigDetail['BIAN_JIA']] == '1'
    #     #return True
    #
    # def allow_view_bao(self):
    #     #return True
    #     return self.hu_type[ConfigDetail['BaoCard']] == '1'
    #
    def is_qg(self):
        return False

    # def is_normal_bao(self):
    #     return True#bool(self.options & 0x00000600 == 0)
    #
    # def is_up_bao(self):
    #     return False#bool(self.options & 0x000006000 == 0x000002000)
    #
    # def is_up_normal_bao(self):
    #     return False#bool(self.options & 0x000006000 == 0x000004000)

    def can_pong_on_zfb(self):
        #return bool(self.options & 0x000f0000 != 0)
        # return self.hu_type[ConfigDetail['ZFB_PONG']] == '1'
        return True
    # def is_fan_hu(self, hu_type):
    #     if hu_type in FANHU_OPTION:
    #         idx = FANHU_OPTION.index(hu_type)
    #         # print "==============idx================"
    #         # print idx
    #         # print idx + ConfigDetail['HDLY']
    #         # print "======================"
    #         # print self.hu_type
    #         if self.hu_type[idx + ConfigDetail['HDLY']] == '0':
    #             return False
    #         else:
    #             return True
    #     return False
    #
    def look_bao_on_ting(self):
        #return self.hu_type[ConfigDetail['MOBAO_TYPE']] == '1'
        return False
    #
    # def kong_score_on_hu(self):
    #     return self.hu_type[ConfigDetail['HUPAI_GANG']] == '1'
    #
    # def pao_score_all_pay(self):
    #     return self.hu_type[ConfigDetail['DIAN_PAO']] == '2'
    #
    # def pao_score_pay_all(self):
    #     return self.hu_type[ConfigDetail['DIAN_PAO']] == '3'
    #
    # def pao_score_self(self):
    #     return self.hu_type[ConfigDetail['DIAN_PAO']] == '1'

    # @property
    # def max_double(self):
    #     if self._max_double == 0:
    #         return 8
    #     elif self._max_double == 1:
    #         return 16
    #     elif self._max_double == 2:
    #         return 32
    #     elif self._max_double == 3:
    #         return 64
    #     elif self._max_double == 4:
    #         return 128
    #     elif self._max_double == 5:
    #         return 0

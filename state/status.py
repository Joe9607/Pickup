# coding: utf-8

PLAYER_STATUS_INIT = 0
PLAYER_STATUS_READY = 1
PLAYER_STATUS_PLAYING = 2
PLAYER_STATUS_SETTLE = 3

player_state_code_map = {
    "InitState": PLAYER_STATUS_INIT,
    "ReadyState": PLAYER_STATUS_READY,
    "DealState": PLAYER_STATUS_PLAYING,
    "DrawState": PLAYER_STATUS_PLAYING,
    "DrawAfterKongState": PLAYER_STATUS_PLAYING,
    "DiscardState": PLAYER_STATUS_PLAYING,
    "PauseState": PLAYER_STATUS_PLAYING,
    "WaitState": PLAYER_STATUS_PLAYING,
    "PromptState": PLAYER_STATUS_PLAYING,
    "PromptDrawState": 5,
    "PromptTingKongState":5,
    "YaoState": PLAYER_STATUS_PLAYING,
    "PromptYaoState": PLAYER_STATUS_PLAYING,
    "PromptDiscardState": PLAYER_STATUS_PLAYING,
    "ChowState": PLAYER_STATUS_PLAYING,
    "PongState": PLAYER_STATUS_PLAYING,
    "TingState":PLAYER_STATUS_PLAYING,
    "WinState": PLAYER_STATUS_PLAYING,
    "DrawWinState": PLAYER_STATUS_PLAYING,
    "DiscardWinState": PLAYER_STATUS_PLAYING,
    "QGWinState": PLAYER_STATUS_PLAYING,
    "DiscardExposedKongState": PLAYER_STATUS_PLAYING,
    "DrawExposedKongState": PLAYER_STATUS_PLAYING,
    "DrawConcealedKongState": PLAYER_STATUS_PLAYING,
    "SettleState": PLAYER_STATUS_SETTLE,
    "AnimationState": 6
}

table_state_code_map = {
    "InitState": 0,
    "ReadyState": 1,
    "DealState": 2,
    "StepState": 3,
    "WaitState": 4,
    "EndState": 5,
    "NiaoState": 6,
    "RestartState": 7,
    "SettleForRoundState": 8,
    "SettleForRoomState": 9,
    "HaiDiState":12,
}

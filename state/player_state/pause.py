# coding: utf-8

from state.player_state.base import PlayerStateBase


class PauseState(PlayerStateBase):

    def enter(self, owner):
        super(PauseState, self).enter(owner)

    def next_state(self, owner):
        owner.machine.last_state.next_state(owner)

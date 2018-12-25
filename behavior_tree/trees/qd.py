# coding: utf-8

from behavior_tree.control_node.selector import SelectorNode
from behavior_tree.base import NodeBase
from behavior_tree.condition_node.qd import QD
from behavior_tree.action_node.xiqd import XIQD
from behavior_tree.action_node.haqd import HAQD


class TreeQD(NodeBase):
    def __init__(self):
        super(TreeQD, self).__init__(1)
        selector = SelectorNode(1,[QD()])
        self.add_child(selector)
        selector.add_child(QD(2))
        selector.add_child(HAQD(3))

    def condition(self, player):
        return len(player.cards_in_hand) == 14

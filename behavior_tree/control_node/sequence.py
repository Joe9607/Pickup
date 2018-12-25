# coding: utf-8


from behavior_tree.base import NodeBase


class SequenceNode(NodeBase):
    def __init__(self, weight, condition_nodes):
        super(SequenceNode, self).__init__(weight)
        self.condition_nodes = condition_nodes

    def condition(self, player):
        # super(SequenceNode, self).condition(player)
        for node in self.condition_nodes:
            if not node.condition(player):
                return False
        return True

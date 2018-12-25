# coding: utf-8


from behavior_tree.base import NodeBase


class SelectorNode(NodeBase):
    def __init__(self, root, condition_nodes):
        super(SelectorNode, self).__init__(0)
        self.condition_nodes = condition_nodes
        self.root = root

    def condition(self, player):
        # super(SelectorNode, self).condition(player)
        for node in self.condition_nodes:
            if node.condition(player):
                return True
        return False

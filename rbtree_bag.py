__author__ = 'Kamil Khadiev'
__date__ = 'December 14, 2014'

import bintrees

class RBTreeBag:
    """ Each Elf starts with a rating of 1.0 and are available at 09:00 on Jan 1.  """
    def __init__(self):
        self.rbtree = bintrees.RBTree()
        self.len = 0



    def max_item(self):
        key, items = self.rbtree.max_item()
        while len(items)==0:
            self.rbtree.remove(key)
            key, items = self.rbtree.max_item()

        item = items.pop(len(items)-1)
        self.rbtree.insert(key, items)
        self.len = self.len - 1
        return key, item

    def insert(self, key, toy):

        try:
            key1, items = self.rbtree.ceiling_item(key)
            if key1 != key:
                self.rbtree.insert(key1, items)
                items = list()
        except KeyError:
            items = list()

        items.append(toy)
        self.len = self.len + 1
        self.rbtree.insert(key, items)

    def ceiling_item(self, key):
        key, items = self.rbtree.ceiling_item(key)
        while len(items)==0:
            self.rbtree.remove(key)
            key, items = self.rbtree.ceiling_item(key)
        item = items.pop(len(items)-1)
        self.rbtree.insert(key, items)
        self.len = self.len - 1
        return key, item

    def floor_item(self, key):
        key, items = self.rbtree.floor_item(key)
        while len(items) == 0:
            self.rbtree.remove(key)
            key, items = self.rbtree.floor_item(key)
        item = items.pop(len(items)-1)

        self.rbtree.insert(key, items)
        self.len = self.len - 1
        return key, item

    def length(self):
        return self.len


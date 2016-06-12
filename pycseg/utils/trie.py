# -*- coding: utf-8 -*-

"""Implementation of a trie data structure.
"""


class TrieNode(object):
    """Internal representation of Trie nodes."""
    __slots__ = ('key', 'value', 'parent', 'children')
    no_value = object()

    def __init__(self, key, value, parent, children):
        self.key = key
        self.value = value
        self.children = children
        self.parent = parent

    @property
    def key_path(self):
        n = self
        kpath = [n.key for n in iter(lambda: n.parent, None) if n.key]
        kpath.reverse()
        kpath.append(self.key)
        return ''.join(kpath)

    def walk(self):
        nodes = [self]
        while nodes:
            node = nodes.pop()
            if node.value is not node.no_value:
                yield node
            nodes.extend(node.children[key] for key in
                         sorted(node.children, reverse=True))


class Trie(object):
    """A simple prefix tree (trie) implementation.

    Trie() -> new empty trie
    Trie(mapping) -> new trie initialized from a mapping object's (key, value) pairs
    Trie(iterable) -> new trie initialized as if via:
        d = {}
        for k, v in iterable:
            d[k] = v
    """

    def __init__(self, mapping=None, root_data=TrieNode.no_value):
        """Initialize a Trie instance.

        Args (both optional):
            mapping:    a mapping object's (key, value) pairs
            root_data:  value of the root node (ie. Trie('hello')[()] == 'hello').
        """
        self.root = TrieNode(None, root_data, None, {})
        if mapping:
            self.extend(mapping)

    def extend(self, mapping):
        """Update the Trie with a sequence of (key, value) pairs."""
        for k, v in mapping.iteritems():
            self[k] = v

    def __setitem__(self, k, v):
        """x.__setitem__(i, y) <==> x[i]=y"""
        n = self.root
        for c in k:
            n = n.children.setdefault(c, TrieNode(c, TrieNode.no_value, n, {}))
        n.value = v

    def _getnode(self, k):
        """Return the node of the given key"""
        n = self.root
        for c in k:
            try:
                n = n.children[c]
            except KeyError:
                raise KeyError(k)
        return n

    def __contains__(self, k):
        """T.__contains__(k) -> True if T has a key k, else False"""
        n = None
        try:
            n = self._getnode(k)
        except KeyError:
            return False
        if n.value is TrieNode.no_value:
            return False
        return True

    def __getitem__(self, k):
        """x.__getitem__(y) <==> x[y]"""
        n = self._getnode(k)
        if n.value is TrieNode.no_value:
            if n.children:
                raise KeyError(k)
            else:
                raise KeyError(k)
        return n.value

    def get(self, k, default=None):
        try:
            return self.__getitem__(k)
        except KeyError:
            return default

    def setdefault(self, k, default=None):
        try:
            return self.__getitem__(k)
        except KeyError:
            self.__setitem__(k, default)
            return default

    def __delitem__(self, k):
        """x.__delitem__(y) <==> del x[y]"""
        n = self._getnode(k)
        if n.value is TrieNode.no_value:
            raise KeyError(k)
        n.value = TrieNode.no_value
        while True:
            if n.children or not n.parent or n.value is not TrieNode.no_value:
                break
            del n.parent.children[n.key]
            n = n.parent

    def __iter__(self):
        """Yield the keys in order."""
        for node in self.root.walk():
            yield node.key_path

    def iteritems(self):
        """Yield (key, value) pairs in order."""
        for node in self.root.walk():
            yield node.key_path, node.value

    def itervalues(self):
        """Yield values in order."""
        for node in self.root.walk():
            yield node.value

    def children(self, k):
        """Return a dict of the immediate children of the given key.
        """
        n = self._getnode(k)
        return dict((k, n.children[k].value)
                    for k in n.children
                    if n.children[k].value is not TrieNode.no_value)

    def has_prefix(self, k):
        """True if Trie has a prefix k, else False"""
        n = None
        try:
            n = self._getnode(k)
        except KeyError:
            return False
        return True

    def longest_prefix(self, k):
        """Return longest common prefix with k"""
        max_length = 0
        n = self.root
        for c in k:
            try:
                n = n.children[c]
                max_length += 1
            except KeyError:
                break
        return max_length

    def longest_key(self, k):
        """Return longest common key with k"""
        key_length, max_length = 0, 0
        n = self.root
        for c in k:
            try:
                n = n.children[c]
                max_length += 1
                if n.value is not TrieNode.no_value:
                    key_length = max_length
            except KeyError:
                break
        return key_length

# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import unittest

from pycseg.utils import trie


class TrieTestCase(unittest.TestCase):
    def setUp(self):
        self.d = {'abc': 1, 'abd': 3, 'abcd': None, 'bcd': 4,
                  '北京': 'ns', '北京大学': None}
        self.t = trie.Trie(mapping=self.d)

    def test_add(self):
        self.t['bce'] = 5
        self.d['bce'] = 5
        td = {}
        for k, v in self.t.iteritems():
            td[k] = v
        self.assertDictEqual(td, self.d)

    def test_get(self):
        self.assertEqual(self.t['abc'], 1)
        self.assertEqual(self.t['abcd'], None)
        self.assertEqual(self.t['北京大学'], None)

    def test_iteritems(self):
        td = {}
        for k, v in self.t.iteritems():
            td[k] = v
        self.assertDictEqual(td, self.d)

    def test_longest_prefix(self):
        self.assertEqual(self.t.longest_prefix('ab'), 2)
        self.assertEqual(self.t.longest_prefix('cd'), 0)
        self.assertEqual(self.t.longest_prefix('bcd'), 3)

    def test_has_prefix(self):
        self.assertTrue(self.t.has_prefix('ab'))
        self.assertTrue(self.t.has_prefix('abc'))
        self.assertTrue(self.t.has_prefix('bc'))
        self.assertFalse(self.t.has_prefix('ad'))
        self.assertTrue(self.t.has_prefix('北京大'))

    def test_longest_key(self):
        self.assertEqual(self.t.longest_key('ab'), 0)
        self.assertEqual(self.t.longest_key('abcef'), 3)
        self.assertEqual(self.t.longest_key('bcd'), 3)
        self.assertEqual(self.t.longest_key('abcdefg'), 4)
        self.assertEqual(self.t.longest_key('北京大学'), 4)

    def test_in(self):
        self.assertIn('abc', self.t)
        self.assertIn('北京', self.t)
        self.assertNotIn('ab', self.t)
        self.assertNotIn('abcdefg', self.t)
        self.assertNotIn('北京大', self.t)


if __name__ == '__main__':
    unittest.main()

# -*- coding: utf-8 -*-

from __future__ import division, unicode_literals, absolute_import

import os
import codecs
import math

import pycseg.definitions as definitions
from pycseg.utils import trie, hmm, shortest_path


class Feature(object):
    """词的词性"""

    def __init__(self, tag=None, tag_code=None):
        if tag_code is not None:
            self.tag_code = tag_code
        elif tag is not None:
            self.tag_code = self.encode(tag)
        else:
            self.tag_code = 0

    def __str__(self):
        return self.tag

    def __repr__(self):
        return '<Feature {0}>'.format(self.tag_code)

    @property
    def tag(self):
        return self.decode(self.tag_code)

    @staticmethod
    def encode(tag):
        tag_code = 0
        tag_length = len(tag)
        if tag_length == 1:
            tag_code = ord(tag[0]) * 256
        elif tag_length == 2:
            tag_code = ord(tag[0]) * 256 + ord(tag[1])
        return tag_code

    @staticmethod
    def decode(tag_code):
        if tag_code < 256:
            return str(tag_code)
        tag_1, tag_2 = tag_code // 256, tag_code % 256
        tag_1 = chr(tag_1) if tag_1 >= 65 else ''
        tag_2 = chr(tag_2) if tag_2 >= 65 else ''
        return ''.join([tag_1, tag_2])


class Atom(object):
    """原子类: 不可拆分的原子，如汉字，英文单词，数字，标点符号"""

    def __init__(self, content=None, feature=None):
        self.content = content
        self.feature = feature

    def __str__(self):
        return self.content

    def __repr__(self):
        return '<Atom {0}>'.format(self.content)


class Word(object):
    """词类: 匹配词，合成词"""

    def __init__(self, content=None, feature=None, weight=0, alias=None):
        self.content = content
        self.feature = feature
        self.weight = weight
        self.alias = alias if alias else content

    def __str__(self):
        return self.content

    def __repr__(self):
        return '<Word {0}>'.format(self.content)


class AtomsDAG():
    """
    原子组成的有向无环图
    顶点代表原子, 每一条边代表一个词
    words = {left_index: {right_index: Word(), ...}, ...}
    left_index: 词左边界在atoms中的索引
    right_index: 词右边界在atoms的索引减1
    即: word.content = atoms[left_index:right_index]
    """
    def __init__(self):
        self.dag = {}

    def add(self, left_index, right_index=None, word=None):
        if right_index is None:
            self.dag[left_index] = {}
        else:
            self.dag[left_index][right_index] = word

    def get(self, left_index, right_index=None):
        try:
            if right_index is not None:
                return self.dag[left_index][right_index]
            else:
                return self.dag[left_index]
        except KeyError:
            return None

    def clear(self):
        self.dag.clear()

    def all_words(self):
        for left_index, words in self.dag.items():
            for right_index, word in words.items():
                yield left_index, right_index, word

    def start_with(self, left_index):
        words = self.dag[left_index]
        for right_index, word in words.items():
            yield right_index, word

    def first_word(self):
        left_index, right_index = None, None
        value = None
        try:
            left_index = min(self.dag.keys())
            right_index = min(self.dag[left_index].keys())
            value = self.dag[left_index][right_index]
        except ValueError:
            pass
        return left_index, right_index, value

    def last_word(self):
        left_index, right_index = None, None
        value = None
        try:
            left_index = max(self.dag.keys())
            right_index = max(self.dag[left_index].keys())
            value = self.dag[left_index][right_index]
        except ValueError:
            pass
        return left_index, right_index, value


class WordsDAG(object):
    """
    二元词图，通过words/AtomsDAG的有向无环图表示，边的权值为词与词之间的bi-gram值
    words_dag = {prev_index: {next_index: value, ...}, ...}
    key_index = left_index*(len(words)+1) + right_index
    """
    def __init__(self):
        self.dag = {}

    def add(self, prev_index, next_index=None, value=None):
        if next_index is None:
            self.dag[prev_index] = {}
        else:
            self.dag[prev_index][next_index] = value

    def get(self, prev_index, next_index=None):
        try:
            if next_index is not None:
                return self.dag[prev_index][next_index]
            else:
                return self.dag[prev_index]
        except KeyError:
            return None

    def clear(self):
        self.dag.clear()

    def all_words(self):
        for left_index, words in self.dag.items():
            for right_index, value in words.items():
                yield left_index, right_index, value

    def first_word(self):
        left_index, right_index = None, None
        value = None
        try:
            left_index = min(self.dag.keys())
            right_index = min(self.dag[left_index].keys())
            value = self.dag[left_index][right_index]
        except ValueError:
            pass
        return left_index, right_index, value

    def last_word(self):
        left_index, right_index = None, None
        value = None
        try:
            left_index = max(self.dag.keys())
            right_index = max(self.dag[left_index].keys())
            value = self.dag[left_index][right_index]
        except ValueError:
            pass
        return left_index, right_index, value

    @staticmethod
    def index_encode(left_index, right_index, total_count):
        return left_index * (total_count + 1) + right_index

    @staticmethod
    def index_decode(index, total_count):
        left_index = index // (total_count + 1)
        right_index = index % (total_count + 1)
        return left_index, right_index


class WordsGraph(object):
    """原词/词的有向无环图类"""

    def __init__(self):
        # 原子列表 [Atom(), ...]
        self.atoms = []

        # 由原子组成的词，通过atoms的有向图来表示
        # words = {left_index: {right_index: Word(), ...}, ...}
        # left_index: 词左边界在atoms中的索引
        # right_index: 词右边界在atoms的索引减1
        # 即: word.content = atoms[left_index:right_index]
        self.words = AtomsDAG()

        # 二元词图，通过words的有向无环图表示，边的权值为词与词之间的bi-gram值
        # words_dag = {prev_index: {next_index: value, ...}, ...}
        # key_index = left_index*(len(words)+1) + right_index
        self.words_dag = WordsDAG()

    def get_atoms(self):
        return self.atoms

    def get_words(self):
        return self.words

    def get_words_dag(self):
        return self.words_dag

    def append_atom(self, content, feature=None):
        self.atoms.append(Atom(content, feature))
        # 每一个原子都是一个词
        self.words.add(len(self.atoms)-1)

    def generate_word(self, left, right, feature=None, weight=0, alias=None):
        """
        合并atom，组成词
        @:param left 词的左边界, 即第一个atom在atoms list中的索引
        @:param right 词的右边界，即最后一个atom的索引加1
        @:param weight 词的权值
        @:param feature 词的词性或其他tag
        @:param alias 词的别名, 如 "北京"在计算词的连接权值时用"未##地"来代替
        """
        content = ''.join([atom.content for atom in self.atoms[left:right]])
        self.words.add(left, right, Word(content, feature, weight, alias))

    def get_word(self, left, right):
        return self.words.get(left, right)

    def generate_words_dag(self, bigram_dct):
        """
        遍历words，生成词的有向无环图words_dag
        """
        self.words_dag.clear()
        words_count = len(self.atoms)
        for left_index, right_index, prev_word in self.words.all_words():
            # 遍历所有的词
            prev_index = self.words_dag.index_encode(left_index, right_index, words_count)
            self.words_dag.add(prev_index)
            if self.words.get(right_index) is None:
                continue
            for right_right_index, next_word in self.words.start_with(right_index):
                # 遍历这个词的后续词
                next_index = self.words_dag.index_encode(right_index, right_right_index, words_count)
                bi_weight = self.calculate_bigram_weight(prev_word, next_word, bigram_dct)
                self.words_dag.add(prev_index, next_index, bi_weight)
        return self.words_dag

    @staticmethod
    def calculate_bigram_weight(prev_word, next_word, bigram_dct):
        """
        计算两个词之间的权重
        weight = -log{a*P(Ci-1)+(1-a)P(Ci|Ci-1)} Note 0<a<1 a=0.1
        """
        smoothing_param = 0.1
        d_temp = 1 / definitions.MAX_FREQUENCE
        bi_word = definitions.WORD_SEGMENTER.join([prev_word.alias,
                                                   next_word.alias])
        bi_word_freq = bigram_dct.get(bi_word, 0)
        weight = - math.log(
            smoothing_param * (1 + prev_word.weight) / (definitions.MAX_FREQUENCE + 80000) +
            (1 - smoothing_param) * ((1 - d_temp) * bi_word_freq / (prev_word.weight + 1) + d_temp)
        )
        return weight

    def words_segment(self, count=1):
        """
        根据词的有向图及权重, 生成分词结果
        返回分词结果及分词对应的在atoms_dag中的(first_idx, second_idx)

        @:return [
                    {
                        'words': ['w1', 'w2', ...]
                        'index': [(w1_left, w1_right), (w2_left, w2_right), ...]
                    },
                    ...
                ]
        """
        seg_words = []
        words_count = len(self.atoms)
        # 第一个词
        first_word_index = self.words_dag.first_word()[0]
        # 最后一个词
        last_word_index = self.words_dag.last_word()[0]
        paths = shortest_path.yen_ksp(self.words_dag.dag,
                                      first_word_index,
                                      last_word_index,
                                      count
                                      )
        for path, distance in paths:
            words, words_index = [], []
            for v in path:
                left_idx, right_idx = self.words_dag.index_decode(v, words_count)
                # print(first_idx, second_idx)
                words.append(self.words.get(left_idx, right_idx))
                words_index.append((left_idx, right_idx))
            seg_words.append({'words': words, 'index': words_index})

        return seg_words

    def print_atoms(self):
        """打印原子列表"""
        print('Atoms List:')
        for idx, c in enumerate(self.atoms):
            print('{0} atom:{1}\tfeature:{2}'.format(idx, c.content, c.feature))

    def print_words(self):
        """打印词列表，即原子组成的有向图"""
        print('Words List:')
        for i, j, word in self.words.all_words():
            print('[{0},{1}] word:{2}\tfeature:{3}\tweight:{4}'.format(
                i, j, word.content, word.feature, word.weight))

    def print_words_dag(self):
        """打印词组成的有向图"""
        words_count = len(self.atoms)

        def dag_to_word_index(index, word_count):
            left_idx = index // (words_count + 1)
            right_idx = index % (words_count + 1)
            return left_idx, right_idx

        print('Words DAG:')
        for i, j, value in self.words_dag.all_words():
            i_index = self.words_dag.index_decode(i, words_count)
            j_index = self.words_dag.index_decode(j, words_count)
            print('{0}@{1} weight:{2}'.format(
                self.get_word(i_index[0], i_index[1]),
                self.get_word(j_index[0], j_index[1]),
                value))


class Dictionary(trie.Trie):
    """
    字典类: 继承自Trie树, 用于存储(词, 词频, 词性)三元组
    """

    def __init__(self, filename=None):
        super(Dictionary, self).__init__()
        if filename is not None and not self.load(filename):
            raise IOError

    def load(self, filename):
        """
        从字典文件生成字典
        字典格式： 词 词频 词性
        TrieNode格式:
        {
            词: [(词频_1，词性_1), (词频_2，词性_2)..],
            ...
        }
        即： key = 词 , value = [(词频_1，词性_1), (词频_2，词性_2)..]
        """
        with codecs.open(filename, 'r', 'utf-8') as f:
            for line in f.readlines():
                items = line.strip().split()
                if len(items) == 3:
                    self.setdefault(items[0], []
                                    ).append((int(items[1]), int(items[2])))
        return True

    def matches(self, k):
        """
        找出字典中所有与k拥有共同前缀的词及词频词性
        @:return matches = [(word, [(freq, pos)...]), ...]
        """
        match_words = []
        n = self.root
        for c in k:
            try:
                n = n.children[c]
                if n.value is not trie.TrieNode.no_value:
                    match_words.append((n.key_path, n.value))
            except KeyError:
                break
        return match_words

    def get_frequence(self, k, k_pos=0):
        """
        获取关键词k在词性是pos时的词频
        如果pos=0，则获取关键词k的总词频
        """
        total_freq = 0
        word_attr = self.get(k, [])
        for freq, pos in word_attr:
            if pos == 0 or (pos != 0 and pos == k_pos):
                total_freq += freq
        return total_freq


class BiDictionary(dict):
    """
    二元字典类: 存储二元词及词频
    """

    def __init__(self, filename=None):
        super(BiDictionary, self).__init__()
        if filename is not None and not self.load(filename):
            raise IOError

    def load(self, filename):
        with codecs.open(filename, 'r', 'utf-8') as f:
            for line in f.readlines():
                items = line.strip().split()
                if len(items) > 1:
                    self.__setitem__(items[0], int(items[1]))
        return True


class Context(hmm.HMM):
    """
    HMM模型: 存储词性及未登录词的概率统计概率
    (state start_probability 和transition_probability)
    """

    def __init__(self, filename=None):
        super(Context, self).__init__()
        self.total_state = 0
        self.total_freq = 0
        self.state_freq = {}
        if filename is not None and not self.load(filename):
            raise IOError

    def load(self, filename):
        with codecs.open(filename, 'r', 'utf-8') as f:
            # 第一行是词性个数，即状态个数
            line = f.readline()
            self.total_state = int(line.strip())
            # 第二行是词性列表，即状态列表
            line = f.readline()
            for item in line.strip().split():
                self.add_state(int(item))
            # 第三行
            line = f.readline()
            # 第四行是所有词性出现总次数
            line = f.readline()
            self.total_freq = int(line.strip())
            # 第五行是各词性出现次数，即初始概率, 采用加一平滑
            line = f.readline()
            for item, state in zip(line.strip().split(), self.states):
                self.state_freq[state] = int(item)
                self.add_start_prob(state,
                                    (int(item) + 1) / (
                                    self.total_freq + self.total_state))
            # 第六行到结束 状态转移概率 采用平滑
            for i in range(0, self.total_state):
                smoothing_param = 0.1
                line = f.readline()
                state_i = self.states[i]
                freq_i = self.state_freq[state_i]
                for item, state_j in zip(line.strip().split(), self.states):
                    prob = 0 if freq_i == 0 else (
                        ((1 - smoothing_param) * int(item) / freq_i) + (
                            smoothing_param * freq_i / self.total_freq))
                    self.add_transition_prob(state_i, state_j, prob)
        return True

    def prob_to_frequence(self, prob):
        """概率转换为频率"""
        return prob * (self.total_freq + self.total_state)


class DataStore(object):
    def __init__(self, data_dir=None):
        if data_dir:
            self.core_dct = Dictionary(os.path.join(data_dir, 'coreDict.dct'))
            self.bigram_dct = BiDictionary(
                os.path.join(data_dir, 'bigramDict.dct'))
            self.lexical_ctx = Context(os.path.join(data_dir, 'lexical.ctx'))
            self.nr_dct = Dictionary(os.path.join(data_dir, 'nr.dct'))
            self.nr_ctx = Context(os.path.join(data_dir, 'nr.ctx'))
            self.ns_dct = Dictionary(os.path.join(data_dir, 'ns.dct'))
            self.ns_ctx = Context(os.path.join(data_dir, 'ns.ctx'))
            self.tr_dct = Dictionary(os.path.join(data_dir, 'tr.dct'))
            self.tr_ctx = Context(os.path.join(data_dir, 'tr.ctx'))
            self.is_load = True
        else:
            self.core_dct = Dictionary()
            self.bigram_dct = BiDictionary()
            self.lexical_ctx = Context()
            self.nr_dct = Dictionary()
            self.nr_ctx = Context()
            self.ns_dct = Dictionary()
            self.ns_ctx = Context()
            self.tr_dct = Dictionary()
            self.tr_ctx = Context()
            self.is_load = True

    def load(self, data_dir):
        self.core_dct.load(os.path.join(data_dir, 'coreDict.dct'))
        self.bigram_dct.load(os.path.join(data_dir, 'bigramDict.dct'))
        self.lexical_ctx.load(os.path.join(data_dir, 'lexical.ctx'))
        self.nr_dct.load(os.path.join(data_dir, 'nr.dct'))
        self.nr_ctx.load(os.path.join(data_dir, 'nr.ctx'))
        self.ns_dct.load(os.path.join(data_dir, 'ns.dct'))
        self.ns_ctx.load(os.path.join(data_dir, 'ns.ctx'))
        self.tr_dct.load(os.path.join(data_dir, 'tr.dct'))
        self.tr_ctx.load(os.path.join(data_dir, 'tr.ctx'))
        self.is_load = True
        return self.is_load

    @property
    def is_loaded(self):
        return self.is_load

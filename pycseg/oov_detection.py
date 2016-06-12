# -*- coding: utf-8 -*-

from __future__ import division, unicode_literals, absolute_import
import math
import re

import pycseg.definitions as definitions
from pycseg.utils import hmm
from pycseg.data_store import Feature, WordsGraph


class OOVDetection(object):
    """未登录词识别"""

    def __init__(self, words_graph=None, d_store=None):
        self.nr_patterns = ("BBCD", "BBC", "BBE", "BBZ", "BCD", "BEE", "BE", "BG",
                            "BXD", "BZ", "CD", "EE", "FB", "Y", "XD"
        )
        self.nr_factor = {"BBCD": 0.003606, "BBC": 0.000021, "BBE": 0.001314, "BBZ": 0.000315,
                          "BCD": 0.656624, "BEE": 0.000021, "BE": 0.146116, "BG": 0.009136,
                          "BXD": 0.000042, "BZ": 0.038971, "CD": 0.090367, "EE": 0.000273,
                          "FB": 0.009157, "Y": 0.034324, "XD": 0.009735
        }
        self.tr_ns_pattern = r'BC*D'

        self.d_store = d_store
        self.words_graph = words_graph

    def oov_detection(self):
        self.words_graph.generate_words_dag(self.d_store.bigram_dct)
        seg_words_result = self.words_graph.words_segment()
        #print(' '.join([w.content for w in seg_words_result[0]['words']]))
        for seg_words in seg_words_result:
            words = seg_words['words']
            index = seg_words['index']
            nr_tag = self.oov_tagging(words,
                                      self.d_store.nr_dct,
                                      self.d_store.nr_ctx,
                                      self.d_store.core_dct)
            tr_tag = self.oov_tagging(words,
                                      self.d_store.tr_dct,
                                      self.d_store.tr_ctx,
                                      self.d_store.core_dct)
            ns_tag = self.oov_tagging(words,
                                      self.d_store.ns_dct,
                                      self.d_store.ns_ctx,
                                      self.d_store.core_dct)

            self.generate_nr_words(nr_tag, index)
            self.generate_tr_words(tr_tag, index)
            self.generate_ns_words(ns_tag, index)

    def generate_nr_words(self, nr_tag, seg_index):
        self.generate_oov_words('nr', nr_tag, seg_index,
                                self.d_store.nr_dct, self.d_store.nr_ctx, definitions.OOV_WORD_NR)

    def generate_tr_words(self, tr_tag, seg_index):
        self.generate_oov_words('tr', tr_tag, seg_index,
                                self.d_store.tr_dct, self.d_store.tr_ctx, definitions.OOV_WORD_NR)

    def generate_ns_words(self, ns_tag, seg_index):
        self.generate_oov_words('ns', ns_tag, seg_index,
                                self.d_store.ns_dct, self.d_store.ns_ctx, definitions.OOV_WORD_NS)

    def generate_oov_words(self, oov_type, oov_tag, seg_index, oov_dct, oov_ctx, oov_alias):
        """
        根据viterbi tag结果，合并未登录词

        @:param oov_type    未登录词类型， 'nr', 'tr', 'ns'
        @:param oov_tag     未登录词标注序列
        @:param seg_index   每个标注项对应的词在word_graph中的索引
        @:param oov_dct     未登录词词典
        @:param oov_alias   未登录词的别名, 如 "北京"用"未##地"来代替
        """
        #print('generate_oov_words: {} {}'.format(oov_type, oov_tag))
        i, len_tag = 0, len(oov_tag)
        while i < len_tag:
            pattern_match = None
            weight = 0
            # 遍历标注序列oov_tag， 找到匹配的模式
            if oov_type == 'nr':
                for pattern in self.nr_patterns:
                    if oov_tag.startswith(pattern, i):
                        pattern_match = pattern
                        poss = self.compute_possibility(i, seg_index, pattern_match, oov_dct, oov_ctx)
                        weight = - math.log(self.nr_factor[pattern_match]) + poss
                        #print('nr: {} {}'.format(pattern_match, weight))
                        break
            elif oov_type == 'tr' or oov_type == 'ns':
                match = re.match(r'BC*D', oov_tag[i:])
                if match:
                    pattern_match = match.group()
                    poss = self.compute_possibility(i, seg_index, pattern_match, oov_dct, oov_ctx)
                    # NOTE: 简化了tr和ns权值的平滑计算，可能会影响准确度
                    weight = math.log(1.0) + poss
            if not pattern_match:
                i += 1
                continue

            # print('match[{}] {} = {}'.format(i, oov_type, pattern_match))
            # 找到未登录词pattern后， 合并未登录词

            # 未登录词的左右边界
            # 左边界等于pattern中第一个tag对应的词的左边界
            # 右边界等于pattern中最后一个tag对应的词的右边界
            oov_left, oov_right = seg_index[i][0], seg_index[i+len(pattern_match)-1][1]

            # 判断是否已经是未登录词， 如果是， 则比较权值
            seg_word = self.words_graph.get_word(oov_left, oov_right)
            #if seg_word is not None:
            #    print('already {} {} {} : {} {}'.format(seg_word.weight, seg_word.content, seg_word.alias, oov_type, weight))
            if seg_word is None or weight < seg_word.weight:
                # 合并未登录词
                feature = Feature('nr') if oov_type == 'tr' else Feature(oov_type)
                self.words_graph.generate_word(oov_left, oov_right,
                                 feature, weight, oov_alias)
            i += len(pattern_match)

    def compute_possibility(self, start_position, seg_index, oov_pattern, oov_dct, oov_ctx):
        # 计算未登录词成词的权值
        weight, j = 0, start_position
        test_word = []
        for tag in oov_pattern:
            word_content = self.words_graph.get_word(seg_index[j][0], seg_index[j][1]).content
            oov_freq = oov_dct.get_frequence(
                word_content,
                self.oov_tag_encode(tag)
            )
            #print('tag:{} word:{} freq:{} start_prob:{}'.format(
            #    tag, word_content, oov_freq, oov_ctx.prob_to_frequence(oov_ctx.start_prob[self.oov_tag_encode(tag)])))
            test_word.append(self.words_graph.get_word(seg_index[j][0], seg_index[j][1]).content)
            #计算方法: dPOSPoss=log((double)(m_context.GetFrequency(0,m_nBestTag[i])+1))-log((double)(nFreq+1));
            poss = math.log(float(oov_ctx.prob_to_frequence(oov_ctx.start_prob[self.oov_tag_encode(tag)]))) - math.log(float(oov_freq + 1))
            weight += poss
            j += 1
        #print('compute_possibility() {} {} = {}'.format(oov_pattern, ''.join(test_word), weight))
        return weight

    @staticmethod
    def oov_tag_decode(code):
        return unichr(65 + code)

    @staticmethod
    def oov_tag_encode(tag):
        return ord(tag) - 65

    def oov_tagging(self, words, oov_dct, oov_ctx, core_dct):
        """
        标注未登录词状态序列
        @:param words   词
        @:param oov_dct 未登录词词典
        @:param oov_ctx 未登录词HMM model
        @:param core_dct    core词典

        @:return viterbi标注序列
        """
        h_model = self.generate_hmm_model(words, oov_dct, oov_ctx, core_dct)
        prob, path = hmm.viterbi(h_model.observations, h_model.states,
                                 h_model.start_prob, h_model.transition_prob,
                                 h_model.emission_prob)

        # 打印结果
        #print(' '.join(['{}/{}'.format(word.content, pos_decode(pos))
        #                 for (word, pos) in zip(words, path)]))
        oov_tag = ''.join([self.oov_tag_decode(pos) for pos in path])
        return oov_tag

    @staticmethod
    def generate_hmm_model(words, oov_dct, oov_ctx, core_dct):
        """
        生成未登录词HMM模型中的观察序列 和 发射概率

        @:return HMM model
        """
        smoothing_param = 0.1
        h_model = hmm.HMM(states=oov_ctx.states,
                          start_prob=oov_ctx.start_prob,
                          transition_prob=oov_ctx.transition_prob)
        for word in words:
            # 观察序列
            h_model.add_observations(word.content)
            # 发射概率
            # 发射概率平滑
            for pos in oov_ctx.states:
                h_model.add_emission_prob(pos, word.content,
                                          smoothing_param * 1 / oov_ctx.total_freq)
            # 发射概率计算
            word_attr = core_dct.get(word.content, [])
            oov_word_attr = oov_dct.get(word.content, [])
            total_freq = sum([freq for freq, pos in word_attr])
            oov_total_freq = sum([freq for freq, pos in oov_word_attr])

            for freq, pos in oov_word_attr + [
                (max(total_freq - oov_total_freq, 1), 0)]:
                if pos == 44:
                    continue
                state_freq = max(oov_ctx.state_freq.get(pos, 0), 1)
                h_model.add_emission_prob(pos, word.content,
                                          (1 - smoothing_param) * (
                                          freq + 0.1) / state_freq + smoothing_param * 1 / oov_ctx.total_freq)
        # self.print_hmm_model(h_model)
        return h_model

    def print_hmm_model(self, hmm_model):
        print('状态序列 - 词性列表:')
        print(hmm_model.states)
        print('观察序列 - 词:')
        print(' '.join(hmm_model.observations))
        print('发射概率 - 词在特定词性下的词频/此词性总数')
        for k, v in hmm_model.emission_prob.items():
            print('{}-{}:{}'.format(Feature(tag_code=k).tag, k, ','.join(
                ['{}={:e}'.format(word, prob) for word, prob in v.items()])))

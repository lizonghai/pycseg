# -*- coding: utf-8 -*-

from __future__ import unicode_literals

SENTENCE_BEGIN = '始##始'
SENTENCE_END = '末##末'
OOV_WORD_NR = '未##人'
OOV_WORD_NS = '未##地'
OOV_WORD_NX = '未##串'
OOV_WORD_T = '未##时'
OOV_WORD_M = '未##数'
OOV_WORD_NT = '未##它'
OOV_WORD_NZ = '未##团'
WORD_SEGMENTER = '@'

# Seperator type
SEPERATOR_C_SENTENCE = '。！？：；…'
SEPERATOR_C_SUB_SENTENCE = '、，（）“”‘’'
SEPERATOR_E_SENTENCE = '!?:;'
SEPERATOR_E_SUB_SENTENCE = ',()\'"'
SEPERATOR_LINK = '\n\r 　'

# Char Type
CT_SENTENCE_BEGIN = 1
CT_SENTENCE_END = 4
# SINGLE byte
CT_SINGLE = 5
CT_DELIMITER = CT_SINGLE + 1
CT_CHINESE = CT_SINGLE + 2
CT_LETTER = CT_SINGLE + 3
CT_NUM = CT_SINGLE + 4
CT_INDEX = CT_SINGLE + 5
CT_OTHER = CT_SINGLE + 12

MAX_FREQUENCE = 2079997

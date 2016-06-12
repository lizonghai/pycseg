# -*- coding: utf-8 -*-

# 需要引入feature unicode_literals
from __future__ import unicode_literals, print_function

import pycseg


def pycseg_test():
    content = "张华平在北京说的确实在理。"

    seg = pycseg.Pycseg()
    # 指定字典目录，加载字典
    seg.load(data_dir='data')
    # result格式: [(word, pos), (word, pos) ...(word, pos)]
    result = seg.process(content)
    str_result = seg.format_result(result)
    print(str_result)

if __name__ == "__main__":
    pycseg_test()

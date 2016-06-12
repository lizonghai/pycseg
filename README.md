# pycseg

pycseg是基于中科院分词[ICTCLAS](http://ictclas.nlpir.org/)开源版本的一个python实现。

项目目前实现了以下功能：

* N-最短路径分词
* NR/TR/NS三种类型的未登录词识别
* 词性标注
* 分词路径评分

**NOTE** 

项目目前仅是研究性实现，还**不**可用于生产环境。

### 测试环境

python 2.7

### 用法说明

参见`example.py`

```python
from __future__ import unicode_literals, print_function
import pycseg

def pycseg_test():
    content = "张华平在北京说的确实在理"

    seg = pycseg.Pycseg()
    seg.load(data_dir='data')
    result = seg.process(content)
    str_result = seg.format_result(result)
    print(str_result)
```

输出

```
张华平/nr 在/p 北京/ns 说/v 的/uj 确实/ad 在理/a 。/w
```

### 参考论文

[1] 张华平,刘群.基于N-最短路径方法的中文词语粗分模型[J].中文信息学报,2002,16(5)

[2] 刘群,张华平,俞鸿魁等.基于层叠隐马模型的汉语词法分析[J].计算机研究与发展,2004,41(8)

[3] 张华平,刘群.基于角色标注的中国人名自动识别研究[J].计算机学报,2004,27(1)

[4] 俞鸿魁,张华平,刘群等.基于层叠隐马尔可夫模型的中文命名实体识别[J].通信学报,2006,27(2)

-------------------------------------
本次作业直接用到的模块:  
re  
cfg_wcec  
pycparser  
graphviz

--------------------------------------
模块解释:  
ply：python对lex&yacc的封装  
pycparser: 利用ply对c源代码进行词法分析与语法分析，得到ast  
cfg_wcec: 利用pycparser得到的ast，分析得到cfg  
graphviz: 与graphviz软件进行交互的python模块

注：cfg_wcec模块并未上传到pypi仓库中，在github中可以找到。这是一个Linux系统上的包，我将其删减以及修改，在Windows上可以运行。作者还提供了将cfg转化为graphml语言的有向图（通过networkx模块或yEd软件可以显示），但作者写的只能用networkx模块显示，而且效果不好，所以我将cfg转化为dot语言，用graphviz绘制有向图。

-----------------------------------------
自己编写的模块解释：
gen_cfg: 分析c源代码 生成cfg 生成cfg的有向图  
gen_du：分析c源代码的cfg和ast 输出某个变量的du path

自己模块详解：  
gen_cfg.py  
GenCfg 输入c源代码生成cfg
CfgToDot 输入cfg生成有向图

gen_du.py  
GenDu 输入c源代码生成ast，利用ast与之前生成的cfg，分析得到du path

-------------------------------------
作业缺点:  
cfg缺点  
只能生成块与块之间的cfg，不能细分到每一个语句。  
无法识别for语句，只能将其视为普通语句。

du缺点  
生成的du path不包括while反馈。  
因为cfg是块与块之间的，所以一个块可能同时包含一个变量的定义与使用，但无法识别使用的先后顺序，所以不考虑这种情况，如果有这种情况，便将其视为一个块包含一个变量的定义。

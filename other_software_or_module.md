注：下面的内容若加模块两个字指的是python模块

--------------------------------------
gcc编译器就可以显示c源代码的cfg 但是是二进制的 而且格式不太好看 所以我选择自己写。  
命令如下：  
gcc -o -dv prog.c -o prog  
gcc -fdump-tree-cfg prog.c  
gcc -fdump-tree-vcg prog.c  

---------------------------------------
cflow：生成c源代码的流图
pycflow2dot模块：利用cflow和dot来绘制c源代码函数调用图  

-----------------------------------------
coflo: 生成c/c++源代码的cfg

-----------------------------------------
python关于graphviz的模块：  
graphviz  
Pygraphviz  
graphviz-python（官方）  
Pydot 

-------------------------------------------
python关于将graphml转化为有向图的模块：  
pygraphml模块：在jupyter里面运行  
graphml2svg模块：不能使用，问了作者没回  
yed软件  
networkx模块：networkx.read_graphml(parameter)  

---------------------------------------------
cdmcparser模块：生成python源代码的cfg  
pyan3模块： 生成python源代码的调用图  


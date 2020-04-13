# -*- coding: utf-8 -*-
"""
@time: 2020-03-28 下午 06:00
@author: leslie lee
"""
from cfg_wcec import cfg  # GenCfg要用到这个模块
import re  # GenCfg和CfgToDot要用到这个模块
from graphviz import Digraph  # CfgToDot要用到这个模块


class GenCfg:
    """
    生成输入C源代码, 生成Cfg
    """
    def __init__(self, source_code, cfg_path='deafult'):
        self.source_code = source_code  # C源代码路径

        # 如果没有给定cfg的保存路径
        if cfg_path == 'deafult':
            name_list = source_code.split('.')
            self.cfg_path = name_list[0] + '.cfg'
            self.name = name_list[0] + '(copy).c'

        # 如果给出了cfg的保存路径
        else:
            self.cfg_path = cfg_path  # 保存cfg的路径
            name = cfg_path.split('.')
            self.name = name[0]+'(copy).c'  # 根据保存路径创建c源代码的副本

    def gen_cfg(self):

        # ---------------------------------------------------------------------
        # 创立副本用于分析  副本通过正则表达式将注释和声明和头文件去掉 即只匹配main里面的
        # ----------------------------------------------------------------------
        # 读取c源代码
        with open(self.source_code, 'r', encoding='utf-8') as f:
            content = f.read()
            f.close()

        # 进行正则匹配 只匹配main{}大括号里面的内容
        pattern = re.compile(r"[{](.*)[}]", re.S)
        content1 = pattern.findall(content)[0]

        # 匹配到的content1是一个字符串 先将通过换行符分割为一个列表
        content2 = content1.split('\n')

        # 通过re正则表达式删去列表中每个元素中可能存在的注释  同时给每个句子后面加上之前删去的换行符
        all_contents = []  # 用于存放所有的content
        for index, val in enumerate(content2):
            # 对val进行遍历 如果val有/* */则key=1  如果val有//则key=2
            if '//' or '/*' in val:
                for i, j in enumerate(val):
                    if i+1 < len(val):
                        if j == '/' and val[i+1] == '*':
                            key = 1
                            break
                        elif j == '/' and val[i+1] == '/':
                            key = 2
                            break
            # 没有key的情况
            if 'key' not in vars():
                val1 = val
            # key=1的情况
            elif key == 1:
                pattern2 = re.compile("[/][*](.*)[*][/]")
                val1 = re.sub(pattern2, '', val)
            # key=2的情况
            elif key == 2:
                pattern3 = re.compile("[/][/](.*)")
                val1 = re.sub(pattern3, '', val)
            # 将val加入到content中
            all_contents.append('\n' + val1)

        # 将列表连接成字符串string
        # 加上开头与结尾 得到string1
        string = ''
        for val in all_contents:
            string = string + val
        string1 = 'main()\n{' + string + '}'

        # 将string1保存为副本
        with open(self.name, 'w') as f:
            f.write(string1)
            f.close()

    def show_cfg(self):
        # ---------------------------------
        # 展示cfg在屏幕上
        # ---------------------------
        graph = cfg.CFG(self.name)
        make_cfg = graph.make_cfg()
        make_cfg[0].show()

    def save_cfg(self):
        # ----------------------------
        # 保存cfg到txt中
        # ----------------------------
        print(self.cfg_path)
        graph = cfg.CFG(self.name)
        make_cfg = graph.make_cfg()
        with open(self.cfg_path, 'w') as f:
            make_cfg[0].show(buf=f)  # show函数的输入参数为file类
            f.close()


class CfgToDot:
    """
    将生成的cfg转化为Dot格式,然后生成pdf
    Args:
        file_path 即cfg文件的路径
    """
    def __init__(self, file_path):
        self.file_path = file_path

    def read_file(self):
        """
        按行读入cfg.txt
        """
        with open(self.file_path, 'r') as f:
            contents = f.readlines()  # 按行读入
            f.close()
        return contents

    def handle_file(self):
        """
        将文件进行处理 得到有用的列表
        """
        # -------------------------
        # 获取文件内容 格式为列表
        # --------------------------
        contents = self.read_file()
        # ----------------------------
        # 对contents进行删除换行符和替换main与end 得到contents1
        # ----------------------------
        contents1 = []
        for index, val in enumerate(contents):
            # 删除换行符
            c = val.replace('\n', '')
            # 替换main与end
            if 'main' in val:
                c = 'entry0'
            elif 'end' in val:
                c = 'end' + str(index)
            contents1.append(c)
        # -------------------------------
        # 对contents1进行删除pseudo节点
        # ------------------------------
        for val in contents1:
            if 'pseudo' in val:
                contents1.remove(val)
        # --------------------------------------------------
        # 对contents1处理 得到all_nodes列表 其元素为首字母加编号
        # 除entry节点外的所有节点
        # --------------------------------------------------
        all_nodes = []
        for index, val in enumerate(contents1):
            if 'common' in val:
                num = re.findall(r'\d+', val)  # 正则表达式匹配到是一个列表 只有一个元素
                all_nodes.append('C'+num[0])
            elif 'while' in val:
                num = re.findall(r'\d+', val)
                all_nodes.append('W'+num[0])
            elif 'if' in val:
                num = re.findall(r'\d+', val)
                all_nodes.append('I'+num[0])
            elif 'call' in val:
                num = re.findall(r'\d+', val)
                all_nodes.append('F'+num[0])
            elif 'end' in val:
                all_nodes.append(val)
        # ------------------------------------------------------------
        # 将all_nodes中的重复元素去除 以及只留一个end元素 得到all_nodes1列表
        # all_nodes1用于dot图的节点定义
        # 包含所有节点 其中只有一个end节点
        # ------------------------------------------------------------
        # 删除所有的end节点   (如果使用list(set))则对被赋值变量进行操作 不会改变赋值变量)
        all_nodes1_ = [i for i in all_nodes]
        for val in all_nodes1_:
            if 'end' in val:
                all_nodes1_.remove(val)
        all_nodes1_.append('end')  # 删除所有end节点后添加一个end节点
        all_nodes1_.insert(0, 'entry')  # 第一个节点命名为entry
        # 去除all_nodes1_中重复的节点 将不重复的节点放到all_nodes中
        all_nodes1 = []
        for val in all_nodes1_:
            if val not in all_nodes1:
                all_nodes1.append(val)

        # -------------------------------------------------------------------------------
        # 对contents1进行处理 得到all_nodes2列表 其中每个节点为node=[列号, 节点编号, 节点名称]
        # 除entry外包含所有结点
        # ------------------------------------------------------------------------------
        all_nodes2 = []
        for index, val in enumerate(contents1[1:]):  # 因为contents比all_nodes多一个entry节点
            if 'end' in val:
                node2 = [0, 0, val]
                all_nodes2.append(node2)
            elif 'end' not in val:
                column = val.find('-') + 1
                num = re.findall(r'\d+', val)[0]  # 注意这里的num是一个字符
                node2 = [column, int(num), all_nodes[index]]
                all_nodes2.append(node2)

        return all_nodes1, all_nodes2

    def get_edges(self):
        """
        通过自己定制规则 得到所有edges 用于dot画图
        """
        all_nodes1, all_nodes2 = self.handle_file()

        # ------------------------------------
        # 找出if-else语句的分支edge与汇聚edge
        # ------------------------------------
        edges1_1 = []  # 盛放分支edge
        edges1_1_ = []  # 格式与edges1_1不一样 后面要用到
        edges1_2 = []  # 盛放汇聚edge
        for index1, val1 in enumerate(all_nodes2):
            if 'I' in val1[2]:
                # 取出if节点的名称
                if_name = val1[2]
                # 取出if第一个分支节点c1
                c1 = all_nodes2[index1+1]
                c1_index = index1+1
                # 取出if第二个分支节点c2
                for index2, val2 in enumerate(all_nodes2):
                    if c1[0] == val2[0] and c1[1] < val2[1]:
                        c2 = val2
                        c2_index = index2
                        break  # 满足条件即跳出循环
                # -------------------------------
                # 如果存在c2
                if 'c2' in vars():
                    # 将两条分支边加入到edges1_1
                    edges1_1.append([if_name, c1[2]])
                    edges1_1.append([if_name, c2[2]])
                    # 将两个分支节点加入到edges1_1_
                    edges1_1_.append([c1, c2])
                    # ----------------------------------
                    # 找出c1的出节点
                    for index4, val4 in enumerate(all_nodes2):
                        # c1_为c1的下一个节点
                        c1_ = all_nodes2[c1_index+1]
                        # 情况1 如果c1_为end节点 那么就是出节点
                        if 'end' in c1_[2]:
                            out1 = [0, 0, 'end']  # 注意这里使用是end节点
                            break  # 找到立即退出循环
                        # 情况2 如果c1的行号小于等于c1_的行号 而且c1的列号小于c1_的列号 那么c1_就是出节点
                        if c1[1] <= c1_[1] and c1[0] < c1_[0]:
                            out1 = c1_
                            break
                        # 情况3 如果c1的行号大于c1_的行号 那么通过for循环遍历得到出节点
                        # 这种情况存在
                        elif c1_[1] < c1[1] < val4[1] and val4[0] < c2[0]:
                            out1 = val4
                            break
                    # --------------------------
                    # 找出c2的出节点
                    for index3, val3 in enumerate(all_nodes2):
                        # c2_为c2的下一个节点
                        c2_ = all_nodes2[c2_index+1]
                        # ----------------------------------
                        # 情况1 如果c2_为end节点 那么就是出节点
                        if 'end' in c2_[2]:
                            out2 = [0, 0, 'end']
                            break  # 找到立即退出循环
                        # 情况2 如果c2_的行与列都大于c2 那么就是出节点
                        if c2[1] <= c2_[1] and c2[0] < c2_[0]:
                            out2 = c2_
                            break
                        # 情况3 如果c2的行号大于c2_的行号 那么通过for循环遍历得到出节点
                        # 这种情况不存在吧!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                        # 由于我不会单元测试所以暂时先不管了
                        elif c2_[1] < c2[1] < val3[1] and val3[0] < c2[0]:
                            out2 = val3
                            break
                    # ----------------------------------
                    # 将两个汇聚边加入到edges1_2
                    edges1_2.append([c1[2], out1[2]])
                    edges1_2.append([c2[2], out2[2]])
                # ----------------------------------------
                # 如果不存在c2
                else:
                    # 将一个分支边加入到edges1_1
                    edges1_1.append([if_name, c1[2]])
                    # 将一个分支节点加入到edges1_1_
                    edges1_1_.append([c1])
                    # -----------------------------------
                    # 找出c1的出节点
                    for index4, val4 in enumerate(all_nodes2):
                        # c1_为c1的下一个节点
                        c1_ = all_nodes2[c1_index+1]
                        # 情况1 如果c1_为end节点 那么就是出节点
                        if 'end' in c1_[2]:
                            out1 = [0, 0, 'end']
                            break  # 找到立即退出循环
                        # 情况2 如果c1_的行与列都大于c1 那么就是出节点
                        if c1[1] <= c1_[1] and c1[0] < c1_[0]:
                            out1 = c1_
                            break
                        # 情况3 如果c1的行号大于c1_的行号 那么通过for循环遍历得到出节点
                        # 情况3不存在
                        elif c1_[1] < c1[1] < val4[1] and val4[0] < c1[0]:
                            out1 = val4
                            break
                    # ------------------------------------
                    # 将一个汇聚边加入到edges1_2中
                    edges1_2.append([c1[2], out1[2]])

        # ----------------------------------
        # 找出while的负反馈edge
        # ----------------------------------
        edges2 = []  # 盛放while负反馈edge
        for index, val in enumerate(all_nodes2):
            if index != 0:
                node_ = all_nodes2[index - 1]
                if 'W' in val[2] and val[0] > node_[0] and \
                        val[1] < node_[1]:
                    edges2.append([node_[2], val[2]])
        # 删除edges2的重复元素 且不改变元素的位置顺序
        edges2_ = []
        for edge in edges2:
            if edge not in edges2_:
                edges2_.append(edge)
        edges2 = edges2_

        # -----------------------------------
        # 找出与end节点相连的edge
        # ----------------------------------
        edges3 = []  # 盛放end节点相连的edge
        for index, val in enumerate(all_nodes2):
            if 'end' in val[2] and index > 1:
                val_ = all_nodes2[index-1]
                edges3.append([val_[2], 'end'])

        # -------------------------------
        # all_nodes4为all_nodes2删除所有while反馈的节点后的列表  all_nodes4之后会作为构造边的列表
        # --------------------------------
        remove4 = []
        all_nodes4 = []
        for index, node in enumerate(all_nodes2):
            if index + 1 < len(all_nodes2):
                node_ = all_nodes2[index + 1]
                if node[1] > node_[1] and 'W' in node_[2]:
                    remove4.append(node_)
        for node in all_nodes2:
            if node not in remove4:
                all_nodes4.append(node)

        # ----------------------------------------------
        # 构造列表del_cond_nodes 用于盛放需要删掉的all_nodes2中的条件节点中的一个
        # 情况1 删除离if节点最远的分支节点  即包括这种情况(该分支节点前一个不是if节点)
        # 情况2 删除两个分支节点中行号最大的节点
        # 情况3 删除后面接end节点的分支节点
        # -----------------------------------------------
        del_cond_nodes = []
        for index, edge in enumerate(edges1_1_):
            # --------------------------------
            # 在if只有一个条件分支时
            if len(edge) == 1:
                node_index = all_nodes2.index(edge[0])
                node_index_ = node_index - 1
                node_val_ = all_nodes2[node_index_]
                # 情况1
                if 'if' not in node_val_[2]:
                    del_cond_nodes.append(edge[0])
            # ---------------------------------------------------
            # if有两个条件分支时
            elif len(edge) == 2:
                # 情况1
                for node in edge:
                    node_index = all_nodes2.index(node)
                    node_index_ = node_index - 1
                    node_val_ = all_nodes2[node_index_]
                    # 如果节点前一个不是if节点 那么删除
                    if 'I' not in node_val_[2]:
                        del_cond_nodes.append(node)
                # 情况3
                for node in edge:
                    node_index = all_nodes2.index(node)
                    node_index__ = node_index + 1
                    node_val__ = all_nodes2[node_index__]
                    if 'end' in node_val__:
                        del_cond_nodes.append(node)
                # 情况2
                if edge[0] not in del_cond_nodes and edge[1] not in del_cond_nodes:
                    if edge[0][1] > edge[1][1]:
                        del_cond_nodes.append(edge[0])

        # -----------------------------------------------
        # 在之前all_nodes4的基础上删除del_cond_nodes中的节点
        # -----------------------------------------------
        for node in all_nodes4:
            if node in del_cond_nodes:
                all_nodes4.remove(node)

        # ----------------------------------------------
        # 将all_nodes4中的节点一个接一个连成edge
        # 如果遇到end节点那么从下一个节点开始继续连接
        # ----------------------------------------------
        edges4 = []
        i_ = 0
        for i in range(len(all_nodes4)):
            # 如果i_+1小于all_nodes4的长度
            if i_ + 1 < len(all_nodes4):
                # 如果下一个节点是endn那么改名为end
                if 'end' in all_nodes4[i_ + 1][2]:
                    edges4.append([all_nodes4[i_][2], 'end'])
                # 如果下一个节点不是endn那么不用改名
                else:
                    edges4.append([all_nodes4[i_][2], all_nodes4[i_ + 1][2]])
            # 加1
            i_ = i_ + 1

        # -------------------------------
        # 删除edges4中不符合规矩的edge  '两个end相连'和'end在前' 这两种情况可以简化为一种即'end在前'
        # --------------------------------
        for edge in edges4:
            if 'end' in edge[0]:
                edges4.remove(edge)

        # ----------------------------------
        # 最后将所有的边汇集到一起 删除重复的
        # 我不需要管顺序 graphviz这个模块会帮我整理的 就好比只要我方程数等于未知数个数,那么我就能求出正确解
        # (但有时候计算难度大时 只能用数值解代替  哈哈这是后话了)
        # ----------------------------------
        # 将不重复的edges1_1 edges1_2 edges2 edges3加入到edges4
        for node in edges1_1:
            if node not in edges4:
                edges4.append(node)
        for node in edges1_2:
            if node not in edges4:
                edges4.append(node)
        for node in edges2:
            if node not in edges4:
                edges4.append(node)
        for node in edges3:
            if node not in edges4:
                edges4.append(node)
        # 将开始节点entry与第一个节点形成的第一条边加入edges4
        edges4.insert(0, ['entry', all_nodes2[0][2]])

        # -------------------------------------
        # 循环 将edges4中不重复的边放到edges5中
        # ------------------------------------
        edges5 = []
        for edge in edges4:
            if edge not in edges5:
                edges5.append(edge)

        return all_nodes1, edges5

    def call_dot(self, filename='test'):
        """
        调用graphviz模块 传入nodes和edges
        """
        nodes, edges = self.get_edges()
        g = Digraph('CFG')
        for node in nodes:
            g.node(name=node)
        for edge in edges:
            g.edge(edge[0], edge[1])
        g.view(filename=filename)


if __name__ == '__main__':

    # file = 'c_files/collatz.cfg'
    # ctd = CfgToDot(file)  # 实例化
    # ctd.call_dot('test2')  # 将cfg转化为dot语言 再生成pdf

    """
    # 生成cfg文件
    c = '' # c源代码的路径
    gcfg = GenCfg(c)
    gcfg.gen_cfg()  # 生成
    gcfg.show_cfg() # 显示
    gcfg.save_cfg() # 保存
    
    # 生成有向图
    c_copy = '' # c副本的路径
    ctd = CfgToDot(c_copy)
    ctd.call_dot('test2')  # 生成有向图
    """

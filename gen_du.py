# -*- coding: utf-8 -*-
"""
@time: 2020-04-12 下午 07:00
@author: leslie lee
"""
from c_json import file_to_json  # c_json模块是对pycparser的输出的加工 将ast转化为json格式
import re
from gen_cfg import CfgToDot


class GenDu:

    # 传入c副本文件的路径
    def __init__(self, c_copy_path, save_ast_path='default'):
        # c副本的路径
        self.c_copy = c_copy_path
        # 如果默认 则保存ast的路径同c_copy的路径
        if save_ast_path == 'default':
            self.c_copy_ast = self.c_copy.split('.')[0] + '.ast'
        # 否则 用传入的路径
        else:
            self.c_copy_ast = save_ast_path

    # 生成c副本文件的ast 从ast中提取每个变量的定义使用情况
    def parse_ast(self):
        """
        返回变量的定义与使用情况 格式为[变量, (行号, 列号), 使用或定义]
        """
        # 将ast转化为json格式
        parse = file_to_json(filename=self.c_copy, indent=4)

        # 将ast保存为txt
        with open(self.c_copy_ast, 'w') as f:
            f.write(parse)
            f.close()

        # 从.ast文件中按每行读取
        with open(self.c_copy_ast, 'r') as f:
            contents = f.readlines()
            f.close()

        # ps存放变量的列表  ps的元素为[变量, (行号, 列号), 使用或定义]
        ps = []
        for index, val in enumerate(contents):
            # 如果val中有'name'字符
            if 'name' in val:
                # 如果nodetype不是FuncCall 而且当前行里面没有declname
                # 满足两个条件才提取变量
                if 'FuncCall' not in contents[index - 4] \
                        and 'declname' not in val:
                    # 用正则表达式提取变量p
                    pattern = re.compile(r'["name":"](.*)[",]')
                    p = pattern.findall(val)[0]  # 匹配到的是只有一个元素的列表
                    # 提取变量p所在c副本文件中的行号与列号
                    num = contents[index + 1].split(':')
                    if len(num) != 4:
                        ps.append([p, (0, 0), 'None'])
                    else:
                        # 如果变量p的前5行是赋值 那么就是定义变量 否则就是使用变量
                        if 'Assignment' in contents[index - 5]:
                            r_num = num[2]  # p的行号
                            c_num = num[3][:-2]  # p的列号
                            ps.append([p, (int(r_num), int(c_num)), 'D'])  # num是一个字符 需要转化为int
                        else:
                            r_num = num[2]  # p的行号
                            c_num = num[3][:-2]  # p的列号
                            ps.append([p, (int(r_num), int(c_num)), 'U'])

        # 对ps中的变量再进行加工 保存到ps1中
        ps1 = []
        for val in ps:
            if val[1] != (0, 0):
                ps1.append([val[0][8:-1], val[1], val[2]])

        # ps2只保存不重复的变量 且没有行号 列号信息
        # 之前觉得这个没什么用 其实还是有用的
        ps2 = []
        for val in ps1:
            if val[0] not in ps2:
                ps2.append(val[0])

        # 如果变量被使用 但是在这之前没有被定义 那么在entry结点处被定义
        # 存放在entry中定义的变量
        undefine = []
        # 遍历所有变量
        for p in ps2:
            # 遍历ps1
            for val in ps1:
                # 如果是当前的变量p
                if p == val[0]:
                    # 如果p为使用
                    if val[2] == 'U':
                        undefine.append(p)
                        break  # 立即退出ps1的for循环
                    else:
                        break  # 立即退出ps1的for循环

        # 将未定义变量放到ps1的第一的位置
        if len(undefine) != 0:
            ps1.insert(0, [i for i in undefine])

        return ps1

    # 生成du文件
    def du_state(self, cfg_file, save_du_path='default', save_rdu=False):

        # 获取all_nodes1
        all_nodes1, all_nodes2 = CfgToDot(cfg_file).handle_file()
        # 获取变量的定义使用情况
        define_use = self.parse_ast()

        # 节点行号
        node_row = []
        for val in all_nodes1[1:-1]:
            node_row.append(int(val[1:]))

        # 变量行号
        p_row = []
        for val in define_use[1:]:
            p_row.append(val[1][0])

        # 节点处的变量 元素为[节点行号,[变量, 定义/使用]]
        node_p = []
        # 遍历变量的行号
        for index, val in enumerate(p_row):
            # 遍历节点的行号
            for index_, val_ in enumerate(node_row):
                if val < val_:
                    d_u = define_use[index + 1]  # 取出变量的定义使用情况
                    node_p.append([node_row[index_ - 1], [d_u[0], d_u[2]]])
                    break

        # 将node_p的所有相同结点整合到一起 即node_p1
        node_p1 = []
        for val in node_p:
            _list = []
            _list.append(val[1])
            for val_ in node_p:
                if val != val_ and val[0] == val_[0]:
                    _list.append(val_[1])
            node_p1.append(_list)
        # 删去node_p1中重复的 得到node_p2
        node_p2 = []
        for val in node_p1:
            if sorted(val) not in node_p2:
                node_p2.append(sorted(val))

        # ---------------------------------------------
        # node_p3 格式为列表  其中每个元素为'node,D:[xxx],U:[xxx]'
        # ---------------------------------------------
        # node_p3列表的元素为一个字符串格式为
        node_p3 = []
        # 加入首节点与在首节点处定义的变量
        if len(define_use[0]) != 0:
            node_p3.append('entry; D:' + str(define_use[0]) + ';')
        else:
            node_p3.append('entry')
        # 遍历all_nodes1
        for index, val in enumerate(all_nodes1[1:-1]):
            # 遍历node_p
            d_list = []
            u_list = []
            for index_, val_ in enumerate(node_p):
                # 如果节点号相同
                if int(val[1:]) == val_[0]:
                    # 如果是定义
                    if val_[1][1] == 'D' and val_[1][0] not in d_list:
                        d_list.append(val_[1][0])
                    elif val_[1][1] == 'U' and val_[1][0] not in u_list:
                        u_list.append(val_[1][0])
            # 将节点号,变量定义使用情况结合成一个字符串加入node_p3
            # 如果d与u两个列表都有元素
            if len(u_list) != 0 and len(d_list) != 0:
                node_p3.append(val + '; D:' + str(d_list) + '; U:' + str(u_list))
            # 如果只有u有元素
            elif len(u_list) != 0 and len(d_list) == 0:
                node_p3.append(val + '; U:' + str(u_list))
            # 如果只有d有元素
            elif len(u_list) == 0 and len(d_list) != 0:
                node_p3.append(val + '; D:' + str(d_list) + ';')
            # 如果d与u都没有元素
            elif len(u_list) == 0 and len(d_list) == 0:
                node_p3.append(val)
        # 加入end结点
        node_p3.append('end')

        # -----------------------------
        # 遍历node_p3的元素 保存到文件的每行中
        # ------------------------------
        # 判断du文件的保存位置
        if save_du_path == 'default':
            du_path = self.c_copy.split('.')[0] + '.du'
        else:
            du_path = save_du_path
        # 遍历node_p3 连成一个字符串
        string = ''
        for val in node_p3:
            string = string + val + '\n'
        # 保存du文件
        with open(du_path, 'w') as f:
            # 写入字符串
            f.write(string)
            # 关闭文件
            f.close()

        # 如果save_rows_du为True 那么保存每行的变量定义使用情况
        if save_rdu == True:
            # 从define_use取出行数
            row_num = []
            for val in define_use[1:]:
                # 得到无重复的行数
                if val[1][0] not in row_num:
                    row_num.append(val[1][0])
            # rows_du盛放每行的变量定义使用情况
            rows_du = []
            # rows_du的首个元素
            if len(define_use[0]) != 0:
                rows_du.append('entry; D:' + str(define_use[0]))
            else:
                rows_du.append('entry')
            # rows_du后面的元素
            for val in row_num:
                rows_d = []
                rows_u = []
                for val_ in define_use[1:]:
                    if val == val_[1][0]:
                        if val_[2] == 'D' and val_[0] not in rows_d:
                            rows_d.append(val_[0])
                        elif val_[2] == 'U' and val_[0] not in rows_u:
                            rows_u.append(val_[0])
                #
                if len(rows_d) != 0 and len(rows_u) != 0:
                    rows_du.append('第' + str(val) + '行; D:' + str(rows_d) + '; U:' + str(rows_u))
                elif len(rows_d) != 0 and len(rows_u) == 0:
                    rows_du.append('第' + str(val) + '行; D:' + str(rows_d))
                elif len(rows_d) == 0 and len(rows_u) != 0:
                    rows_du.append('第' + str(val) + '行; U:' + str(rows_u))
            # rows_du在结尾处加上end
            rows_du.append('end')
            # 将rows_du写入文件
            string = ''
            for val in rows_du:
                string = string + val + '\n'
            with open(du_path.split('.')[0] + '.rdu', 'w', encoding='utf-8') as f:
                f.write(string)
                f.close()

        return du_path

    # 通过dot.txt 分析得到所有的变量路径  注：除了While反馈
    def para_path(self, dot_txt):

        path = dot_txt
        # 输入之前在cfg中的dot_txt文件
        with open(path) as f:
            contents = f.readlines()
            f.close()

        contents1 = []
        for val in contents:
            if '->' in val:
                val1 = val.replace('\n', '')
                val2 = val1.replace('\t', '')
                contents1.append(val2.split(' -> '))  # 注意还有空格 ' -> '

        # 第一条变量路径
        p1 = []
        # 剩余的局部路径
        rest_edge = []
        for index, val in enumerate(contents1):
            if val[1] != 'end':
                p1.append(val[0])
            # 如果等于end 那么将当前val加入p1 然后立即退出循环
            else:
                p1.append(val[0])
                p1.append(val[1])
                rest_edge = contents1[index + 1:-1]
                break

        # rest_edge包含了反馈 现在去掉反馈
        rest_edge1 = []
        for val in rest_edge:
            if int(val[1][1:]) > int(val[0][1:]):
                rest_edge1.append(val)

        # 剩余的局部连接
        local_pn = []
        for val1 in rest_edge1:
            if 'C' in val1[1]:
                elem = [val1[0], val1[1]]
                for val2 in rest_edge1:
                    if val1[1] == val2[0]:
                        elem.append(val2[1])
                        local_pn.append(elem)
                if len(elem) == 2:
                    local_pn.append(elem)

        # 用local_pn中的元素 替换p1中的某些节点 从而得到所有变量路径pn
        pn = [p1]  # pn中当开始只有一个元素p1
        for val in local_pn:
            for pi in pn.copy():  # 用一个copy解决"for循环区间不能改变"的现象
                index1 = pi.index(val[0])
                index2 = pi.index(val[-1])
                val1 = pi[0:index1] + val + pi[index2 + 1:]
                pn.append(val1)

        # 去除重复的路径
        pn1 = []
        for val in pn:
            if val not in pn1:
                pn1.append(val)

        return pn1

    # 通过du文件 分析得到关于某个变量的,与para_path对应的du_path
    def du_path(self, du_file, dot_txt, para_name):
        # -------------------------------------------
        # 读取du文件 得到变量i的定义 使用情况
        with open(du_file) as f:
            du = f.readlines()  # 读取每行的内容
            f.close()

        para_d = []
        for index, val in enumerate(du):
            # 匹配 定义
            pattern1 = re.compile('D:(.*);')
            res1 = pattern1.findall(val)
            if len(res1) != 0:
                # 如果变量在该行定义
                if para_name in eval(res1[0]):
                    node = val.split(';')[0]
                    para_d.append(node)

        para_u = []
        for index, val in enumerate(du):
            # 匹配 定义
            pattern2 = re.compile('U:(.*)')
            res2 = pattern2.findall(val)
            if len(res2) != 0:
                # 如果变量在该行使用
                if para_name in eval(res2[0]):
                    node = val.split(';')[0]
                    para_u.append(node)

        # ------------------------------------------
        # 所有变量路径
        pn = self.para_path(dot_txt)

        # -------------------------------------------
        # dn用于存储定义使用情况  对应pn
        # di对应pi  di的元素为'd'或'u'或0 不讨论['d', 'u']这种情况
        # 因为我取的是结点处的,是一个块的du情况 所以同时存在的那种情况暂不讨论
        dn = []
        for pi in pn:
            di = []
            for index, val in enumerate(pi):
                # 考虑了结点处有d或有u或都有,都有的时候去掉u
                if val in para_d:
                    di.append((index, 'd'))
                elif val in para_u and val not in para_d:
                    di.append((index, 'u'))
                elif val not in para_d and para_u:
                    di.append((index, 0))
            dn.append(di)

        # ------------------------------------------
        # define_use 输入di pi 生成对应的du路径
        def define_use(di, pi):
            # d2为di去除0元素
            d2 = []
            for val in di:
                if val[1] != 0:
                    d2.append(val)
            # p1为pi
            p1 = pi
            # du_index 存放一条du路径的下标  du_indexs 存放所有的
            du_index = []
            du_indexs = []
            for index1, val1 in enumerate(d2):
                if val1[1] == 'd':
                    du_index = [val1[0]]
                    for index2, val2 in enumerate(d2[index1 + 1:]):
                        if val2[1] == 'd':
                            break
                        else:
                            du_index.append(val2[0])
                    du_indexs.append(du_index)

            # 只取开头与结尾的下标 存到du_indexs1中
            du_indexs1 = []
            for val in du_indexs:
                if len(val) > 1:
                    du_indexs1.append([val[0],val[-1]])
                    num = len(val)-1
                    val1 = val.copy()
                    for i in range(1,num):
                        val1.pop(-1)
                        du_indexs1.append([val1[0], val1[-1]])

            # du_path
            du_path = []
            for val in du_indexs1:
                index1, index2 = val[0], val[1]
                du_path.append(p1[index1:index2+1])

            return du_path

        # 做个循环调用define_use 生成所有的du路径
        define_use_paths = []
        for i in range(len(pn)):
            define_use_path = define_use(dn[i], pn[i])
            define_use_paths.append(define_use_path)

        # 将define_use_paths进行去重
        define_use_paths1 = []
        for val in define_use_paths:
            for val1 in val:
                if val1 not in define_use_paths1:
                    define_use_paths1.append(val1)
        return define_use_paths1


if __name__ == '__main__':
    c_copy_path = 'c_files/collatz(copy).c'
    gdu = GenDu(c_copy_path)
    c_cfg_path = 'c_files/collatz.cfg'
    c_copy_du_path = gdu.du_state(c_cfg_path)
    c_copy_dot_path = 'test2.txt'
    para_name = 'max'
    paths = gdu.du_path(c_copy_du_path, c_copy_dot_path, para_name)
    for i in paths:
        print(i)




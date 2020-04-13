# -*- coding: utf-8 -*-
"""
@time: 2020-04-12 下午 11:23
@author: leslie lee
"""
from gen_cfg import GenCfg, CfgToDot
from gen_du import GenDu


def run_cfg(c_file):
    # 生成cfg
    gcfg = GenCfg(c_file)
    gcfg.gen_cfg()  # 生成
    gcfg.save_cfg()  # 保存

    # 将cfg转化为有向图
    c_copy_cfg = c_file.split('.')[0] + '.cfg'
    ctd = CfgToDot(c_copy_cfg)
    c_copy_dot = c_file.split('.')[0]+'_dot'
    ctd.call_dot(c_copy_dot)  # 生成有向图


def run_du(c_file, para_name):
    c_copy = c_file.split('.')[0] + '(copy).c'
    c_copy_dot = c_file.split('.')[0] + '_dot'
    c_copy_cfg = c_file.split('.')[0] + '.cfg'

    # 生成du paths
    gdu = GenDu(c_copy)
    c_copy_du = gdu.du_state(c_copy_cfg)
    paths = gdu.du_path(c_copy_du, c_copy_dot, para_name)
    for path in paths:
        print(path)


if __name__ == '__main__':
    c_file = 'c_files/collatz.c'
    run_cfg(c_file)

    para_name1 = 'n'
    para_name2 = 'maxi'
    run_du(c_file, para_name2)
#!/usr/local/bin/python2.7
# -*- coding=utf-8 -*-
import ansible.runner
import ansible.playbook
import ansible.inventory
from ansible import callbacks
from ansible import utils
import json
import sys
import linecache
import pymysql

### 获取数据库存储的项目路径及更新软件包路径 ####
PNAME = sys.argv[1]
NAME = PNAME.split('_')
con = pymysql.connect(host='127.0.0.1', user='****', password='*****', database='asjf_update')
sql = "select * from asjf_update.jinrong where name='%s'" % (NAME[0])
cur = con.cursor()
NUM = cur.execute(sql)
result = cur.fetchone()
cur.close()
con.close()

### 判断项目 使用相应发布模板 ###

play = 'aishang.yaml'

### 获取 hosts 文件中对应项目的IP列表 ###


def Hostlist(app):
    IP = []
    gname = '[%s]' % (app)
    str = linecache.getlines("/home/update/conf/hosts")
    num = str.index("%s\n" % (gname))
    for line in range(num + 1, len(str)):
        if "[" in str[line]:
            break
        else:
            S = str[line].split()
            IP.append(S[0])
    return IP


### 设置回调显示方法 ###
stats = callbacks.AggregateStats()
playbook_cb = callbacks.PlaybookCallbacks(verbose=utils.VERBOSITY)
runner_cb = callbacks.PlaybookRunnerCallbacks(stats, verbose=utils.VERBOSITY)


# creating the playbook instance to run, based on "yml" file
### 创建playbook 任务并调用相应 'yaml' 模板 ###


def execute(IPX):
    pb = ansible.playbook.PlayBook(
        playbook="/home/update/playbooks/%s" % (play),
        host_list='/home/update/conf/hosts',
        stats=stats,
        callbacks=playbook_cb,
        runner_callbacks=runner_cb,
        inventory=None,
        check=False,
        extra_vars=eval(IPX)
    )
    ### 调用playbook并执行 playbook 模板
    return pb.run()

### 按脚本顺序逐台执行剧本

if __name__ == '__main__':
    IP = Hostlist(NAME[0])
    for IPs in IP:
        IPX = '{"host":"%s", "app_addr":"%s", "soc_addr":"%s", "name":"%s", "entry_name":"%s"}' % (
        IPs, result[2], result[3], result[1], PNAME)
        res = execute(IPX)
    print json.dumps(res, sort_keys=True, indent=4, separators=(',', ': '))

#!/bin/env python3
# -*- coding: UTF-8 -*-

import random
import os
import shutil
import hashlib

filenum = 0
num = 0
# ssl证书路径(末尾需加/)
sslpath = '/opt/xuissl/cert/'
# 站点ssl路径(末尾需加/)
sitepath = '/www/server/panel/vhost/cert/yun.fcwys.cc/'
# nginx路径(末尾需加/)
nginxpath = '/www/server/nginx/'

# 获取证书数量,证书名称统一命名为 1.key 1.pem 2.key 2.pem 以此类推
filenum=int(len(os.listdir(sslpath))/2)

# 证书对比
while True:
    #随机数
    num = random.randint(1, filenum)
    now = sslpath + str(num) +'.key'
    sitefile = open(f'{sitepath}privkey.pem','rb')
    nowfile = open(now,'rb')
    # 对比文件MD5是否一致
    if not hashlib.md5(sitefile.read()).hexdigest() == hashlib.md5(nowfile.read()).hexdigest():
        break;
    sitefile.close()
    nowfile.close()
    print('[INFO] SSL Repeat: '+str(num))
print('[INFO] SSL NUM: '+str(num))

#复制更换私钥
shutil.copyfile(f'{sslpath}{str(num)}.key',f'{sitepath}privkey.pem')
print('[INFO] SSL Key writed.')

#复制更换证书
shutil.copyfile(f'{sslpath}{str(num)}.pem',f'{sitepath}fullchain.pem')
print('[INFO] SSL Cert writed.')

# 重载Nginx服务
os.system(f'{nginxpath}sbin/nginx -p {nginxpath} -s reload')
print('[INFO] Nginx reloaded.')

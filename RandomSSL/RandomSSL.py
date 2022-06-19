# -*- coding: UTF-8 -*-
import random
import os
import filecmp
        
dirnum = 0
filenum = 0
num = 0
#ssl证书路径
sslpath = '/your/ssl/path/'
#站点ssl路径
sitepath = '/your/site/path'
# nginx路径(末尾需加/)
nginxpath = '/www/server/nginx/'

filenum=int(len(os.listdir(sslpath))/2)

while True:
    #随机数
    num = random.randint(1, filenum)
    now = sslpath+ str(num) +'.key'
    if not filecmp.cmp(sitepath+'privkey.pem', now):
        break;
    print('[INFO] SSL Repeat ['+str(num)+']!')
print('[INFO] SSL NUM: '+str(num))

#更换私钥
with open(sslpath + str(num) + '.key') as f:
    contents = f.read().rstrip()
    with open(f'{sitepath}privkey.pem','w') as k:
        k.write(contents)
        k.close()
        print('[INFO] SSL Key writed.')

#更换证书
with open(sslpath + str(num) + '.pem') as f:
    contents = f.read().rstrip()
    with open(f'{sitepath}fullchain.pem','w') as k:
        k.write(contents)
        k.close()
        print('[INFO] SSL Cert writed.')

# 重载Nginx服务
os.system(f'{nginxpath}sbin/nginx -p {nginxpath} -s reload')
print('[INFO] Nginx reloaded.')
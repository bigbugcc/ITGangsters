# -*- coding: UTF-8 -*-
import datetime
from OpenSSL import crypto
#  pip install pyopenssl
import random
import os
import shutil
import hashlib

num = 0
filenum = 0
# ssl证书集路径(末尾需加/)
sslpath = '/www/cert/path/ssl/'
# 站点ssl路径(末尾需加/)
sitepath = '/www/server/panel/vhost/cert/www.example.com/'
# nginx路径(末尾需加/)
nginxpath = '/www/server/nginx/'



# 检查证书是否过期
def check_ssl_cert_expiry(cert_file):
    # 检查证书文件是否存在
    if not os.path.isfile(cert_file):
        raise TypeError(cert_file + " does not exist")
    with open(cert_file, 'r') as f:
        cert_data = f.read()
    x509 = crypto.load_certificate(crypto.FILETYPE_PEM, cert_data)
    bytes = x509.get_notAfter()
    timestamp = bytes.decode('utf-8')
    time = datetime.datetime.strptime(timestamp, '%Y%m%d%H%M%S%z').date().isoformat()

    # 检查证书是否过期
    if time <= datetime.datetime.now().isoformat():
        print('证书已过期', time)
        return False
    else:
        print('证书有效期至：', time)
        return True

# 移除过期证书后整理文件夹
def FileRename():
    start_num = 1
    for i in range(0, len(os.listdir(sslpath)), 2):
        # 获取key和pem文件名
        file = os.listdir(sslpath);
        # 排序
        file.sort()
        key_filename = file[i]
        pem_filename = file[i + 1]
        # 构造新的文件名
        new_filename = str(start_num) + os.path.splitext(key_filename)[1]
        # 重命名文件
        os.rename(os.path.join(sslpath, key_filename), os.path.join(sslpath, new_filename))
        os.rename(os.path.join(sslpath, pem_filename), os.path.join(sslpath, new_filename[:-4] + ".pem"))
        # 增加序号
        start_num += 1
    print('[INFO] SSL Rename.')


# 随机更换证书
def RandomSSL():
    # 证书对比
    while True:
        # 获取证书数量,证书名称统一命名为 1.key 1.pem 2.key 2.pem 以此类推
        filenum = int(len(os.listdir(sslpath)) / 2)
        num = random.randint(1, filenum)
        now = sslpath + str(num) + '.key'
        nowpem = sslpath + str(num) + '.pem'
        # 检查证书是否过期
        if not check_ssl_cert_expiry(nowpem):
            # 删除该证书
            os.remove(nowpem)
            os.remove(now)
            print('[INFO] SSL Delete >> : ' + str(num))
            # 重新整理目录
            FileRename()
            continue
        
        sitefile = open(f'{sitepath}privkey.pem', 'rb')
        nowfile = open(now, 'rb')
        
        # 对比文件MD5是否一致
        if not hashlib.md5(sitefile.read()).hexdigest() == hashlib.md5(nowfile.read()).hexdigest():
            break
        sitefile.close()
        nowfile.close()
        print('[INFO] SSL Repeat: ' + str(num))
    print('[INFO] SSL NUM: ' + str(num))

    # 复制更换私钥
    shutil.copyfile(f'{sslpath}{str(num)}.key', f'{sitepath}privkey.pem')
    print('[INFO] SSL Key writed.')

    # 复制更换证书
    shutil.copyfile(f'{sslpath}{str(num)}.pem', f'{sitepath}fullchain.pem')
    print('[INFO] SSL Cert writed.')

    # 重载Nginx服务
    os.system(f'{nginxpath}sbin/nginx -p {nginxpath} -s reload')
    print('[INFO] Nginx reloaded.')


RandomSSL()
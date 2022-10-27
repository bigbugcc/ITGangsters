import os
import sys
import requests
import json
import socket
import time
import threading

domain=''
pswd=''
ipv4=''
ipv6=''
ipapi='http://ip.zxinc.org/getip'
check=600   # 默认十分钟

# 当前程序路径
baseDir=os.path.dirname(os.path.realpath(sys.argv[0]))

# 判断是否是ipv4
def isIPv4(ip):
    try:
        socket.inet_pton(socket.AF_INET, ip)
    except AttributeError:  # no inet_pton here, sorry
        try:
            socket.inet_aton(ip)
        except socket.error:
            return False
        return ip.count('.') == 3
    except socket.error:  # not a valid ip
        return False
    return True

# 判断是否是ipv6
def isIPv6(ip):
    try:
        socket.inet_pton(socket.AF_INET6, ip)
    except socket.error:  # not a valid ip
        return False
    return True

# 获取本机ip地址
def getIP():
    req=requests.get(ipapi)
    req.encoding='utf8'
    ip=req.text.strip()
    return ip

# 设置配置文件
def setConf():
    with open(f'{baseDir}/conf.json','w',encoding='utf8') as f:
            conf=json.dumps({'domain':domain,'pswd':pswd,'ipv4':ipv4,'ipv6':ipv6,'ipapi':ipapi,'check':check})
            f.write(conf)
            f.close()            

# 加载配置文件
def getConf():
    global domain,pswd,ipv4,ipv6,ipapi,check
    # print('### 加载配置文件...')
    if (os.path.exists(f'{baseDir}/conf.json')):
        # 配置文件存在
        with open(f'{baseDir}/conf.json','r',encoding='utf8') as f:            
            conf=json.loads(f.read().rstrip())
            f.close()
            domain=conf['domain']
            pswd=conf['pswd']
            ipv4=conf['ipv4']
            ipv6=conf['ipv6']
            ipapi=conf['ipapi']
            check=conf['check']
            # print('>>> 配置文件已加载!')
            # 判断地址是否变更，若变更则解析
            ip=getIP()  # 获取ip
            # 判断ip类型
            if isIPv6(ip) and ip!=ipv6:
                ipv6=ip                
                setIPv6(ip)       # 更新ipv6
            elif isIPv4(ip) and ip!=ipv4:
                ipv4=ip
                setIPv4(ip)     # 更新ipv4          
            else:
                nowTime=time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time()))
                print(f'>>> [{nowTime}] IP地址 {ip} 未改变无需更新!')
    else:
        # 配置文件不存在
        with open(f'{baseDir}/conf.json','w',encoding='utf8') as f:
            f.write('{"domain":"xxx.msns.cn","pswd":"","ipv4":"","ipv6":"","ipapi":"http://ip.zxinc.org/getip","check":600}')
            f.close()            
            print('>>> 配置文件不存在,已重新生成!')

# 设置每步ipv6dns
def setIPv6(ip):
    nowTime=time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time()))
    url = f'http://ipv6.meibu.com/?name={domain}&pwd={pswd}&ipv6={ip}'
    response = requests.request("GET", url)
    res=response.text
    if 'chenggong' in res:
        print(f'>>> [{nowTime}]-[IPv6] 域名 {domain} 解析到 {ip} 成功!')
        setConf()   # 更新配置
    elif 'chongfu' in res:
        print(f'>>> [{nowTime}]-[IPv6] 域名 {domain} 解析重复!')
    elif 'err1' in res:
        print(f'>>> [{nowTime}]-[IPv6] 密码错误!')
    elif 'err2' in res:
        print(f'>>> [{nowTime}]-[IPv6] 域名错误!')
    elif 'daoqi' in res:
        print(f'>>> [{nowTime}]-[IPv6] 域名到期!')
    else:
        print(f'>>> [{nowTime}]-[IPv6] 未知错误!')

# 设置每步ipv4dns
def setIPv4(ip):
    nowTime=time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time()))
    url = f'http://ipv4.meibu.com/ipv4.asp?name={domain}&pwd={pswd}'
    response = requests.request("GET", url)
    res=response.text
    if 'chenggong' in res:
        print(f'>>> [{nowTime}]-[IPv4] 域名 {domain} 解析到 {ip} 成功!')
        setConf()   # 更新配置
    elif 'chongfu' in res:
        print(f'>>> [{nowTime}]-[IPv4] 域名 {domain} 解析重复!')
    elif 'err1' in res:
        print(f'>>> [{nowTime}]-[IPv4] 密码错误!')
    elif 'err2' in res:
        print(f'>>> [{nowTime}]-[IPv4] 域名错误!')
    elif 'daoqi' in res:
        print(f'>>> [{nowTime}]-[IPv4] 域名到期!')
    else:
        print(f'>>> [{nowTime}]-[IPv4] 未知错误!')

# 守护线程
def watchDog():
    # print(f'### 刷新解析状态(每{check}s)...')
    while 1==1:
        getConf()
        time.sleep(check)

# 主程序入口
if __name__=='__main__':
    print('=================== 每步DDNS解析工具(meibu.com) ===================')
    print(f'提示:每{check}s刷新解析状态,按回车键退出...')
    # 子线程执行
    t=threading.Thread(target=watchDog)
    t.setDaemon(True)
    t.start()
    x=input('')


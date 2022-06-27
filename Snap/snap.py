#!/bin/env python3
# -*- coding: UTF-8 -*-
# 腾讯轻量云快照助手
# by 风吹我已散
# 注: 默认删除最旧快照并生成新快照

import json
import os
import sys
import datetime
import time
import platform
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.lighthouse.v20200324 import lighthouse_client, models

# 定义全局变量
sid=''
skey=''
region=''
client=''
instotal=0
snaptotal=0
pathtag='/'     # 用于Linux平台路径分割，Windows不需要

# 当前程序路径
baseDir=os.path.dirname(sys.argv[0])
# 当天时间
nowDay=time.strftime("%Y%m%d%H%M",time.localtime(time.time()))

# 获取快照信息
def getSnaps():
    global snaptotal
    print('### 获取快照信息...')
    try:
        req = models.DescribeSnapshotsRequest()
        params = {}
        req.from_json_string(json.dumps(params))
        resp = client.DescribeSnapshots(req)
        resp = json.loads(resp.to_json_string())
        # print(resp)
        snapnum=0
        snaps=[]
        snaptotal=resp['TotalCount']    # 快照总数
        print('>>> 快照数量:',snaptotal)   
        for s in resp['SnapshotSet']:
            snapnum+=1
            snaps.append(s['SnapshotId'])
            # print('快照序号:',snapnum)
            # print('快照 ID:',s['SnapshotId'])
            # print('磁盘 ID:',s['DiskId'])
            # print('快照名称:',s['SnapshotName'])
            # print('快照状态:',s['SnapshotState'])
            # print('快照进度:',str(s['Percent'])+'%')
            # print('创建时间:',utc2local(s['CreatedTime']))
            # print('')
        print('>>> 快照列表:',snaps) 
        return snaps
    except TencentCloudSDKException as err:
        print(err)

# 获取轻量云实例ID
def getInstances():
    global instotal
    print('### 获取轻量云实例ID...')
    try:
        req = models.DescribeInstancesRequest()
        params = {}
        req.from_json_string(json.dumps(params))
        resp = client.DescribeInstances(req)
        resp = json.loads(resp.to_json_string())
        # print(resp)
        insnum=0        
        inslist=[]
        instotal=resp['TotalCount']    # 实例总数
        print('>>> 实例数量:',instotal)
        for s in resp['InstanceSet']:
            insnum+=1
            inslist.append(s['InstanceId'])
            # print('实例序号:',insnum)
            # print('实例 ID:',s['InstanceId'])
            # print('磁盘ID:',s['SystemDisk']['DiskId'])
            # print('实例名称:',s['InstanceName'])
            # print('实例区域:',s['Zone'])            
            # print('公网地址:',s['PublicAddresses'])
            # print('实例状态:',s['InstanceState'])
            # print('创建时间:',utc2local(s['CreatedTime']))
            # print('过期时间:',utc2local(s['ExpiredTime']))
            # print('')          
        print('>>> 实例列表:',inslist) 
        return inslist
    except TencentCloudSDKException as err:
        print(err)

# 创建快照（实例 ID）
def createSnap(inslist):
    print('### 创建快照...')
    try:
        req = models.CreateInstanceSnapshotRequest()
        # 遍历实例ID列表
        for i in inslist:
            snapname=f'实例{i}_{nowDay}'   # 快照名称，可自定义
            params = {
                "InstanceId": i,
                "SnapshotName": snapname  
            }
            req.from_json_string(json.dumps(params))
            resp = client.CreateInstanceSnapshot(req)
            resp = json.loads(resp.to_json_string())
            # print(resp)
            if(resp['SnapshotId']!=''):
                print(f'>>> 快照创建成功,[ID] {resp["SnapshotId"]},[名称] {snapname},[关联实例ID] {i}')
    except TencentCloudSDKException as err:
        print(err)

# 删除快照(快照ID)
def delSanp(snapids):
    print('### 删除快照...')
    try:
        req = models.DeleteSnapshotsRequest()
        params = {
            "SnapshotIds": snapids
        }
        req.from_json_string(json.dumps(params))
        resp = client.DeleteSnapshots(req)        
        resp = json.loads(resp.to_json_string())
        # print(resp)
        if(resp['RequestId']!=''):
            print(f'>>> 删除快照 {snapids} 成功!')
    except TencentCloudSDKException as err:
        print(err)

# UTC时间转本地时间
def utc2local(utctime):
    utc_date = datetime.datetime.strptime(utctime, "%Y-%m-%dT%H:%M:%SZ")
    local_date = utc_date + datetime.timedelta(hours=8)
    local_date_str = datetime.datetime.strftime(local_date ,'%Y-%m-%d %H:%M:%S')
    # print(local_date_str )    # 2019-07-26 16:20:54
    return local_date_str

# 获取配置文件
def getConf():
    global sid,skey,region,client
    print('### 加载配置文件...')
    if(os.path.exists(f'{baseDir}{pathtag}snapconf.json')):
        # 配置文件存在
        with open(f'{baseDir}{pathtag}snapconf.json','r',encoding='utf8') as f:            
            conf=json.loads(f.read().rstrip())
            f.close()
            sid=conf['SecretId']
            skey=conf['SecretKey']
            region=conf['Region']
            print('>>> 配置文件已加载!')
        # 初始化腾讯SDK连接
        try:
            cred = credential.Credential(sid, skey)
            httpProfile = HttpProfile()
            httpProfile.endpoint = "lighthouse.tencentcloudapi.com"
            clientProfile = ClientProfile()
            clientProfile.httpProfile = httpProfile
            client = lighthouse_client.LighthouseClient(cred, region, clientProfile)
        except TencentCloudSDKException as err:
            print(err)
    else:
        # 配置文件不存在
        with open(f'{baseDir}{pathtag}snapconf.json','w',encoding='utf8') as f:
            f.write('{"SecretId":"","SecretKey":"","Region":"ap-hongkong"}')
            f.close()            
            print('>>> 配置文件不存在,已重新生成!')

# 主程序开始
if __name__=='__main__':
    print('============== 腾讯轻量云快照助手 ==============')
    # Windows平台去除路径/
    if platform.system().lower() == "windows":
        pathtag=''
    # 获取配置
    getConf()
    # 获取实例
    inslist=getInstances()
    # 获取快照
    snaplist=getSnaps()
    # 判断快照数量
    if(snaptotal>0 and snaptotal==1):
        # 仅一个快照
        delSanp(snaplist[-1])
    elif(snaptotal>0 and snaptotal>instotal):
        # 快照数大于实例数
        delSanp(snaplist[instotal:])
    # 创建新快照
    createSnap(inslist)

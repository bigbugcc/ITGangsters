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
# 当前程序路径
baseDir=os.path.dirname(sys.argv[0])
# 当天时间
nowDay=time.strftime("%Y-%m-%d",time.localtime(time.time()))

# 获取快照信息
def getSnaps():
    print('### 获取快照信息...')
    try:
        req = models.DescribeSnapshotsRequest()
        params = {

        }
        req.from_json_string(json.dumps(params))

        resp = client.DescribeSnapshots(req)
        # print(resp.to_json_string())
        resp = json.loads(resp.to_json_string())
        # print(resp)
        snapnum=0
        snaps=[]
        # snaptotal=resp['TotalCount']    # 快照总数
        for s in resp['SnapshotSet']:
            snapnum+=1
            snaps.append(s['SnapshotId'])
            # print('快照序号:',snapnum)
            # print('快照 ID:',s['SnapshotId'])
            # print('快照名称:',s['SnapshotName'])
            # print('快照状态:',s['SnapshotState'])
            # print('快照进度:',str(s['Percent'])+'%')
            # print('创建时间:',utc2local(s['CreatedTime']))
            # print('')
        print('>>> 快照列表:',snaps) 
        return [snaps[-1]]      # 删除最旧的一个
    except TencentCloudSDKException as err:
        print(err)

# 获取轻量云实例ID
def getInstances():
    print('### 获取轻量云实例ID...')
    try:
        req = models.DescribeInstancesRequest()
        params = {

        }
        req.from_json_string(json.dumps(params))

        resp = client.DescribeInstances(req)
        # print(resp.to_json_string())
        resp = json.loads(resp.to_json_string())
        # print(resp)
        insnum=0
        inslist=[]
        for s in resp['InstanceSet']:
            insnum+=1
            inslist.append(s['InstanceId'])
            # print('实例序号:',insnum)
            # print('实例 ID:',s['InstanceId'])
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
    snapname="快照_" + nowDay   # 快照名称，可自定义
    try:
        req = models.CreateInstanceSnapshotRequest()
        # 遍历实例ID列表
        for i in inslist:
            params = {
                "InstanceId": i,
                "SnapshotName": snapname  
            }
            req.from_json_string(json.dumps(params))
            resp = client.CreateInstanceSnapshot(req)
            resp = json.loads(resp.to_json_string())
            # print(resp.to_json_string())
            if(resp['SnapshotId']!=''):
                print('>>> 快照创建成功!')
                print('>>> 快照 ID:', str(resp['SnapshotId']))
                print('>>> 快照名称:', snapname)
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
        # print(resp.to_json_string())
        resp = json.loads(resp.to_json_string())
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
    if(os.path.exists(f'{baseDir}/snapconf.json')):
        # 配置文件存在
        with open(f'{baseDir}/snapconf.json','r',encoding='utf8') as f:            
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
        with open(f'{baseDir}/snapconf.json','w',encoding='utf8') as f:
            f.write('{"SecretId":"","SecretKey":"","Region":"ap-hongkong"}')
            f.close()            
            print('>>> 配置文件不存在,已重新生成!')

# 主程序开始
if __name__=='__main__':
    print('========== 腾讯轻量云快照创建助手 ==========')
    # 获取配置
    getConf()
    # 删除最旧快照
    delSanp(getSnaps())
    # 创建新快照
    createSnap(getInstances())

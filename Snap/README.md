# 腾讯轻量云快照助手

## 功能 
自动删除最旧快照并创建新快照

## 使用
使用之前请先运行程序生成配置文件模板，然后填入对应信息如下：
```json
{
	"SecretId": "腾讯云账户SecretId",
	"SecretKey": "腾讯云账户SecretKey",
	"Region": "轻量云地域,如ap-hongkong"
}
```
### 二进制运行
bin目录为Windows(amd64)和Linux(amd64)平台二进制文件，可直接运行；
```bash
# Linux平台
chmod +x snap
./snap

# Windows平台
命令行或者直接执行snap.exe
```

### 源码运行
安装依赖后运行 python3 snap.py
```bash
# 安装依赖
pip3 install reqs.txt
chmod +x ./snap.py
./snap.py
```

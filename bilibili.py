#!/usr/bin/env python3

import base64
import datetime
import hashlib
import random
import re
import requests
import rsa
import time
from urllib import parse

# 登陆方式(优先级由高至低, 留空跳过)
# 1. 用户名与密码
account = {'username': '', 'password': ''}
# 2. Cookie
cookie = ''
# 3. 批量导入用户名与密码(格式: 用户名----密码)
accountsFile = ''
# 4. 批量导入Cookie
cookiesFile = ''

# 任务列表
tasks = {'getUserInfo': True, # 查询主站用户信息
         'getLiveInfo': True, # 查询直播站用户信息
         'silverToCoin': True, # 银瓜子兑硬币
         'silverToCoinOld': True, # 银瓜子兑硬币(旧API)
         'watchVideo': True, # 观看视频
         'giveCoin': True, # 投币
         'shareVideo': True, # 分享视频(需使用用户名与密码登陆以获取AccessKey)
         'addFavourite': True} # 收藏

# av列表
avs = [20032006, 14594803, 14361946]

# 代理开关
useProxy = False
# HTTP代理列表
proxies = ['61.135.217.7:80', '180.101.205.253:8888', '122.183.139.101:8080', '218.28.131.34:3128', '119.10.67.144:808', '117.127.0.210:80', '49.51.70.42:1080', '114.212.12.4:3128', '101.248.64.69:8080', '59.48.247.130:8060', '94.177.224.181:8080', '221.182.133.242:80', '221.176.212.98:3128', '61.136.163.245:3128', '101.248.64.69:80', '61.183.172.164:9090', '202.100.83.139:80', '223.96.95.229:3128', '101.96.11.4:80', '101.96.10.4:80', '114.215.95.188:3128', '39.137.69.6:8080', '118.31.33.206:3128', '117.127.0.209:80', '101.53.101.172:9999', '166.111.80.162:3128', '49.51.193.128:1080', '218.106.205.145:8080', '221.7.255.168:80', '118.212.137.135:31288', '118.25.104.254:1080', '120.78.78.141:8888', '39.106.160.36:3128', '112.115.57.20:3128', '117.127.0.197:8080', '59.44.16.6:80', '121.196.218.197:3128', '61.136.163.245:8102', '103.78.213.147:80', '211.159.171.58:80', '39.137.69.8:8080', '121.41.171.223:3128', '50.233.137.38:80', '39.105.78.30:3128', '118.114.77.47:8080', '116.62.139.136:3128', '216.250.99.38:80', '42.236.123.17:80', '39.137.69.8:80', '59.44.16.6:8000', '139.224.24.26:8888', '50.233.137.37:80', '36.67.20.251:52136', '113.200.56.13:8010', '118.190.210.227:3128', '183.224.101.158:63000', '118.24.22.152:3128', '59.188.151.138:3128', '117.127.0.210:8080', '66.82.144.29:8080', '39.134.14.81:8080', '175.6.2.174:8088', '117.127.0.196:80', '124.42.7.103:80', '101.96.10.5:80', '47.94.230.42:9999', '89.236.17.106:3128', '119.39.48.205:9090', '50.233.137.32:80', '103.205.177.44:53281', '223.19.105.42:3128', '117.127.0.205:80', '118.24.61.22:3128', '222.33.192.238:8118', '122.183.139.104:8080', '124.238.235.135:8000', '61.136.163.244:3128', '117.127.0.205:8080', '61.136.163.244:8103', '61.136.163.245:8103', '117.127.0.198:80', '101.248.64.66:80', '39.106.35.201:3128', '117.127.0.198:8080']

timeStamp = lambda: str(int(time.mktime(datetime.datetime.now().timetuple())))

class Bilibili():
    def __init__(self):
        self.username = ''
        self.password = ''
        self.cookie = ''
        self.csrf = ''
        self.uid = ''
        self.accessKey = ''
        if (useProxy):
            self.proxy = {'http': random.choice(proxies)}
            print('使用代理: {}'.format(self.proxy['http']))
        else:
            self.proxy = None
    
    def login(self, username, password):
        self.username = str(username)
        self.password = str(password)
        print('用户名: {}'.format(self.username))
        print('密码: {}'.format(self.password))
        print('正在登陆......', end=' ')
        url = 'https://passport.bilibili.com/api/oauth2/getKey'
        data = {'appkey': '1d8b6e7d45233436', 'sign': self.getSign('appkey=1d8b6e7d45233436')}
        response = requests.post(url, data=data, proxies=self.proxy)
        keyHash = str(response.json()['data']['hash'])
        pubKey = rsa.PublicKey.load_pkcs1_openssl_pem(response.json()['data']['key'].encode())
        url = 'https://passport.bilibili.com/api/v2/oauth2/login'
        param = 'appkey=1d8b6e7d45233436&password=' + parse.quote_plus(base64.b64encode(rsa.encrypt((keyHash + self.password).encode('utf-8'), pubKey))) + '&username=' + parse.quote_plus(self.username)
        data = param + '&sign=' + self.getSign(param)
        headers = {'Content-type': 'application/x-www-form-urlencoded'}
        response = requests.post(url, data=data, headers=headers, proxies=self.proxy)
        try:
            cookies = response.json()['data']['cookie_info']['cookies']
            self.cookie = ''
            for i in range(len(cookies)):
                self.cookie += cookies[i]['name'] + '=' + cookies[i]['value'] + ';'
            self.csrf = re.findall(r'bili_jct=(\S+)', self.cookie, re.M)[0].split(';')[0]
            self.uid = re.findall(r'DedeUserID=(\S+)', self.cookie, re.M)[0].split(';')[0]
            self.accessKey = response.json()['data']['token_info']['access_token']
            print('成功')
            print('Cookies: {}'.format(self.cookie))
            return True
        except:
            print('失败 {}'.format(response.json()))
            return False
    
    def setCookie(self, cookie):
        self.cookie = cookie
        self.csrf = re.findall(r'bili_jct=(\S+)', self.cookie, re.M)[0].split(';')[0]
        self.uid = re.findall(r'DedeUserID=(\S+)', self.cookie, re.M)[0].split(';')[0]
        print('已导入Cookie')
    
    def getSign(self, param):
        signHash = hashlib.md5()
        signHash.update((param + '560c52ccd288fed045859ed18bffd973').encode())
        return signHash.hexdigest()
    
    # 查询主站用户信息
    def getUserInfo(self):
        print('查询主站用户信息......', end=' ')
        url = 'https://account.bilibili.com/home/reward'
        headers = {'Cookie': self.cookie,
                   'Referer': 'https://account.bilibili.com/account/home',
                   'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'}
        response = requests.get(url, headers=headers, proxies=self.proxy)
        if (response.json()['code'] == 0):
            print('成功')
            print('等级: {}'.format(response.json()['data']['level_info']['current_level']))
            print('经验: {}/{}'.format(response.json()['data']['level_info']['current_exp'], response.json()['data']['level_info']['next_exp']))
            print('每日登陆: {}'.format('5经验值到手' if response.json()['data']['login'] else '未完成'))
            print('每日观看视频: {}'.format('5经验值到手' if response.json()['data']['watch_av'] else '未完成'))
            print('每日投币: 已获得{}/50'.format(response.json()['data']['coins_av']))
            print('每日分享视频: {}'.format('5经验值到手' if response.json()['data']['share_av'] else '未完成'))
            print('邮箱: {}'.format('已绑定' if response.json()['data']['email'] else '未绑定'))
            print('手机: {}'.format('已绑定' if response.json()['data']['tel'] else '未绑定'))
            print('密保: {}'.format('已设置' if response.json()['data']['safequestion'] else '未设置'))
            print('实名认证: {}'.format('已认证' if response.json()['data']['identify_card'] else '未认证'))
            return True
        else:
            print('失败 {}'.format(response.json()))
            return False
        
    # 查询直播站用户信息
    def getLiveInfo(self):
        print('查询直播站用户信息......', end=' ')
        url = 'https://api.live.bilibili.com/User/getUserInfo'
        headers = {'Cookie': self.cookie,
                   'Host': 'api.live.bilibili.com',
                   'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'}
        response = requests.get(url, headers=headers, proxies=self.proxy)
        if (response.json()['code'] == 0):
            print('成功')
            print('昵称: {}'.format(response.json()['data']['uname']))
            print('等级: {}'.format(response.json()['data']['user_level']))
            print('经验: {}/{}'.format(response.json()['data']['user_intimacy'], response.json()['data']['user_next_intimacy']))
            print('排名: {}'.format(response.json()['data']['user_level_rank']))
            print('老爷: {}'.format('是' if (response.json()['data']['vip'] or response.json()['data']['svip']) else '否'))
            print('硬币: {}'.format(response.json()['data']['billCoin']))
            print('银瓜子: {}'.format(response.json()['data']['silver']))
            print('金瓜子: {}'.format(response.json()['data']['gold']))
            print('成就: {}'.format(response.json()['data']['achieve']))
            return True
        else:
            print('失败 {}'.format(response.json()))
            return False
    
    # 银瓜子兑硬币
    def silverToCoin(self):
        print('使用银瓜子兑换硬币......', end=' ')
        url = 'https://api.live.bilibili.com/pay/v1/Exchange/silver2coin'
        data = {'platform': 'pc',
                'csrf_token': self.csrf}
        headers = {'Cookie': self.cookie,
                   'Host': 'api.live.bilibili.com',
                   'Origin': 'https://live.bilibili.com',
                   'Referer': 'https://live.bilibili.com/exchange',
                   'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'}
        response = requests.post(url, data=data, headers=headers, proxies=self.proxy)
        if (response.json()['code'] == 0):
            print('成功')
            return True
        else:
            print('失败 {}'.format(response.json()))
            return False
    
    # 银瓜子兑硬币(旧API)
    def silverToCoinOld(self):
        print('使用银瓜子兑换硬币(旧API)......', end=' ')
        url = 'https://api.live.bilibili.com/exchange/silver2coin'
        headers = {'Cookie': self.cookie,
                   'Host': 'api.live.bilibili.com',
                   'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'}
        response = requests.get(url, headers=headers, proxies=self.proxy)
        if (response.json()['code'] == 0):
            print('成功')
            return True
        else:
            print('失败 {}'.format(response.json()))
            return False
    
    # 观看视频
    def watchVideo(self, aid):
        # aid = 稿件av号
        print('观看av{}......'.format(aid), end=' ')
        url = 'https://www.bilibili.com/widget/getPageList?aid=' + str(aid)
        response = requests.get(url, proxies=self.proxy)
        cid = response.json()[0]['cid']
        url = 'https://api.bilibili.com/x/report/web/heartbeat'
        data = {'aid': aid,
                'cid': cid,
                'mid': self.uid,
                'csrf': self.csrf,
                'played_time': '0',
                'realtime': '0',
                'start_ts': timeStamp(),
                'type': '3',
                'dt': '2',
                'play_type': '1'}
        headers = {'Cookie': self.cookie,
                   'Host': 'api.bilibili.com',
                   'Referer': 'https://www.bilibili.com/video/av' + str(aid),
                   'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'}
        response = requests.post(url, data=data, headers=headers, proxies=self.proxy)
        if (len(response.content) == 0 or response.json()['code'] == 0):
            print('成功')
            return True
        else:
            print('失败 {}'.format(response.json()))
            return False
    
    # 投币
    def giveCoin(self, aid, multiply):
        # aid = 稿件av号
        # multiply = 投硬币个数(1或2)
        print('为av{}投硬币{}枚......'.format(aid, multiply), end=' ')
        url = 'https://api.bilibili.com/x/web-interface/coin/add'
        data = {'aid': str(aid),
                'multiply': str(multiply),
                'cross_domain': 'true',
                'csrf': self.csrf}
        headers = {'Cookie': self.cookie,
                   'Host': 'api.bilibili.com',
                   'Origin': 'https://www.bilibili.com',
                   'Referer': 'https://www.bilibili.com/video/av' + str(aid),
                   'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'}
        response = requests.post(url, data=data, headers=headers, proxies=self.proxy)
        if (response.json()['code'] == 0):
            print('成功')
            return True
        else:
            print('失败 {}'.format(response.json()))
            return False
    
    # 分享视频
    def shareVideo(self, aid):
        # aid = 稿件av号
        print('分享av{}......'.format(aid), end=' ')
        url = 'https://app.bilibili.com/x/v2/view/share/add'
        ts = timeStamp()
        data = {'access_key': self.accessKey,
                'aid': aid,
                'appkey': '1d8b6e7d45233436',
                'build': '5260003',
                'from': '7',
                'mobi_app': 'android',
                'platform': 'android',
                'ts': ts,
                'sign': self.getSign('access_key=' + self.accessKey + '&aid=' + str(aid) + '&appkey=1d8b6e7d45233436&build=5260003&from=7&mobi_app=android&platform=android&ts=' + str(ts))}
        headers = {'Cookie': 'sid=8wfvu7i7',
                   'Host': 'app.bilibili.com',
                   'User-Agent': 'Mozilla/5.0 BiliDroid/5.26.3 (bbcallen@gmail.com)'}
        response = requests.post(url, data=data, headers=headers, proxies=self.proxy)
        url = 'https://www.bilibili.com/widget/getPageList?aid=' + str(aid)
        response = requests.get(url, proxies=self.proxy)
        cid = response.json()[0]['cid']
        url = 'https://api.bilibili.com/x/report/heartbeat'
        ts = timeStamp()
        data = {'aid': aid,
                'appkey': '1d8b6e7d45233436',
                'build': '5260003',
                'cid': cid,
                'epid': '0',
                'from': '7',
                'mid': self.uid,
                'mobi_app': 'android',
                'platform': 'android',
                'play_type': '4',
                'played_time': '0',
                'sid': '0',
                'start_ts': '0',
                'sub_type': '0',
                'ts': ts,
                'type': '3',
                'sign': self.getSign('aid=' + str(aid) + '&appkey=1d8b6e7d45233436&build=5260003&cid=' + str(cid) + '&epid=0&from=7&mid=' + str(self.uid) + '&mobi_app=android&platform=android&play_type=4&played_time=0&sid=0&start_ts=0&sub_type=0&ts=' + ts + '&type=3')}
        headers = {'Cookie': 'sid=8wfvu7i7',
                   'Host': 'api.bilibili.com',
                   'User-Agent': 'Mozilla/5.0 BiliDroid/5.26.3 (bbcallen@gmail.com)'}
        response = requests.post(url, data=data, headers=headers, proxies=self.proxy)
        if (len(response.content) == 0 or response.json()['code'] == 0):
            print('成功')
            return True
        else:
            print('失败 {}'.format(response.json()))
            return False
    
    # 收藏
    def addFavourite(self, aid):
        # aid = 稿件av号
        print('收藏av{}......'.format(aid), end=' ')
        url = 'https://api.bilibili.com/x/v2/fav/folder'
        headers = {'Cookie': self.cookie,
                   'Host': 'api.bilibili.com',
                   'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'}
        response = requests.get(url, headers=headers, proxies=self.proxy)
        fid = response.json()['data'][0]['fid']
        url = 'https://api.bilibili.com/x/v2/fav/video/add'
        data = {'aid': aid,
                'fid': fid,
                'jsonp': 'jsonp',
                'csrf': self.csrf}
        headers = {'Cookie': self.cookie,
                   'Host': 'api.bilibili.com',
                   'Origin': 'https://www.bilibili.com',
                   'Referer': 'https://www.bilibili.com/video/av' + str(aid),
                   'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'}
        response = requests.post(url, data=data, headers=headers, proxies=self.proxy)
        if (response.json()['code'] == 0):
            print('成功')
            return True
        else:
            print('失败 {}'.format(response.json()))
            return False

def execute():
    try:
        if (tasks['getUserInfo']):
            bili.getUserInfo()
        if (tasks['getLiveInfo']):
            bili.getLiveInfo()
        if (tasks['silverToCoin']):
            bili.silverToCoin()
        if (tasks['silverToCoinOld']):
            bili.silverToCoinOld()
        random.shuffle(avs)
        for av in avs:
            if (tasks['watchVideo']):
                bili.watchVideo(av)
            if (tasks['giveCoin']):
                bili.giveCoin(av, 2)
            if (tasks['shareVideo'] and bili.accessKey):
                bili.shareVideo(av)
            if (tasks['addFavourite']):
                bili.addFavourite(av)
    except:
        print('任务执行中断')

if __name__ == '__main__':
    if (account['username'] and account['password']):
        bili = Bilibili()
        if (bili.login(account['username'], account['password'])):
            execute()
    elif (cookie):
        bili = Bilibili()
        bili.setCookie(cookie)
        execute()
    elif (accountsFile):
        with open(accountsFile) as f:
            for line in f.readlines():
                line = line.strip('\n')
                usr = line.split('----')[0]
                pwd = line.split('----')[1]
                bili = Bilibili()
                if (bili.login(usr, pwd)):
                    execute()
    elif (cookiesFile):
        with open(cookiesFile) as f:
            for line in f.readlines():
                cookie = line.strip('\n')
                bili = Bilibili()
                bili.setCookie(cookie)
                execute()
    else:
        print('未配置登陆信息')

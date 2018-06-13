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

# 登录方式(优先级由高至低, 留空跳过)
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
         'silverToCoin': True, # 银瓜子兑换硬币
         'silverToCoin2': True, # 银瓜子兑换硬币(旧API)
         'watchVideo': True, # 观看视频
         'giveCoin': True, # 投币
         'shareVideo': True, # 分享视频(需使用用户名与密码登录以获取AccessKey)
         'addFavourite': True} # 收藏视频

# av列表
avs = [20032006, 14594803, 14361946]

# 双倍投币
doubleCoins = True

# 代理开关
# 使用用户名与密码进行登录时应避免使用代理，以防止出现账号异常
useProxy = False
# HTTP代理列表
proxies = ['180.101.205.253:8888', '140.205.222.3:80', '120.35.103.24:6666', '101.248.64.66:8080', '45.32.195.95:8118', '180.97.83.42:3128', '49.51.193.134:1080', '59.48.247.130:8060', '221.14.140.66:80', '221.182.133.242:80', '42.104.84.106:8080', '60.255.186.169:8888', '49.51.69.179:1080', '101.248.64.69:80', '166.111.80.162:3128', '114.215.174.227:8080', '218.28.131.34:3128', '186.68.85.26:53281', '218.14.115.211:3128', '114.215.95.188:3128', '113.200.56.13:8010', '221.7.255.168:80', '101.53.101.172:9999', '117.127.0.210:80', '101.4.136.34:81', '101.132.136.83:808', '118.212.137.135:31288', '167.114.224.6:80', '103.10.228.221:8080', '222.222.236.207:8060', '39.104.84.72:8080', '59.44.16.6:80', '61.136.163.245:8102', '221.193.177.45:8060', '58.221.72.184:3128', '222.89.85.130:8060', '49.51.195.24:1080', '61.183.172.164:9090', '139.224.24.26:8888', '117.127.0.197:80', '61.135.217.7:80', '101.96.10.5:80', '59.44.16.6:8000', '151.106.52.38:1080', '222.89.85.158:8060', '50.233.137.37:80', '117.127.0.196:80', '118.190.210.227:3128', '117.127.0.205:80', '60.250.79.187:80', '117.127.0.210:8080', '119.28.99.194:3128', '175.98.239.87:8888', '121.8.98.198:80', '39.134.14.81:8080', '49.51.86.151:3128', '39.137.69.10:80', '50.233.137.32:80', '223.19.105.42:3128', '39.106.160.36:3128', '118.24.61.22:3128', '183.56.177.130:808', '121.22.7.137:8000', '222.33.192.238:8118', '117.127.0.204:8080', '39.137.69.8:80', '58.87.77.126:3128', '101.248.64.66:80', '39.106.35.201:3128', '183.179.199.225:8080', '45.32.193.119:8164', '222.85.31.177:8060', '42.236.123.17:80', '183.128.240.254:6666', '39.104.75.54:8080', '60.165.54.144:8060', '47.90.87.225:88', '119.122.215.102:9000', '114.212.12.4:3128', '60.205.228.133:9999', '36.67.48.11:65103', '94.177.224.181:8080', '221.195.49.100:8060', '117.127.0.195:8080', '203.69.87.196:8080', '218.207.212.86:80', '59.48.237.6:8060', '61.136.163.245:3128', '202.100.83.139:80', '117.127.0.196:8080', '218.50.2.102:8080', '39.137.69.6:8080', '121.231.155.137:6666', '118.24.88.240:1080', '119.188.162.165:8081', '217.23.69.198:3128', '112.115.57.20:3128', '218.66.232.26:3128', '120.78.78.141:8888', '46.218.85.101:3129', '124.238.235.135:8000', '203.69.87.194:8080', '121.196.218.197:3128', '123.57.207.2:3128', '219.141.153.2:8080', '39.137.69.8:8080', '217.91.90.46:53281', '39.105.78.30:3128', '118.114.77.47:8080', '121.42.167.160:3128', '191.253.208.132:20183', '117.127.0.205:8080', '39.104.80.107:8080', '183.163.43.163:31588', '61.136.163.244:8103', '191.28.160.114:8080', '119.28.152.208:80', '118.24.22.152:3128', '120.131.9.254:1080', '45.32.193.119:8123', '39.104.75.55:8080', '39.137.69.9:80', '220.166.96.90:82', '202.46.42.156:80', '203.130.46.108:9090', '122.114.31.177:808', '101.248.64.69:8080', '119.39.48.205:9090', '111.6.187.52:8080', '120.199.224.77:80', '117.127.0.198:80', '222.88.154.56:8060', '103.78.213.147:80', '39.108.97.146:8888', '45.32.193.119:8118', '61.136.163.244:3128', '117.65.100.60:63909', '61.136.163.245:8103', '39.104.13.180:8080', '121.17.18.178:8060', '203.69.87.193:8080']

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
    
    def getSign(self, param):
        signHash = hashlib.md5()
        signHash.update((param + '560c52ccd288fed045859ed18bffd973').encode())
        return signHash.hexdigest()
    
    # 登录
    def login(self, username, password):
        self.username = str(username)
        self.password = str(password)
        print('用户名: {}'.format(self.username))
        print('密码: {}'.format(self.password))
        print('正在登录......', end=' ')
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
    
    # 导入Cookie
    def importCookie(self, cookie):
        self.cookie = cookie
        self.csrf = re.findall(r'bili_jct=(\S+)', self.cookie, re.M)[0].split(';')[0]
        self.uid = re.findall(r'DedeUserID=(\S+)', self.cookie, re.M)[0].split(';')[0]
        print('已导入Cookie: {}'.format(self.cookie))
    
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
            print('经验: {}/{} ({:.2%})'.format(response.json()['data']['level_info']['current_exp'], response.json()['data']['level_info']['next_exp'], response.json()['data']['level_info']['current_exp'] / response.json()['data']['level_info']['next_exp']))
            print('每日登录: {}'.format('5经验值到手' if response.json()['data']['login'] else '未完成'))
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
            print('经验: {}/{} ({:.2%})'.format(response.json()['data']['user_intimacy'], response.json()['data']['user_next_intimacy'], response.json()['data']['user_intimacy'] / response.json()['data']['user_next_intimacy']))
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
    
    # 银瓜子兑换硬币
    def silverToCoin(self):
        print('银瓜子兑换硬币......', end=' ')
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
    
    # 银瓜子兑换硬币(旧API)
    def silverToCoin2(self):
        print('银瓜子兑换硬币(旧API)......', end=' ')
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
    def giveCoin(self, aid, double):
        # aid = 稿件av号
        # double = 双倍投币
        print('投币{}枚给av{}......'.format('2' if double else '1', aid), end=' ')
        url = 'https://api.bilibili.com/x/web-interface/coin/add'
        data = {'aid': str(aid),
                'multiply': '2' if double else '1',
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
    
    # 收藏视频
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

def execute(instance):
    print('[{}]UID={}开始执行任务'.format(datetime.datetime.now(), instance.uid))
    if (tasks['getUserInfo']):
        try:
            instance.getUserInfo()
        except:
            print('异常')
    if (tasks['getLiveInfo']):
        try:
            instance.getLiveInfo()
        except:
            print('异常')
    if (tasks['silverToCoin']):
        try:
            instance.silverToCoin()
        except:
            print('异常')
    if (tasks['silverToCoin2']):
        try:
            instance.silverToCoin2()
        except:
            print('异常')
    random.shuffle(avs)
    for av in avs:
        if (tasks['watchVideo']):
            try:
                instance.watchVideo(av)
            except:
                print('异常')
        if (tasks['giveCoin']):
            try:
                instance.giveCoin(av, doubleCoins)
            except:
                print('异常')
        if (tasks['shareVideo'] and bili.accessKey):
            try:
                instance.shareVideo(av)
            except:
                print('异常')
        if (tasks['addFavourite']):
            try:
                instance.addFavourite(av)
            except:
                print('异常')
    print('[{}]UID={}任务执行完毕'.format(datetime.datetime.now(), instance.uid))
    print()

if __name__ == '__main__':
    if (account['username'] and account['password']):
        bili = Bilibili()
        if (bili.login(account['username'], account['password'])):
            execute(bili)
    elif (cookie):
        bili = Bilibili()
        bili.importCookie(cookie)
        execute(bili)
    elif (accountsFile):
        with open(accountsFile) as f:
            for line in f.readlines():
                line = line.strip('\n')
                username = line.split('----')[0]
                password = line.split('----')[1]
                bili = Bilibili()
                if (bili.login(username, password)):
                    execute(bili)
    elif (cookiesFile):
        with open(cookiesFile) as f:
            for line in f.readlines():
                cookie = line.strip('\n')
                bili = Bilibili()
                bili.importCookie(cookie)
                execute(bili)
    else:
        print('未配置登录信息')

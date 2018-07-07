#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-

import base64
import hashlib
import io
import json
import random
import re
import requests
import rsa
import string
import sys
import time
from multiprocessing import Pool
from urllib import parse

# 登录方式(优先级由高至低, 留空跳过)
# 1. 用户名与密码
account = {'username': "",
           'password': ""}
# 2. Cookie
cookie = ""
# 3. 批量导入用户名与密码(格式: 用户名----密码)
accountsFile = ""
# 4. 批量导入Cookie
cookiesFile = ""

# 任务列表
tasks = {'query': True, # 获取用户信息
         'silver2Coins': True, # 银瓜子兑换硬币
         'watch': True, # 观看
         'like': True, # 好评
         'reward': True, # 投币
         'favour': True, # 收藏
         'share': False, # 分享
         'follow': True, # 关注
         'commentLike': False, # 评论点赞
         'commentRush': False, # 评论抢楼
         'dynamicLike': False, # 动态点赞
         'dynamicRepost': False, # 动态转发
         'mallAssist': False, # 会员购周年庆活动助力
         'mallLottery': False, # 会员购周年庆活动抽奖
         'mallPrize': False, # 会员购周年庆活动中奖查询
         'mi6XLottery': False} # 小米6X抢F码活动抽奖

# av列表
avs = [20032006, 14594803, 14361946]

# 双倍投币
doubleRewards = True

# 关注列表(mid为被关注用户UID, secret为悄悄关注)
follows = [{'mid': 124811915,
            'secret': True}]

# 评论相关
# otype为作品类型(视频对应video, 活动对应activity, 相簿对应gallery, 文章对应article), oid为作品ID
# 点赞评论列表(rpid为评论ID)
likeComments = [{'otype': "article",
                 'oid': 617468,
                 'rpid': 864171896}]
# 抢楼评论(floor为抢楼楼层, message为评论内容)
rushComment = {'otype': "video",
               'oid': 25581792,
               'floor': 2233,
               'message': "哔哩哔哩 (゜-゜)つロ 干杯~"}

# 动态相关
# 点赞动态ID列表
likeDynamicIDs = [134705258328201427]
# 转发动态列表(did为动态ID, message为转发内容)
repostDynamics = [{'did': 134705258328201427,
                   'message': "哔哩哔哩 (゜-゜)つロ 干杯~"}]

# 会员购周年庆活动助力用户UID列表
beAssistedUIDs = [124811915, 44587175]

# 导出Cookie到文件, 留空则不导出
exportCookie = "Bilibili-Cookies.txt"

# 进程池容量
processPoolCap = 10

# 代理开关, 强烈建议多用户操作时打开
useProxy = True
# HTTPS代理列表
proxies = ["113.207.44.70:3128", "112.115.57.20:3128", "101.37.146.95:3128", "113.200.214.164:9999", "113.200.56.13:8010", "118.31.220.3:8080", "47.96.239.158:3128", "101.37.79.125:3128", "211.149.218.247:80", "180.101.205.253:8888", "118.31.223.194:3128", "58.152.40.61:8888", "101.236.18.101:8866", "118.212.137.135:31288", "1.71.188.37:3128", "43.247.70.250:3128", "119.188.162.165:8081", "120.78.71.63:3128", "221.7.255.168:8080", "166.111.80.162:3128", "221.7.255.168:80", "101.236.21.22:8866", "101.236.60.225:8866", "180.97.83.42:3128", "54.222.177.145:3128", "183.179.199.225:8080", "180.101.146.174:3128", "114.115.144.137:3128", "115.193.75.121:8123", "39.106.160.36:3128", "221.204.213.75:3128", "58.240.172.110:3128", "223.68.190.130:8181", "124.193.37.5:8888", "221.218.220.167:3128", "114.212.12.4:3128", "118.24.121.231:3128", "1.196.161.241:9999", "58.22.9.14:3128", "202.99.172.165:8081", "123.13.247.254:9999", "121.201.33.100:11430", "47.75.90.14:443", "211.161.103.247:9999", "160.16.113.52:60088", "124.235.208.252:443", "163.43.28.237:60088", "59.106.218.188:60088", "27.133.128.174:60088", "60.211.166.42:63000", "140.143.96.216:80", "39.135.35.18:80", "125.62.26.197:3128", "123.185.80.246:8118", "59.106.218.51:60088", "47.96.227.203:3128", "39.135.35.19:80", "14.136.246.173:3128", "59.106.217.16:60088", "163.43.30.9:60088", "163.43.29.166:60088", "47.96.12.10:3128", "119.196.18.50:8080", "163.43.30.42:60088", "163.43.31.194:60088", "121.156.109.92:8080", "120.198.223.69:63000", "121.150.244.200:3128", "59.106.223.171:60088", "47.96.121.22:3128", "27.133.153.227:60088", "59.106.223.57:60088", "163.43.30.191:60088", "221.120.161.200:53281", "223.255.191.109:3128", "163.43.31.107:60088", "27.133.155.162:60088", "27.133.155.225:60088", "110.74.196.152:53281", "160.16.201.57:60088", "59.106.210.192:60088", "59.106.216.142:60088", "123.48.150.154:80", "203.130.46.108:9090", "43.252.10.244:8181", "43.228.245.164:80", "103.245.18.5:53281", "163.43.30.69:60088", "221.228.17.172:8181", "160.16.219.177:60088", "218.26.227.108:80", "121.152.17.96:3128", "59.21.14.68:3128", "13.78.35.191:3128", "121.225.25.152:3128", "119.207.78.155:80", "103.48.206.254:53281", "101.236.19.165:8866", "218.106.205.145:8080", "47.97.207.93:3128", "119.23.73.27:3128", "188.93.132.11:41258", "101.128.68.113:8080", "145.255.137.20:8087", "103.48.205.174:53281", "83.246.139.24:8080", "185.135.80.15:3128", "95.154.64.173:8080", "27.123.1.86:53281", "59.106.209.106:60088", "218.207.212.86:80", "81.1.245.94:8080", "94.242.58.14:1448", "94.242.58.14:10010", "62.249.156.13:53281", "85.95.153.100:8080", "144.76.62.29:3128", "94.242.59.245:10010", "94.242.59.245:1448", "5.128.26.77:8080", "94.242.58.108:1448", "94.242.58.108:10010", "195.201.139.159:3128", "163.43.31.6:60088", "80.89.133.210:3128", "92.222.213.107:3128", "195.201.43.199:3128", "94.242.58.142:10010", "80.240.33.181:53281", "58.26.10.67:8080", "194.88.105.156:3128", "185.22.174.69:10010", "178.128.250.51:3128", "94.242.58.142:1448", "78.46.119.108:3128", "5.8.200.203:8080", "94.230.119.197:8585", "94.16.117.29:3128", "195.201.156.125:3128", "185.22.173.161:1448", "104.211.159.55:3128", "46.148.216.94:53281", "209.97.129.32:3128", "78.47.153.221:3128", "5.189.162.175:3128", "217.61.108.24:80", "51.15.121.195:3128", "138.201.106.89:3128", "109.110.42.210:41258", "94.251.6.193:81", "194.67.221.125:3128", "180.97.193.58:3128", "188.0.20.45:53281", "94.130.92.60:3128", "54.36.162.123:10000", "163.172.220.221:8888", "94.130.240.14:3128", "185.216.35.170:3128", "163.125.68.73:9999", "90.189.145.99:8080", "209.97.138.221:80", "123.31.47.8:3128", "124.172.232.49:8010", "185.22.174.69:1448", "78.136.240.42:8080", "163.172.180.176:3128", "51.15.86.88:3128", "217.150.61.53:8080", "91.121.108.164:3128", "213.129.57.10:80", "121.201.38.71:16053", "145.249.106.107:8118", "178.32.181.66:3128", "35.177.162.201:3128", "91.185.237.71:8080", "144.76.76.25:3128", "80.211.213.200:3128", "188.213.25.197:3128", "159.89.212.102:8118", "94.251.19.158:81", "176.62.178.62:8080", "59.106.216.158:60088", "185.22.174.68:10010", "80.211.83.165:3128", "188.68.56.71:3128", "185.22.173.161:10010", "37.230.114.6:3128", "80.240.112.22:41258", "23.94.223.173:8888", "43.252.11.123:8080", "104.40.151.148:3128", "150.95.151.68:8197", "83.234.163.46:8080", "206.125.41.135:80", "5.101.131.26:8080", "212.164.214.169:8080", "88.222.187.98:3128", "95.80.121.79:41258", "78.156.32.142:41258", "85.234.126.107:55555"]

class Bilibili():
    ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36"
        
    def __init__(self):
        self.username = ""
        self.password = ""
        self.cookie = ""
        self.csrf = ""
        self.uid = ""
        self.accessKey = ""
        self.info = {'nickname': "",
                     'face': "",
                     'coins': 0,
                     'main': {'level': 0,
                              'experience': {'current': 0,
                                             'next': 0},
                              'tasks': {'login': False,
                                        'watch': False,
                                        'reward': 0,
                                        'share': False},
                              'security': {'email': False,
                                           'phone': False,
                                           'safeQuestion': False,
                                           'realName': False}},
                     'live': {'level': 0,
                              'experience': {'current': 0,
                                             'next': 0},
                              'rank': "",
                              'vip': False,
                              'silver': 0,
                              'gold': 0,
                              'achievement': 0}}
        self.proxy = None
    
    def setProxy(self):
        url = "https://api.live.bilibili.com/gift/v2/gift/bag_list"
        while True:
            proxy = random.choice(proxies)
            self.proxy = {'https': f"https://{proxy}"}
            response = self.get(url, timeout=3)
            if response and response.get('code') is not None:
                self.log(f"使用代理: {proxy}")
                return
            else:
                self.log(f"代理不可用: {proxy}")
    
    def post(self, url, data=None, headers=None, decode=True, timeout=10):
        try:
            response = requests.post(url, data=data, headers=headers, timeout=timeout, proxies=self.proxy)
            return response.json() if decode else response.content
        except:
            return None
    
    def get(self, url, headers=None, decode=True, timeout=10):
        try:
            response = requests.get(url, headers=headers, timeout=timeout, proxies=self.proxy)
            return response.json() if decode else response.content
        except:
            return None
    
    def log(self, message):
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))}][{self.uid}] {message}")
        sys.stdout.flush()
    
    def getSign(self, param):
        salt = "560c52ccd288fed045859ed18bffd973"
        signHash = hashlib.md5()
        signHash.update(f"{param}{salt}".encode())
        return signHash.hexdigest()
    
    # 登录
    def login(self, username, password):
        self.username, self.password = username, password
        appKey = "1d8b6e7d45233436"
        url = "https://passport.bilibili.com/api/oauth2/getKey"
        data = {'appkey': appKey,
                'sign': self.getSign(f"appkey={appKey}")}
        response = self.post(url, data=data)
        if response and response.get('code') == 0:
            keyHash = response['data']['hash']
            pubKey = rsa.PublicKey.load_pkcs1_openssl_pem(response['data']['key'].encode())
        else:
            self.log(f"Key获取失败 {response}")
            return False
        url = "https://passport.bilibili.com/api/v2/oauth2/login"
        param = f"appkey={appKey}&password={parse.quote_plus(base64.b64encode(rsa.encrypt(f'{keyHash}{self.password}'.encode(), pubKey)))}&username={parse.quote_plus(self.username)}"
        data = f"{param}&sign={self.getSign(param)}"
        headers = {'Content-type': "application/x-www-form-urlencoded"}
        response = self.post(url, data=data, headers=headers)
        while response and response.get('code') == -105:
            self.cookie = f"sid={''.join(random.choices(string.ascii_lowercase + string.digits, k=8))}"
            url = "https://passport.bilibili.com/captcha"
            headers = {'Cookie': self.cookie,
                       'Host': "passport.bilibili.com",
                       'User-Agent': Bilibili.ua}
            response = self.get(url, headers=headers, decode=False)
            if response is None:
                continue
            url = "http://101.236.6.31:8080/code"
            data = {'image': base64.b64encode(response)}
            response = self.post(url, data=data, decode=False)
            if response is None:
                continue
            captcha = response.decode()
            self.log(f"验证码识别结果为: {captcha}")
            url = "https://passport.bilibili.com/api/v2/oauth2/login"
            param = f"appkey={appKey}&captcha={captcha}&password={parse.quote_plus(base64.b64encode(rsa.encrypt(f'{keyHash}{self.password}'.encode(), pubKey)))}&username={parse.quote_plus(self.username)}"
            data = f"{param}&sign={self.getSign(param)}"
            headers = {'Content-type': "application/x-www-form-urlencoded",
                       'Cookie': self.cookie}
            response = self.post(url, data=data, headers=headers)
        if response and response.get('code') == 0:
            self.cookie = ";".join(f"{i['name']}={i['value']}" for i in response['data']['cookie_info']['cookies'])
            self.csrf = response['data']['cookie_info']['cookies'][0]['value']
            self.uid = response['data']['cookie_info']['cookies'][1]['value']
            self.accessKey = response['data']['token_info']['access_token']
            self.log(f"{self.username}登录成功")
            if exportCookie:
                with open(exportCookie, "a") as f:
                    f.write(f"{self.cookie}\n")
            return True
        else:
            self.log(f"{self.username}登录失败 {response}")
            return False
    
    # 导入Cookie
    def importCookie(self, cookie):
        try:
            self.cookie = cookie
            self.csrf = re.findall(r"bili_jct=(\S+)", self.cookie, re.M)[0].split(";")[0]
            self.uid = re.findall(r"DedeUserID=(\S+)", self.cookie, re.M)[0].split(";")[0]
            self.log("Cookie导入成功")
            return True
        except:
            self.log("Cookie导入失败")
            return False
    
    # 获取用户信息
    def query(self):
        url = "https://account.bilibili.com/home/reward"
        headers = {'Cookie': self.cookie,
                   'Referer': "https://account.bilibili.com/account/home",
                   'User-Agent': Bilibili.ua}
        response = self.get(url, headers=headers)
        if response and response.get('code') == 0:
            self.info['main']['level'] = response['data']['level_info']['current_level']
            self.info['main']['experience']['current'] = response['data']['level_info']['current_exp']
            self.info['main']['experience']['next'] = response['data']['level_info']['next_exp']
            self.info['main']['tasks']['login'] = response['data']['login']
            self.info['main']['tasks']['watch'] = response['data']['watch_av']
            self.info['main']['tasks']['reward'] = response['data']['coins_av']
            self.info['main']['tasks']['share'] = response['data']['share_av']
            self.info['main']['security']['email'] = response['data']['email']
            self.info['main']['security']['phone'] = response['data']['tel']
            self.info['main']['security']['safeQuestion'] = response['data']['safequestion']
            self.info['main']['security']['realName'] = response['data']['identify_card']
            self.log("主站信息获取成功")
        else:
            self.log("主站信息获取失败")
        url = "https://api.live.bilibili.com/User/getUserInfo"
        headers = {'Cookie': self.cookie,
                   'Host': "api.live.bilibili.com",
                   'User-Agent': Bilibili.ua}
        response = self.get(url, headers=headers)
        if response and response.get('code') == "REPONSE_OK":
            self.info['nickname'] = response['data']['uname']
            self.info['face'] = response['data']['face']
            self.info['coins'] = response['data']['billCoin']
            self.info['live']['level'] = response['data']['user_level']
            self.info['live']['experience']['current'] = response['data']['user_intimacy']
            self.info['live']['experience']['next'] = response['data']['user_next_intimacy']
            self.info['live']['rank'] = response['data']['user_level_rank']
            self.info['live']['vip'] = response['data']['vip'] or response['data']['svip']
            self.info['live']['silver'] = response['data']['silver']
            self.info['live']['gold'] = response['data']['gold']
            self.info['live']['achievement'] = response['data']['achieve']
            self.log("直播信息获取成功")
        else:
            self.log("直播信息获取失败")
        self.log(f"昵称: {self.info['nickname']}")
        self.log(f"等级: 主站LV{self.info['main']['level']}({self.info['main']['experience']['current']}/{self.info['main']['experience']['next']}) 直播LV{self.info['live']['level']}({self.info['live']['experience']['current']}/{self.info['live']['experience']['next']})")
        self.log(f"资产: 硬币{self.info['coins']} 银瓜子{self.info['live']['silver']} 金瓜子{self.info['live']['gold']}")
        self.log(f"每日任务: 登录({'✓' if self.info['main']['tasks']['login'] else '✕'}) 观看视频({'✓' if self.info['main']['tasks']['watch'] else '✕'}) 投币({self.info['main']['tasks']['reward'] // 10}/5) 分享视频({'✓' if self.info['main']['tasks']['share'] else '✕'})")
        self.log(f"账号安全: 邮箱({'✓' if self.info['main']['security']['email'] else '✕'}) 手机({'✓' if self.info['main']['security']['phone'] else '✕'}) 密保({'✓' if self.info['main']['security']['safeQuestion'] else '✕'}) 实名认证({'✓' if self.info['main']['security']['realName'] else '✕'})")
    
    # 银瓜子兑换硬币
    def silver2Coins(self):
        url = "https://api.live.bilibili.com/pay/v1/Exchange/silver2coin"
        data = {'platform': "pc",
                'csrf_token': self.csrf}
        headers = {'Cookie': self.cookie,
                   'Host': "api.live.bilibili.com",
                   'Origin': "https://live.bilibili.com",
                   'Referer': "https://live.bilibili.com/exchange",
                   'User-Agent': Bilibili.ua}
        response = self.post(url, data=data, headers=headers)
        if response and response.get('code') == 0:
            self.log("银瓜子兑换硬币(通道1)成功")
        else:
            self.log(f"银瓜子兑换硬币(通道1)失败 {response}")
        url = "https://api.live.bilibili.com/exchange/silver2coin"
        headers = {'Cookie': self.cookie,
                   'Host': "api.live.bilibili.com",
                   'User-Agent': Bilibili.ua}
        response = self.get(url, headers=headers)
        if response and response.get('code') == 0:
            self.log("银瓜子兑换硬币(通道2)成功")
        else:
            self.log(f"银瓜子兑换硬币(通道2)失败 {response}")
    
    # 观看
    def watch(self, aid):
        # aid = 稿件av号
        url = f"https://www.bilibili.com/widget/getPageList?aid={aid}"
        response = self.get(url)
        if response:
            cid = response[0]['cid']
        else:
            self.log("cid解析失败")
            return False
        url = "https://api.bilibili.com/x/report/web/heartbeat"
        data = {'aid': aid,
                'cid': cid,
                'mid': self.uid,
                'csrf': self.csrf,
                'played_time': 0,
                'realtime': 0,
                'start_ts': int(time.time()),
                'type': 3,
                'dt': 2,
                'play_type': 1}
        headers = {'Cookie': self.cookie,
                   'Host': "api.bilibili.com",
                   'Referer': f"https://www.bilibili.com/video/av{aid}",
                   'User-Agent': Bilibili.ua}
        response = self.post(url, data=data, headers=headers)
        if (response and response['code'] == 0) or (response is None):
            self.log(f"av{aid}观看成功")
            return True
        else:
            self.log(f"av{aid}观看失败 {response}")
            return False
    
    # 好评
    def like(self, aid):
        # aid = 稿件av号
        url = "https://api.bilibili.com/x/web-interface/archive/like"
        data = {'aid': aid,
                'like': 1,
                'csrf': self.csrf}
        headers = {'Cookie': self.cookie,
                   'Host': "api.bilibili.com",
                   'Origin': "https://www.bilibili.com",
                   'Referer': f"https://www.bilibili.com/video/av{aid}",
                   'User-Agent': Bilibili.ua}
        response = self.post(url, data=data, headers=headers)
        if response and response.get('code') == 0:
            self.log(f"av{aid}好评成功")
            return True
        else:
            self.log(f"av{aid}好评失败 {response}")
            return False
    
    # 投币
    def reward(self, aid, double):
        # aid = 稿件av号
        # double = 双倍投币
        url = "https://api.bilibili.com/x/web-interface/coin/add"
        data = {'aid': aid,
                'multiply': 2 if double else 1,
                'cross_domain': "true",
                'csrf': self.csrf}
        headers = {'Cookie': self.cookie,
                   'Host': "api.bilibili.com",
                   'Origin': "https://www.bilibili.com",
                   'Referer': f"https://www.bilibili.com/video/av{aid}",
                   'User-Agent': Bilibili.ua}
        response = self.post(url, data=data, headers=headers)
        if response and response.get('code') == 0:
            self.log(f"av{aid}投{2 if double else 1}枚硬币成功")
            return True
        else:
            self.log(f"av{aid}投{2 if double else 1}枚硬币失败 {response}")
            return False
    
    # 收藏
    def favour(self, aid):
        # aid = 稿件av号
        url = "https://api.bilibili.com/x/v2/fav/folder"
        headers = {'Cookie': self.cookie,
                   'Host': "api.bilibili.com",
                   'User-Agent': Bilibili.ua}
        response = self.get(url, headers=headers)
        if response and response.get('data'):
            fid = response['data'][0]['fid']
        else:
            self.log("fid获取失败")
            return False
        time.sleep(1)
        url = "https://api.bilibili.com/x/v2/fav/video/add"
        data = {'aid': aid,
                'fid': fid,
                'jsonp': "jsonp",
                'csrf': self.csrf}
        headers = {'Cookie': self.cookie,
                   'Host': "api.bilibili.com",
                   'Origin': "https://www.bilibili.com",
                   'Referer': f"https://www.bilibili.com/video/av{aid}",
                   'User-Agent': Bilibili.ua}
        response = self.post(url, data=data, headers=headers)
        if response and response.get('code') == 0:
            self.log(f"av{aid}收藏成功")
            return True
        else:
            self.log(f"av{aid}收藏失败 {response}")
            return False
    
    # 分享
    def share(self, aid):
        # aid = 稿件av号
        url = "https://api.bilibili.com/x/web-interface/share/add"
        data = {'aid': aid,
                'jsonp': "jsonp",
                'csrf': self.csrf}
        headers = {'Cookie': self.cookie,
                   'Host': "api.bilibili.com",
                   'Origin': "https://www.bilibili.com",
                   'Referer': f"https://www.bilibili.com/video/av{aid}",
                   'User-Agent': Bilibili.ua}
        response = self.post(url, data=data, headers=headers)
        if response and response.get('code') == 0:
            self.log(f"av{aid}分享成功")
            return True
        else:
            self.log(f"av{aid}分享失败 {response}")
            return False
    
    # 关注
    def follow(self, mid, secret):
        # mid = 被关注用户UID
        # secret = 悄悄关注
        url = "https://api.bilibili.com/x/relation/modify"
        data = {'fid': mid,
                'act': 3 if secret else 1,
                're_src': 11,
                'jsonp': "jsonp",
                'csrf': self.csrf}
        headers = {'Cookie': self.cookie,
                   'Host': "api.bilibili.com",
                   'Origin': "https://space.bilibili.com",
                   'Referer': f"https://space.bilibili.com/{mid}/",
                   'User-Agent': Bilibili.ua}
        response = self.post(url, data=data, headers=headers)
        if response and response.get('code') == 0:
            self.log(f"用户{mid}{'悄悄' if secret else ''}关注成功")
            return True
        else:
            self.log(f"用户{mid}{'悄悄' if secret else ''}关注失败 {response}")
            return False
    
    # 评论点赞
    def commentLike(self, otype, oid, rpid):
        # otype = 作品类型
        # oid = 作品ID
        # rpid = 评论ID
        patterns = {'video': {'id': 1,
                              'prefix': "https://www.bilibili.com/video/av"},
                    'activity': {'id': 4,
                                 'prefix': "https://www.bilibili.com/blackboard/"},
                    'gallery': {'id': 11,
                                'prefix': "https://h.bilibili.com/"},
                    'article': {'id': 12,
                                'prefix': "https://www.bilibili.com/read/cv"}}
        if patterns.get(otype) is None:
            self.log("不支持的作品类型")
            return False
        url = "https://api.bilibili.com/x/v2/reply/action"
        data = {'oid': oid,
                'type': patterns[otype]['id'],
                'rpid': rpid,
                'action': 1,
                'jsonp': "jsonp",
                'csrf': self.csrf}
        headers = {'Content-Type': "application/x-www-form-urlencoded; charset=UTF-8",
                   'Cookie': self.cookie,
                   'Host': "api.bilibili.com",
                   'Origin': "https://www.bilibili.com",
                   'Referer': f"{patterns[otype]['prefix']}{oid}",
                   'User-Agent': Bilibili.ua}
        response = self.post(url, data=data, headers=headers)
        if response and response.get('code') == 0:
            self.log(f"评论{rpid}点赞成功")
            return True
        else:
            self.log(f"评论{rpid}点赞失败 {response}")
            return False
    
    # 评论抢楼
    def commentRush(self, otype, oid, floor, message):
        # otype = 作品类型
        # oid = 作品ID
        # floor = 抢楼楼层
        # message = 评论内容
        patterns = {'video': {'id': 1,
                              'prefix': "https://www.bilibili.com/video/av"},
                    'activity': {'id': 4,
                                 'prefix': "https://www.bilibili.com/blackboard/"},
                    'gallery': {'id': 11,
                                'prefix': "https://h.bilibili.com/"},
                    'article': {'id': 12,
                                'prefix': "https://www.bilibili.com/read/cv"}}
        critical = 3
        if patterns.get(otype) is None:
            self.log("不支持的作品类型")
            return False
        while True:
            url = f"https://api.bilibili.com/x/v2/reply?jsonp=jsonp&pn=1&type={patterns[otype]['id']}&oid={oid}&sort=0&_={int(time.time())}"
            headers = {'Host': "api.bilibili.com",
                       'Referer': f"{patterns[otype]['prefix']}{oid}",
                       'User-Agent': Bilibili.ua}
            response = self.get(url, headers=headers)
            if response and response.get('code') == 0:
                currentFloor = response['data']['replies'][0]['floor']
                deltaFloor = floor - currentFloor
                if deltaFloor > critical:
                    self.log(f"当前评论楼层数为{currentFloor}, 距离目标楼层还有{deltaFloor}层")
                    time.sleep(min(3, max(0, (deltaFloor - 10) * 0.1)))
                elif deltaFloor > 0:
                    self.log(f"当前评论楼层数为{currentFloor}, 开始抢楼")
                    url = "https://api.bilibili.com/x/v2/reply/add"
                    data = {'oid': oid,
                            'type': patterns[otype]['id'],
                            'message': message,
                            'plat': 1,
                            'jsonp': "jsonp",
                            'csrf': self.csrf}
                    headers = {'Content-Type': "application/x-www-form-urlencoded; charset=UTF-8",
                               'Cookie': self.cookie,
                               'Host': "api.bilibili.com",
                               'Origin': "https://www.bilibili.com",
                               'Referer': f"{patterns[otype]['prefix']}{oid}",
                               'User-Agent': Bilibili.ua}
                    success = 0
                    while True:
                        response = self.post(url, data=data, headers=headers)
                        if response and response.get('code') == 0:
                            success += 1
                            self.log(f"评论({success}/{deltaFloor})提交成功")
                        else:
                            self.log(f"评论({success}/{deltaFloor})提交失败 {response}")
                        if (success >= deltaFloor):
                            self.log("停止抢楼")
                            break
                else:
                    self.log(f"当前评论楼层数为{currentFloor}, 目标楼层已过")
                    break
            else:
                self.log(f"当前评论楼层数获取失败 {response}")
                time.sleep(1)
    
    # 动态点赞
    def dynamicLike(self, did):
        # did = 动态ID
        url = "https://api.vc.bilibili.com/dynamic_like/v1/dynamic_like/thumb"
        data = {'uid': self.uid,
                'dynamic_id': did,
                'up': 1,
                'csrf_token': self.csrf}
        headers = {'Content-Type': "application/x-www-form-urlencoded",
                   'Cookie': self.cookie,
                   'Host': "api.vc.bilibili.com",
                   'Origin': "https://space.bilibili.com",
                   'Referer': "https://space.bilibili.com/208259/",
                   'User-Agent': Bilibili.ua}
        response = self.post(url, data=data, headers=headers)
        if response and response.get('code') == 0:
            self.log(f"动态{did}点赞成功")
            return True
        else:
            self.log(f"动态{did}点赞失败 {response}")
            return False
    
    # 动态转发
    def dynamicRepost(self, did, message):
        # did = 动态ID
        # message = 转发内容
        url = "https://api.vc.bilibili.com/dynamic_repost/v1/dynamic_repost/repost"
        data = {'uid': self.uid,
                'dynamic_id': did,
                'content': message,
                'at_uids': None,
                'ctrl': "[]",
                'csrf_token': self.csrf}
        headers = {'Content-Type': "application/x-www-form-urlencoded",
                   'Cookie': self.cookie,
                   'Host': "api.vc.bilibili.com",
                   'Origin': "https://space.bilibili.com",
                   'Referer': "https://space.bilibili.com/208259/",
                   'User-Agent': Bilibili.ua}
        response = self.post(url, data=data, headers=headers)
        if response and response.get('code') == 0:
            self.log(f"动态{did}转发成功")
            return True
        else:
            self.log(f"动态{did}转发失败 {response}")
            return False
    
    # 会员购周年庆活动助力
    def mallAssist(self, mid):
        # mid = 被助力用户UID
        if not (self.info['nickname'] and self.info['face']):
            self.query()
        url = "https://space.bilibili.com/ajax/member/GetInfo"
        data = f"mid={mid}&csrf="
        headers = {'Content-Type': "application/x-www-form-urlencoded",
                   'Host': "space.bilibili.com",
                   'Origin': "https://space.bilibili.com",
                   'Referer': f"https://space.bilibili.com/{mid}/",
                   'User-Agent': Bilibili.ua}
        response = self.post(url, data=data, headers=headers)
        beAssistedUserPortrait = response['data']['face']
        beAssistedUserUname = response['data']['name']
        url = "https://mall.bilibili.com/mall-c/activity_626/buddy_assist_record/buddy_assist"
        data = {'assistUserPortrait': self.info['face'],
                'assistUserUname': self.info['nickname'],
                'beAssistedMid': mid,
                'beAssistedUserPortrait': beAssistedUserPortrait,
                'beAssistedUserUname': beAssistedUserUname}
        headers = {'Content-Type': "application/json",
                   'Cookie': self.cookie,
                   'Host': "mall.bilibili.com",
                   'Origin': "https://www.bilibili.com",
                   'Referer': f"https://www.bilibili.com/blackboard/mall/activity-B1oZiV-Z7.html?uid={mid}",
                   'User-Agent': Bilibili.ua}
        response = self.post(url, data=json.dumps(data), headers=headers)
        if response and response.get('code') == 0:
            self.log(f"{beAssistedUserUname}({mid})会员购周年庆活动助力成功")
            return True
        else:
            self.log(f"{beAssistedUserUname}({mid})会员购周年庆活动助力失败 {response}")
            return False
    
    # 会员购周年庆活动抽奖
    def mallLottery(self):
        jackpots = {'钻石宝库': 14,
                    '黄金宝库': 15,
                    '白银宝库': 16}
        if not (self.info['nickname'] and self.info['face']):
            self.query()
        url = "https://mall.bilibili.com/mall-c/activity_626/lucky_draw"
        data = {'jackpotId': jackpots['钻石宝库'],
                'portrait': self.info['face'],
                'uname': self.info['nickname']}
        headers = {'Content-Type': "application/json",
                   'Cookie': self.cookie,
                   'Host': "mall.bilibili.com",
                   'Origin': "https://www.bilibili.com",
                   'Referer': "https://www.bilibili.com/blackboard/mall/activity-B1oZiV-Z7.html",
                   'User-Agent': Bilibili.ua}
        while True:
            response = self.post(url, data=json.dumps(data), headers=headers)
            if response and response.get('code') is not None:
                if response['code'] == 0:
                    self.log(f"从{next((jackpotName for jackpotName, jackpotID in jackpots.items() if jackpotID == response['data']['jackpotId']), '未知宝库')}中抽到了{response['data']['prizeName']}, 还剩余{response['data']['remainPopularValue']}把钥匙")
                elif response['code'] == 83110025:
                    self.log(f"奖池(ID={data['jackpotId']})不存在, 停止碰撞新奖池ID")
                    break
                elif response['code'] == 83110026:
                    self.log(f"奖池(ID={data['jackpotId']})已失效, 尝试碰撞新奖池ID")
                    jackpots = {jackpotName: jackpots[jackpotName] + len(jackpots) for jackpotName in jackpots}
                    data['jackpotId'] += len(jackpots)
                elif response['code'] == 83110027:
                    self.log(f"钥匙数量已不足以打开{next((jackpotName for jackpotName, jackpotID in jackpots.items() if jackpotID == data['jackpotId']), '未知宝库')}")
                    if data['jackpotId'] in jackpots.values() and list(jackpots.values()).index(data['jackpotId']) < len(jackpots) - 1:
                        data['jackpotId'] = list(jackpots.values())[list(jackpots.values()).index(data['jackpotId']) + 1]
                    else:
                        break
                elif response['code'] == 83110029:
                    self.log(f"{next((jackpotName for jackpotName, jackpotID in jackpots.items() if jackpotID == data['jackpotId']), '未知宝库')}中已经没有奖品了")
                    if data['jackpotId'] in jackpots.values() and list(jackpots.values()).index(data['jackpotId']) < len(jackpots) - 1:
                        data['jackpotId'] = list(jackpots.values())[list(jackpots.values()).index(data['jackpotId']) + 1]
                    else:
                        break
                else:
                    self.log(f"会员购周年庆活动抽奖失败 {response}")
            time.sleep(2)
    
    # 会员购周年庆活动中奖查询
    def mallPrize(self):
        url = "https://mall.bilibili.com/mall-c/activity_626/lucky_draw_record/my_lcuky_draw_list"
        data = {'mid': self.uid}
        headers = {'Content-Type': "application/json",
                   'Cookie': self.cookie,
                   'Host': "mall.bilibili.com",
                   'Origin': "https://www.bilibili.com",
                   'Referer': "https://www.bilibili.com/blackboard/mall/activity-B1oZiV-Z7.html",
                   'User-Agent': Bilibili.ua}
        response = self.post(url, data=json.dumps(data), headers=headers)
        if response and response.get('code') == 0:
            self.log("会员购周年庆活动中奖查询成功")
            prizeNames = [prize['prizeName'] for prize in response['data']]
            prizeNames.sort()
            prizes = {}
            for prizeName in prizeNames:
                prizes[prizeName] = prizes[prizeName] + 1 if prizeName in prizes else 1
            for prizeName, prizeNum in prizes.items():
                self.log(f"{prizeName} x{prizeNum}")
            self.log(f"总计{len(prizeNames)}件奖品")
            return True
        else:
            self.log(f"会员购周年庆活动中奖查询失败 {response}")
            return False
    
    # 小米6X抢F码活动抽奖
    def mi6XLottery(self):
        url = "https://www.bilibili.com/matsuri/get/act/mylotterytimes?act_id=159"
        headers = {'Cookie': self.cookie,
                   'Host': "www.bilibili.com",
                   'Referer': "https://www.bilibili.com/blackboard/activity-mixchuyin.html",
                   'User-Agent': Bilibili.ua}
        response = self.get(url, headers=headers)
        attempts = 0
        while True:
            url = "https://www.bilibili.com/matsuri/index?act_id=159"
            headers = {'Cookie': self.cookie,
                       'Host': "www.bilibili.com",
                       'Origin': "https://www.bilibili.com",
                       'Referer': "https://www.bilibili.com/blackboard/activity-mixchuyin.html",
                       'User-Agent': Bilibili.ua}
            response = self.post(url, headers=headers)
            if response and response.get('code') is not None:
                if response['code'] == -30001:
                    self.log("活动已结束")
                    break
                elif response['code'] == -30010:
                    attempts += 1
                    self.log(f"第{attempts}次抽奖, 未中奖")
                elif response['code'] == -30011:
                    url = "https://www.bilibili.com/matsuri/add/lottery/times?act_id=159"
                    headers = {'Cookie': self.cookie,
                               'Host': "www.bilibili.com",
                               'Referer': "https://www.bilibili.com/blackboard/activity-mixchuyin.html",
                               'User-Agent': Bilibili.ua}
                    response = self.get(url, headers=headers)
                    if response and response.get('code') is not None:
                        if response['code'] == 0:
                            self.log("获取额外5次F码抽奖机会成功")
                        elif response['code'] == -30030:
                            self.log("今日抽奖机会已用完, 停止抽奖")
                            break
                        else:
                            self.log(f"获取额外5次F码抽奖机会失败 {response}")
                    continue
                elif response['code'] == -30019:
                    self.log(f"当前IP被封禁1小时, {'尝试更换代理' if self.proxy else '停止抽奖'}")
                    if self.proxy:
                        self.setProxy()
                        continue
                    else:
                        break
                else:
                    attempts += 1
                    self.log(f"第{attempts}次抽奖, 疑似中奖 {response}")
            time.sleep(1)

def execute(instance):
    instance.log("任务开始执行")
    if useProxy:
        instance.setProxy()
    if tasks['query']:
        instance.query()
    if tasks['silver2Coins']:
        instance.silver2Coins()
    if tasks['watch'] or tasks['like'] or tasks['reward'] or tasks['favour'] or tasks['share']:
        random.shuffle(avs)
        for av in avs:
            if tasks['watch']:
                instance.watch(av)
                time.sleep(1)
            if tasks['like']:
                instance.like(av)
                time.sleep(1)
            if tasks['reward']:
                instance.reward(av, doubleRewards)
                time.sleep(1)
            if tasks['favour']:
                instance.favour(av)
                time.sleep(1)
            if tasks['share']:
                instance.share(av)
                time.sleep(1)
    if tasks['follow']:
        random.shuffle(follows)
        for follow in follows:
            instance.follow(follow['mid'], follow['secret'])
            time.sleep(1)
    if tasks['commentLike']:
        random.shuffle(likeComments)
        for comment in likeComments:
            instance.commentLike(comment['otype'], comment['oid'], comment['rpid'])
            time.sleep(1)
    if tasks['commentRush']:
        instance.commentRush(rushComment['otype'], rushComment['oid'], rushComment['floor'], rushComment['message'])
    if tasks['dynamicLike']:
        random.shuffle(likeDynamicIDs)
        for did in likeDynamicIDs:
            instance.dynamicLike(did)
            time.sleep(1)
    if tasks['dynamicRepost']:
        random.shuffle(repostDynamics)
        for dynamic in repostDynamics:
            instance.dynamicRepost(dynamic['did'], dynamic['message'])
            time.sleep(1)
    if tasks['mallAssist']:
        for uid in beAssistedUIDs:
            instance.mallAssist(uid)
    if tasks['mallLottery']:
        instance.mallLottery()
    if tasks['mallPrize']:
        instance.mallPrize()
    if tasks['mi6XLottery']:
        instance.mi6XLottery()
    instance.log("任务执行完毕")

def wrapper(args):
    instance = Bilibili()
    if (len(args) == 2 and instance.login(args[0], args[1])) or (len(args) == 1 and instance.importCookie(args[0])):
        execute(instance)

if __name__ == '__main__':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    except:
        pass
    if account['username'] and account['password']:
        wrapper([account['username'], account['password']])
    elif cookie:
        wrapper([cookie])
    elif accountsFile:
        accounts = []
        with open(accountsFile) as f:
            for line in f.readlines():
                line = line.strip("\n")
                if len(line.split("----")) == 2:
                    accounts.append(line.split("----"))
        with Pool(processPoolCap) as p:
            p.map(wrapper, [account for account in accounts])
            p.close()
            p.join()
    elif cookiesFile:
        cookies = []
        with open(cookiesFile) as f:
            for line in f.readlines():
                cookies.append([line.strip("\n")])
        with Pool(processPoolCap) as p:
            p.map(wrapper, [cookie for cookie in cookies])
            p.close()
            p.join()
    else:
        print("未配置登录信息")

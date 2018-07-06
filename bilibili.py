#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-

import base64
import datetime
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
account = {'username': "", 'password': ""}
# 2. Cookie
cookie = ""
# 3. 批量导入用户名与密码(格式: 用户名----密码)
accountsFile = ""
# 4. 批量导入Cookie
cookiesFile = ""

# 任务列表
tasks = {'query': True, # 获取用户信息
         'silver2Coins': True, # 银瓜子兑换硬币
         'watch': False, # 观看视频
         'reward': True, # 投币
         'share': False, # 分享视频
         'favour': False, # 收藏视频
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

# 评论相关
# otype为作品类型(视频对应video, 活动对应activity, 相簿对应gallery, 文章对应article), oid为作品ID
# 点赞评论列表(rpid为评论ID)
likeComments = [{'otype': "article", 'oid': 617468, 'rpid': 864171896}]
# 抢楼评论(floor为抢楼楼层, message为评论内容)
rushComment = {'otype': "video", 'oid': 25581792, 'floor': 2233, 'message': "哔哩哔哩 (゜-゜)つロ 干杯~"}

# 动态相关
# 点赞动态ID列表
likeDynamicIDs = [134705258328201427]
# 转发动态列表(did为动态ID, message为转发内容)
repostDynamics = [{'did': 134705258328201427, 'message': "哔哩哔哩 (゜-゜)つロ 干杯~"}]

# 会员购周年庆活动助力用户UID列表
beAssistedUIDs = [124811915, 44587175]

# 导出Cookie到文件, 留空则不导出
exportCookie = "Bilibili-Cookies.txt"

# 进程池容量
processPoolCap = 10

# 代理开关, 强烈建议批量操作时打开
useProxy = False
# HTTPS代理列表
proxies = ["140.143.96.216:80", "118.24.61.165:8118", "113.207.44.70:3128", "180.101.205.253:8888", "106.14.206.26:8118", "113.200.56.13:8010", "118.31.220.3:8080", "47.97.207.93:3128", "118.31.223.194:3128", "119.23.73.27:3128", "118.212.137.135:31288", "47.96.239.158:3128", "47.96.107.52:3128", "223.93.172.248:3128", "54.222.177.145:3128", "115.233.209.134:3128", "1.71.188.37:3128", "101.236.18.101:8866", "14.136.246.173:3128", "221.218.220.167:3128", "118.24.157.22:3128", "120.78.71.63:3128", "101.236.60.225:8866", "43.247.70.250:3128", "166.111.80.162:3128", "101.236.21.22:8866", "180.97.83.42:3128", "39.106.160.36:3128", "58.240.172.110:3128", "114.212.12.4:3128", "221.7.255.168:80", "180.118.241.110:61234", "221.7.255.168:8080", "221.204.213.75:3128", "171.37.158.98:8123", "218.207.212.86:80", "124.193.37.5:8888", "183.129.207.73:12960", "114.115.146.100:3128", "47.96.121.22:3128", "139.224.24.26:8888", "58.22.9.14:3128", "183.129.207.74:17792", "211.136.127.125:80", "47.97.166.158:3128", "160.16.201.57:60088", "163.43.28.199:60088", "124.235.208.252:443", "218.39.192.206:3128", "125.62.26.197:3128", "163.43.28.237:60088", "211.161.103.247:9999", "163.43.30.69:60088", "150.95.147.66:3128", "59.106.223.171:60088", "222.186.45.18:65309", "59.106.217.16:60088", "183.129.207.73:11919", "202.99.172.165:8081", "163.43.31.107:60088", "133.18.174.27:32586", "163.43.30.9:60088", "119.196.18.50:8080", "118.171.31.225:3128", "13.78.35.191:3128", "121.184.72.203:8080", "27.133.153.227:60088", "113.116.127.238:9797", "121.156.109.92:8080", "133.18.173.82:32586", "119.207.78.155:80", "160.16.219.177:60088", "121.152.17.96:3128", "120.78.83.223:3128", "36.66.126.203:8080", "23.100.107.150:3128", "121.150.244.200:3128", "150.95.154.91:3128", "183.245.99.52:80", "112.73.6.40:3128", "150.95.190.145:3128", "133.130.118.134:3128", "58.87.86.75:3128", "223.85.196.75:9999", "39.104.60.114:8080", "5.8.200.203:8080", "46.38.1.0:53281", "5.100.105.250:8080", "94.242.58.14:1448", "103.15.51.160:8080", "113.161.173.10:3128", "178.33.150.97:3128", "94.242.58.14:10010", "183.179.199.225:8080", "46.101.145.206:3128", "185.22.173.161:1448", "185.22.174.69:1448", "94.242.58.108:10010", "94.242.58.142:10010", "185.22.173.130:10010", "185.22.173.130:1448", "173.249.38.68:3128", "94.16.117.29:3128", "51.38.127.242:3128", "195.201.156.125:3128", "95.156.66.94:8080", "94.130.20.85:31288", "103.37.125.120:80", "138.201.223.250:31288", "209.97.129.32:3128", "91.185.237.71:8080", "194.67.201.106:3128", "133.130.117.241:3128", "209.97.138.221:80", "185.216.35.170:3128", "185.22.174.65:1448", "185.22.173.161:10010", "173.249.48.140:8080", "91.121.108.164:3128", "89.31.109.235:8080", "82.64.6.222:3128", "103.200.133.27:8080", "85.234.126.107:55555", "137.74.198.136:80", "188.213.25.197:3128", "178.128.250.51:3128", "194.88.105.156:3128", "94.242.58.108:1448", "80.211.213.200:8080", "217.61.108.24:80", "94.242.58.142:1448", "81.1.245.94:8080", "5.45.107.137:8118", "87.106.23.164:3128", "78.251.218.80:8118", "46.50.141.217:8080", "140.82.38.52:8080", "178.32.181.66:3128", "163.172.180.176:3128", "80.211.213.200:3128", "180.94.88.202:53281", "80.211.148.244:8080", "217.69.3.93:8080", "37.230.114.6:3128", "212.47.235.197:3128", "54.36.162.123:10000", "51.15.86.88:3128", "1.10.141.121:8080", "37.187.114.184:8080", "104.40.151.148:3128", "180.183.122.210:8080", "5.189.163.229:3128", "78.47.153.221:3128", "178.33.35.183:8090", "95.179.131.92:8000", "83.234.163.46:8080", "163.43.30.42:60088", "206.125.41.130:80", "163.172.220.221:8888", "173.82.219.113:3128", "94.130.92.60:3128", "5.189.162.175:3128", "5.101.131.26:8080", "212.237.0.5:8888", "167.99.232.126:8991", "194.67.221.125:3128", "80.211.12.175:3128", "80.211.189.165:3128", "81.25.29.166:41258", "119.28.21.144:8080", "206.81.5.117:8080", "5.255.79.123:8080", "92.53.84.16:8080", "35.184.109.90:3128", "78.108.102.112:53281", "213.114.64.204:80", "114.115.169.31:3128", "94.177.228.81:8080", "80.211.148.244:53", "89.251.32.44:8080", "80.211.169.186:80", "80.211.83.223:3128", "150.95.151.68:8197", "23.100.5.103:8888", "212.67.75.181:41258", "212.237.51.47:3128", "27.133.155.225:60088", "212.237.15.218:3128", "80.211.87.192:80", "212.237.30.203:8888", "23.95.47.86:3128", "80.211.88.108:3128", "137.74.58.147:3128", "51.15.121.195:3128", "138.201.63.123:31288", "212.237.53.59:3128", "82.202.70.15:53281", "80.211.50.116:3128", "82.202.70.132:8080", "46.148.216.94:53281"]

class Bilibili():
    ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36"
    
    timeStamp = lambda: str(int(time.mktime(datetime.datetime.now().timetuple())))
    
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
        data = {'appkey': appKey, 'sign': self.getSign(f"appkey={appKey}")}
        response = self.post(url, data=data)
        if response and response.get('code') == 0:
            keyHash = str(response['data']['hash'])
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
    
    # 观看视频
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
                'played_time': "0",
                'realtime': "0",
                'start_ts': Bilibili.timeStamp(),
                'type': "3",
                'dt': "2",
                'play_type': "1"}
        headers = {'Cookie': self.cookie,
                   'Host': "api.bilibili.com",
                   'Referer': f"https://www.bilibili.com/video/av{aid}",
                   'User-Agent': Bilibili.ua}
        response = self.post(url, data=data, headers=headers)
        if (response and response['code'] == 0) or (response is None):
            self.log(f"av{aid}观看完毕")
            return True
        else:
            self.log(f"av{aid}观看失败 {response}")
            return False
    
    # 投币
    def reward(self, aid, double):
        # aid = 稿件av号
        # double = 双倍投币
        url = "https://api.bilibili.com/x/web-interface/coin/add"
        data = {'aid': str(aid),
                'multiply': "2" if double else "1",
                'cross_domain': "true",
                'csrf': self.csrf}
        headers = {'Cookie': self.cookie,
                   'Host': "api.bilibili.com",
                   'Origin': "https://www.bilibili.com",
                   'Referer': f"https://www.bilibili.com/video/av{aid}",
                   'User-Agent': Bilibili.ua}
        response = self.post(url, data=data, headers=headers)
        if response and response.get('code') == 0:
            self.log(f"av{aid}投{'2' if double else '1'}枚硬币成功")
            return True
        else:
            self.log(f"av{aid}投{'2' if double else '1'}枚硬币失败 {response}")
            return False
    
    # 分享视频
    def share(self, aid):
        # aid = 稿件av号
        url = "https://api.bilibili.com/x/web-interface/share/add"
        data = {'aid': str(aid),
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
    
    # 收藏视频
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
    
    # 评论点赞
    def commentLike(self, otype, oid, rpid):
        # otype = 作品类型
        # oid = 作品ID
        # rpid = 评论ID
        patterns = {'video': {'id': 1, 'prefix': "https://www.bilibili.com/video/av"},
                    'activity': {'id': 4, 'prefix': "https://www.bilibili.com/blackboard/"},
                    'gallery': {'id': 11, 'prefix': "https://h.bilibili.com/"},
                    'article': {'id': 12, 'prefix': "https://www.bilibili.com/read/cv"}}
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
        patterns = {'video': {'id': 1, 'prefix': "https://www.bilibili.com/video/av"},
                    'activity': {'id': 4, 'prefix': "https://www.bilibili.com/blackboard/"},
                    'gallery': {'id': 11, 'prefix': "https://h.bilibili.com/"},
                    'article': {'id': 12, 'prefix': "https://www.bilibili.com/read/cv"}}
        critical = 3
        if patterns.get(otype) is None:
            self.log("不支持的作品类型")
            return False
        while True:
            url = f"https://api.bilibili.com/x/v2/reply?jsonp=jsonp&pn=1&type={patterns[otype]['id']}&oid={oid}&sort=0&_={Bilibili.timeStamp()}"
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
                    self.log("开始抢楼")
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
                'beAssistedMid': str(mid),
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
    if useProxy: instance.setProxy()
    if tasks['query']: instance.query()
    if tasks['silver2Coins']: instance.silver2Coins()
    if tasks['watch'] or tasks['reward'] or tasks['share'] or tasks['favour']:
        random.shuffle(avs)
        for av in avs:
            if tasks['watch']: instance.watch(av); time.sleep(1)
            if tasks['reward']: instance.reward(av, doubleRewards); time.sleep(1)
            if tasks['share']: instance.share(av); time.sleep(1)
            if tasks['favour']: instance.favour(av); time.sleep(1)
    if tasks['commentLike']:
        random.shuffle(likeComments)
        for comment in likeComments:
            instance.commentLike(comment['otype'], comment['oid'], comment['rpid'])
            time.sleep(1)
    if tasks['commentRush']: instance.commentRush(rushComment['otype'], rushComment['oid'], rushComment['floor'], rushComment['message'])
    if tasks['dynamicLike']: [instance.dynamicLike(did) for did in likeDynamicIDs]
    if tasks['dynamicRepost']: [instance.dynamicRepost(dynamic['did'], dynamic['message']) for dynamic in repostDynamics]
    if tasks['mallAssist']: [instance.mallAssist(uid) for uid in beAssistedUIDs]
    if tasks['mallLottery']: instance.mallLottery()
    if tasks['mallPrize']: instance.mallPrize()
    if tasks['mi6XLottery']: instance.mi6XLottery()
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

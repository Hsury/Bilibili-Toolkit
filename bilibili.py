#!/usr/bin/env python3

import base64
import datetime
import hashlib
import json
import random
import re
import requests
import rsa
import time
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
         'watch': True, # 观看视频
         'reward': True, # 投币
         'share': True, # 分享视频
         'favour': True, # 收藏视频
         'mallAssist': True, # 会员购周年庆活动助力
         'mallLuckyDraw': True} # 会员购周年庆活动抽奖

# av列表
avs = [20032006, 14594803, 14361946]

# 双倍投币
doubleRewards = True

# 会员购周年庆活动助力用户UID列表
beAssistedUIDs = [124811915]

# 代理开关
# 使用用户名与密码进行登录时应避免使用代理，以防止出现账号异常
useProxy = False
# HTTP代理列表
proxies = ["101.236.60.225:8866", "101.96.10.5:80", "54.37.238.128:3128", "125.120.53.253:8060", "101.96.10.4:80", "221.234.244.160:8197", "58.250.82.121:9090", "39.137.77.68:80", "101.248.64.66:8080", "114.250.25.19:80", "140.143.96.216:80", "101.236.18.101:8866", "203.95.222.206:31323", "221.7.255.168:80", "118.212.137.135:31288", "101.248.64.69:80", "1.196.161.241:9999", "119.147.93.210:3128", "61.136.163.245:8108", "117.127.0.205:8080", "221.7.255.168:8080", "117.131.235.198:8060", "180.168.251.28:8080", "88.99.149.188:31288", "121.8.98.197:80", "218.106.205.145:8080", "60.165.54.144:8060", "121.43.60.109:3128", "60.255.186.169:8888", "136.243.145.143:80", "118.190.95.25:9001", "58.87.68.189:1080", "101.248.64.66:80", "222.33.192.238:8118", "113.119.81.230:3128", "139.129.207.72:808", "59.44.16.6:8000", "114.226.128.64:6666", "180.97.83.42:3128", "221.193.177.45:8060", "101.236.41.207:3128", "183.189.234.135:8060", "118.24.172.149:1080", "61.136.163.245:3128", "42.236.123.17:80", "180.76.111.69:3128", "113.200.56.13:8010", "140.205.222.3:80", "118.24.127.144:1080", "121.17.18.178:8060", "117.127.0.196:80", "61.183.172.164:9090", "117.127.0.209:8080", "159.226.249.93:8080", "211.21.120.163:8080", "111.231.115.150:8888", "39.105.78.30:3128", "124.166.140.195:8197", "117.127.0.197:80", "1.28.52.192:8197", "180.101.205.253:8888", "116.55.77.81:61202", "183.190.248.157:8060", "119.118.19.216:8197", "120.35.103.238:6666", "27.8.213.223:8060", "59.44.16.6:80", "122.114.31.177:808", "39.137.69.6:80", "110.185.227.237:9999", "1.196.161.172:9999", "47.89.41.164:80", "117.127.0.210:80", "118.70.219.124:53281", "118.190.95.35:9001", "182.86.208.150:8908", "49.51.70.42:1080", "117.141.215.3:1080", "103.78.213.147:80", "121.8.98.198:80", "116.213.98.6:8080", "175.23.251.27:8118", "27.191.234.69:9999", "39.137.69.8:8080", "49.51.193.134:1080", "221.8.171.98:8060", "123.59.199.93:9999", "222.175.73.14:8060", "202.100.83.139:80", "117.65.39.219:31588", "166.111.80.162:3128", "89.31.44.108:3128", "120.78.78.141:8888", "221.182.133.193:1080", "218.207.212.86:80", "60.205.228.133:9999", "106.104.12.222:80", "114.115.182.59:3128", "117.127.0.205:80", "111.172.232.48:8060", "119.41.162.206:53281", "124.207.178.174:9090", "49.51.193.128:1080", "101.248.64.69:8080", "119.39.48.205:9090", "27.154.240.222:8060", "117.65.36.44:31588", "59.32.37.31:808", "60.168.241.190:8888", "49.51.195.24:1080", "219.141.153.2:80", "219.141.153.12:80", "119.179.177.83:8060", "118.24.61.22:3128", "59.44.16.6:8080", "112.73.6.40:3128", "39.137.69.9:80", "39.137.77.66:80", "222.222.236.207:8060", "118.190.95.43:9001", "121.42.167.160:3128", "120.131.9.254:1080", "118.24.22.152:3128", "219.141.153.2:8080", "114.245.1.114:8060", "124.128.76.142:8060", "125.77.25.120:80", "61.135.217.7:80", "211.161.103.247:9999", "222.179.230.2:8060", "218.64.4.220:8060", "117.127.0.209:80", "222.222.250.143:8060", "49.64.7.30:61202", "103.75.27.94:80", "60.18.5.220:80", "66.82.144.29:8080", "39.135.24.11:80", "219.141.153.12:8080", "118.190.95.26:9001", "115.53.79.243:8060", "101.236.60.52:8866", "122.72.108.53:80", "124.235.208.252:443", "39.137.69.6:8080", "122.183.137.190:8080", "125.77.25.117:80", "112.115.57.20:3128", "171.113.195.229:808", "222.88.144.173:8060", "14.118.254.169:6666", "101.236.35.98:8866", "39.104.74.25:8080", "119.187.120.118:8060", "222.88.149.32:8060", "103.206.254.170:65103", "118.114.77.47:8080", "175.9.76.7:8060", "119.23.217.114:3128", "101.236.60.8:8866", "39.137.77.67:8080", "175.98.239.87:8888", "101.236.23.202:8866", "175.146.6.188:8060", "118.190.210.227:3128", "58.247.46.123:8088", "218.59.139.238:80", "124.238.235.135:8000", "221.195.49.100:8060", "124.118.31.104:8060", "49.51.68.122:1080", "119.176.102.45:9999", "112.25.60.32:8080", "107.21.56.41:8080", "27.216.55.161:8888", "121.69.37.238:8118", "221.14.140.130:80", "58.87.98.150:1080", "117.156.234.3:8060", "39.104.28.190:8080", "175.181.40.61:8080", "125.86.120.117:8197", "114.215.95.188:3128", "60.248.222.206:8080", "211.75.82.206:3128", "117.190.90.20:8060", "176.106.39.20:53281", "115.221.230.112:5555", "39.137.69.7:80", "120.76.77.152:9999", "101.81.143.153:8060", "119.10.67.144:808", "39.137.69.10:80", "114.234.81.181:9000", "116.62.139.136:3128", "39.135.24.12:80", "219.157.146.34:8118", "139.224.24.26:8888", "218.60.8.99:3129", "211.159.171.58:80", "89.236.17.106:3128", "39.137.77.67:80", "61.136.163.245:8102", "222.217.68.148:8089", "111.225.10.159:9999", "218.60.8.98:3129", "116.231.34.195:8060", "59.188.151.138:3128", "106.56.102.233:8070", "59.52.57.210:8060", "101.53.101.172:9999", "120.26.110.59:8080", "183.179.199.225:8080", "114.113.126.87:80", "113.200.159.155:9999", "61.136.163.245:8105"]

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
        if useProxy:
            self.proxy = {'http': random.choice(proxies)}
            self.log(f"使用代理: {self.proxy['http']}")
        else:
            self.proxy = None
    
    def post(self, url, data=None, headers=None):
        try:
            return requests.post(url, data=data, headers=headers, proxies=self.proxy).json()
        except:
            return None
    
    def get(self, url, headers=None):
        try:
            return requests.get(url, headers=headers, proxies=self.proxy).json()
        except:
            return None
    
    def log(self, message):
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))}][{self.uid}] {message}")
    
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
        if response and response['code'] == 0:
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
        if response and response['code'] == 0:
            self.cookie = ";".join(f"{i['name']}={i['value']}" for i in response['data']['cookie_info']['cookies'])
            self.csrf = response['data']['cookie_info']['cookies'][0]['value']
            self.uid = response['data']['cookie_info']['cookies'][1]['value']
            self.accessKey = response['data']['token_info']['access_token']
            self.log(f"{self.username}登录成功")
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
        if response and response['code'] == 0:
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
        if response and response['code'] == "REPONSE_OK":
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
        if response and response['code'] == 0:
            self.log("银瓜子兑换硬币(渠道1)成功")
        else:
            self.log(f"银瓜子兑换硬币(渠道1)失败 {response}")
        url = "https://api.live.bilibili.com/exchange/silver2coin"
        headers = {'Cookie': self.cookie,
                   'Host': "api.live.bilibili.com",
                   'User-Agent': Bilibili.ua}
        response = self.get(url, headers=headers)
        if response and response['code'] == 0:
            self.log("银瓜子兑换硬币(渠道2)成功")
        else:
            self.log(f"银瓜子兑换硬币(渠道2)失败 {response}")
    
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
        if response and response['code'] == 0:
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
        if response and response['code'] == 0:
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
        if response:
            fid = response['data'][0]['fid']
        else:
            self.log("fid获取失败")
            return False
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
        if response and response['code'] == 0:
            self.log(f"av{aid}收藏成功")
            return True
        else:
            self.log(f"av{aid}收藏失败 {response}")
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
        if response and response['code'] == 0:
            self.log(f"{beAssistedUserUname}({mid})会员购周年庆活动助力成功")
            return True
        else:
            self.log(f"{beAssistedUserUname}({mid})会员购周年庆活动助力失败 {response}")
            return False
    
    # 会员购周年庆活动抽奖
    def mallLuckyDraw(self):
        if not (self.info['nickname'] and self.info['face']):
            self.query()
        url = "https://mall.bilibili.com/mall-c/activity_626/lucky_draw"
        data = {'jackpotId': 5,
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
            if response:
                if response['code'] == 0:
                    self.log(f"从{'钻石宝库' if response['data']['jackpotId'] == 5 else '黄金宝库' if response['data']['jackpotId'] == 6 else '白银宝库' if response['data']['jackpotId'] == 7 else '未知宝库'}中抽到了{response['data']['prizeName']}, 还剩余{response['data']['remainPopularValue']}把钥匙")
                elif response['code'] == 83110029:
                    self.log(f"{'钻石宝库' if data['jackpotId'] == 5 else '黄金宝库' if data['jackpotId'] == 6 else '白银宝库' if data['jackpotId'] == 7 else '未知宝库'}中已经没有奖品了")
                    if data['jackpotId'] < 7:
                        data['jackpotId'] += 1
                    else:
                        break
                elif response['code'] == 83110027:
                    self.log(f"钥匙数量已不足以打开{'钻石宝库' if data['jackpotId'] == 5 else '黄金宝库' if data['jackpotId'] == 6 else '白银宝库' if data['jackpotId'] == 7 else '未知宝库'}")
                    if data['jackpotId'] < 7:
                        data['jackpotId'] += 1
                    else:
                        break
                else:
                    self.log(f"会员购周年庆活动抽奖失败 {response}")
            time.sleep(1)

def execute(instance):
    instance.log("任务开始执行")
    if tasks['query']: instance.query()
    if tasks['silver2Coins']: instance.silver2Coins()
    random.shuffle(avs)
    for av in avs:
        if tasks['watch']: instance.watch(av)
        if tasks['reward']: instance.reward(av, doubleRewards)
        if tasks['share']: instance.share(av)
        if tasks['favour']: instance.favour(av)
    if tasks['mallAssist']: [instance.mallAssist(uid) for uid in beAssistedUIDs]
    if tasks['mallLuckyDraw']: instance.mallLuckyDraw()
    instance.log("任务执行完毕")

if __name__ == '__main__':
    if account['username'] and account['password']:
        bili = Bilibili()
        if bili.login(account['username'], account['password']):
            execute(bili)
    elif cookie:
        bili = Bilibili()
        if bili.importCookie(cookie):
            execute(bili)
    elif accountsFile:
        with open(accountsFile) as f:
            for line in f.readlines():
                line = line.strip("\n")
                if len(line.split("----")) == 2:
                    username, password = line.split("----")
                    bili = Bilibili()
                    if bili.login(username, password):
                        execute(bili)
                else:
                    print("账号格式有误")
    elif cookiesFile:
        with open(cookiesFile) as f:
            for line in f.readlines():
                cookie = line.strip("\n")
                bili = Bilibili()
                if bili.importCookie(cookie):
                    execute(bili)
    else:
        print("未配置登录信息")

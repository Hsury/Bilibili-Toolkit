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
         'mallLuckyDraw': True, # 会员购周年庆活动抽奖
         'mallPrize': True} # 会员购周年庆活动中奖查询

# av列表
avs = [20032006, 14594803, 14361946]

# 双倍投币
doubleRewards = True

# 会员购周年庆活动助力用户UID列表
beAssistedUIDs = [124811915]

# 代理开关
# 使用用户名与密码进行登录时应避免使用代理, 以防止出现账号异常
useProxy = False
# HTTP代理列表
proxies = ["182.16.171.18:53281", "101.236.18.101:8866", "101.236.60.8:8866", "117.127.0.196:80", "83.219.142.133:3128", "183.196.170.247:9000", "14.102.76.26:8080", "39.137.77.68:80", "219.141.153.12:80", "78.39.101.251:8080", "118.24.22.152:3128", "118.212.137.135:31288", "101.236.35.98:8866", "117.87.178.242:9000", "125.121.120.181:6666", "115.233.209.134:3128", "221.7.255.168:8080", "175.23.251.27:8118", "59.44.16.6:8080", "122.72.108.53:80", "117.127.0.204:80", "114.215.95.188:3128", "218.60.8.98:3129", "182.90.9.97:53", "119.23.217.114:3128", "61.183.172.164:9090", "122.183.139.104:8080", "39.104.122.119:8888", "113.239.243.22:80", "182.245.233.215:8060", "49.51.193.134:1080", "220.143.184.59:3128", "117.127.0.196:8080", "115.148.155.192:8060", "220.130.205.58:8080", "122.116.253.158:8082", "183.189.234.135:8060", "47.94.230.42:9999", "182.88.89.131:8123", "60.13.156.45:8060", "182.18.13.149:53281", "218.207.212.86:80", "60.255.186.169:8888", "180.101.205.253:8888", "101.248.64.66:80", "59.44.16.6:8000", "101.248.64.69:80", "221.7.255.168:80", "101.96.10.5:80", "111.172.232.48:8060", "39.137.69.8:8080", "39.137.77.67:80", "118.190.95.26:9001", "39.137.69.6:80", "218.56.132.155:8080", "175.9.76.7:8060", "114.115.169.31:3128", "101.248.64.69:8080", "219.147.153.185:8080", "119.28.118.116:1080", "27.152.73.36:8197", "139.224.24.26:8888", "39.135.24.11:80", "119.10.67.144:808", "49.51.193.128:1080", "1.64.134.84:808", "116.62.139.136:3128", "121.8.98.198:80", "114.115.182.59:3128", "221.228.17.172:8181", "118.171.188.247:3128", "217.219.25.19:8080", "124.235.208.252:443", "117.127.0.209:80", "49.51.195.24:1080", "120.131.9.254:1080", "183.56.177.130:808", "219.141.153.2:8080", "222.90.19.229:8197", "118.24.89.206:1080", "119.188.162.165:8081", "119.28.194.66:8888", "115.28.209.249:3128", "115.46.88.159:8123", "101.37.79.125:3128", "180.168.251.28:8080", "106.56.102.24:8070", "222.222.250.143:8060", "37.29.48.78:8080", "218.26.227.108:80", "211.21.120.163:8080", "61.236.127.23:8888", "115.28.90.79:9001", "219.141.153.2:80", "223.166.225.101:8060", "175.9.107.190:8197", "221.182.133.87:80", "49.51.70.42:1080", "49.51.68.122:1080", "125.77.25.120:80", "222.33.192.238:8118", "39.135.24.12:80", "221.234.160.17:8197", "47.89.41.164:80", "59.44.16.6:80", "106.1.200.193:8090", "113.200.56.13:8010", "218.59.139.238:80", "140.205.222.3:80", "218.64.4.220:8060", "222.223.203.109:8060", "117.127.0.204:8080", "222.179.226.25:8060", "112.25.60.32:8080", "125.77.25.116:80", "59.127.38.117:8080", "119.39.48.205:9090", "125.72.70.46:8060", "118.24.170.46:1080", "39.137.69.6:8080", "101.248.64.66:8080", "124.42.7.103:80", "117.127.0.205:8080", "121.43.60.109:3128", "115.53.78.17:8060", "117.127.0.209:8080", "125.118.241.81:6666", "121.17.18.178:8060", "194.88.105.156:3128", "121.58.17.52:80", "121.42.167.160:3128", "59.52.57.210:8060", "39.137.69.9:80", "60.165.54.144:8060", "120.35.100.52:6666", "117.141.155.243:53281", "118.190.95.35:9001", "59.48.247.130:8060", "116.62.196.146:3128", "183.189.196.122:8060", "202.100.83.139:80", "118.190.95.43:9001", "101.236.22.141:8866", "139.211.46.185:8197", "101.236.60.48:8866", "140.143.96.216:80", "118.114.77.47:8080", "124.234.254.29:8118", "61.135.217.7:80", "137.59.162.70:8080", "101.236.60.52:8866", "101.236.60.225:8866", "122.114.31.177:808", "121.8.98.197:80", "118.25.16.35:1080", "221.182.133.193:9999", "221.234.244.160:8197", "139.189.252.123:8060"]

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
            self.log("银瓜子兑换硬币(通道1)成功")
        else:
            self.log(f"银瓜子兑换硬币(通道1)失败 {response}")
        url = "https://api.live.bilibili.com/exchange/silver2coin"
        headers = {'Cookie': self.cookie,
                   'Host': "api.live.bilibili.com",
                   'User-Agent': Bilibili.ua}
        response = self.get(url, headers=headers)
        if response and response['code'] == 0:
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
        jackpots = {'钻石宝库': 11,
                    '黄金宝库': 12,
                    '白银宝库': 13}
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
            if response:
                if response['code'] == 0:
                    self.log(f"从{next((jackpotName for jackpotName, jackpotID in jackpots.items() if jackpotID == response['data']['jackpotId']), '未知宝库')}中抽到了{response['data']['prizeName']}, 还剩余{response['data']['remainPopularValue']}把钥匙")
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
        if response and response['code'] == 0:
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
    if tasks['mallPrize']: instance.mallPrize()
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

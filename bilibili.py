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
         'favour': True} # 收藏视频

# av列表
avs = [20032006, 14594803, 14361946]

# 双倍投币
doubleRewards = True

# 代理开关
# 使用用户名与密码进行登录时应避免使用代理，以防止出现账号异常
useProxy = False
# HTTP代理列表
proxies = ["171.37.164.26:8123", "101.96.11.4:80", "200.109.119.126:63909", "39.106.160.36:3128", "61.136.163.245:8103", "211.75.82.206:3128", "39.109.127.7:3128", "114.228.75.247:6666", "117.190.91.209:8060", "203.95.222.206:31323", "50.233.137.32:80", "61.183.172.164:9090", "222.88.147.121:8060", "218.66.232.26:3128", "36.110.175.130:8088", "222.222.236.207:8060", "61.136.163.245:3128", "118.31.33.206:3128", "221.176.212.98:3128", "101.96.10.5:80", "88.247.158.51:8080", "222.88.147.104:8060", "121.196.211.154:3128", "148.243.37.101:53281", "117.127.0.205:8080", "101.248.64.69:80", "122.112.2.9:80", "140.205.222.3:80", "60.13.156.45:8060", "203.69.87.194:8080", "103.38.177.90:53281", "124.42.7.103:80", "221.7.255.168:8080", "61.136.163.245:8106", "116.62.196.146:3128", "39.108.97.146:8888", "36.231.16.132:8080", "121.17.18.178:8060", "203.189.141.162:65103", "117.127.0.205:80", "103.78.213.147:80", "59.44.16.6:8000", "112.115.57.20:3128", "60.205.228.133:9999", "195.234.87.211:53281", "221.228.17.172:8181", "203.95.221.242:53281", "49.51.193.128:1080", "117.127.0.196:80", "118.24.22.152:3128", "101.248.64.69:8080", "59.44.16.6:80", "163.172.220.221:8888", "60.250.79.187:80", "223.96.95.229:3128", "39.105.78.30:3128", "119.176.102.45:9999", "39.104.71.15:8080", "175.23.248.127:8118", "117.127.0.197:8080", "125.121.112.69:6666", "119.23.217.114:3128", "222.33.192.238:8118", "27.50.161.152:808", "203.69.87.193:8080", "39.137.69.6:80", "58.221.72.189:3128", "61.136.163.245:8105", "221.14.140.130:80", "125.72.70.46:8060", "180.168.251.28:8080", "39.137.77.68:8080", "121.58.17.52:80", "118.212.137.135:31288", "113.76.96.232:9797", "114.212.12.4:3128", "117.127.0.204:80", "61.136.163.245:8104", "119.188.162.165:8081", "219.141.153.12:80", "140.240.177.116:8888", "117.127.0.197:80", "122.114.31.177:808", "42.104.84.106:8080", "221.194.108.8:8060", "218.50.2.102:8080", "218.59.139.238:80", "183.179.199.225:8080", "124.238.235.135:8000", "47.94.230.42:9999", "120.92.174.37:1080", "117.44.134.107:36901", "223.93.172.248:3128", "218.207.212.86:80", "39.104.62.87:8080", "116.213.98.6:8080", "114.215.95.188:3128", "117.127.0.210:80", "222.88.154.56:8060", "101.53.101.172:9999", "114.226.128.190:6666", "117.127.0.209:80", "59.44.16.6:8080", "39.137.69.7:80", "89.187.235.59:8080", "49.51.70.42:1080", "113.255.29.133:8197", "121.43.60.109:3128", "120.131.9.254:1080", "122.72.108.53:80", "101.132.136.83:808", "202.46.42.156:8080", "66.82.144.29:8080", "101.248.64.66:80", "50.233.137.37:80", "118.24.61.22:3128", "103.36.35.106:8080", "49.51.68.122:1080", "114.115.169.31:3128", "220.143.169.211:3128", "180.101.205.253:8888", "222.89.85.158:8060", "221.182.133.242:80", "221.7.255.168:80", "119.10.67.144:808", "59.48.247.130:8060", "136.243.145.143:80", "27.158.161.71:808", "121.8.98.197:80", "221.14.140.66:80", "117.127.0.196:8080", "101.37.79.125:3128", "49.51.232.45:1080", "112.24.107.116:8908", "50.233.137.39:80", "116.62.139.136:3128", "119.28.99.194:3128", "121.17.18.218:8060", "118.24.157.22:3128", "121.42.167.160:3128", "222.73.68.144:8090", "117.127.0.209:8080", "49.51.195.24:1080", "58.87.86.75:3128", "222.222.169.60:53281", "120.55.53.109:3128", "101.96.10.4:80", "219.141.153.12:8080", "59.188.151.138:3128", "111.3.122.245:8060", "202.100.83.139:80", "58.247.46.123:8088", "218.93.207.26:8088", "122.183.137.190:8080", "58.221.72.184:3128", "123.57.207.2:3128", "60.255.186.169:8888", "119.123.176.175:9000", "118.24.172.37:1080", "107.21.56.41:8080", "115.28.209.249:3128", "218.60.8.99:3129", "101.248.64.66:8080", "87.226.192.193:8080", "117.131.235.198:8060", "119.147.93.210:3128", "113.200.56.13:8010", "139.224.24.26:8888", "182.18.13.149:53281", "112.73.6.40:3128", "119.39.48.205:9090", "115.28.90.79:9001", "49.51.193.134:1080", "118.114.77.47:8080", "124.118.31.104:8060", "117.127.0.195:8080", "110.164.181.164:8080", "61.135.217.7:80"]

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
                    username = line.split("----")[0]
                    password = line.split("----")[1]
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

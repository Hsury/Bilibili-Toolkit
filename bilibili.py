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
import sys
import time
from multiprocessing import Pool
from urllib import parse

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

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
         'likeComment': False, # 评论点赞
         'rushComment': False, # 评论抢楼
         'mallAssist': False, # 会员购周年庆活动助力
         'mallLuckyDraw': False, # 会员购周年庆活动抽奖
         'mallPrize': False} # 会员购周年庆活动中奖查询

# av列表
avs = [20032006, 14594803, 14361946]

# 双倍投币
doubleRewards = True

# 评论相关
# otype为作品类型(视频对应video, 相簿对应gallery, 文章对应article), oid为作品ID
# 点赞评论列表(rpid为评论ID)
likeComments = [{'otype': "video", 'oid': 25581792, 'rpid': 861027737}, {'otype': "article", 'oid': 617468, 'rpid': 864171896}]
# 抢楼评论(floor为抢楼楼层, message为评论内容)
rushComment = {'otype': "video", 'oid': 25581792, 'floor': 2233, 'message': "哔哩哔哩 (゜-゜)つロ 干杯~"}

# 会员购周年庆活动助力用户UID列表
beAssistedUIDs = [124811915, 44587175]

# 导出Cookie到文件, 留空则不导出
exportCookie = "Bilibili-Cookies.txt"

# 进程池容量
processPoolCap = 10

# 代理开关
# 使用用户名与密码进行登录时应避免使用代理, 以防止出现账号异常
useProxy = False
# HTTP代理列表
proxies = ["58.251.234.144:9797", "59.44.16.6:8080", "116.62.139.136:3128", "101.96.10.5:80", "114.212.12.4:3128", "218.59.139.238:80", "119.28.21.144:8080", "117.127.0.210:80", "114.115.169.31:3128", "61.136.163.245:3128", "113.222.42.12:8060", "118.24.157.22:3128", "47.94.230.42:9999", "116.62.196.146:3128", "39.106.160.36:3128", "87.103.234.116:3128", "182.113.85.216:8118", "24.132.146.51:80", "122.114.31.177:808", "39.104.122.119:8888", "124.118.31.104:8060", "118.114.77.47:8080", "220.169.232.132:808", "122.72.18.34:80", "221.7.255.168:8080", "117.127.0.205:8080", "116.226.65.250:8060", "116.62.115.14:3128", "60.169.6.150:8080", "58.247.46.123:8088", "61.135.217.7:80", "118.24.156.163:8080", "115.192.193.211:8060", "92.38.47.226:80", "117.45.230.214:3128", "101.236.35.98:8866", "121.8.98.198:80", "212.49.84.113:65103", "118.24.61.22:3128", "118.31.220.3:8080", "118.212.137.135:31288", "166.111.80.162:3128", "42.104.84.107:8080", "39.137.69.8:8080", "39.105.78.30:3128", "112.115.57.20:3128", "183.179.199.225:8080", "101.37.79.125:3128", "219.147.153.185:8080", "122.72.18.35:80", "101.96.10.4:80", "101.236.60.225:8866", "117.127.0.209:80", "218.207.212.86:80", "119.188.162.165:8081", "202.100.83.139:80", "117.127.0.198:80", "119.10.67.144:808", "113.200.56.13:8010", "222.88.154.56:8060", "222.88.147.104:8060", "221.1.205.74:8060", "124.238.235.135:8000", "218.201.55.74:63000", "112.25.60.32:8080", "59.44.16.6:80", "221.7.255.168:80", "114.215.95.188:3128", "222.33.192.238:8118", "119.39.48.205:9090", "121.17.18.219:8060", "125.77.25.120:80", "39.104.168.160:3128", "222.85.31.177:8060", "121.42.167.160:3128", "223.99.25.194:80", "39.137.69.6:8080", "115.28.90.79:9001", "119.122.31.52:9000", "140.143.224.79:3128", "139.224.24.26:8888", "118.190.95.43:9001", "223.197.56.102:80", "117.127.0.204:80", "219.146.153.249:8080", "223.96.95.229:3128", "117.127.0.197:80", "221.234.246.183:8197", "124.235.208.252:443", "61.183.172.164:9090", "60.250.79.187:80", "139.129.99.9:3128", "59.44.16.6:8000", "117.127.0.196:80", "101.236.19.165:8866", "101.96.11.4:80", "117.127.0.204:8080", "42.236.123.17:80", "118.190.95.35:9001", "180.101.205.253:8888", "101.236.22.141:8866", "122.183.139.101:8080"]

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
        time.sleep(random.uniform(1.0, 2.0))
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
    def likeComment(self, otype, oid, rpid):
        # otype = 作品类型
        # oid = 作品ID
        # rpid = 评论ID
        patterns = {'video': {'id': 1, 'prefix': "https://www.bilibili.com/video/av"},
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
    def rushComment(self, otype, oid, floor, message):
        # otype = 作品类型
        # oid = 作品ID
        # floor = 抢楼楼层
        # message = 评论内容
        patterns = {'video': {'id': 1, 'prefix': "https://www.bilibili.com/video/av"},
                    'gallery': {'id': 11, 'prefix': "https://h.bilibili.com/"},
                    'article': {'id': 12, 'prefix': "https://www.bilibili.com/read/cv"}}
        critical = 2
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
                    time.sleep(min(3, (deltaFloor - critical - 1) * 0.1))
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
    def mallLuckyDraw(self):
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

def execute(instance):
    instance.log("任务开始执行")
    if tasks['query']: instance.query()
    if tasks['silver2Coins']: instance.silver2Coins()
    if tasks['watch'] or tasks['reward'] or tasks['share'] or tasks['favour']:
        random.shuffle(avs)
        for av in avs:
            if tasks['watch']: instance.watch(av)
            if tasks['reward']: instance.reward(av, doubleRewards)
            if tasks['share']: instance.share(av)
            if tasks['favour']: instance.favour(av)
            time.sleep(random.uniform(1.0, 2.0))
    if tasks['likeComment']:
        random.shuffle(likeComments)
        for comment in likeComments:
            instance.likeComment(comment['otype'], comment['oid'], comment['rpid'])
            time.sleep(random.uniform(1.0, 2.0))
    if tasks['rushComment']: instance.rushComment(rushComment['otype'], rushComment['oid'], rushComment['floor'], rushComment['message'])
    if tasks['mallAssist']: [instance.mallAssist(uid) for uid in beAssistedUIDs]
    if tasks['mallLuckyDraw']: instance.mallLuckyDraw()
    if tasks['mallPrize']: instance.mallPrize()
    instance.log("任务执行完毕")

def wrapper(args):
    instance = Bilibili()
    if (len(args) == 2 and instance.login(args[0], args[1])) or (len(args) == 1 and instance.importCookie(args[0])):
        execute(instance)

if __name__ == '__main__':
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

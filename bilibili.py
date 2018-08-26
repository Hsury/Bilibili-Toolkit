#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-

import base64
import hashlib
import io
import json
import os
import platform
import random
import requests
import rsa
import shutil
import string
import subprocess
import sys
import threading
import time
import toml
from multiprocessing import freeze_support, Pool
from selenium import webdriver
from urllib import parse

class Bilibili():
    appKey = "1d8b6e7d45233436"
    ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.84 Safari/537.36"
    
    def __init__(self):
        self.cookie = ""
        self.csrf = ""
        self.uid = ""
        self.accessToken = ""
        self.refreshToken = ""
        self.username = ""
        self.password = ""
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
        self.proxyPool = set()
    
    def log(self, message):
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))}][{self.uid}] {message}", flush=True)
    
    def get(self, url, headers=None, decodeLevel=2, timeout=10, retry=5):
        for i in range(retry + 1):
            try:
                response = requests.get(url, headers=headers, timeout=timeout, proxies=self.proxy)
                return response.json() if decodeLevel == 2 else response.content if decodeLevel == 1 else response
            except:
                if self.proxy:
                    self.setProxy()
        return None
    
    def post(self, url, data=None, headers=None, decodeLevel=2, timeout=10, retry=5):
        for i in range(retry + 1):
            try:
                response = requests.post(url, data=data, headers=headers, timeout=timeout, proxies=self.proxy)
                return response.json() if decodeLevel == 2 else response.content if decodeLevel == 1 else response
            except:
                if self.proxy:
                    self.setProxy()
        return None
    
    def addProxy(self, proxy):
        if isinstance(proxy, str):
            self.proxyPool.add(proxy)
        elif isinstance(proxy, list):
            self.proxyPool.update(proxy)
    
    def setProxy(self):
        proxy = random.sample(self.proxyPool, 1)[0]
        self.proxy = {'https': f"https://{proxy}"}
        self.log(f"使用代理: {proxy}")
    
    def getSign(self, param):
        salt = "560c52ccd288fed045859ed18bffd973"
        signHash = hashlib.md5()
        signHash.update(f"{param}{salt}".encode())
        return signHash.hexdigest()
    
    def importCredential(self, pairs):
        for key, value in pairs.items():
            if key in ["bili_jct", "DedeUserID", "DedeUserID__ckMd5", "sid", "SESSDATA"]:
                if key == "bili_jct":
                    self.csrf = value
                elif key == "DedeUserID":
                    self.uid = value
                self.cookie = f"{self.cookie}{key}={value};"
            elif key == "accessToken":
                self.accessToken = value
            elif key == "refreshToken":
                self.refreshToken = value
            elif key == "username":
                self.username = value
            elif key == "password":
                self.password = value
    
    # 登录
    def login(self):
        def useCookie():
            url = "https://api.bilibili.com/x/space/myinfo"
            headers = {'Cookie': self.cookie,
                       'Host': "api.bilibili.com",
                       'User-Agent': Bilibili.ua}
            response = self.get(url, headers=headers)
            if response and response.get("code") != -101:
                self.log("Cookie仍有效")
                return True
            else:
                self.cookie = ""
                self.log("Cookie已失效")
                return False
        
        def useToken():
            param = f"access_key={self.accessToken}&appkey={Bilibili.appKey}&ts={int(time.time())}"
            url = f"https://passport.bilibili.com/api/v2/oauth2/info?{param}&sign={self.getSign(param)}"
            response = self.get(url)
            if response and response.get("code") == 0:
                self.uid = response['data']['mid']
                self.log(f"Token仍有效, 有效期至{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time() + int(response['data']['expires_in'])))}")
                if not self.cookie:
                    param = f"access_key={self.accessToken}&appkey={Bilibili.appKey}&gourl=https%3A%2F%2Faccount.bilibili.com%2Faccount%2Fhome&ts={int(time.time())}"
                    url = f"https://passport.bilibili.com/api/login/sso?{param}&sign={self.getSign(param)}"
                    session = requests.session()
                    session.get(url)
                    self.importCredential(session.cookies.get_dict())
                return True
            else:
                self.log(f"Token已失效")
                url = "https://passport.bilibili.com/api/v2/oauth2/refresh_token"
                param = f"access_key={self.accessToken}&appkey={Bilibili.appKey}&refresh_token={self.refreshToken}&ts={int(time.time())}"
                data = f"{param}&sign={self.getSign(param)}"
                headers = {'Content-type': "application/x-www-form-urlencoded"}
                response = self.post(url, data=data, headers=headers)
                if response and response.get("code") == 0:
                    self.cookie = "".join(f"{i['name']}={i['value']};" for i in response['data']['cookie_info']['cookies'])
                    self.csrf = response['data']['cookie_info']['cookies'][0]['value']
                    self.uid = response['data']['cookie_info']['cookies'][1]['value']
                    self.accessToken = response['data']['token_info']['access_token']
                    self.refreshToken = response['data']['token_info']['refresh_token']
                    self.log(f"Token刷新成功, 有效期至{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time() + int(response['data']['expires_in'])))}")
                    return True
                else:
                    self.accessToken = ""
                    self.refreshToken = ""
                    self.log("Token刷新失败")
            return False
        
        def usePassword():
            url = "https://passport.bilibili.com/api/oauth2/getKey"
            data = {'appkey': Bilibili.appKey,
                    'sign': self.getSign(f"appkey={Bilibili.appKey}")}
            response = self.post(url, data=data)
            if response and response.get("code") == 0:
                keyHash = response['data']['hash']
                pubKey = rsa.PublicKey.load_pkcs1_openssl_pem(response['data']['key'].encode())
            else:
                self.log(f"Key获取失败 {response}")
                return False
            freeze = False
            while True:
                url = "https://passport.bilibili.com/api/v2/oauth2/login"
                param = f"appkey={Bilibili.appKey}&password={parse.quote_plus(base64.b64encode(rsa.encrypt(f'{keyHash}{self.password}'.encode(), pubKey)))}&username={parse.quote_plus(self.username)}"
                data = f"{param}&sign={self.getSign(param)}"
                headers = {'Content-type': "application/x-www-form-urlencoded"}
                response = self.post(url, data=data, headers=headers)
                if response:
                    while True:
                        if response["code"] == -105:
                            self.cookie = f"sid={''.join(random.choices(string.ascii_lowercase + string.digits, k=8))}"
                            url = "https://passport.bilibili.com/captcha"
                            headers = {'Cookie': self.cookie,
                                       'Host': "passport.bilibili.com",
                                       'User-Agent': Bilibili.ua}
                            response = self.get(url, headers=headers, decodeLevel=1)
                            url = "http://47.95.255.188:5000/code"
                            data = {'image': base64.b64encode(response)}
                            response = self.post(url, data=data, decodeLevel=1, timeout=15)
                            captcha = response.decode() if response and len(response) == 5 else None
                            if captcha:
                                self.log(f"验证码识别结果为: {captcha}")
                                url = "https://passport.bilibili.com/api/v2/oauth2/login"
                                param = f"appkey={Bilibili.appKey}&captcha={captcha}&password={parse.quote_plus(base64.b64encode(rsa.encrypt(f'{keyHash}{self.password}'.encode(), pubKey)))}&username={parse.quote_plus(self.username)}"
                                data = f"{param}&sign={self.getSign(param)}"
                                headers = {'Content-type': "application/x-www-form-urlencoded",
                                           'Cookie': self.cookie}
                                response = self.post(url, data=data, headers=headers)
                            else:
                                self.log(f"验证码识别服务暂时不可用, {'尝试更换代理' if self.proxy else '30秒后重试'}")
                                if self.proxy:
                                    self.setProxy()
                                else:
                                    time.sleep(30)
                                break
                        elif response["code"] == 0:
                            self.cookie = "".join(f"{i['name']}={i['value']};" for i in response['data']['cookie_info']['cookies'])
                            self.csrf = response['data']['cookie_info']['cookies'][0]['value']
                            self.uid = response['data']['cookie_info']['cookies'][1]['value']
                            self.accessToken = response['data']['token_info']['access_token']
                            self.refreshToken = response['data']['token_info']['refresh_token']
                            self.log(f"{self.username}登录成功")
                            return True
                        else:
                            self.log(f"{self.username}登录失败 {response}")
                            return False
                else:
                    if not freeze:
                        self.log("当前IP登录过于频繁, 进入冷却模式")
                        freeze = True
                    time.sleep(5)
        
        if self.cookie and useCookie():
            return True
        elif self.accessToken and self.refreshToken and useToken():
            return True
        elif self.username and self.password and usePassword():
            return True
        else:
            return False
    
    # 获取用户信息
    def query(self):
        url = "https://account.bilibili.com/home/reward"
        headers = {'Cookie': self.cookie,
                   'Referer': "https://account.bilibili.com/account/home",
                   'User-Agent': Bilibili.ua}
        response = self.get(url, headers=headers)
        if response and response.get("code") == 0:
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
        if response and response.get("code") == "REPONSE_OK":
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
    
    # 修改隐私设置
    def setPrivacy(self, showFavourite=None, showBangumi=None, showTag=None, showReward=None, showInfo=None, showGame=None):
        # showFavourite = 展示[我的收藏夹]
        # showBangumi = 展示[订阅番剧]
        # showTag = 展示[订阅标签]
        # showReward = 展示[最近投币的视频]
        # showInfo = 展示[个人资料]
        # showGame = 展示[最近玩过的游戏]
        privacy = {'fav_video': showFavourite,
                   'bangumi': showBangumi,
                   'tags': showTag,
                   'coins_video': showReward,
                   'user_info': showInfo,
                   'played_game': showGame}
        url = f"https://space.bilibili.com/ajax/settings/getSettings?mid={self.uid}"
        headers = {'Cookie': self.cookie,
                   'Host': "space.bilibili.com",
                   'Referer': f"https://space.bilibili.com/{self.uid}/",
                   'User-Agent': Bilibili.ua}
        response = self.get(url, headers=headers)
        if response and response.get("status") == True:
            for key, value in privacy.items():
                if not response['data']['privacy'][key] ^ value:
                    privacy[key] = None
        else:
            self.log(f"隐私设置获取失败 {response}")
            return False
        url = "https://space.bilibili.com/ajax/settings/setPrivacy"
        headers = {'Cookie': self.cookie,
                   'Host': "space.bilibili.com",
                   'Origin': "https://space.bilibili.com",
                   'Referer': f"https://space.bilibili.com/{self.uid}/",
                   'User-Agent': Bilibili.ua}
        fail = []
        for key, value in privacy.items():
            if value is not None:
                data = {key: 1 if value else 0,
                        'csrf': self.csrf}
                response = self.post(url, data=data, headers=headers)
                if not response or response.get("status") != True:
                    fail.append(key)
        if not fail:
            self.log("隐私设置修改成功")
            return True
        else:
            self.log(f"隐私设置修改失败 {fail}")
            return False
    
    # 银瓜子兑换硬币
    def silver2Coins(self, app=True, pc=False):
        # app = APP通道
        # pc = PC通道
        if app:
            param = f"access_key={self.accessToken}&appkey={Bilibili.appKey}&ts={int(time.time())}"
            url = f"https://api.live.bilibili.com/AppExchange/silver2coin?{param}&sign={self.getSign(param)}"
            headers = {'Cookie': self.cookie}
            response = self.get(url, headers=headers)
            if response and response.get("code") == 0:
                self.log("银瓜子兑换硬币(APP通道)成功")
            else:
                self.log(f"银瓜子兑换硬币(APP通道)失败 {response}")
        if pc:
            url = "https://api.live.bilibili.com/pay/v1/Exchange/silver2coin"
            data = {'platform': "pc",
                    'csrf_token': self.csrf}
            headers = {'Cookie': self.cookie,
                       'Host': "api.live.bilibili.com",
                       'Origin': "https://live.bilibili.com",
                       'Referer': "https://live.bilibili.com/exchange",
                       'User-Agent': Bilibili.ua}
            response = self.post(url, data=data, headers=headers)
            if response and response.get("code") == 0:
                self.log("银瓜子兑换硬币(PC通道)成功")
            else:
                self.log(f"银瓜子兑换硬币(PC通道)失败 {response}")
    
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
        if response and response['code'] == 0 or response is None:
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
        if response and response.get("code") == 0:
            self.log(f"av{aid}好评成功")
            return True
        else:
            self.log(f"av{aid}好评失败 {response}")
            return False
    
    # 投币
    def reward(self, aid, double=True):
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
        if response and response.get("code") == 0:
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
        if response and response.get("data"):
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
        if response and response.get("code") == 0:
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
        if response and response.get("code") == 0:
            self.log(f"av{aid}分享成功")
            return True
        else:
            self.log(f"av{aid}分享失败 {response}")
            return False
    
    # 关注
    def follow(self, mid, secret=False):
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
        if response and response.get("code") == 0:
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
        if response and response.get("code") == 0:
            self.log(f"评论{rpid}点赞成功")
            return True
        else:
            self.log(f"评论{rpid}点赞失败 {response}")
            return False
    
    # 评论发表
    def commentPost(self, otype, oid, message, floor=0, critical=1):
        # otype = 作品类型
        # oid = 作品ID
        # message = 评论内容
        # floor = 目标楼层
        # critical = 临界范围
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
        while True:
            url = f"https://api.bilibili.com/x/v2/reply?jsonp=jsonp&pn=1&type={patterns[otype]['id']}&oid={oid}&sort=0&_={int(time.time())}"
            headers = {'Host': "api.bilibili.com",
                       'Referer': f"{patterns[otype]['prefix']}{oid}",
                       'User-Agent': Bilibili.ua}
            response = self.get(url, headers=headers)
            if response and response.get("code") == 0:
                currentFloor = response['data']['replies'][0]['floor']
                deltaFloor = floor - currentFloor if floor else 1
                if deltaFloor > max(1, critical):
                    self.log(f"当前评论楼层数为{currentFloor}, 距离目标楼层还有{deltaFloor}层")
                    time.sleep(min(3, max(0, (deltaFloor - 10) * 0.1)))
                elif deltaFloor > 0:
                    self.log(f"当前评论楼层数为{currentFloor}, 开始提交评论")
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
                    while success < deltaFloor:
                        response = self.post(url, data=data, headers=headers)
                        if response and response.get("code") == 0:
                            success += 1
                            self.log(f"评论({success}/{deltaFloor})提交成功")
                        else:
                            self.log(f"评论({success}/{deltaFloor})提交失败 {response}")
                    if not floor:
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
        if response and response.get("code") == 0:
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
        if response and response.get("code") == 0:
            self.log(f"动态{did}转发成功")
            return True
        else:
            self.log(f"动态{did}转发失败 {response}")
            return False
    
    # 会员购抢购
    def mallRush(self, itemID, thread=1, headless=True, timeout=10):
        # itemID = 商品ID
        # thread = 线程数
        # headless = 隐藏窗口
        # timeout = 超时刷新
        def executor(threadID):
            def findAndClick(className):
                try:
                    element = driver.find_element_by_class_name(className)
                    element.click()
                except:
                    element = None
                return element
            
            options = webdriver.ChromeOptions()
            options.add_argument("log-level=3")
            if headless:
                options.add_argument("headless")
            else:
                options.add_argument("disable-infobars")
                options.add_argument("window-size=374,729")
            if platform.system() == "Linux":
                options.add_argument("no-sandbox")
            options.add_experimental_option("mobileEmulation", {'deviceName': "Nexus 5"})
            if platform.system() == "Windows":
                options.binary_location = "chrome-win32\\chrome.exe"
            driver = webdriver.Chrome(executable_path="chromedriver.exe" if platform.system() == "Windows" else "chromedriver", chrome_options=options)
            driver.get(f"https://mall.bilibili.com/detail.html?itemsId={itemID}")
            for cookie in self.cookie.strip(";").split(";"):
                name, value = cookie.split("=")
                driver.add_cookie({'domain': ".bilibili.com", 'name': name, 'value': value})
            self.log(f"(线程{threadID})商品{itemID}开始监视库存")
            timestamp = time.time()
            inStock = False
            while True:
                try:
                    result = {className: findAndClick(className) for className in ["bottom-buy-button", "button", "confrim-close", "pay-btn", "expire-time-format", "alert-ok", "error-button"]}
                    if result['bottom-buy-button']:
                        if "bottom-buy-disable" not in result['bottom-buy-button'].get_attribute("class"):
                            if not inStock:
                                self.log(f"(线程{threadID})商品{itemID}已开放购买")
                                inStock = True
                        else:
                            if inStock:
                                self.log(f"(线程{threadID})商品{itemID}暂无法购买, 原因为{result['bottom-buy-button'].text}")
                                inStock = False
                            driver.refresh()
                            timestamp = time.time()
                    if result['pay-btn']:
                        timestamp = time.time()
                    if result['alert-ok']:
                        driver.refresh()
                    if result['expire-time-format']:
                        self.log(f"(线程{threadID})商品{itemID}订单提交成功, 请在{result['expire-time-format'].text}内完成支付")
                        driver.quit()
                        return True
                    if time.time() - timestamp > timeout:
                        self.log(f"(线程{threadID})商品{itemID}操作超时, 当前页面为{driver.current_url}")
                        driver.get(f"https://mall.bilibili.com/detail.html?itemsId={itemID}")
                        timestamp = time.time()
                except:
                    pass
        
        threads = []
        for i in range(thread):
            threads.append(threading.Thread(target=executor, args=(i + 1,)))
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
    
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
        if response and response.get("code") == 0:
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
            if response and response.get("code") is not None:
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
        if response and response.get("code") == 0:
            self.log("会员购周年庆活动中奖查询成功")
            prizeNames = sorted([prize['prizeName'] for prize in response['data']])
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
            if response and response.get("code") is not None:
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
                    if response and response.get("code") is not None:
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

def download(url, saveAs=None):
    print(f"正在下载{url}", flush=True)
    if saveAs is None:
        saveAs = url.split("/")[-1]
    with open(saveAs, "wb") as f:
        response = requests.get(url, stream=True)
        length = response.headers.get("content-length")
        if length:
            length = int(length)
            receive = 0
            for data in response.iter_content(chunk_size=100 * 1024):
                f.write(data)
                receive += len(data)
                percent = receive / length
                print(f"\r[{'=' * int(50 * percent)}{' ' * (50 - int(50 * percent))}] {percent:.0%}", end="", flush=True)
            print(flush=True)
        else:
            f.write(response.content)
    return saveAs

def decompress(file, remove=True):
    shutil.unpack_archive(file)
    if remove:
        os.remove(file)
    print(f"{file}解压完毕", flush=True)

def wrapper(arg):
    addInterval = lambda func, delay: time.sleep(delay)
    config, account = arg['config'], arg['account']
    instance = Bilibili()
    if config['proxy']['enable']:
        instance.addProxy(config['proxy']['pool'])
        instance.setProxy()
    instance.importCredential(account)
    if instance.login():
        threads = []
        if config['query']['enable']:
            threads.append(threading.Thread(target=instance.query))
        if config['setPrivacy']['enable']:
            threads.append(threading.Thread(target=instance.setPrivacy, args=(config['setPrivacy']['showFavourite'], config['setPrivacy']['showBangumi'], config['setPrivacy']['showTag'], config['setPrivacy']['showReward'], config['setPrivacy']['showInfo'], config['setPrivacy']['showGame'])))
        if config['silver2Coins']['enable']:
            threads.append(threading.Thread(target=instance.silver2Coins))
        if config['watch']['enable']:
            threads.append(threading.Thread(target=lambda: [addInterval(instance.watch(aid), 1) for aid in config['watch']['aid']]))
        if config['like']['enable']:
            threads.append(threading.Thread(target=lambda: [addInterval(instance.like(aid), 1) for aid in config['like']['aid']]))
        if config['reward']['enable']:
            threads.append(threading.Thread(target=lambda: [addInterval(instance.reward(aid, double), 1) for aid, double in zip(config['reward']['aid'], config['reward']['double'])]))
        if config['favour']['enable']:
            threads.append(threading.Thread(target=lambda: [addInterval(instance.favour(aid), 1) for aid in config['favour']['aid']]))
        if config['share']['enable']:
            threads.append(threading.Thread(target=lambda: [addInterval(instance.share(aid), 1) for aid in config['share']['aid']]))
        if config['follow']['enable']:
            threads.append(threading.Thread(target=lambda: [addInterval(instance.follow(mid, secret), 1) for mid, secret in zip(config['follow']['mid'], config['follow']['secret'])]))
        if config['commentLike']['enable']:
            threads.append(threading.Thread(target=lambda: [addInterval(instance.commentLike(otype, oid, rpid), 1) for otype, oid, rpid in zip(config['commentLike']['otype'], config['commentLike']['oid'], config['commentLike']['rpid'])]))
        if config['commentPost']['enable']:
            for comment in zip(config['commentPost']['otype'], config['commentPost']['oid'], config['commentPost']['message'], config['commentPost']['floor'], config['commentPost']['critical']):
                threads.append(threading.Thread(target=instance.commentPost, args=(comment[0], comment[1], comment[2], comment[3], comment[4])))
        if config['dynamicLike']['enable']:
            threads.append(threading.Thread(target=lambda: [addInterval(instance.dynamicLike(did), 1) for did in config['dynamicLike']['did']]))
        if config['dynamicRepost']['enable']:
            threads.append(threading.Thread(target=lambda: [addInterval(instance.dynamicRepost(did, message), 1) for did, message in zip(config['dynamicRepost']['did'], config['dynamicRepost']['message'])]))
        if config['mallRush']['enable']:
            for item in zip(config['mallRush']['itemID'], config['mallRush']['thread']):
                threads.append(threading.Thread(target=instance.mallRush, args=(item[0], item[1], config['mallRush']['headless'], config['mallRush']['timeout'])))
        if config['mallAssist']['enable']:
            for mid in config['mallAssist']['mid']:
                threads.append(threading.Thread(target=instance.mallAssist, args=(mid,)))
        if config['mallLottery']['enable']:
            threads.append(threading.Thread(target=instance.mallLottery))
        if config['mallPrize']['enable']:
            threads.append(threading.Thread(target=instance.mallPrize))
        if config['mi6XLottery']['enable']:
            threads.append(threading.Thread(target=instance.mi6XLottery))
        instance.log("任务开始执行")
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        instance.log("任务执行完毕")
    return {'cookie': instance.cookie,
            'accessToken': instance.accessToken,
            'refreshToken': instance.refreshToken,
            'username': instance.username,
            'password': instance.password}

def main():
    configFile = sys.argv[1] if len(sys.argv) > 1 else "bilibili.toml"
    try:
        config = toml.load(configFile)
    except:
        print(f"无法加载{configFile}", flush=True)
        return
    accounts = []
    for line in config['user']['account'].split("\n"):
        try:
            if line[0] == "#":
                continue
            pairs = {}
            for pair in line.strip(";").split(";"):
                if len(pair.split("=")) == 2:
                    key, value = pair.split("=")
                    pairs[key] = value
            cookie = True if all(key in pairs for key in ["bili_jct", "DedeUserID", "DedeUserID__ckMd5", "sid", "SESSDATA"]) else False
            token = True if all(key in pairs for key in ["accessToken", "refreshToken"]) else False
            password = True if all(key in pairs for key in ["username", "password"]) else False
            if cookie or token or password:
                accounts.append(pairs)
        except:
            pass
    config['user'].pop("account")
    print(f"导入了{len(accounts)}个用户", flush=True)
    if not accounts:
        return
    if config['mallRush']['enable']:
        if platform.system() == "Linux" and os.path.exists("/etc/debian_version"):
            prefix = "sudo " if shutil.which("sudo") else ""
            if shutil.which("chromium-browser") is None:
                os.system(f"{prefix}apt -y install chromium-browser")
            if shutil.which("chromedriver") is None:
                os.system(f"{prefix}apt -y install chromium-chromedriver")
                os.system(f"{prefix}ln -s /usr/lib/chromium-browser/chromedriver /usr/bin")
        elif platform.system() == "Linux" and os.path.exists("/etc/redhat-release"):
            prefix = "sudo " if shutil.which("sudo") else ""
            if shutil.which("chromium-browser") is None:
                os.system(f"{prefix}yum -y install chromium")
            if shutil.which("chromedriver") is None:
                os.system(f"{prefix}yum -y install chromedriver")
        elif platform.system() == "Windows":
            if not os.path.exists("chrome-win32\\chrome.exe"):
                decompress(download("https://npm.taobao.org/mirrors/chromium-browser-snapshots/Win/579032/chrome-win32.zip"))
            if not os.path.exists("chromedriver.exe"):
                decompress(download("https://npm.taobao.org/mirrors/chromedriver/2.41/chromedriver_win32.zip"))
        else:
            print("会员购抢购组件不支持在当前平台上运行", flush=True)
            config['mallRush']['enable'] = False
    liveToolProcess = None
    if config['liveTool']['enable']:
        if platform.system() == "Linux" and platform.machine() == "x86_64":
            liveToolSupport = True
            liveToolPkg = "bilibili-live-tool-linux-amd64.tar.gz"
            liveToolCwd = "./bilibili-live-tool-linux-amd64"
            liveToolExec = "./bilibiliLiveTool"
        elif platform.system() == "Linux" and "arm" in platform.machine():
            liveToolSupport = True
            liveToolPkg = "bilibili-live-tool-linux-arm.tar.gz"
            liveToolCwd = "./bilibili-live-tool-linux-arm"
            liveToolExec = "./bilibiliLiveTool"
        elif platform.system() == "Windows":
            liveToolSupport = True
            liveToolPkg = "bilibili-live-tool-windows.zip"
            liveToolCwd = "bilibili-live-tool-windows"
            liveToolExec = f"{liveToolCwd}\\bilibiliLiveTool.exe"
        else:
            liveToolSupport = False
            print("直播助手组件不支持在当前平台上运行", flush=True)
        if liveToolSupport:
            try:
                with open(os.path.join(liveToolCwd, "commit"), "r") as f:
                    LiveToolCurrentCommit = f.read()
            except:
                LiveToolCurrentCommit = None
            liveToolLatestCommit = LiveToolCurrentCommit if LiveToolCurrentCommit else "77c4c85"
            if config['liveTool']['autoUpdate']:
                try:
                    liveToolLatestCommit = requests.get("https://api.github.com/repos/Hsury/Bilibili-Live-Tool/releases/latest").json()["tag_name"]
                    if LiveToolCurrentCommit and LiveToolCurrentCommit != liveToolLatestCommit:
                        print("发现新版本直播助手组件", flush=True)
                except:
                    pass
            if LiveToolCurrentCommit != liveToolLatestCommit:
                decompress(download(f"https://github.com/Hsury/Bilibili-Live-Tool/releases/download/{liveToolLatestCommit}/{liveToolPkg}"))
            liveToolConfig = {}
            liveToolConfig['users'] = []
            liveToolConfig['platform'] = {}
            liveToolConfig['print_control'] = {}
            liveToolConfig['task_control'] = {}
            liveToolConfig['other_control'] = {}
            for account in accounts:
                liveToolConfig['users'].append({'username': account['username'] if account.get("username") else "",
                                                'password': account['password'] if account.get("password") else "",
                                                'access_key': account['accessToken'] if account.get("accessToken") else "",
                                                'cookie': ";".join(f"{key}={value}" for key, value in account.items() if key in ["bili_jct", "DedeUserID", "DedeUserID__ckMd5", "sid", "SESSDATA"]),
                                                'csrf': account['bili_jct'] if account.get("bili_jct") else "",
                                                'uid': account['DedeUserID'] if account.get("DedeUserID") else "",
                                                'refresh_token': account['refreshToken'] if account.get("refreshToken") else ""})
            liveToolConfig['platform']['platform'] = "ios_pythonista"
            liveToolConfig['print_control']['danmu'] = config['liveTool']['printDanmaku']
            liveToolConfig['task_control']['clean-expiring-gift'] = config['liveTool']['giveExpiringGifts']['enable']
            liveToolConfig['task_control']['set-expiring-time'] = config['liveTool']['giveExpiringGifts']['expiringTime']
            liveToolConfig['task_control']['clean_expiring_gift2all_medal'] = config['liveTool']['giveExpiringGifts']['toMedal']
            liveToolConfig['task_control']['clean-expiring-gift2room'] = config['liveTool']['giveExpiringGifts']['toRoom']
            liveToolConfig['task_control']['silver2coin'] = config['liveTool']['dailySilver2Coins']
            liveToolConfig['task_control']['send2wearing-medal'] = config['liveTool']['gainIntimacy']['enable']
            liveToolConfig['task_control']['send2medal'] = config['liveTool']['gainIntimacy']['otherRoom']
            liveToolConfig['task_control']['doublegain_coin2silver'] = config['liveTool']['dailyCoins2Silver']
            liveToolConfig['task_control']['givecoin'] = config['liveTool']['dailyGiveCoins']['number']
            liveToolConfig['task_control']['fetchrule'] = "uper" if config['liveTool']['dailyGiveCoins']['specialUp'] else "bilitop"
            liveToolConfig['task_control']['mid'] = config['liveTool']['dailyGiveCoins']['specialUp']
            liveToolConfig['other_control']['default_monitor_roomid'] = config['liveTool']['monitorRoom']
            with open(os.path.join(liveToolCwd, "config", "user.toml"), "w") as f:
                toml.dump(liveToolConfig, f)
            with open(os.path.join(liveToolCwd, "config", "ips.toml"), "w") as f:
                toml.dump({'list_ips': config['proxy']['pool']}, f)
            try:
                liveToolProcess = subprocess.Popen([liveToolExec], cwd=liveToolCwd)
            except:
                print("直播助手组件启动失败", flush=True)
    try:
        with Pool(min(config['user']['process'], len(accounts))) as p:
            result = p.map(wrapper, [{'config': config,
                                      'account': account} for account in accounts])
            p.close()
            p.join()
        if config['user']['update']:
            with open(configFile, "r+", encoding="utf-8") as f:
                content = f.read()
                before = content.split("account")[0]
                after = content.split("account")[-1].split("\"\"\"")[-1]
                f.seek(0)
                f.truncate()
                f.write(before)
                f.write("account = \"\"\"\n")
                for credential in result:
                    newLine = False
                    for key, value in credential.items():
                        if value:
                            if key == "cookie":
                                f.write(value)
                            else:
                                f.write(f"{key}={value};")
                            newLine = True
                    if newLine:
                        f.write("\n")
                f.write("\"\"\"")
                f.write(after)
            print("凭据已更新", flush=True)
        if liveToolProcess:
            liveToolProcess.wait()
    except:
        if liveToolProcess:
            liveToolProcess.terminate()

if __name__ == '__main__':
    if platform.system() == "Windows":
        freeze_support()
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    except:
        pass
    main()
    if platform.system() == "Windows":
        os.system("pause")

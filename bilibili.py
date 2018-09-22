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
    ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.81 Safari/537.36"
    
    def __init__(self, https=True):
        self.cookie = ""
        self.csrf = ""
        self.uid = ""
        self.sid = ""
        self.accessToken = ""
        self.refreshToken = ""
        self.username = ""
        self.password = ""
        self.info = {'ban': False,
                     'coins': 0,
                     'experience': {'current': 0,
                                    'next': 0},
                     'face': "",
                     'join': "",
                     'level': 0,
                     'nickname': ""}
        self.protocol = "https" if https else "http"
        self.proxy = None
        self.proxyPool = set()
    
    def log(self, message):
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))}][{self.username if self.username else '#' + self.uid if self.uid else ''}] {message}", flush=True)
    
    def get(self, url, headers=None, decodeLevel=2, timeout=15, retry=10):
        for i in range(retry + 1):
            try:
                response = requests.get(url, headers=headers, timeout=timeout, proxies=self.proxy)
                return response.json() if decodeLevel == 2 else response.content if decodeLevel == 1 else response
            except:
                if self.proxy:
                    self.setProxy()
        return None
    
    def post(self, url, data=None, headers=None, decodeLevel=2, timeout=15, retry=10):
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
        if self.proxyPool:
            proxy = random.sample(self.proxyPool, 1)[0]
            self.proxy = {self.protocol: f"{self.protocol}://{proxy}"}
            # self.log(f"使用{self.protocol.upper()}代理: {proxy}")
            return True
        else:
            return False
    
    def getSign(self, param):
        salt = "560c52ccd288fed045859ed18bffd973"
        signHash = hashlib.md5()
        signHash.update(f"{param}{salt}".encode())
        return signHash.hexdigest()
    
    def importCredential(self, pairs):
        for key, value in pairs.items():
            if key == "username":
                self.username = value
            elif key == "password":
                self.password = value
            elif key == "accessToken":
                self.accessToken = value
            elif key == "refreshToken":
                self.refreshToken = value
            elif key in ["bili_jct", "DedeUserID", "DedeUserID__ckMd5", "sid", "SESSDATA"]:
                if key == "bili_jct":
                    self.csrf = value
                elif key == "DedeUserID":
                    self.uid = value
                elif key == "sid":
                    self.sid = value
                self.cookie = f"{self.cookie}{key}={value};"
    
    # 登录
    def login(self):
        def byCookie():
            url = f"{self.protocol}://api.bilibili.com/x/space/myinfo"
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
        
        def byToken():
            param = f"access_key={self.accessToken}&appkey={Bilibili.appKey}&ts={int(time.time())}"
            url = f"{self.protocol}://passport.bilibili.com/api/v2/oauth2/info?{param}&sign={self.getSign(param)}"
            response = self.get(url)
            if response and response.get("code") == 0:
                self.uid = response['data']['mid']
                self.log(f"Token仍有效, 有效期至{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time() + int(response['data']['expires_in'])))}")
                if not self.cookie:
                    param = f"access_key={self.accessToken}&appkey={Bilibili.appKey}&gourl={self.protocol}%3A%2F%2Faccount.bilibili.com%2Faccount%2Fhome&ts={int(time.time())}"
                    url = f"{self.protocol}://passport.bilibili.com/api/login/sso?{param}&sign={self.getSign(param)}"
                    session = requests.session()
                    session.get(url)
                    self.importCredential(session.cookies.get_dict())
                return True
            else:
                url = f"{self.protocol}://passport.bilibili.com/api/v2/oauth2/refresh_token"
                param = f"access_key={self.accessToken}&appkey={Bilibili.appKey}&refresh_token={self.refreshToken}&ts={int(time.time())}"
                data = f"{param}&sign={self.getSign(param)}"
                headers = {'Content-type': "application/x-www-form-urlencoded"}
                response = self.post(url, data=data, headers=headers)
                if response and response.get("code") == 0:
                    self.cookie = "".join(f"{i['name']}={i['value']};" for i in response['data']['cookie_info']['cookies'])
                    self.csrf = response['data']['cookie_info']['cookies'][0]['value']
                    self.uid = response['data']['cookie_info']['cookies'][1]['value']
                    self.sid = response['data']['cookie_info']['cookies'][3]['value']
                    self.accessToken = response['data']['token_info']['access_token']
                    self.refreshToken = response['data']['token_info']['refresh_token']
                    self.log(f"Token刷新成功, 有效期至{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time() + int(response['data']['token_info']['expires_in'])))}")
                    return True
                else:
                    self.accessToken = ""
                    self.refreshToken = ""
                    self.log("Token刷新失败")
            return False
        
        def byPassword():
            def getKey():
                url = f"{self.protocol}://passport.bilibili.com/api/oauth2/getKey"
                data = {'appkey': Bilibili.appKey,
                        'sign': self.getSign(f"appkey={Bilibili.appKey}")}
                while True:
                    response = self.post(url, data=data)
                    if response and response.get("code") == 0:
                        return {'keyHash': response['data']['hash'],
                                'pubKey': rsa.PublicKey.load_pkcs1_openssl_pem(response['data']['key'].encode())}
                    else:
                        time.sleep(1)
            
            while True:
                key = getKey()
                keyHash, pubKey = key['keyHash'], key['pubKey']
                url = f"{self.protocol}://passport.bilibili.com/api/v2/oauth2/login"
                param = f"appkey={Bilibili.appKey}&password={parse.quote_plus(base64.b64encode(rsa.encrypt(f'{keyHash}{self.password}'.encode(), pubKey)))}&username={parse.quote_plus(self.username)}"
                data = f"{param}&sign={self.getSign(param)}"
                headers = {'Content-type': "application/x-www-form-urlencoded"}
                response = self.post(url, data=data, headers=headers)
                while True:
                    if response:
                        if response['code'] == -105:
                            sid = "".join(random.choices(string.ascii_lowercase + string.digits, k=8))
                            url = f"{self.protocol}://passport.bilibili.com/captcha"
                            headers = {'Cookie': f"sid={sid}",
                                       'Host': "passport.bilibili.com",
                                       'User-Agent': Bilibili.ua}
                            response = self.get(url, headers=headers, decodeLevel=1)
                            url = "http://132.232.138.236:2233/captcha"
                            data = base64.b64encode(response)
                            response = self.post(url, data=data, decodeLevel=1)
                            captcha = response.decode() if response and len(response) == 5 else None
                            if captcha:
                                self.log(f"验证码识别结果: {captcha}")
                                key = getKey()
                                keyHash, pubKey = key['keyHash'], key['pubKey']
                                url = f"{self.protocol}://passport.bilibili.com/api/v2/oauth2/login"
                                param = f"appkey={Bilibili.appKey}&captcha={captcha}&password={parse.quote_plus(base64.b64encode(rsa.encrypt(f'{keyHash}{self.password}'.encode(), pubKey)))}&username={parse.quote_plus(self.username)}"
                                data = f"{param}&sign={self.getSign(param)}"
                                headers = {'Content-type': "application/x-www-form-urlencoded",
                                           'Cookie': f"sid={sid}"}
                                response = self.post(url, data=data, headers=headers)
                            else:
                                self.log(f"验证码识别服务暂时不可用, {'尝试更换代理' if self.proxy else '5秒后重试'}")
                                if self.proxy:
                                    self.setProxy()
                                else:
                                    time.sleep(5)
                                break
                        elif response['code'] == 0 and response['data']['status'] == 0:
                            self.cookie = "".join(f"{i['name']}={i['value']};" for i in response['data']['cookie_info']['cookies'])
                            self.csrf = response['data']['cookie_info']['cookies'][0]['value']
                            self.uid = response['data']['cookie_info']['cookies'][1]['value']
                            self.sid = response['data']['cookie_info']['cookies'][3]['value']
                            self.accessToken = response['data']['token_info']['access_token']
                            self.refreshToken = response['data']['token_info']['refresh_token']
                            self.log("登录成功")
                            return True
                        else:
                            self.log(f"登录失败 {response}")
                            return False
                    else:
                        self.log(f"当前IP登录过于频繁, {'尝试更换代理' if self.proxy else '30秒后重试'}")
                        if self.proxy:
                            self.setProxy()
                        else:
                            time.sleep(30)
                        break
        
        if self.cookie and byCookie():
            return True
        elif self.accessToken and self.refreshToken and byToken():
            return True
        elif self.username and self.password and byPassword():
            return True
        else:
            return False
    
    # 获取用户信息
    def query(self):
        url = f"{self.protocol}://api.bilibili.com/x/space/myinfo?jsonp=jsonp"
        headers = {'Cookie': self.cookie,
                   'Host': "api.bilibili.com",
                   'Referer': f"https://space.bilibili.com/{self.uid}/",
                   'User-Agent': Bilibili.ua}
        response = self.get(url, headers=headers)
        if response and response.get("code") == 0:
            self.info['ban'] = bool(response['data']['silence'])
            self.info['coins'] = response['data']['coins']
            self.info['experience']['current'] = response['data']['level_exp']['current_exp']
            self.info['experience']['next'] = response['data']['level_exp']['next_exp']
            self.info['face'] = response['data']['face']
            self.info['join'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(response['data']['jointime']))
            self.info['level'] = response['data']['level']
            self.info['nickname'] = response['data']['name']
            self.log(f"{self.info['nickname']}(UID={self.uid}), Lv.{self.info['level']}({self.info['experience']['current']}/{self.info['experience']['next']}), 拥有{self.info['coins']}枚硬币, 注册于{self.info['join']}, 账号{'状态正常' if not self.info['ban'] else '被封禁'}")
            return True
        else:
            self.log("用户信息获取失败")
            return False
    
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
        url = f"{self.protocol}://space.bilibili.com/ajax/settings/getSettings?mid={self.uid}"
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
        url = f"{self.protocol}://space.bilibili.com/ajax/settings/setPrivacy"
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
            url = f"{self.protocol}://api.live.bilibili.com/AppExchange/silver2coin?{param}&sign={self.getSign(param)}"
            headers = {'Cookie': self.cookie}
            response = self.get(url, headers=headers)
            if response and response.get("code") == 0:
                self.log("银瓜子兑换硬币(APP通道)成功")
            else:
                self.log(f"银瓜子兑换硬币(APP通道)失败 {response}")
        if pc:
            url = f"{self.protocol}://api.live.bilibili.com/pay/v1/Exchange/silver2coin"
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
        url = f"{self.protocol}://api.bilibili.com/x/web-interface/view?aid={aid}"
        response = self.get(url)
        if response:
            cid = response['data']['cid']
            duration = response['data']['duration']
        else:
            self.log(f"av{aid}信息解析失败")
            return False
        url = f"{self.protocol}://api.bilibili.com/x/report/click/h5"
        data = {'aid': aid,
                'cid': cid,
                'part': 1,
                'did': self.sid,
                'ftime': int(time.time()),
                'jsonp': "jsonp",
                'lv': None,
                'mid': self.uid,
                'csrf': self.csrf,
                'stime': int(time.time())}
        headers = {'Cookie': self.cookie,
                   'Host': "api.bilibili.com",
                   'Origin': "https://www.bilibili.com",
                   'Referer': f"https://www.bilibili.com/video/av{aid}",
                   'User-Agent': Bilibili.ua}
        response = self.post(url, data=data, headers=headers)
        if response and response.get("code") == 0:
            url = f"{self.protocol}://api.bilibili.com/x/report/web/heartbeat"
            data = {'aid': aid,
                    'cid': cid,
                    'jsonp': "jsonp",
                    'mid': self.uid,
                    'csrf': self.csrf,
                    'played_time': 0,
                    'pause': False,
                    'realtime': duration,
                    'dt': 7,
                    'play_type': 1,
                    'start_ts': int(time.time())}
            response = self.post(url, data=data, headers=headers)
            if response and response.get("code") == 0:
                time.sleep(5)
                data['played_time'] = duration - 1
                data['play_type'] = 0
                data['start_ts'] = int(time.time())
                response = self.post(url, data=data, headers=headers)
                if response and response.get("code") == 0:
                    self.log(f"av{aid}观看成功")
                    return True
        self.log(f"av{aid}观看失败 {response}")
        return False
    
    # 好评
    def like(self, aid):
        # aid = 稿件av号
        url = f"{self.protocol}://api.bilibili.com/x/web-interface/archive/like"
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
        url = f"{self.protocol}://api.bilibili.com/x/web-interface/coin/add"
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
        url = f"{self.protocol}://api.bilibili.com/x/v2/fav/folder"
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
        url = f"{self.protocol}://api.bilibili.com/x/v2/fav/video/add"
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
        url = f"{self.protocol}://api.bilibili.com/x/web-interface/share/add"
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
        url = f"{self.protocol}://api.bilibili.com/x/relation/modify"
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
    
    # 弹幕发送
    def danmakuPost(self, aid, message, moment=-1):
        # aid = 稿件av号
        # message = 弹幕内容
        # moment = 弹幕发送时间
        url = f"{self.protocol}://api.bilibili.com/x/web-interface/view?aid={aid}"
        response = self.get(url)
        if response:
            oid = response['data']['cid']
            duration = response['data']['duration']
        else:
            self.log(f"av{aid}信息解析失败")
            return False
        while True:
            url = f"{self.protocol}://api.bilibili.com/x/v2/dm/post"
            data = {'type': 1,
                    'oid': oid,
                    'msg': message,
                    'aid': aid,
                    'progress': int(moment * 1000) if moment != -1 else random.randint(0, duration * 1000),
                    'color': 16777215,
                    'fontsize': 25,
                    'pool': 0,
                    'mode': 1,
                    'rnd': int(time.time() * 1000000),
                    'plat': 1,
                    'csrf': self.csrf}
            headers = {'Cookie': self.cookie,
                       'Host': "api.bilibili.com",
                       'Origin': "https://www.bilibili.com",
                       'Referer': f"https://www.bilibili.com/video/av{aid}",
                       'User-Agent': Bilibili.ua}
            response = self.post(url, data=data, headers=headers)
            if response and response.get("code") is not None:
                if response['code'] == 0:
                    self.log(f"av{aid}弹幕\"{message}\"发送成功")
                    return True
                elif response['code'] == 36703:
                    self.log(f"av{aid}弹幕发送频率过快, 10秒后重试")
                    time.sleep(10)
                else:
                    self.log(f"av{aid}弹幕\"{message}\"发送失败 {response}")
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
        url = f"{self.protocol}://api.bilibili.com/x/v2/reply/action"
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
            url = f"{self.protocol}://api.bilibili.com/x/v2/reply?jsonp=jsonp&pn=1&type={patterns[otype]['id']}&oid={oid}&sort=0&_={int(time.time())}"
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
                    url = f"{self.protocol}://api.bilibili.com/x/v2/reply/add"
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
        url = f"{self.protocol}://api.vc.bilibili.com/dynamic_like/v1/dynamic_like/thumb"
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
        url = f"{self.protocol}://api.vc.bilibili.com/dynamic_repost/v1/dynamic_repost/repost"
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
            driver.get(f"{self.protocol}://mall.bilibili.com/detail.html?itemsId={itemID}")
            for cookie in self.cookie.strip(";").split(";"):
                name, value = cookie.split("=")
                driver.add_cookie({'domain': ".bilibili.com", 'name': name, 'value': value})
            self.log(f"(线程{threadID})商品{itemID}开始监视库存")
            url = f"{self.protocol}://mall.bilibili.com/mall-c/items/info?itemsId={itemID}"
            while True:
                response = self.get(url)
                if response and response.get("code") == 0 and response['data']['status'] not in [13, 14] and response['data']['activityInfoVO']['serverTime'] >= response['data']['activityInfoVO']['startTime'] if response['data']['activityInfoVO'] else True:
                    break
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
                        driver.get(f"{self.protocol}://mall.bilibili.com/detail.html?itemsId={itemID}")
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
    
    # 会员购周年庆活动签到
    def mallSign(self):
        url = f"{self.protocol}://mall.bilibili.com/activity/game/sign?gameId=3"
        headers = {'Cookie': self.cookie,
                   'Host': "mall.bilibili.com",
                   'Origin': "https://www.bilibili.com",
                   'Referer': "https://www.bilibili.com/blackboard/mall/activity-fySleoNP-.html",
                   'User-Agent': Bilibili.ua}
        response = self.get(url, headers=headers)
        if response and response.get("code") == 0:
            self.log("会员购周年庆活动签到成功")
            return True
        else:
            self.log(f"会员购周年庆活动签到失败 {response}")
            return False
    
    # 会员购周年庆活动扭蛋
    def mallLottery(self):
        jackpots = {'A档': 10,
                    'B档': 11}
        if not (self.info['nickname'] and self.info['face']):
            self.query()
        url = f"{self.protocol}://mall.bilibili.com/activity/luckydraw"
        data = {'gameId': 3,
                'jackpotId': jackpots['A档'],
                'mid': self.uid,
                'portrait': self.info['face'],
                'uname': self.info['nickname']}
        headers = {'Content-Type': "application/json",
                   'Cookie': self.cookie,
                   'Host': "mall.bilibili.com",
                   'Origin': "https://www.bilibili.com",
                   'Referer': "https://www.bilibili.com/blackboard/mall/activity-fySleoNP-.html",
                   'User-Agent': Bilibili.ua}
        while True:
            response = self.post(url, data=json.dumps(data), headers=headers)
            if response and response.get("code") is not None:
                if response['code'] == 0:
                    self.log(f"从{next((jackpotName for jackpotName, jackpotID in jackpots.items() if jackpotID == response['data']['jackpotId']), '未知档')}中扭到了{response['data']['prizeName']}, 还剩余{response['data']['remainPopularValue']}枚扭蛋币")
                elif response['code'] == 83110025:
                    self.log(f"扭蛋档(ID={data['jackpotId']})不存在, 停止碰撞新扭蛋档ID")
                    break
                elif response['code'] == 83110026:
                    self.log(f"扭蛋档(ID={data['jackpotId']})已失效, 尝试碰撞新扭蛋档ID")
                    jackpots = {jackpotName: jackpots[jackpotName] + len(jackpots) for jackpotName in jackpots}
                    data['jackpotId'] += len(jackpots)
                elif response['code'] == 83110027:
                    self.log(f"扭蛋币数量已不足以扭{next((jackpotName for jackpotName, jackpotID in jackpots.items() if jackpotID == data['jackpotId']), '未知档')}扭蛋")
                    if data['jackpotId'] in jackpots.values() and list(jackpots.values()).index(data['jackpotId']) < len(jackpots) - 1:
                        data['jackpotId'] = list(jackpots.values())[list(jackpots.values()).index(data['jackpotId']) + 1]
                    else:
                        break
                elif response['code'] == 83110029:
                    self.log(f"{next((jackpotName for jackpotName, jackpotID in jackpots.items() if jackpotID == data['jackpotId']), '未知档')}中已经没有扭蛋了")
                    if data['jackpotId'] in jackpots.values() and list(jackpots.values()).index(data['jackpotId']) < len(jackpots) - 1:
                        data['jackpotId'] = list(jackpots.values())[list(jackpots.values()).index(data['jackpotId']) + 1]
                    else:
                        break
                else:
                    self.log(f"会员购周年庆活动扭蛋失败 {response}")
            time.sleep(2)
    
    # 会员购周年庆活动中奖查询
    def mallPrize(self):
        url = f"{self.protocol}://mall.bilibili.com/activity/lucky_draw_record/my_lucky_draw_list?gameId=3"
        headers = {'Cookie': self.cookie,
                   'Host': "mall.bilibili.com",
                   'Origin': "https://www.bilibili.com",
                   'Referer': "https://www.bilibili.com/blackboard/mall/activity-fySleoNP-.html",
                   'User-Agent': Bilibili.ua}
        response = self.get(url, headers=headers)
        if response and response.get("code") == 0:
            self.log("会员购周年庆活动中奖查询成功")
            prizeNames = sorted([prize['prizeName'] for prize in response['data']['luckyDrawRecordDTOS']])
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
    instance = Bilibili(config['global']['https'])
    if config['proxy']['enable']:
        if isinstance(config['proxy']['pool'], str):
            try:
                with open(config['proxy']['pool'], "r") as f:
                    instance.addProxy([proxy for proxy in f.read().strip().split("\n") if proxy])
            except:
                pass
        elif isinstance(config['proxy']['pool'], list):
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
        if config['danmakuPost']['enable']:
            for danmaku in zip(config['danmakuPost']['aid'], config['danmakuPost']['message'], config['danmakuPost']['moment']):
                threads.append(threading.Thread(target=instance.danmakuPost, args=(danmaku[0], danmaku[1], danmaku[2])))
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
        if config['mallSign']['enable']:
            threads.append(threading.Thread(target=instance.mallSign))
        if config['mallLottery']['enable']:
            threads.append(threading.Thread(target=instance.mallLottery))
        if config['mallPrize']['enable']:
            threads.append(threading.Thread(target=instance.mallPrize))
        # instance.log("任务开始执行")
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        # instance.log("任务执行完毕")
    return {'username': instance.username,
            'password': instance.password,
            'accessToken': instance.accessToken,
            'refreshToken': instance.refreshToken,
            'cookie': instance.cookie}

def main():
    configFile = sys.argv[1] if len(sys.argv) > 1 else "config.toml"
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
            password = True if all(key in pairs for key in ["username", "password"]) else False
            token = True if all(key in pairs for key in ["accessToken", "refreshToken"]) else False
            cookie = True if all(key in pairs for key in ["bili_jct", "DedeUserID", "DedeUserID__ckMd5", "sid", "SESSDATA"]) else False
            if password or token or cookie:
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
                decompress(download("https://npm.taobao.org/mirrors/chromium-browser-snapshots/Win/590951/chrome-win32.zip"))
            if not os.path.exists("chromedriver.exe"):
                decompress(download("https://npm.taobao.org/mirrors/chromedriver/2.42/chromedriver_win32.zip"))
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
            liveToolLatestCommit = LiveToolCurrentCommit if LiveToolCurrentCommit else "058fac1"
            if config['liveTool']['autoUpdate']:
                try:
                    liveToolLatestCommit = requests.get("https://api.github.com/repos/Hsury/Bilibili-Live-Tool/releases/latest").json()['tag_name']
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
        with Pool(min(config['global']['process'], len(accounts))) as p:
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

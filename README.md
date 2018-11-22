<p align="center">
<img src="https://cdn.kagamiz.com/Bilibili-Toolkit/bilibili.png" width="300">
</p>

<h1 align="center">- Bilibili Toolkit -</h1>

<p align="center">
<img src="https://img.shields.io/badge/version-2018.11.23-green.svg?longCache=true&style=for-the-badge">
<img src="https://img.shields.io/badge/license-SATA-blue.svg?longCache=true&style=for-the-badge">
</p>

<h4 align="center">🛠️ 哔哩哔哩（B站）辅助工具箱，支持Cookie/Token/Password融合持久化登录与多用户操作</h4>

## 功能

|组件                |版本           |描述                          |
|--------------------|---------------|------------------------------|
|login               |2018/11/22     |登录                          |
|query               |2018/8/28      |获取用户信息                  |
|set_privacy         |2018/7/24      |修改隐私设置                  |
|silver_to_coin      |2018/8/8       |银瓜子兑换硬币                |
|watch               |2018/8/30      |观看                          |
|like                |2018/7/8       |好评                          |
|reward              |2018/11/22     |投币                          |
|favour              |2018/6/20      |收藏                          |
|share               |2018/6/20      |分享                          |
|follow              |2018/7/8       |关注                          |
|danmaku_post        |2018/8/28      |弹幕发送                      |
|comment_like        |2018/6/27      |评论点赞                      |
|comment_post        |2018/8/26      |评论发表                      |
|dynamic_like        |2018/6/29      |动态点赞                      |
|dynamic_repost      |2018/10/13     |动态转发                      |
|mall_rush           |2018/9/24      |会员购抢购                    |
|mall_sign           |2018/9/19      |会员购周年庆活动签到          |
|mall_lottery        |2018/9/24      |会员购周年庆活动扭蛋          |
|mall_prize          |2018/9/19      |会员购周年庆活动中奖查询      |
|live_tool           |2018/8/30      |直播助手                      |

*注：[liveTool直播助手组件](https://github.com/Hsury/Bilibili-Live-Tool)编译自[yjqiang/bili2.0](https://github.com/yjqiang/bili2.0)*

## 使用指南

### 源代码版本（推荐）

1. 克隆或[下载](https://github.com/Hsury/Bilibili-Toolkit/archive/master.zip)本代码仓库，并修改默认配置文件config.toml

```
$ git clone https://github.com/Hsury/Bilibili-Toolkit.git
$ cd Bilibili-Toolkit
$ nano config.toml
```

2. 使用pip安装所需依赖

```
$ python3.6 -m pip install -U requests rsa selenium toml
```

3. 使用Python 3.6启动脚本

```
$ python3.6 bilibili.py
```

### 二进制版本

从[Release页面](https://github.com/Hsury/Bilibili-Toolkit/releases)下载并解压与您的平台适配的压缩包，修改默认配置文件config.toml后运行即可

## 登录验证码识别API

使用CNN卷积神经网络构建，识别准确率达到98.6%

```
url = "http://132.232.138.236:2233/captcha"
payload = base64.b64encode(image)
response = requests.post(url, data=payload)
captcha = response.text
```

## 捐赠

若本项目对您有所帮助，欢迎请我喝杯~~妹汁~~ (=・ω・=)

<p align="center">
<img src="https://cdn.kagamiz.com/Bilibili-Toolkit/donate_alipay.png" width="250">
<img src="https://cdn.kagamiz.com/Bilibili-Toolkit/donate_wechat.png" width="250">
<img src="https://cdn.kagamiz.com/Bilibili-Toolkit/donate_alipay_redpacket.png" width="250">
</p>

## 鸣谢

本项目的灵感与使用到的部分API来自以下项目：

> [czp3009/bilibili-api](https://github.com/czp3009/bilibili-api)

> [yjqiang/bilibili-live-tools](https://github.com/yjqiang/bilibili-live-tools)

## 许可证

Bilibili Toolkit is under The Star And Thank Author License (SATA)

本项目基于MIT协议发布，并增加了SATA协议

您有义务为此开源项目点赞，并考虑额外给予作者适当的奖励 ∠( ᐛ 」∠)＿

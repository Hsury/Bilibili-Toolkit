<p align="center">
<img src="http://dl.kagamiz.com/Bilibili.png" alt="Bilibili" width="300px">
</p>

<h1 align="center">Bilibili-Toolkit</h1>

<p align="center">
<img src="https://img.shields.io/badge/version-2018.8.30-green.svg?longCache=true&style=for-the-badge">
<img src="https://img.shields.io/badge/license-SATA-blue.svg?longCache=true&style=for-the-badge">
</p>

> 🛠️ 哔哩哔哩（B站）辅助工具箱，支持Cookie/Token/Password融合持久化登录与多用户操作

## 功能

|组件                |版本           |描述                          |
|--------------------|---------------|------------------------------|
|login               |2018/8/27      |登录                          |
|query               |2018/8/28      |获取用户信息                  |
|setPrivacy          |2018/7/24      |修改隐私设置                  |
|silver2Coins        |2018/8/8       |银瓜子兑换硬币                |
|watch               |2018/8/30      |观看                          |
|like                |2018/7/8       |好评                          |
|reward              |2018/6/20      |投币                          |
|favour              |2018/6/20      |收藏                          |
|share               |2018/6/20      |分享                          |
|follow              |2018/7/8       |关注                          |
|danmakuPost         |2018/8/28      |弹幕发送                      |
|commentLike         |2018/6/27      |评论点赞                      |
|commentPost         |2018/8/26      |评论发表                      |
|dynamicLike         |2018/6/29      |动态点赞                      |
|dynamicRepost       |2018/6/29      |动态转发                      |
|mallRush            |2018/7/19      |会员购抢购                    |
|mallAssist          |2018/6/22      |会员购周年庆活动助力          |
|mallLottery         |2018/6/23      |会员购周年庆活动抽奖          |
|mallPrize           |2018/6/23      |会员购周年庆活动中奖查询      |
|mi6XLottery         |2018/6/30      |小米6X抢F码活动抽奖           |
|liveTool            |2018/8/30      |直播助手                      |

*注：liveTool直播助手组件编译自[yjqiang/bili2.0](https://github.com/yjqiang/bili2.0)*

## 使用指南

### 二进制版本

从[Release页面](https://github.com/Hsury/Bilibili-Toolkit/releases)下载并解压与您的平台适配的压缩包，修改默认配置文件bilibili.toml后运行即可

### 源代码版本

1. 下载（克隆）本代码仓库，并修改默认配置文件bilibili.toml

```
$ git clone https://github.com/Hsury/Bilibili-Toolkit.git
$ cd Bilibili-Toolkit
$ nano bilibili.toml
```

2. 使用pip安装所需依赖

```
$ python3.6 -m pip install requests rsa selenium toml
```

3. 使用Python 3.6启动脚本

```
$ python3.6 bilibili.py
```

## 鸣谢

本项目的灵感与使用到的部分API来自以下项目：

> [BiliHelper](https://github.com/lkeme/BiliHelper)

> [bilibili-live-tools](https://github.com/yjqiang/bilibili-live-tools)

## 许可证

Bilibili-Toolkit is under The Star And Thank Author License (SATA).

本项目基于MIT协议发布，并增加了SATA协议。

当你使用了使用SATA的开源软件或文档的时候，在遵守基础许可证的前提下，你必须马不停蹄地给你所使用的开源项目“点赞”，比如在GitHub上Star。

然后你必须感谢这个帮助了你的开源项目的作者，作者信息可以在许可证头部的版权声明部分找到。

本项目的所有代码文件、配置项，除另有说明外，均基于上述介绍的协议发布。

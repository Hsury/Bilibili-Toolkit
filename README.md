<p align="center">
<img src="http://dl.kagamiz.com/Bilibili.jpeg" alt="Bilibili" width="300px">
</p>

<h1 align="center">Bilibili-Toolkit</h1>

<p align="center">
<img src="https://img.shields.io/badge/version-2018.6.22-green.svg?longCache=true&style=for-the-badge">
<img src="https://img.shields.io/badge/license-SATA-blue.svg?longCache=true&style=for-the-badge">
</p>

> 🛠️ 哔哩哔哩（B站）辅助工具箱，支持Cookie导入与多用户操作

## 功能

|组件                |版本           |描述                          |
|--------------------|---------------|------------------------------|
|login               |2018/6/20      |登录                          |
|importCookie        |2018/6/20      |导入Cookie                    |
|query               |2018/6/20      |获取用户信息                  |
|silver2Coins        |2018/6/20      |银瓜子兑换硬币                |
|watch               |2018/6/20      |观看视频                      |
|reward              |2018/6/20      |投币                          |
|share               |2018/6/20      |分享视频                      |
|favour              |2018/6/20      |收藏视频                      |
|mallAssist          |2018/6/22      |会员购周年庆活动助力          |
|mallLuckyDraw       |2018/6/22      |会员购周年庆活动抽奖          |

## 使用指南

1. 下载（克隆）本代码仓库，并修改bilibili.py文件中的配置区（详见代码注释）

```
$ git clone https://github.com/Hsury/Bilibili-Toolkit.git
$ cd Bilibili-Toolkit
$ nano bilibili.py
```

2. 启动脚本

```
$ python3 bilibili.py
```

## 计划

|待开发的组件   |
|---------------|
|视频点赞       |
|关注用户       |
|修改账号资料   |
|异步执行任务   |
|自动更新代理   |
|图形界面       |
|<未完待续>     |

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

<p align="center">
<img src="https://cdn.kagamiz.com/Bilibili-Toolkit/bilibili.png" width="300">
</p>

<h1 align="center">- Bilibili Toolkit -</h1>

<p align="center">
<img src="https://img.shields.io/badge/version-2019.11.30-green.svg?longCache=true&style=for-the-badge">
<img src="https://img.shields.io/badge/license-SATA-blue.svg?longCache=true&style=for-the-badge">
<img src="https://img.shields.io/travis/com/Hsury/Bilibili-Toolkit?style=for-the-badge">
</p>

<h4 align="center">🛠️ 哔哩哔哩（B站）辅助工具箱，支持Cookie/Token/Password融合持久化登录与多用户操作</h4>

<p align="center">
<img src="https://cdn.kagamiz.com/Bilibili-Toolkit/demo.png" width="750">
</p>

## 功能

|组件                |版本           |描述                          |
|--------------------|---------------|------------------------------|
|login               |2019/9/15      |登录                          |
|get_user_info       |2019/9/15      |获取用户信息                  |
|set_privacy         |2018/7/24      |修改隐私设置                  |
|silver_to_coin      |2018/8/8       |银瓜子兑换硬币                |
|watch               |2018/8/30      |观看                          |
|like                |2018/7/8       |点赞                          |
|reward              |2018/11/22     |投币                          |
|favour              |2018/6/20      |收藏                          |
|combo               |2018/12/18     |三连推荐                      |
|share               |2018/6/20      |分享                          |
|follow              |2018/7/8       |关注                          |
|danmaku_post        |2019/3/11      |弹幕发送                      |
|comment_like        |2018/6/27      |评论点赞                      |
|comment_post        |2019/8/3       |评论发表                      |
|dynamic_like        |2018/6/29      |动态点赞                      |
|dynamic_repost      |2019/3/11      |动态转发                      |
|dynamic_purge       |2019/3/11      |动态清理                      |
|system_notice       |2019/8/3       |系统通知查询                  |
|mall_rush           |2019/9/15      |会员购抢购                    |
|mall_coupon         |2019/3/3       |会员购优惠卷领取              |
|mall_order_list     |2019/9/15      |会员购订单列表查询            |
|mall_coupon_list    |2019/8/4       |会员购优惠卷列表查询          |
|mall_prize_list     |2019/8/3       |会员购奖品列表查询            |
|live_prize_list     |2019/8/3       |直播奖品列表查询              |

## 使用指南

### 源代码版本（推荐）

1. 克隆或[下载](https://github.com/Hsury/Bilibili-Toolkit/archive/master.zip)本代码仓库，并修改默认配置文件config.toml

```
git clone https://github.com/Hsury/Bilibili-Toolkit.git
cd Bilibili-Toolkit
nano config.toml
```

2. 安装Python 3.6/3.7，并使用pip安装依赖

```
pip install -r requirements.txt -U -i https://pypi.tuna.tsinghua.edu.cn/simple
```

3. 启动脚本

```
python bilibili.py
```

### 二进制版本

从[Release页面](https://github.com/Hsury/Bilibili-Toolkit/releases)下载并解压与您的平台适配的压缩包，修改默认配置文件config.toml后运行可执行文件bilibili即可

*若要加载非默认配置文件，将其路径作为命令行参数传入即可*

### docker版本

1. 安装好[Docker](https://yeasy.gitbooks.io/docker_practice/content/install/)
2. 下载 [config.toml](https://raw.githubusercontent.com/Hsury/Bilibili-Toolkit/master/config.toml) **必须**
3. 如果需要代理，需要下载 [proxy.txt](https://raw.githubusercontent.com/Hsury/Bilibili-Toolkit/master/proxy.txt) **非必须**
5. 在本地修改好文件。
6. docker镜像启动时，把文件挂载到容器即可。

---

#### Linux

```
docker run --rm -it \
  -v $(pwd)/config.toml:/app/config.toml \
  -v $(pwd)/proxy.txt:/app/proxy.txt zsnmwy/bilibili-toolkit
```

```shell script
# 如果你没有配置代理。请自行移除 

-v $(pwd)/proxy.txt:/app/proxy.txt

# 即不做该文件的映射
```

`$(pwd)` 获取当前目录路径。

#### Windows

假设下载的文件都在`D:\python`。

```
下面命令需要在powershell上面执行。

docker run --rm -it `
  -v D:\python\config.toml:/app/config.toml `
  -v D:\python\proxy.txt:/app/proxy.txt `
  zsnmwy/bilibili-toolkit

如果你没有配置代理。请自行移除

-v D:\python\proxy.txt:/app/proxy.txt
```
---

下面的指令都是docker本身的指令，适用于`Windows`以及`Linux`。

`--rm` 退出的时候，会把容器删除。

`-i` 让容器的标准输入保持打开。

`-t` 让Docker分配一个伪终端（pseudo-tty）并绑定到容器的标准输入上。

`-d `让容器后台运行。如果你想后台，加个在`-it`后面加个`d`就行。

`-v` 可以把本机的(目录/文件)挂载到容器里面，起到加入/替换的作用。如果你使用的是项目的默认值，则不用-v来指定文件替换。但是配置文件（`config.toml`）是一定要的，不然程序找不到用户的。

---

如果有什么奇葩问题，或者需要更新镜像，使用`docker pull zsnmwy/bilibili-toolkit`进行更新（保证不更新）。

### 已知问题

在`-it`交互模式下，在容器运行着的python直接用`Ctrl+C`无法正常退出容器。

需要使用`docker rm -f`强制结束。

```
$docker ps
CONTAINER ID        IMAGE                        COMMAND                  CREATED             STATUS              PORTS               NAMES
a746fb0325fb        zsnmwy/bilibili-toolkit      "/bin/sh -c 'git pul…"   44 seconds ago      Up 42 seconds                           frosty_mccarthy

$docker rm -f a7
a7
```

## 图形验证码识别API

使用CNN卷积神经网络构建，已实现对**登录、评论**验证码的自适应识别

```
requests.post("https://bili.dev:2233/captcha", json={'image': base64.b64encode(image).decode("utf-8")})
```

## 交流

QQ群：[956399361](https://jq.qq.com/?_wv=1027&k=5BO0c7o)

## 捐赠

作者在本项目的开发过程中投入了大量的时间与精力，且验证码识别服务器的运行也需要一定的成本

若本项目帮助到了您，为您带来了直接或间接的收益，不要吝啬请我喝几杯~~妹汁~~喔 (=・ω・=)

<p align="center">
<img src="https://cdn.kagamiz.com/Bilibili-Toolkit/donate_alipay.png" width="250">
<img src="https://cdn.kagamiz.com/Bilibili-Toolkit/donate_wechat.png" width="250">
<img src="https://cdn.kagamiz.com/Bilibili-Toolkit/donate_alipay_redpacket.png" width="250">
</p>

## 鸣谢

本项目的灵感与使用到的部分API来自以下项目：

> [czp3009/bilibili-api](https://github.com/czp3009/bilibili-api)

## 许可证

Bilibili Toolkit is under The Star And Thank Author License (SATA)

本项目基于MIT协议发布，并增加了SATA协议

您有义务为此开源项目点赞，并考虑额外给予作者适当的奖励 ∠( ᐛ 」∠)＿

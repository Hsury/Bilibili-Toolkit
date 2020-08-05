FROM python:3.6-alpine

LABEL zsnmwy <szlszl35622@gmail.com>

ENV LIBRARY_PATH=/lib:/usr/lib

WORKDIR /app

RUN apk add --no-cache --virtual bili git build-base python-dev py-pip jpeg-dev zlib-dev && \
    git clone https://github.com/Hsury/Bilibili-Toolkit.git /app && \
    pip install --no-cache-dir -r requirements.txt && \
    rm -r /var/cache/apk && \
    rm -r /usr/share/man && \
    apk del bili && \
    apk add --no-cache libjpeg-turbo git tzdata && \
    ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && \
    echo "Asia/Shanghai" > /etc/timezone

# DEV
#RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.ustc.edu.cn/g' /etc/apk/repositories && \
#    apk add --no-cache --virtual bili git build-base python-dev py-pip jpeg-dev zlib-dev && \
#    git clone https://github.com/Hsury/Bilibili-Toolkit.git /app && \
#    pip install --no-cache-dir -r requirements.txt -U -i https://pypi.tuna.tsinghua.edu.cn/simple && \
#    rm -r /var/cache/apk && \
#    rm -r /usr/share/man && \
#    apk del bili && \
#    apk add --no-cache libjpeg-turbo git tzdata && \
#    ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && \
#    echo "Asia/Shanghai" > /etc/timezone

CMD git pull && \
    pip install --no-cache-dir -r requirements.txt -U -i https://pypi.tuna.tsinghua.edu.cn/simple && \
    python ./bilibili.py

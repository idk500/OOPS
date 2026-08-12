# build/win-build/Dockerfile —— 在 CNB(Linux) 上构建 Windows exe 的交叉编译环境
#
# 原理:用 Wine64 运行 Windows 版 Python 3.11 + PyInstaller,在 Linux 容器中产出 Windows .exe。
# 该镜像由 CNB 流水线 `docker.build` 指令构建并缓存,仅在 Dockerfile/requirements.txt 变更时重建。
#
# 使用方式:在 .cnb.yml 的 tag_push 事件中通过 docker.build 引用本文件。

FROM ubuntu:22.04

# 安装 Wine64 及必要工具(仅需 64 位 Wine 构建 64 位 exe)
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        wine64 \
        xvfb \
        wget \
        ca-certificates \
        zip \
        unzip \
        curl \
        git \
        && rm -rf /var/lib/apt/lists/*

# Wine 环境变量
ENV WINEPREFIX=/root/.wine
ENV WINEDEBUG=-all
ENV WINEARCH=win64
ENV PYTHON_VERSION=3.11.9

# 下载并静默安装 Windows 版 Python 3.11 (64位)
RUN wget -q "https://www.python.org/ftp/python/${PYTHON_VERSION}/python-${PYTHON_VERSION}-amd64.exe" \
        -O /tmp/python-installer.exe && \
    xvfb-run -a wine64 /tmp/python-installer.exe \
        /quiet \
        InstallAllUsers=1 \
        PrependPath=1 \
        Include_test=0 \
        Include_launcher=0 \
        Include_doc=0 \
        Include_tcltk=1 \
        Include_pip=1 \
        && rm -f /tmp/python-installer.exe

# Windows Python 路径(在 Wine 的 C: 盘 = /root/.wine/drive_c)
ENV WINPY="C:\\Python311\\python.exe"

# 升级 Windows pip 并安装 PyInstaller
RUN xvfb-run -a wine64 "${WINPY}" -m pip install --no-cache-dir --upgrade pip && \
    xvfb-run -a wine64 "${WINPY}" -m pip install --no-cache-dir pyinstaller

# 安装项目运行时依赖(Windows 版)
COPY requirements.txt /tmp/requirements.txt
RUN xvfb-run -a wine64 "${WINPY}" -m pip install --no-cache-dir -r /tmp/requirements.txt

# 默认工作目录
WORKDIR /workspace

# 默认命令
CMD ["/bin/bash"]

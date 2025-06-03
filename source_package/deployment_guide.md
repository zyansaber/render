# PowerBI 门户应用部署指南

## 目录
1. [项目概述](#项目概述)
2. [系统要求](#系统要求)
3. [部署步骤](#部署步骤)
   - [本地开发环境部署](#本地开发环境部署)
   - [生产环境部署](#生产环境部署)
4. [数据库配置](#数据库配置)
5. [自定义域名设置](#自定义域名设置)
6. [安全建议](#安全建议)
7. [常见问题](#常见问题)
8. [维护指南](#维护指南)

## 项目概述

PowerBI 门户应用是一个基于 Flask 的 Web 应用，用于管理和展示 PowerBI 报表。主要功能包括：

- 用户认证和权限管理
- PowerBI 报表页面管理
- 基于用户权限的动态导航菜单
- 管理员界面，用于管理页面、用户和权限

## 系统要求

### 最低配置
- Python 3.8 或更高版本
- 2GB RAM
- 10GB 存储空间
- 互联网连接

### 推荐配置
- Python 3.11 或更高版本
- 4GB RAM
- 20GB SSD 存储
- 稳定的互联网连接

### 支持的操作系统
- Ubuntu 20.04 LTS 或更高版本
- CentOS 8 或更高版本
- Windows Server 2019 或更高版本
- macOS 11 或更高版本

## 部署步骤

### 本地开发环境部署

以下步骤适用于本地测试和开发环境。

#### 1. 准备环境

首先，确保您已安装 Python 和 pip：

```bash
# 检查 Python 版本
python --version

# 如果没有安装 Python，请安装（Ubuntu 示例）
sudo apt update
sudo apt install python3 python3-pip
```

#### 2. 解压源代码

将提供的源代码包解压到您选择的目录：

```bash
unzip powerbi_portal_source.zip -d /path/to/destination
cd /path/to/destination
```

#### 3. 创建虚拟环境

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# 在 Linux/macOS 上：
source venv/bin/activate
# 在 Windows 上：
venv\Scripts\activate
```

#### 4. 安装依赖

```bash
pip install -r requirements.txt
```

#### 5. 初始化数据库

```bash
# 确保您在项目根目录下
python -c "from src.main import app; app.app_context().push(); from src.models import db; db.create_all()"
```

#### 6. 运行应用

```bash
# 运行开发服务器
python src/main.py
```

现在，您可以通过浏览器访问 http://localhost:5000 来访问应用。

默认管理员账户：
- 用户名：`zhihaiyan`
- 密码：`abc`

### 生产环境部署

以下步骤适用于生产环境部署。

#### 选项 1：使用 Gunicorn 和 Nginx（推荐，适用于 Linux）

##### 1. 安装 Gunicorn 和 Nginx

```bash
# 安装 Gunicorn
pip install gunicorn

# 安装 Nginx（Ubuntu 示例）
sudo apt update
sudo apt install nginx
```

##### 2. 配置 Gunicorn

创建一个 Gunicorn 服务文件：

```bash
sudo nano /etc/systemd/system/powerbi_portal.service
```

添加以下内容（请根据您的实际路径进行修改）：

```ini
[Unit]
Description=PowerBI Portal Gunicorn Service
After=network.target

[Service]
User=your_username
Group=your_group
WorkingDirectory=/path/to/powerbi_portal
Environment="PATH=/path/to/powerbi_portal/venv/bin"
ExecStart=/path/to/powerbi_portal/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:8000 "src.main:app"
Restart=always

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
sudo systemctl start powerbi_portal
sudo systemctl enable powerbi_portal
```

##### 3. 配置 Nginx

创建一个 Nginx 配置文件：

```bash
sudo nano /etc/nginx/sites-available/powerbi_portal
```

添加以下内容：

```nginx
server {
    listen 80;
    server_name your_domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

创建符号链接并重启 Nginx：

```bash
sudo ln -s /etc/nginx/sites-available/powerbi_portal /etc/nginx/sites-enabled
sudo nginx -t  # 测试配置
sudo systemctl restart nginx
```

#### 选项 2：使用 Docker（适用于所有平台）

##### 1. 安装 Docker

请参考 [Docker 官方文档](https://docs.docker.com/get-docker/) 安装 Docker。

##### 2. 创建 Dockerfile

在项目根目录创建一个名为 `Dockerfile` 的文件：

```bash
nano Dockerfile
```

添加以下内容：

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV FLASK_APP=src/main.py
ENV FLASK_ENV=production

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "src.main:app"]
```

##### 3. 构建和运行 Docker 镜像

```bash
# 构建 Docker 镜像
docker build -t powerbi-portal .

# 运行 Docker 容器
docker run -d -p 80:5000 --name powerbi-portal powerbi-portal
```

现在，您可以通过浏览器访问 http://localhost 来访问应用。

#### 选项 3：使用云服务提供商

##### 阿里云 ECS

1. 创建一个 ECS 实例（推荐 Ubuntu 20.04）
2. 连接到实例并按照上述 Gunicorn 和 Nginx 的步骤进行部署
3. 配置安全组，开放 80 和 443 端口

##### AWS EC2

1. 创建一个 EC2 实例（推荐 Amazon Linux 2 或 Ubuntu）
2. 连接到实例并按照上述 Gunicorn 和 Nginx 的步骤进行部署
3. 配置安全组，开放 80 和 443 端口

##### 腾讯云 CVM

1. 创建一个 CVM 实例（推荐 Ubuntu 20.04）
2. 连接到实例并按照上述 Gunicorn 和 Nginx 的步骤进行部署
3. 配置安全组，开放 80 和 443 端口

## 数据库配置

### SQLite（默认，适用于小型部署）

默认情况下，应用使用 SQLite 数据库，存储在 `/data/powerbi_portal.db`。您可以在 `src/main.py` 文件中修改数据库路径：

```python
db_path = os.path.join('/data', 'powerbi_portal.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_path}"
```

### MySQL（推荐用于生产环境）

对于生产环境，建议使用 MySQL 数据库：

1. 安装 MySQL：

```bash
# Ubuntu 示例
sudo apt update
sudo apt install mysql-server
```

2. 创建数据库和用户：

```sql
CREATE DATABASE powerbi_portal;
CREATE USER 'powerbi_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON powerbi_portal.* TO 'powerbi_user'@'localhost';
FLUSH PRIVILEGES;
```

3. 安装 MySQL 客户端库：

```bash
pip install pymysql
```

4. 修改 `src/main.py` 中的数据库配置：

```python
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://powerbi_user:your_password@localhost/powerbi_portal"
```

## 自定义域名设置

### 1. 购买域名

您可以通过阿里云、腾讯云、GoDaddy 等服务商购买域名。

### 2. 配置 DNS 记录

在您的域名管理面板中，添加一条 A 记录，将您的域名指向您的服务器 IP 地址：

- 记录类型：A
- 主机记录：@ 或 www
- 记录值：您的服务器 IP 地址
- TTL：600（或默认值）

### 3. 配置 HTTPS（推荐）

使用 Let's Encrypt 获取免费的 SSL 证书：

```bash
# 安装 Certbot
sudo apt update
sudo apt install certbot python3-certbot-nginx

# 获取证书并自动配置 Nginx
sudo certbot --nginx -d your_domain.com -d www.your_domain.com
```

## 安全建议

1. **更改默认密码**：首次登录后立即更改默认管理员密码
2. **启用 HTTPS**：使用 SSL 证书加密所有通信
3. **定期备份数据库**：设置自动备份计划
4. **更新依赖**：定期更新应用依赖以修复安全漏洞
5. **限制访问**：使用防火墙限制服务器访问
6. **设置强密码策略**：要求用户使用强密码
7. **监控日志**：定期检查应用和服务器日志

## 常见问题

### 问题：应用无法启动

**解决方案**：
- 检查 Python 版本是否兼容
- 确保所有依赖都已正确安装
- 检查日志文件中的错误信息

### 问题：无法连接到数据库

**解决方案**：
- 确保数据库服务正在运行
- 检查数据库连接字符串是否正确
- 验证数据库用户权限

### 问题：页面加载缓慢

**解决方案**：
- 优化数据库查询
- 考虑使用更强大的服务器
- 检查网络连接

### 问题：PowerBI 报表无法显示

**解决方案**：
- 确保 PowerBI 嵌入 URL 是正确的
- 检查 PowerBI 服务是否可访问
- 验证用户是否有权限查看报表

## 维护指南

### 日常维护

1. **监控服务器资源**：定期检查 CPU、内存和磁盘使用情况
2. **备份数据库**：每日或每周备份数据库
3. **检查日志**：定期检查应用和服务器日志，查找潜在问题

### 更新应用

1. 备份当前应用和数据库
2. 拉取最新代码或解压新版本
3. 安装新的依赖
4. 执行数据库迁移（如果需要）
5. 重启应用服务

### 扩展应用

如果您需要添加新功能或修改现有功能，请参考以下文件结构：

```
powerbi_portal/
├── src/                    # 源代码目录
│   ├── main.py             # 应用入口点
│   ├── models/             # 数据库模型
│   │   ├── __init__.py     # 数据库初始化
│   │   ├── user.py         # 用户模型
│   │   ├── page.py         # 页面模型
│   │   └── permission.py   # 权限模型
│   ├── routes/             # 路由控制器
│   │   ├── __init__.py     # 路由初始化
│   │   ├── auth.py         # 认证相关路由
│   │   ├── main.py         # 主页面路由
│   │   ├── admin.py        # 管理界面路由
│   │   └── context.py      # 上下文处理
│   ├── static/             # 静态资源
│   │   ├── css/            # CSS 样式
│   │   └── js/             # JavaScript 脚本
│   └── templates/          # HTML 模板
│       ├── base.html       # 基础模板
│       ├── auth/           # 认证相关模板
│       ├── main/           # 主页面模板
│       └── admin/          # 管理界面模板
├── requirements.txt        # Python 依赖列表
└── README.md               # 项目说明
```

---

如果您在部署过程中遇到任何问题，请参考上述常见问题部分或联系技术支持。祝您使用愉快！

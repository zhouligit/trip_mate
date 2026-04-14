本地启动（Mac）
1) 准备依赖
在项目根目录 trip_mate：

python3 -m pip install --upgrade pip
pip install poetry
poetry install
2) 准备 MySQL / Redis
你本地要有：

MySQL 8（库名：trip_mate）
Redis 6/7
创建数据库示例：

mysql -uroot -p -e "CREATE DATABASE IF NOT EXISTS trip_mate DEFAULT CHARACTER SET utf8mb4;"
3) 环境变量
cp .env.example .env
按你本地实际账号改 .env 里的 MYSQL_DSN、REDIS_URL、JWT_SECRET。

4) 建表
poetry run alembic upgrade head
5) 启动 API
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
访问：

Swagger: http://127.0.0.1:8000/docs
健康检查: http://127.0.0.1:8000/api/v1/health
Ubuntu 服务器部署（单机 MVP）
建议目录：/opt/trip_mate

1) 安装系统依赖
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3-pip nginx git
sudo pip3 install poetry
2) 拉代码并安装
sudo mkdir -p /opt/trip_mate && sudo chown -R $USER:$USER /opt/trip_mate
cd /opt/trip_mate
git clone <你的gredis://...
JWT_SECRET=强随机密钥
4) 执行迁移
cd /opt/trip_mate
poetry run alembic upgrade head
5) systemd 启动 FastAPI
创建 /etc/systemd/system/tripmate-api.service：

[Unit]
Description=TripMate FastAPI
After=network.target
[Service]
User=ubuntu
WorkingDirectory=/opt/trip_mate
Environment="PATH=/opt/trip_mate/.venv/bin"
ExecStart=/opt/trip_mate/.venv/bin/gunicorn app.main:app -k uvicorn.workers.UvicornWorker -w 2 -b 127.0.0.1:8000
Restart=always
RestartSec=5
[Install]
WantedBy=multi-user.target
启动：

sudo systemctl daemon-reload
sudo systemctl enable --now tripmate-api
sudo systemctl status tripmate-api
6) Nginx 反代
创建 /etc/nginx/sites-available/tripmate.conf：

server {
    listen 80;
    server_name your_domain_or_ip;
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
启用：

sudo ln -s /etc/nginx/sites-avdo nginx -t
sudo systemctl reload nginx
7) 防火墙（Ubuntu）
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable
sudo ufw status
生产最少注意点
不要对外暴露 MySQL/Redis 端口，只开放给内网/localhost。
JWT_SECRET 必须换成强随机值。
先用 HTTP 跑通，再加 HTTPS（建议 certbot）。
每次发版流程：git pull -> poetry install -> alembic upgrade head -> systemctl restart tripmate-api。
如果你要，我下一条可以直接给你一套“可复制执行的部署脚本版”（包含 systemd + nginx 完整命令），你只改域名和仓库地址即可。

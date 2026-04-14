# TripMate Ubuntu One-Click Deploy

## 1. Copy code to server
- `git clone <your-repo-url>`

## 2. Run one-click script as root
```bash
cd trip_mate
chmod +x scripts/deploy_ubuntu.sh
sudo APP_USER=ubuntu \
  REPO_URL=https://github.com/<yourname>/<repo>.git \
  BRANCH=main \
  DOMAIN=<your-domain-or-_> \
  MYSQL_PASS='<strong-password>' \
  JWT_SECRET='<long-random-secret>' \
  bash scripts/deploy_ubuntu.sh
```

## 3. Verify
- `curl http://127.0.0.1/api/v1/health`
- `curl http://<server-ip>/api/v1/health`
- Open `http://<server-ip>/docs`

## Notes
- Keep MySQL/Redis bound to localhost only.
- Open only ports 22/80/443 in cloud security group.
- For HTTPS, install certbot and configure SSL in nginx.

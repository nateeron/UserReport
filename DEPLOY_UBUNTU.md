# Deploy UserReport on Ubuntu

## 1. Prepare the server

```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv
```

## 2. Upload your project

Copy the project folder to the server (e.g. `/var/www/UserReport` or `~/UserReport`):

```bash
# From your PC (example with scp):
scp -r /path/to/UserReport user@your-server-ip:/var/www/
```

Or clone from git if you use a repository.

## 3. Create virtualenv and install dependencies

```bash
cd /var/www/UserReport   # or your path
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn   # for production
```

## 4. Run with Gunicorn (recommended for production)

```bash
source venv/bin/activate
gunicorn -w 2 -b 0.0.0.0:5000 app:app
```

- `-w 2`: 2 worker processes  
- `-b 0.0.0.0:5000`: bind to all interfaces, port 5000  
- `app:app`: module `app`, variable `app`

To run in background:

```bash
nohup gunicorn -w 2 -b 0.0.0.0:5000 app:app --access-logfile - --error-logfile - &
```

## 5. Run as a systemd service (starts on boot)

Create a service file:

```bash
sudo nano /etc/systemd/system/userreport.service
```

Paste (adjust paths if needed):

```ini
[Unit]
Description=UserReport Flask App
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/UserReport
Environment="PATH=/var/www/UserReport/venv/bin"
ExecStart=/var/www/UserReport/venv/bin/gunicorn -w 2 -b 127.0.0.1:5000 app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

Then:

```bash
sudo systemctl daemon-reload
sudo systemctl enable userreport
sudo systemctl start userreport
sudo systemctl status userreport
```

Use `127.0.0.1:5000` if you put Nginx in front (see below).

## 6. Optional: Nginx as reverse proxy

Install Nginx:

```bash
sudo apt install -y nginx
```

Create a site config:

```bash
sudo nano /etc/nginx/sites-available/userreport
```

Example (replace `your-domain.com` or use `_` for default server):

```nginx
server {
    listen 80;
    server_name your-domain.com;   # or your server IP
    client_max_body_size 50M;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable and restart:

```bash
sudo ln -s /etc/nginx/sites-available/userreport /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## 7. Firewall (if enabled)

```bash
sudo ufw allow 80/tcp
sudo ufw allow 5000/tcp   # only if not using Nginx
sudo ufw enable
```

## 8. Folders and permissions

Ensure the app can write to `image/` and `reports/` and can read `data.json`:

```bash
cd /var/www/UserReport
mkdir -p image reports
chown -R www-data:www-data /var/www/UserReport
```

## Quick test (no Gunicorn)

```bash
cd /var/www/UserReport
source venv/bin/activate
python3 app.py
```

Then open `http://your-server-ip:5000` in a browser.

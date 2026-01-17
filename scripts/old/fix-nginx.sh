#!/bin/bash
# Script para configurar Nginx en puerto 80

echo "🔧 Configurando Nginx..."

# Detener Nginx
systemctl stop nginx 2>/dev/null

# Backup
cp /etc/nginx/nginx.conf /etc/nginx/nginx.conf.bak 2>/dev/null

# Crear configuración
cat > /etc/nginx/nginx.conf << 'NGINXCONF'
user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log;
pid /run/nginx.pid;
include /usr/share/nginx/modules/*.conf;

events {
    worker_connections 1024;
}

http {
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent"';
    access_log /var/log/nginx/access.log main;
    sendfile on;
    tcp_nopush on;
    keepalive_timeout 65;
    types_hash_max_size 4096;
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    server {
        listen 80 default_server;
        listen [::]:80 default_server;
        server_name _;

        location / {
            proxy_pass http://127.0.0.1:3000;
            proxy_http_version 1.1;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        }
    }

    server {
        listen 8447;
        server_name _;
        root /var/www/html;
        index index.html;
        location / {
            try_files $uri $uri/ =404;
        }
    }
}
NGINXCONF

# Test y arrancar
nginx -t && systemctl start nginx && systemctl enable nginx

echo ""
echo "✅ Nginx configurado"
systemctl status nginx --no-pager | head -3
echo ""
curl -s http://127.0.0.1 | grep -o "ASO RankGuard" | head -1
echo ""
echo "🌐 Accede a: http://194.164.160.111"

#!/bin/bash

echo "🔧 Configurando puerto 80 para Next.js..."

# Detener Nginx de Plesk temporalmente
systemctl stop nginx

# Crear configuración simple de Nginx
cat > /etc/nginx/sites-available/aso-rankguard << 'EOF'
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
EOF

# Habilitar sitio
mkdir -p /etc/nginx/sites-enabled
ln -sf /etc/nginx/sites-available/aso-rankguard /etc/nginx/sites-enabled/

# Iniciar Nginx
systemctl start nginx

echo "✅ Nginx configurado en puerto 80"
echo "🌐 Accede sin puerto: http://194.164.160.111"

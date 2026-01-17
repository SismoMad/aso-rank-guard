#!/bin/bash
# Auto-configuración completa del servidor tras reinstalación

set -e

echo "🚀 Configurando servidor ASO Rank Guard..."

# 1. Actualizar sistema
echo "📦 Actualizando sistema..."
dnf update -y

# 2. Instalar Node.js 20
echo "📥 Instalando Node.js 20..."
curl -fsSL https://rpm.nodesource.com/setup_20.x | bash -
dnf install -y nodejs

# 3. Instalar PM2
echo "📥 Instalando PM2..."
npm install -g pm2

# 4. Crear estructura de directorios
echo "📁 Creando directorios..."
mkdir -p /root/aso-rank-guard/web-app

# 5. Configurar firewall del servidor
echo "🔥 Configurando firewall..."
firewall-cmd --permanent --add-port=22/tcp
firewall-cmd --permanent --add-port=80/tcp
firewall-cmd --permanent --add-port=443/tcp
firewall-cmd --permanent --add-port=3000/tcp
firewall-cmd --permanent --add-port=8443/tcp
firewall-cmd --reload

# 6. Configurar nginx como proxy
echo "🌐 Configurando nginx..."
cat > /etc/nginx/conf.d/nextjs.conf << 'EOF'
server {
    listen 80 default_server;
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

systemctl enable nginx
systemctl restart nginx

# 7. Configurar PM2 para autoarranque
pm2 startup systemd -u root --hp /root
pm2 save

echo ""
echo "✅ Servidor configurado!"
echo "📁 Directorio: /root/aso-rank-guard/web-app"
echo "🌐 URL: http://194.164.160.111/"
echo ""
echo "Ahora ejecuta el deploy desde tu Mac:"
echo "  cd /Users/javi/aso-rank-guard && ./deploy-quick.sh"

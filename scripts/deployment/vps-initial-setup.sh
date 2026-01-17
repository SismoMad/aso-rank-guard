#!/bin/bash

# =============================================================================
# Setup Inicial del Servidor VPS
# Ejecuta este script DENTRO del servidor la primera vez
# =============================================================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   ASO Rank Guard - VPS Initial Setup                    ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""

# Verificar que se ejecuta como root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}Este script debe ejecutarse como root${NC}"
    echo "Ejecuta: sudo $0"
    exit 1
fi

# 1. Actualizar sistema
echo -e "${YELLOW}➤ Actualizando sistema...${NC}"
dnf update -y
echo -e "${GREEN}✓ Sistema actualizado${NC}\n"

# 2. Instalar herramientas básicas
echo -e "${YELLOW}➤ Instalando herramientas básicas...${NC}"
dnf install -y git curl wget vim htop
echo -e "${GREEN}✓ Herramientas instaladas${NC}\n"

# 3. Instalar Node.js 20
echo -e "${YELLOW}➤ Instalando Node.js 20 LTS...${NC}"
curl -fsSL https://rpm.nodesource.com/setup_20.x | bash -
dnf install -y nodejs

# Verificar versión
NODE_VERSION=$(node --version)
echo -e "${GREEN}✓ Node.js instalado: ${NODE_VERSION}${NC}\n"

# 4. Instalar PM2
echo -e "${YELLOW}➤ Instalando PM2...${NC}"
npm install -g pm2
pm2 startup systemd
echo -e "${GREEN}✓ PM2 instalado${NC}\n"

# 5. Instalar Python 3.11
echo -e "${YELLOW}➤ Instalando Python 3.11...${NC}"
dnf install -y python3.11 python3.11-pip python3.11-devel

# Configurar Python 3.11 como default
alternatives --set python3 /usr/bin/python3.11

# Actualizar pip
python3 -m pip install --upgrade pip

# Verificar versión
PYTHON_VERSION=$(python3 --version)
echo -e "${GREEN}✓ Python instalado: ${PYTHON_VERSION}${NC}\n"

# 6. Instalar Nginx (si no está con Plesk)
echo -e "${YELLOW}➤ Verificando Nginx...${NC}"
if command -v nginx &> /dev/null; then
    NGINX_VERSION=$(nginx -v 2>&1 | awk '{print $3}')
    echo -e "${GREEN}✓ Nginx ya instalado: ${NGINX_VERSION}${NC}\n"
else
    dnf install -y nginx
    systemctl enable nginx
    systemctl start nginx
    echo -e "${GREEN}✓ Nginx instalado y habilitado${NC}\n"
fi

# 7. Configurar Firewall
echo -e "${YELLOW}➤ Configurando firewall...${NC}"
firewall-cmd --permanent --add-service=http
firewall-cmd --permanent --add-service=https
firewall-cmd --permanent --add-port=3000/tcp
firewall-cmd --permanent --add-port=8000/tcp
firewall-cmd --reload
echo -e "${GREEN}✓ Firewall configurado${NC}\n"

# 8. Crear directorio de trabajo
echo -e "${YELLOW}➤ Creando directorio de trabajo...${NC}"
mkdir -p /var/www/aso-rank-guard
mkdir -p /var/www/aso-rank-guard/logs
chown -R root:root /var/www/aso-rank-guard
echo -e "${GREEN}✓ Directorio creado: /var/www/aso-rank-guard${NC}\n"

# 9. Instalar certbot (para SSL)
echo -e "${YELLOW}➤ Instalando Certbot (Let's Encrypt)...${NC}"
dnf install -y certbot python3-certbot-nginx
echo -e "${GREEN}✓ Certbot instalado${NC}\n"

# 10. Configurar Nginx Reverse Proxy
echo -e "${YELLOW}➤ Configurando Nginx Reverse Proxy...${NC}"
cat > /etc/nginx/conf.d/aso-rank-guard.conf << 'EOF'
# ASO Rank Guard - Nginx Configuration

upstream aso_api {
    server 127.0.0.1:8000;
    keepalive 32;
}

upstream aso_web {
    server 127.0.0.1:3000;
    keepalive 32;
}

server {
    listen 80;
    server_name 194.164.160.111;

    access_log /var/log/nginx/aso-rank-guard-access.log;
    error_log /var/log/nginx/aso-rank-guard-error.log;

    client_max_body_size 10M;
    proxy_connect_timeout 60s;
    proxy_send_timeout 60s;
    proxy_read_timeout 60s;

    # API Backend
    location /api/ {
        proxy_pass http://aso_api/api/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }

    location /health {
        proxy_pass http://aso_api/health;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
    }

    location /docs {
        proxy_pass http://aso_api/docs;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
    }

    # Frontend Next.js
    location / {
        proxy_pass http://aso_web;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }

    location /_next/static {
        proxy_pass http://aso_web/_next/static;
        proxy_cache_valid 200 60m;
        add_header Cache-Control "public, immutable";
    }
}
EOF

# Verificar configuración Nginx
nginx -t

# Reload Nginx
systemctl reload nginx
echo -e "${GREEN}✓ Nginx configurado correctamente${NC}\n"

# 11. Resumen
echo -e "${GREEN}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   ✅ SETUP INICIAL COMPLETADO                           ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "📦 Software instalado:"
echo -e "   - Node.js:  ${NODE_VERSION}"
echo -e "   - Python:   ${PYTHON_VERSION}"
echo -e "   - PM2:      $(pm2 --version)"
echo -e "   - Nginx:    Configurado"
echo ""
echo -e "🔧 Próximos pasos:"
echo -e "   1. Salir del servidor: ${YELLOW}exit${NC}"
echo -e "   2. Desde tu Mac, ejecutar: ${YELLOW}./deploy-to-vps.sh${NC}"
echo -e "   3. Verificar despliegue: ${YELLOW}http://194.164.160.111${NC}"
echo ""
echo -e "📖 Documentación: ${YELLOW}DEPLOY_VPS_GUIA.md${NC}"
echo ""

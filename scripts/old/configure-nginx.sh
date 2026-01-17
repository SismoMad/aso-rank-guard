#!/bin/bash

# Configurar Nginx como proxy reverso para Next.js
echo "🔧 Configurando Nginx para redirigir a Next.js..."

# Crear configuración de Nginx
cat > /etc/nginx/conf.d/aso-rankguard.conf << 'EOL'
server {
    listen 80 default_server;
    listen [::]:80 default_server;
    server_name _;

    # Logs
    access_log /var/log/nginx/aso-rankguard-access.log;
    error_log /var/log/nginx/aso-rankguard-error.log;

    # Proxy a Next.js
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
}
EOL

# Deshabilitar configuración default de Plesk si existe
mv /etc/nginx/conf.d/default.conf /etc/nginx/conf.d/default.conf.bak 2>/dev/null || true

# Verificar configuración
nginx -t

# Reiniciar Nginx
systemctl restart nginx

echo ""
echo "✅ Nginx configurado correctamente!"
echo ""
echo "🌐 Ahora accede a:"
echo "   http://194.164.160.111"
echo ""
echo "   (Sin necesidad de poner :3000)"

#!/bin/bash

# Script para desplegar Next.js en el servidor
# Ejecutar: ssh root@194.164.160.111 'bash -s' < deploy-server.sh

echo "🚀 Desplegando ASO RankGuard en servidor..."

# 1. Instalar Node.js si no está instalado
if ! command -v node &> /dev/null; then
    echo "📦 Instalando Node.js..."
    curl -fsSL https://rpm.nodesource.com/setup_20.x | bash -
    dnf install -y nodejs
fi

echo "✅ Node.js version: $(node -v)"
echo "✅ npm version: $(npm -v)"

# 2. Crear directorio para la app
mkdir -p /var/www/aso-rankguard
cd /var/www/aso-rankguard

# 3. Extraer build
echo "📦 Extrayendo build..."
tar -xzf /root/nextjs-build.tar.gz

# 4. Instalar dependencias de producción
echo "📦 Instalando dependencias..."
npm install --production

# 5. Crear archivo .env para producción
echo "📝 Configurando variables de entorno..."
cat > .env.local << 'EOL'
NEXT_PUBLIC_SUPABASE_URL=https://bidqxydrybpuwyskrarh.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJpZHF4eWRyeWJwdXd5c2tyYXJoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzcwNTQ1OTksImV4cCI6MjA1MjYzMDU5OX0.SnJvVF7nz8k1OI-1UY-FMUvUJD_qW8gZNEbpP_4Xy6Q
NEXT_PUBLIC_API_URL=http://194.164.160.111:8000
EOL

# 6. Crear servicio systemd para que se ejecute automáticamente
echo "⚙️ Creando servicio systemd..."
cat > /etc/systemd/system/aso-rankguard.service << 'EOL'
[Unit]
Description=ASO RankGuard Next.js App
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/var/www/aso-rankguard
Environment="NODE_ENV=production"
Environment="PORT=3000"
ExecStart=/usr/bin/npm start
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOL

# 7. Recargar systemd y arrancar servicio
echo "🔄 Iniciando servicio..."
systemctl daemon-reload
systemctl enable aso-rankguard
systemctl restart aso-rankguard

# 8. Verificar estado
sleep 3
systemctl status aso-rankguard --no-pager

# 9. Configurar firewall para puerto 3000
echo "🔥 Configurando firewall..."
firewall-cmd --permanent --add-port=3000/tcp 2>/dev/null || true
firewall-cmd --reload 2>/dev/null || true

echo ""
echo "✅ ¡DESPLIEGUE COMPLETADO!"
echo ""
echo "🌐 Tu app está corriendo en:"
echo "   http://194.164.160.111:3000"
echo ""
echo "📊 Ver logs: journalctl -u aso-rankguard -f"
echo "🔄 Reiniciar: systemctl restart aso-rankguard"
echo "⛔ Detener: systemctl stop aso-rankguard"

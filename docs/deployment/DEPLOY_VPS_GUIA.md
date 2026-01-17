# 🚀 Guía de Despliegue en VPS (IONOS)

## 📋 Resumen del Servidor

**Datos del VPS:**
- **Host:** 194.164.160.111
- **Usuario:** root
- **SO:** Alma Linux 9 + Plesk
- **CPU:** 2 vCores
- **RAM:** 2 GB
- **Disco:** 80 GB NVMe SSD
- **Firewall:** Configurado

---

## 🏗️ Arquitectura del Despliegue

```
┌─────────────────────────────────────────────┐
│          VPS (194.164.160.111)              │
├─────────────────────────────────────────────┤
│                                             │
│  ┌────────────────┐  ┌──────────────────┐  │
│  │   Next.js      │  │   FastAPI        │  │
│  │   (puerto 3000)│  │   (puerto 8000)  │  │
│  └────────────────┘  └──────────────────┘  │
│           │                    │            │
│  ┌────────────────────────────────────┐    │
│  │         Nginx Reverse Proxy        │    │
│  │            (puerto 80/443)         │    │
│  └────────────────────────────────────┘    │
│                    │                        │
└────────────────────┼────────────────────────┘
                     │
              ┌──────▼──────┐
              │  Supabase   │
              │  (Cloud DB) │
              └─────────────┘
```

**Componentes:**
1. **Frontend Next.js** → Puerto 3000 (SSR + Client)
2. **Backend FastAPI** → Puerto 8000 (API REST)
3. **Nginx** → Puerto 80/443 (Reverse Proxy)
4. **Supabase** → Base de datos (Cloud)
5. **PM2** → Process Manager (mantiene apps corriendo)
6. **Cron Jobs** → Tracking automático de rankings

---

## 🔧 Paso 1: Preparar el Servidor

### 1.1 Conectar por SSH

```bash
ssh root@194.164.160.111
# Contraseña: rCYRQdS6
```

### 1.2 Actualizar sistema

```bash
# Actualizar paquetes
dnf update -y

# Instalar herramientas esenciales
dnf install -y git curl wget vim htop
```

### 1.3 Instalar Node.js (para Next.js)

```bash
# Instalar Node.js 20 LTS
curl -fsSL https://rpm.nodesource.com/setup_20.x | bash -
dnf install -y nodejs

# Verificar instalación
node --version  # Debe mostrar v20.x
npm --version   # Debe mostrar 10.x

# Instalar PM2 (process manager)
npm install -g pm2
```

### 1.4 Instalar Python 3.11 (para FastAPI)

```bash
# Python 3.9 viene por defecto en Alma 9, pero queremos 3.11+
dnf install -y python3.11 python3.11-pip python3.11-devel

# Crear alias
alternatives --set python3 /usr/bin/python3.11

# Verificar versión
python3 --version  # Debe mostrar Python 3.11.x

# Actualizar pip
python3 -m pip install --upgrade pip
```

### 1.5 Configurar Firewall (permitir puertos)

```bash
# Abrir puertos HTTP/HTTPS
firewall-cmd --permanent --add-service=http
firewall-cmd --permanent --add-service=https

# Abrir puertos para desarrollo (temporal)
firewall-cmd --permanent --add-port=3000/tcp  # Next.js
firewall-cmd --permanent --add-port=8000/tcp  # FastAPI

# Recargar firewall
firewall-cmd --reload

# Verificar puertos abiertos
firewall-cmd --list-all
```

---

## 📦 Paso 2: Clonar el Proyecto

### 2.1 Crear directorio de trabajo

```bash
# Crear directorio para aplicaciones
mkdir -p /var/www/aso-rank-guard
cd /var/www/aso-rank-guard
```

### 2.2 Clonar repositorio (o subir archivos)

**Opción A: Si tienes Git repo configurado**
```bash
git clone https://github.com/TU_USUARIO/aso-rank-guard.git .
```

**Opción B: Subir manualmente con rsync** (desde tu Mac)
```bash
# Ejecutar desde tu Mac (no en el servidor)
rsync -avz --exclude 'node_modules' \
           --exclude '.next' \
           --exclude '__pycache__' \
           --exclude 'data/' \
           --exclude '.env.local' \
           /Users/javi/aso-rank-guard/ \
           root@194.164.160.111:/var/www/aso-rank-guard/

# Esto copiará todo excepto carpetas pesadas
```

**Opción C: Usar script de despliegue automático** (recomendado)
```bash
# Ver el script deploy-to-vps.sh que crearemos más adelante
```

---

## 🔐 Paso 3: Configurar Variables de Entorno

### 3.1 Backend API (FastAPI)

```bash
cd /var/www/aso-rank-guard

# Crear archivo .env para el backend
cat > .env << 'EOF'
# Supabase Configuration
SUPABASE_URL=https://bidqxydrybpuwyskrarh.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJpZHF4eWRyeWJwdXd5c2tyYXJoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njg2NjE3MjYsImV4cCI6MjA4NDIzNzcyNn0.jpMJgqjErP3u7XlzulGg7sMmBEH1Q8SbkVTFcXreaXE
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJpZHF4eWRyeWJwdXd5c2tyYXJoIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2ODY2MTcyNiwiZXhwIjoyMDg0MjM3NzI2fQ.LzvaXJDvE7nipsmnl-maaKcUzZkeRbnuccgw08gwOB8

# Telegram Bot
TELEGRAM_BOT_TOKEN=8531462519:AAFvX5PPyB177DUzylwgC8LMIUztrWPYfbI

# Admin Configuration
ADMIN_EMAIL=gutierrezjavier1989@gmail.com

# API Settings
ITUNES_API_DELAY=1.5
ITUNES_API_MAX_RETRIES=3
TEST_MODE=false
LOG_LEVEL=INFO
LOG_FILE=/var/www/aso-rank-guard/logs/rank_guard.log
EOF

# Permisos seguros
chmod 600 .env
```

### 3.2 Frontend Next.js

```bash
cd /var/www/aso-rank-guard/web-app

# Crear .env.production
cat > .env.production << 'EOF'
# Supabase
NEXT_PUBLIC_SUPABASE_URL=https://bidqxydrybpuwyskrarh.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJpZHF4eWRyeWJwdXd5c2tyYXJoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njg2NjE3MjYsImV4cCI6MjA4NDIzNzcyNn0.jpMJgqjErP3u7XlzulGg7sMmBEH1Q8SbkVTFcXreaXE

# Backend API
NEXT_PUBLIC_API_URL=http://194.164.160.111:8000

# App
NEXT_PUBLIC_APP_NAME=ASO Rank Guard
NEXT_PUBLIC_APP_URL=http://194.164.160.111
EOF

# Permisos seguros
chmod 600 .env.production
```

---

## 📦 Paso 4: Instalar Dependencias

### 4.1 Backend (Python)

```bash
cd /var/www/aso-rank-guard

# Crear entorno virtual
python3 -m venv venv

# Activar entorno
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Verificar instalación
python -c "import fastapi; import supabase; print('✅ Backend OK')"

# Desactivar entorno (por ahora)
deactivate
```

### 4.2 Frontend (Next.js)

```bash
cd /var/www/aso-rank-guard/web-app

# Instalar dependencias
npm install

# Build de producción
npm run build

# Verificar que se creó .next/
ls -la .next/
```

---

## 🚀 Paso 5: Configurar PM2 (Process Manager)

### 5.1 Configurar PM2 para Backend y Frontend

```bash
cd /var/www/aso-rank-guard

# Crear archivo de configuración PM2
cat > ecosystem.config.js << 'EOF'
module.exports = {
  apps: [
    {
      // Backend FastAPI
      name: 'aso-api',
      cwd: '/var/www/aso-rank-guard',
      script: '/var/www/aso-rank-guard/venv/bin/uvicorn',
      args: 'api.main:app --host 0.0.0.0 --port 8000',
      env: {
        PYTHONPATH: '/var/www/aso-rank-guard',
      },
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '500M',
      error_file: '/var/www/aso-rank-guard/logs/api-error.log',
      out_file: '/var/www/aso-rank-guard/logs/api-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
    },
    {
      // Frontend Next.js
      name: 'aso-web',
      cwd: '/var/www/aso-rank-guard/web-app',
      script: 'npm',
      args: 'start',
      env: {
        NODE_ENV: 'production',
        PORT: 3000,
      },
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '500M',
      error_file: '/var/www/aso-rank-guard/logs/web-error.log',
      out_file: '/var/www/aso-rank-guard/logs/web-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
    },
  ],
};
EOF
```

### 5.2 Iniciar aplicaciones con PM2

```bash
# Crear directorio de logs si no existe
mkdir -p /var/www/aso-rank-guard/logs

# Iniciar aplicaciones
pm2 start ecosystem.config.js

# Verificar estado
pm2 status

# Ver logs en tiempo real
pm2 logs

# Guardar configuración para auto-inicio
pm2 save
pm2 startup systemd
# Ejecutar el comando que te muestre PM2
```

### 5.3 Comandos útiles PM2

```bash
# Ver estado
pm2 status

# Ver logs
pm2 logs aso-api       # Solo API
pm2 logs aso-web       # Solo Web
pm2 logs --lines 100   # Últimas 100 líneas

# Reiniciar aplicaciones
pm2 restart aso-api
pm2 restart aso-web
pm2 restart all

# Detener aplicaciones
pm2 stop aso-api
pm2 stop aso-web

# Monitoreo en tiempo real
pm2 monit
```

---

## 🌐 Paso 6: Configurar Nginx

### 6.1 Instalar Nginx (si no está con Plesk)

```bash
# Verificar si Nginx está instalado
nginx -v

# Si no está, instalar
dnf install -y nginx

# Habilitar e iniciar
systemctl enable nginx
systemctl start nginx
```

### 6.2 Configurar Reverse Proxy

```bash
# Crear configuración para ASO Rank Guard
cat > /etc/nginx/conf.d/aso-rank-guard.conf << 'EOF'
# ASO Rank Guard - Configuración Nginx

# Upstream para Backend API
upstream aso_api {
    server 127.0.0.1:8000;
    keepalive 32;
}

# Upstream para Frontend Next.js
upstream aso_web {
    server 127.0.0.1:3000;
    keepalive 32;
}

# Servidor principal
server {
    listen 80;
    server_name 194.164.160.111;

    # Logs
    access_log /var/log/nginx/aso-rank-guard-access.log;
    error_log /var/log/nginx/aso-rank-guard-error.log;

    # Aumentar límites
    client_max_body_size 10M;
    client_body_timeout 60s;
    proxy_connect_timeout 60s;
    proxy_send_timeout 60s;
    proxy_read_timeout 60s;

    # API Backend (FastAPI)
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

    # Health check endpoint
    location /health {
        proxy_pass http://aso_api/health;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
    }

    # Frontend Next.js (todas las demás rutas)
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

    # Archivos estáticos Next.js
    location /_next/static {
        proxy_pass http://aso_web/_next/static;
        proxy_cache_valid 200 60m;
        add_header Cache-Control "public, immutable";
    }
}
EOF

# Verificar configuración
nginx -t

# Si todo OK, recargar Nginx
systemctl reload nginx
```

### 6.3 Verificar que funciona

```bash
# Probar endpoints
curl http://localhost/health
curl http://localhost/api/stats
curl http://localhost/

# Desde tu Mac
curl http://194.164.160.111/health
```

---

## ⏰ Paso 7: Configurar Cron Jobs (Tracking Automático)

### 7.1 Crear script de tracking

```bash
cd /var/www/aso-rank-guard

# Crear script wrapper para cron
cat > run-tracking.sh << 'EOF'
#!/bin/bash

# Activar entorno virtual
cd /var/www/aso-rank-guard
source venv/bin/activate

# Ejecutar tracking
python src/rank_tracker_supabase.py >> logs/cron-tracking.log 2>&1

# Desactivar entorno
deactivate
EOF

# Dar permisos de ejecución
chmod +x run-tracking.sh
```

### 7.2 Configurar crontab

```bash
# Editar crontab
crontab -e

# Añadir estas líneas (tracking cada día a las 9:00 AM)
0 9 * * * /var/www/aso-rank-guard/run-tracking.sh

# Opcional: Tracking cada 6 horas
#0 */6 * * * /var/www/aso-rank-guard/run-tracking.sh

# Guardar y salir
```

### 7.3 Verificar cron

```bash
# Ver trabajos programados
crontab -l

# Ver logs de cron
tail -f /var/www/aso-rank-guard/logs/cron-tracking.log
```

---

## 🔒 Paso 8: SSL/HTTPS (Opcional pero Recomendado)

### 8.1 Instalar Certbot (Let's Encrypt)

```bash
# Instalar certbot
dnf install -y certbot python3-certbot-nginx

# Obtener certificado SSL
certbot --nginx -d 194.164.160.111

# Seguir instrucciones (email, aceptar términos)
```

### 8.2 Auto-renovación SSL

```bash
# Certbot crea automáticamente un cron job
# Verificar con:
systemctl status certbot-renew.timer

# Probar renovación manual
certbot renew --dry-run
```

---

## 📊 Paso 9: Monitoreo y Mantenimiento

### 9.1 Ver logs en tiempo real

```bash
# Logs de PM2
pm2 logs

# Logs de Nginx
tail -f /var/log/nginx/aso-rank-guard-access.log
tail -f /var/log/nginx/aso-rank-guard-error.log

# Logs de tracking
tail -f /var/www/aso-rank-guard/logs/rank_guard.log
```

### 9.2 Monitorear recursos

```bash
# CPU y RAM en tiempo real
htop

# Espacio en disco
df -h

# Procesos PM2
pm2 monit
```

### 9.3 Backup automático

```bash
# Crear script de backup
cat > /var/www/aso-rank-guard/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/var/backups/aso-rank-guard"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup de datos
tar -czf $BACKUP_DIR/data_$DATE.tar.gz /var/www/aso-rank-guard/data/

# Backup de logs
tar -czf $BACKUP_DIR/logs_$DATE.tar.gz /var/www/aso-rank-guard/logs/

# Mantener solo últimos 7 días
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

echo "✅ Backup completado: $DATE"
EOF

chmod +x /var/www/aso-rank-guard/backup.sh

# Añadir a crontab (diario a las 2 AM)
crontab -e
# Añadir:
# 0 2 * * * /var/www/aso-rank-guard/backup.sh >> /var/www/aso-rank-guard/logs/backup.log 2>&1
```

---

## 🧪 Paso 10: Testing de Producción

### 10.1 Test de conectividad

```bash
# Desde el servidor
curl http://localhost/health
curl http://localhost/api/stats

# Desde tu Mac
curl http://194.164.160.111/health
curl http://194.164.160.111/api/stats
```

### 10.2 Test de autenticación Supabase

```bash
# Crear usuario de prueba en Supabase Dashboard
# Luego probar login en la web:
# http://194.164.160.111/login
```

### 10.3 Test de tracking manual

```bash
# Ejecutar tracking manualmente
cd /var/www/aso-rank-guard
source venv/bin/activate
python src/rank_tracker_supabase.py
deactivate

# Verificar que se guardaron datos en Supabase
```

---

## 🚨 Troubleshooting

### Problema: PM2 no inicia aplicaciones

```bash
# Ver logs detallados
pm2 logs --err

# Reiniciar PM2
pm2 delete all
pm2 start ecosystem.config.js

# Verificar permisos
ls -la /var/www/aso-rank-guard/
chown -R root:root /var/www/aso-rank-guard/
```

### Problema: Nginx retorna 502 Bad Gateway

```bash
# Verificar que PM2 esté corriendo
pm2 status

# Verificar puertos
netstat -tlnp | grep -E '3000|8000'

# Reiniciar Nginx
systemctl restart nginx
```

### Problema: Next.js no encuentra variables de entorno

```bash
# Verificar .env.production
cat /var/www/aso-rank-guard/web-app/.env.production

# Rebuild Next.js
cd /var/www/aso-rank-guard/web-app
npm run build
pm2 restart aso-web
```

### Problema: Python no encuentra módulos

```bash
# Verificar entorno virtual
cd /var/www/aso-rank-guard
source venv/bin/activate
pip list

# Reinstalar dependencias
pip install -r requirements.txt --force-reinstall
```

---

## 📝 Checklist de Despliegue

- [ ] Servidor actualizado (dnf update)
- [ ] Node.js 20+ instalado
- [ ] Python 3.11+ instalado
- [ ] PM2 instalado globalmente
- [ ] Nginx configurado y corriendo
- [ ] Firewall abierto (puertos 80, 443, 3000, 8000)
- [ ] Proyecto clonado en /var/www/aso-rank-guard
- [ ] Variables de entorno configuradas (.env, .env.production)
- [ ] Dependencias Python instaladas (venv)
- [ ] Dependencias Next.js instaladas (npm install)
- [ ] Next.js buildeado (npm run build)
- [ ] PM2 iniciado y guardado (pm2 save)
- [ ] Nginx reverse proxy configurado
- [ ] Cron jobs configurados
- [ ] SSL/HTTPS configurado (opcional)
- [ ] Backup automático configurado
- [ ] Tests de producción pasados ✅

---

## 🎉 URLs Finales

Una vez completado el despliegue:

- **Web App:** http://194.164.160.111
- **API:** http://194.164.160.111/api
- **Health Check:** http://194.164.160.111/health
- **API Docs:** http://194.164.160.111/api/docs (FastAPI auto-docs)

---

## 📞 Contacto y Soporte

Si tienes problemas durante el despliegue:

1. Revisa logs: `pm2 logs`, `/var/log/nginx/error.log`
2. Verifica estado: `pm2 status`, `systemctl status nginx`
3. Consulta esta guía paso a paso

**¡Buena suerte con el despliegue! 🚀**

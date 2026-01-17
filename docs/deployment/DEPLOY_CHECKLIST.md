# ✅ Checklist de Despliegue - ASO Rank Guard VPS

## 🎯 Pre-requisitos

- [ ] Tienes acceso SSH al servidor (194.164.160.111)
- [ ] Contraseña root guardada de forma segura
- [ ] Tu Mac tiene rsync instalado (`brew install rsync`)
- [ ] Git configurado (opcional, para versionado)

---

## 📦 Fase 1: Preparación del Servidor

### Conectar al servidor
```bash
ssh root@194.164.160.111
# Contraseña: rCYRQdS6
```

### Copiar script de setup inicial
```bash
# Opción A: Copiar/pegar contenido del archivo vps-initial-setup.sh
cat > setup.sh
# Pegar contenido
# Ctrl+D para guardar

# Opción B: Usar rsync para subir el archivo
# (desde tu Mac)
scp vps-initial-setup.sh root@194.164.160.111:~/setup.sh
```

### Ejecutar setup
```bash
# En el servidor
chmod +x setup.sh
./setup.sh
```

**Checklist de verificación:**
- [ ] Node.js 20+ instalado (`node --version`)
- [ ] Python 3.11+ instalado (`python3 --version`)
- [ ] PM2 instalado (`pm2 --version`)
- [ ] Nginx corriendo (`systemctl status nginx`)
- [ ] Firewall configurado (puertos 80, 443, 3000, 8000)
- [ ] Directorio /var/www/aso-rank-guard creado

---

## 🚀 Fase 2: Despliegue de la Aplicación

### Desde tu Mac
```bash
cd /Users/javi/aso-rank-guard
./deploy-to-vps.sh
```

**Checklist de verificación:**
- [ ] Archivos sincronizados correctamente
- [ ] .env creado en servidor
- [ ] .env.production creado en web-app
- [ ] Dependencias Python instaladas (venv)
- [ ] Dependencias Node.js instaladas (node_modules)
- [ ] Next.js buildeado (.next/)
- [ ] PM2 iniciado (aso-api y aso-web)
- [ ] `pm2 status` muestra ambas apps "online"

### Verificar endpoints
```bash
# Desde tu Mac
curl http://194.164.160.111/health
# Debe responder: {"status": "healthy", ...}

curl http://194.164.160.111/api/stats
# Debe responder con JSON de estadísticas

curl http://194.164.160.111/
# Debe responder con HTML de Next.js
```

**Checklist de verificación:**
- [ ] Health check funciona (http://194.164.160.111/health)
- [ ] API responde (http://194.164.160.111/api/stats)
- [ ] Web carga (http://194.164.160.111)
- [ ] API Docs accesible (http://194.164.160.111/docs)

---

## 🔐 Fase 3: Seguridad y Optimización

### 3.1 Configurar SSH con clave pública (recomendado)

```bash
# En tu Mac, generar clave SSH si no tienes
ssh-keygen -t ed25519 -C "gutierrezjavier1989@gmail.com"

# Copiar clave pública al servidor
ssh-copy-id root@194.164.160.111

# Probar conexión sin contraseña
ssh root@194.164.160.111
# No debería pedir contraseña
```

**Checklist de verificación:**
- [ ] Clave SSH generada
- [ ] Clave copiada al servidor
- [ ] Puedes conectar sin contraseña

### 3.2 Deshabilitar login con contraseña (opcional, muy recomendado)

```bash
# En el servidor
ssh root@194.164.160.111

# Editar configuración SSH
vim /etc/ssh/sshd_config

# Cambiar estas líneas:
# PasswordAuthentication no
# PermitRootLogin prohibit-password

# Reiniciar SSH
systemctl restart sshd
```

**Checklist de verificación:**
- [ ] PasswordAuthentication no
- [ ] PermitRootLogin prohibit-password
- [ ] SSH reiniciado
- [ ] Puedes conectar con clave SSH

### 3.3 Configurar SSL/HTTPS con Let's Encrypt

```bash
# En el servidor
ssh root@194.164.160.111

# Obtener certificado SSL
certbot --nginx -d 194.164.160.111

# Seguir instrucciones:
# - Ingresar email
# - Aceptar términos
# - Elegir redirección HTTP -> HTTPS
```

**Checklist de verificación:**
- [ ] Certificado SSL obtenido
- [ ] Nginx configurado para HTTPS
- [ ] http:// redirige a https://
- [ ] Renovación automática configurada

### 3.4 Actualizar URLs en .env.production

```bash
# En el servidor, después de SSL
ssh root@194.164.160.111

# Editar .env.production
vim /var/www/aso-rank-guard/web-app/.env.production

# Cambiar:
# NEXT_PUBLIC_API_URL=https://194.164.160.111
# NEXT_PUBLIC_APP_URL=https://194.164.160.111

# Rebuild y reiniciar
cd /var/www/aso-rank-guard/web-app
npm run build
pm2 restart all
```

**Checklist de verificación:**
- [ ] URLs actualizadas a https://
- [ ] Next.js rebuildeado
- [ ] PM2 reiniciado
- [ ] Web funciona con HTTPS

---

## ⏰ Fase 4: Automatización

### 4.1 Configurar tracking automático

```bash
# En el servidor
ssh root@194.164.160.111

# Crear script wrapper
cat > /var/www/aso-rank-guard/run-tracking.sh << 'EOF'
#!/bin/bash
cd /var/www/aso-rank-guard
source venv/bin/activate
python src/rank_tracker_supabase.py >> logs/cron-tracking.log 2>&1
deactivate
EOF

chmod +x /var/www/aso-rank-guard/run-tracking.sh

# Configurar cron
crontab -e

# Añadir (tracking diario a las 9 AM):
0 9 * * * /var/www/aso-rank-guard/run-tracking.sh

# Guardar y salir
```

**Checklist de verificación:**
- [ ] Script run-tracking.sh creado
- [ ] Script tiene permisos de ejecución
- [ ] Cron job configurado
- [ ] Puedes ejecutar manualmente: `./run-tracking.sh`

### 4.2 Configurar backups automáticos

```bash
# En el servidor
ssh root@194.164.160.111

# Crear directorio de backups
mkdir -p /var/backups/aso-rank-guard

# Crear script de backup
cat > /var/www/aso-rank-guard/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/var/backups/aso-rank-guard"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup de datos
tar -czf $BACKUP_DIR/data_$DATE.tar.gz /var/www/aso-rank-guard/data/ 2>/dev/null || true

# Backup de logs
tar -czf $BACKUP_DIR/logs_$DATE.tar.gz /var/www/aso-rank-guard/logs/ 2>/dev/null || true

# Backup de configuración
tar -czf $BACKUP_DIR/config_$DATE.tar.gz \
    /var/www/aso-rank-guard/.env \
    /var/www/aso-rank-guard/web-app/.env.production \
    /var/www/aso-rank-guard/ecosystem.config.js \
    /etc/nginx/conf.d/aso-rank-guard.conf

# Mantener solo últimos 7 días
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

echo "✅ Backup completado: $DATE"
EOF

chmod +x /var/www/aso-rank-guard/backup.sh

# Configurar cron (diario a las 2 AM)
crontab -e

# Añadir:
0 2 * * * /var/www/aso-rank-guard/backup.sh >> /var/www/aso-rank-guard/logs/backup.log 2>&1
```

**Checklist de verificación:**
- [ ] Directorio /var/backups/aso-rank-guard creado
- [ ] Script backup.sh creado y ejecutable
- [ ] Cron job de backup configurado
- [ ] Backup manual ejecutado correctamente

---

## 📊 Fase 5: Monitoreo

### 5.1 Configurar PM2 para auto-inicio

```bash
# En el servidor
ssh root@194.164.160.111

# Guardar configuración actual de PM2
pm2 save

# Configurar auto-inicio en boot
pm2 startup systemd

# Ejecutar el comando que te muestre PM2
# (algo como: systemctl enable pm2-root)
```

**Checklist de verificación:**
- [ ] `pm2 save` ejecutado
- [ ] `pm2 startup` configurado
- [ ] Comando systemctl ejecutado
- [ ] Reiniciar servidor y verificar que PM2 arranca: `reboot`

### 5.2 Configurar monitoreo con monitor-vps.sh

```bash
# Desde tu Mac
./monitor-vps.sh

# Deberías ver:
# - Estado de PM2
# - Recursos del sistema (CPU, RAM, Disco)
# - Últimos logs
# - Health checks
```

**Checklist de verificación:**
- [ ] Script monitor-vps.sh funciona
- [ ] PM2 muestra apps "online"
- [ ] CPU < 50%
- [ ] RAM < 80%
- [ ] Disco < 70%
- [ ] Health checks OK

---

## 🎨 Fase 6: Configuración Final de la App

### 6.1 Crear usuario administrador en Supabase

```bash
# Ir a Supabase Dashboard: https://supabase.com
# Authentication -> Users -> Add User

# Crear con:
# Email: gutierrezjavier1989@gmail.com
# Password: [elegir contraseña segura]
```

**Checklist de verificación:**
- [ ] Usuario administrador creado en Supabase
- [ ] Puedes hacer login en http://194.164.160.111/login
- [ ] Dashboard carga correctamente
- [ ] Puedes ver datos de rankings

### 6.2 Importar datos iniciales (si tienes)

```bash
# Si tienes datos en CSV locales
# Ejecutar script de migración

# Desde tu Mac
scp data/ranks.csv root@194.164.160.111:/var/www/aso-rank-guard/data/

# En el servidor
ssh root@194.164.160.111
cd /var/www/aso-rank-guard
source venv/bin/activate
python scripts/migrate_csv_to_supabase.py
deactivate
```

**Checklist de verificación:**
- [ ] Datos CSV subidos al servidor
- [ ] Script de migración ejecutado
- [ ] Datos visibles en Supabase Dashboard
- [ ] Datos visibles en tu web app

---

## ✅ Verificación Final

### URLs funcionando
- [ ] https://194.164.160.111 (Web App)
- [ ] https://194.164.160.111/api/stats (API)
- [ ] https://194.164.160.111/health (Health Check)
- [ ] https://194.164.160.111/docs (API Docs)

### Funcionalidades
- [ ] Puedes hacer login
- [ ] Dashboard muestra datos
- [ ] API responde correctamente
- [ ] Tracking manual funciona
- [ ] Cron ejecuta tracking automáticamente
- [ ] Backups se crean diariamente

### Seguridad
- [ ] SSL/HTTPS configurado
- [ ] Firewall activo
- [ ] SSH con clave pública
- [ ] Variables de entorno seguras (chmod 600)

### Monitoreo
- [ ] PM2 auto-arranca en boot
- [ ] Logs se guardan correctamente
- [ ] `monitor-vps.sh` funciona
- [ ] Health checks pasan

---

## 🎉 ¡Despliegue Completado!

Si todos los checkboxes están marcados, ¡tu aplicación está en producción! 🚀

### Próximos pasos recomendados:

1. **Dominio personalizado** (opcional)
   - Comprar dominio (ej: asorankguard.com)
   - Apuntar DNS a 194.164.160.111
   - Reconfigurar SSL para el dominio

2. **Monitoreo avanzado** (opcional)
   - Uptime Robot: https://uptimerobot.com (gratis)
   - Sentry para error tracking
   - Google Analytics

3. **Optimización** (opcional)
   - CDN para assets estáticos
   - Redis para caché
   - Base de datos PostgreSQL local (migrar de Supabase)

---

## 📞 Soporte

Si algo falla, revisa:
- Logs: `./monitor-vps.sh` o `ssh root@194.164.160.111 'pm2 logs'`
- Guía completa: [DEPLOY_VPS_GUIA.md](DEPLOY_VPS_GUIA.md)
- Quick Start: [DEPLOY_QUICK_START.md](DEPLOY_QUICK_START.md)

**¡Felicitaciones por tu despliegue! 🎊**

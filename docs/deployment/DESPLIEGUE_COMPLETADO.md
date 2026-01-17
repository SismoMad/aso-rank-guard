# ✅ Despliegue en VPS IONOS - Completado

**Servidor:** 194.164.160.111  
**Fecha:** 17 de enero de 2026  
**Estado:** ✅ Aplicaciones funcionando, requiere configuración de firewall

---

## 🎉 Estado Actual

### ✅ Backend API (FastAPI)
- **Puerto:** 8000
- **Proceso:** PM2 (online, 90MB RAM)
- **Estado:** ✅ Funcionando correctamente
- **Health Check:** `http://localhost:8000/health` → `{"status":"healthy"}`
- **Acceso local:** ✅ Funciona
- **Acceso externo:** ❌ Bloqueado por firewall IONOS

### ✅ Frontend (Next.js)
- **Puerto:** 3000
- **Proceso:** PM2 (online, 56MB RAM)
- **Estado:** ✅ Funcionando correctamente
- **Build:** Completado (optimizado para producción)
- **Acceso local:** ✅ Funciona
- **Acceso externo:** ❌ Bloqueado por firewall IONOS

### ✅ Puerto 80 (Plesk)
- **Estado:** ✅ Accesible desde internet
- **Contenido:** Página de redirección a puerto 3000
- **URL:** http://194.164.160.111/

---

## 🔥 ACCIÓN REQUERIDA: Configurar Firewall de IONOS

El firewall del VPS en IONOS está bloqueando los puertos 3000 y 8000.

### Pasos para abrir puertos:

1. **Acceder al panel de IONOS:**
   - URL: https://my.ionos.com/
   - Login con tus credenciales

2. **Ir a tu VPS:**
   - Menú: Servidores & Cloud → Servidores
   - Seleccionar: VPS 194.164.160.111

3. **Configurar Firewall:**
   - Opción: Firewall / Seguridad
   - Añadir las siguientes reglas:

   ```
   Regla 1: Permitir puerto 3000/TCP (Frontend Next.js)
   Regla 2: Permitir puerto 8000/TCP (Backend FastAPI)
   ```

4. **Verificar:**
   ```bash
   curl http://194.164.160.111:3000/  # Debería mostrar Next.js
   curl http://194.164.160.111:8000/health  # Debería mostrar {"status":"healthy"}
   ```

---

## 📊 Verificación del Estado

### Desde tu Mac (local):

```bash
# Verificar API (actualmente timeout)
curl http://194.164.160.111:8000/health

# Verificar Frontend (actualmente timeout)
curl http://194.164.160.111:3000/

# Página de redirección (funciona)
curl http://194.164.160.111/
```

### Desde el servidor (SSH):

```bash
ssh root@194.164.160.111

# Ver estado de PM2
pm2 status

# Ver logs de API
pm2 logs aso-api --lines 20

# Ver logs de Frontend
pm2 logs aso-web --lines 20

# Verificar puertos locales
curl http://localhost:8000/health  # ✅ Funciona
curl http://localhost:3000/        # ✅ Funciona
```

---

## 🔧 Configuración Actual del Servidor

### PM2 (Process Manager)
```bash
┌────┬────────────┬──────────┬──────────┐
│ id │ name       │ status   │ memory   │
├────┼────────────┼──────────┼──────────┤
│ 2  │ aso-api    │ online   │ 90.0mb   │
│ 1  │ aso-web    │ online   │ 56.3mb   │
└────┴────────────┴──────────┴──────────┘
```

### Ubicaciones de archivos:
- **Proyecto:** `/var/www/aso-rank-guard/`
- **Frontend:** `/var/www/aso-rank-guard/web-app/`
- **Backend:** `/var/www/aso-rank-guard/api/`
- **Logs:** `/var/www/aso-rank-guard/logs/`
- **PM2 Config:** `/var/www/aso-rank-guard/ecosystem.config.js`

### Variables de entorno:
- **Backend:** `/var/www/aso-rank-guard/.env`
- **Frontend:** `/var/www/aso-rank-guard/web-app/.env.production`

### Python Virtual Environment:
- **Ubicación:** `/var/www/aso-rank-guard/venv/`
- **Python:** 3.11.13
- **Dependencias:** FastAPI, Uvicorn, Supabase, python-dotenv, etc.

---

## 🚀 Comandos Útiles

### Gestión de PM2:

```bash
# Ver estado
pm2 status

# Reiniciar aplicaciones
pm2 restart aso-api
pm2 restart aso-web
pm2 restart all

# Ver logs en tiempo real
pm2 logs
pm2 logs aso-api
pm2 logs aso-web

# Detener aplicaciones
pm2 stop all

# Iniciar aplicaciones
pm2 start ecosystem.config.js

# Guardar configuración PM2
pm2 save

# Configurar PM2 para inicio automático
pm2 startup
```

### Actualizar código:

```bash
# Desde tu Mac, sincronizar cambios
rsync -avz --exclude 'node_modules' --exclude '.next' --exclude 'venv' \
  /Users/javi/aso-rank-guard/ root@194.164.160.111:/var/www/aso-rank-guard/

# En el servidor, después de sincronizar
ssh root@194.164.160.111

# Actualizar dependencias de Python si es necesario
cd /var/www/aso-rank-guard
source venv/bin/activate
pip install -r api/requirements.txt

# Rebuild de Next.js si hay cambios en frontend
cd /var/www/aso-rank-guard/web-app
npm run build

# Reiniciar aplicaciones
pm2 restart all
```

---

## 🔐 Próximos Pasos Recomendados

### 1. Configurar Dominio (Opcional)
```bash
# Apuntar tu dominio a 194.164.160.111
# Ejemplo: aso-rank-guard.com → 194.164.160.111

# Luego configurar en Plesk:
plesk bin domain --create aso-rank-guard.com -owner admin
```

### 2. Configurar SSL/HTTPS
```bash
# Instalar Certbot
dnf install certbot python3-certbot-nginx -y

# Obtener certificado SSL
certbot --nginx -d tu-dominio.com

# Renovación automática ya configurada
```

### 3. Configurar Cron Jobs para Tracking
```bash
# Editar crontab
crontab -e

# Añadir tracking automático (ejemplo: cada 6 horas)
0 */6 * * * cd /var/www/aso-rank-guard && source venv/bin/activate && python track_and_save.py
```

### 4. Configurar Backups Automáticos
```bash
# Script de backup (ya existe en scripts/backup.sh)
chmod +x /var/www/aso-rank-guard/scripts/backup.sh

# Añadir a crontab (backup diario a las 2 AM)
0 2 * * * /var/www/aso-rank-guard/scripts/backup.sh
```

### 5. Monitoreo y Alertas
```bash
# PM2 Plus para monitoreo (opcional)
pm2 plus

# Configurar alertas de Telegram
# Ya configurado en bot_telegram_supabase.py
```

---

## 📞 Troubleshooting

### La API no responde
```bash
# Ver logs de error
pm2 logs aso-api --err --lines 50

# Reiniciar API
pm2 restart aso-api

# Verificar que está escuchando
ss -tlnp | grep :8000
```

### El Frontend no carga
```bash
# Ver logs
pm2 logs aso-web --lines 50

# Verificar build
cd /var/www/aso-rank-guard/web-app
ls -la .next/

# Rebuild
npm run build
pm2 restart aso-web
```

### Error de base de datos
```bash
# Verificar variables de entorno
cat /var/www/aso-rank-guard/.env | grep SUPABASE

# Probar conexión desde Python
cd /var/www/aso-rank-guard
source venv/bin/activate
python -c "from supabase import create_client; import os; from dotenv import load_dotenv; load_dotenv(); print('OK')"
```

---

## 📝 Notas Importantes

1. **Firewall IONOS**: Es la última barrera que impide el acceso externo. Una vez configurado, todo debería funcionar.

2. **PM2 Auto-restart**: Configurado para reiniciar automáticamente si las apps fallan.

3. **Persistencia**: PM2 está configurado para iniciar automáticamente al reiniciar el servidor.

4. **Logs**: Se guardan en `/var/www/aso-rank-guard/logs/` y también puedes verlos con `pm2 logs`.

5. **Memoria**: El servidor tiene 2GB RAM, actualmente usando ~150MB para ambas apps (suficiente).

---

## ✅ Checklist de Despliegue

- [x] Servidor configurado (Node.js, Python, PM2)
- [x] Código sincronizado
- [x] Variables de entorno configuradas
- [x] Dependencias instaladas (Python y Node.js)
- [x] Next.js build completado
- [x] PM2 configurado y apps en ejecución
- [x] Firewall del servidor configurado (iptables)
- [x] Página de redirección en puerto 80
- [ ] **Firewall IONOS configurado** ← PENDIENTE
- [ ] Dominio configurado (opcional)
- [ ] SSL/HTTPS configurado (opcional)
- [ ] Cron jobs configurados (opcional)

---

**Última actualización:** 17 de enero de 2026, 20:00 UTC  
**Estado:** Aplicaciones funcionando, esperando configuración de firewall IONOS

# 🔧 Comandos Útiles - ASO Rank Guard VPS

## 🚀 Despliegue

```bash
# Deploy completo (primera vez o con cambios en dependencias)
./deploy-to-vps.sh

# Quick deploy (solo código, sin reinstalar dependencias)
./quick-deploy.sh

# Ver estado del servidor
./monitor-vps.sh
```

---

## 🔌 Conexión SSH

```bash
# Conectar al servidor
ssh root@194.164.160.111

# Conectar y ejecutar comando directo
ssh root@194.164.160.111 "pm2 status"

# Copiar archivo al servidor
scp archivo.txt root@194.164.160.111:/var/www/aso-rank-guard/

# Descargar archivo del servidor
scp root@194.164.160.111:/var/www/aso-rank-guard/logs/error.log ./
```

---

## 📦 PM2 (Process Manager)

```bash
# Ver estado de aplicaciones
pm2 status

# Ver logs en tiempo real
pm2 logs

# Ver logs solo de API
pm2 logs aso-api

# Ver logs solo de Web
pm2 logs aso-web

# Ver últimas 100 líneas
pm2 logs --lines 100

# Reiniciar todas las apps
pm2 restart all

# Reiniciar solo API
pm2 restart aso-api

# Reiniciar solo Web
pm2 restart aso-web

# Detener apps
pm2 stop all
pm2 stop aso-api
pm2 stop aso-web

# Eliminar apps de PM2
pm2 delete all
pm2 delete aso-api

# Monitoreo en tiempo real (CPU, RAM)
pm2 monit

# Ver información detallada
pm2 show aso-api
pm2 show aso-web

# Limpiar logs viejos
pm2 flush

# Guardar configuración actual
pm2 save

# Configurar auto-inicio
pm2 startup systemd
```

---

## 🌐 Nginx

```bash
# Ver estado
systemctl status nginx

# Iniciar/Detener/Reiniciar
systemctl start nginx
systemctl stop nginx
systemctl restart nginx

# Recargar configuración (sin detener)
systemctl reload nginx
nginx -s reload

# Verificar configuración
nginx -t

# Ver logs
tail -f /var/log/nginx/aso-rank-guard-access.log
tail -f /var/log/nginx/aso-rank-guard-error.log

# Ver últimas 100 líneas
tail -n 100 /var/log/nginx/aso-rank-guard-error.log
```

---

## 🐍 Python (Backend)

```bash
# Activar entorno virtual
cd /var/www/aso-rank-guard
source venv/bin/activate

# Ejecutar tracking manual
python src/rank_tracker_supabase.py

# Ver paquetes instalados
pip list

# Instalar nuevo paquete
pip install nombre-paquete
pip freeze > requirements.txt

# Desactivar entorno
deactivate

# Recrear entorno virtual desde cero
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## ⚛️ Next.js (Frontend)

```bash
cd /var/www/aso-rank-guard/web-app

# Instalar dependencias
npm install

# Desarrollo local (no usar en producción)
npm run dev

# Build de producción
npm run build

# Iniciar en producción (usa PM2 en vez de esto)
npm start

# Ver espacio que ocupa .next/
du -sh .next/

# Limpiar build anterior
rm -rf .next/
npm run build

# Ver paquetes instalados
npm list --depth=0

# Instalar nuevo paquete
npm install nombre-paquete
```

---

## 📊 Logs y Debugging

```bash
# Ver todos los logs de tracking
tail -f /var/www/aso-rank-guard/logs/rank_guard.log

# Ver logs de cron (tracking automático)
tail -f /var/www/aso-rank-guard/logs/cron-tracking.log

# Ver logs de backup
tail -f /var/www/aso-rank-guard/logs/backup.log

# Ver resumen del último tracking
cat /var/www/aso-rank-guard/logs/last_run_summary.txt

# Buscar errores en logs de PM2
grep -i error /var/www/aso-rank-guard/logs/api-error.log
grep -i error /var/www/aso-rank-guard/logs/web-error.log

# Ver logs del sistema (systemd)
journalctl -u nginx -f
journalctl -u pm2-root -f
```

---

## 🔒 Firewall y Seguridad

```bash
# Ver reglas del firewall
firewall-cmd --list-all

# Abrir puerto
firewall-cmd --permanent --add-port=PUERTO/tcp
firewall-cmd --reload

# Cerrar puerto
firewall-cmd --permanent --remove-port=PUERTO/tcp
firewall-cmd --reload

# Ver puertos abiertos
netstat -tlnp
ss -tlnp

# Ver conexiones activas
netstat -anp | grep :80
netstat -anp | grep :3000
netstat -anp | grep :8000
```

---

## 💾 Base de Datos (Supabase)

```bash
# Desde el backend, ejecutar query SQL
cd /var/www/aso-rank-guard
source venv/bin/activate
python << 'EOF'
from src.supabase_client import get_supabase_client
client = get_supabase_client()

# Ver total de rankings
result = client.table("rankings").select("id", count="exact").execute()
print(f"Total rankings: {result.count}")

# Ver keywords activas
result = client.table("keywords").select("*").eq("is_active", True).execute()
print(f"Keywords activas: {len(result.data)}")
EOF
deactivate
```

---

## 🔄 Backups

```bash
# Ejecutar backup manual
/var/www/aso-rank-guard/backup.sh

# Ver backups existentes
ls -lh /var/backups/aso-rank-guard/

# Restaurar backup de datos
cd /var/www/aso-rank-guard
tar -xzf /var/backups/aso-rank-guard/data_20260117_020000.tar.gz -C /

# Descargar backup a tu Mac
scp root@194.164.160.111:/var/backups/aso-rank-guard/data_20260117_020000.tar.gz ~/Downloads/

# Limpiar backups antiguos (más de 30 días)
find /var/backups/aso-rank-guard -name "*.tar.gz" -mtime +30 -delete
```

---

## ⏰ Cron Jobs

```bash
# Ver cron jobs configurados
crontab -l

# Editar cron jobs
crontab -e

# Ver logs de cron
tail -f /var/log/cron

# Ejemplos de cron jobs:
# Cada día a las 9 AM
# 0 9 * * * comando

# Cada 6 horas
# 0 */6 * * * comando

# Cada lunes a las 8 AM
# 0 8 * * 1 comando
```

---

## 📈 Monitoreo del Sistema

```bash
# CPU y RAM en tiempo real
htop
top

# Espacio en disco
df -h

# Uso de disco por directorio
du -sh /var/www/aso-rank-guard/*

# Memoria disponible
free -h

# Procesos que más consumen
ps aux --sort=-%mem | head -n 10
ps aux --sort=-%cpu | head -n 10

# Temperatura del sistema (si está disponible)
sensors

# Ver uptime
uptime

# Ver usuarios conectados
who
w
```

---

## 🔄 Actualizaciones del Sistema

```bash
# Ver actualizaciones disponibles
dnf check-update

# Actualizar paquetes
dnf update -y

# Actualizar solo seguridad
dnf update --security -y

# Limpiar caché
dnf clean all

# Reiniciar servidor (¡cuidado!)
reboot

# Apagar servidor (¡cuidado!)
shutdown -h now
```

---

## 🔍 Testing y Verificación

```bash
# Test de conectividad
curl http://194.164.160.111/health
curl http://194.164.160.111/api/stats

# Test con headers verbosos
curl -v http://194.164.160.111/

# Test de SSL
curl -I https://194.164.160.111/

# Verificar DNS
dig 194.164.160.111
nslookup 194.164.160.111

# Test de velocidad de conexión
ping 194.164.160.111
traceroute 194.164.160.111

# Verificar puertos abiertos desde fuera
telnet 194.164.160.111 80
telnet 194.164.160.111 443
```

---

## 🧹 Limpieza y Mantenimiento

```bash
# Limpiar logs antiguos de PM2
pm2 flush

# Limpiar logs de Nginx (rotar)
logrotate -f /etc/logrotate.d/nginx

# Limpiar caché de npm
cd /var/www/aso-rank-guard/web-app
npm cache clean --force

# Limpiar caché de pip
pip cache purge

# Eliminar archivos temporales
find /tmp -type f -atime +7 -delete

# Ver archivos grandes
find /var/www/aso-rank-guard -type f -size +100M

# Comprimir logs antiguos
gzip /var/www/aso-rank-guard/logs/*.log
```

---

## 🛡️ SSL/HTTPS (Let's Encrypt)

```bash
# Obtener certificado SSL
certbot --nginx -d 194.164.160.111

# Renovar certificado manualmente
certbot renew

# Renovar forzado (test)
certbot renew --dry-run

# Ver certificados existentes
certbot certificates

# Revocar certificado
certbot revoke --cert-path /etc/letsencrypt/live/194.164.160.111/cert.pem

# Ver timer de renovación automática
systemctl status certbot-renew.timer
systemctl list-timers certbot-renew.timer
```

---

## 🚨 Emergency Commands

```bash
# Matar proceso que no responde
pkill -9 node
pkill -9 python

# Liberar puerto ocupado
fuser -k 3000/tcp
fuser -k 8000/tcp

# Reiniciar todo desde cero
pm2 delete all
pm2 start ecosystem.config.js
systemctl restart nginx

# Restaurar configuración Nginx
cp /etc/nginx/conf.d/aso-rank-guard.conf.backup /etc/nginx/conf.d/aso-rank-guard.conf
nginx -t && systemctl reload nginx

# Ver procesos zombies
ps aux | grep defunct

# Forzar sync de disco (antes de reboot)
sync
```

---

## 📞 Contacto Rápido

```bash
# Ver IP pública
curl ifconfig.me

# Ver hostname
hostname

# Ver info del sistema
uname -a
cat /etc/os-release
```

---

**Tip:** Puedes guardar estos comandos en tu historial de bash:

```bash
# En el servidor
history | grep "pm2 logs"
history | grep "systemctl restart"

# Guardar historial
history > ~/comandos_utiles.txt
```

# 🚀 DEPLOYMENT GUIDE - ASO Rank Guard

**ÚLTIMA ACTUALIZACIÓN**: 16 Enero 2026  
**SERVER**: AlmaLinux 9.7 + Plesk  
**IP**: 194.164.160.111  
**DASHBOARD**: http://194.164.160.111:8447

---

## ⚠️ CONFIGURACIÓN CRÍTICA - NO TOCAR

### 🔐 Credenciales
- **SSH**: root / 43GRAvsq
- **Dashboard**: Sin autenticación (acceso público)

### 🌐 Firewall IONOS (Política: "My firewall policy")
**Puertos abiertos**: 22, 80, 443, 8443, 8447

**⚠️ IMPORTANTE**: 
- Puerto 80 → Usado por Plesk (NO disponible)
- Puerto 8443 → Usado por Plesk Admin Panel (NO disponible)
- Puerto 8447 → **DASHBOARD** ✅
- Puerto 8080 → BLOQUEADO por firewall

### 🔒 SELinux
**Estado**: `Permissive` (Deshabilitado)

```bash
# Si necesitas deshabilitarlo:
setenforce 0
```

---

## 📁 Estructura de Archivos

```
/root/aso-rank-guard/          # Proyecto principal
├── src/                        # Código Python
├── data/                       # Datos de rankings
├── config/                     # Configuración
├── logs/                       # Logs
└── web/                        # Dashboard generado

/var/www/aso-rank-guard/       # Web root
└── index.html                  # Dashboard (287KB)

/etc/httpd/conf.d/             # Configuración Apache
└── aso-rank-guard.conf         # VirtualHost puerto 8447

/root/backups/                  # Backups automáticos
```

---

## 🔄 Cron Jobs

```cron
# Dashboard diario a las 16:00 UTC
0 16 * * * cd /root/aso-rank-guard && /usr/bin/python3 src/scheduler.py >> logs/cron.log 2>&1

# Backup diario a las 02:00 UTC  
0 2 * * * /root/backup.sh >> /root/backups/backup.log 2>&1
```

---

## 🛠️ Apache Configuración

**Archivo**: `/etc/httpd/conf.d/aso-rank-guard.conf`

```apache
Listen 8447
<VirtualHost *:8447>
    DocumentRoot /var/www/aso-rank-guard
    DirectoryIndex index.html
    
    <Directory /var/www/aso-rank-guard>
        Options -Indexes
        AllowOverride None
        Require all granted
    </Directory>
</VirtualHost>
```

**Comandos útiles**:
```bash
systemctl status httpd
systemctl restart httpd
journalctl -xeu httpd.service
```

---

## 🔄 Proceso de Actualización del Dashboard

```bash
# 1. Conectar al servidor
ssh root@194.164.160.111

# 2. Ir al proyecto
cd /root/aso-rank-guard

# 3. Regenerar dashboard
python3 src/dashboard_generator.py

# 4. Copiar a web root
cp web/dashboard-interactive.html /var/www/aso-rank-guard/index.html

# 5. Verificar permisos
chmod 644 /var/www/aso-rank-guard/index.html
```

---

## 💾 BACKUP Y RESTAURACIÓN

### Hacer Backup Manual
```bash
ssh root@194.164.160.111
/root/backup.sh
```

### Ver Backups
```bash
ls -lh /root/backups/
```

### Restaurar desde Backup
```bash
# 1. Listar backups
ls /root/backups/

# 2. Restaurar proyecto
cd /root
tar -xzf /root/backups/backup_YYYYMMDD_HHMMSS/aso-rank-guard.tar.gz

# 3. Restaurar web root
tar -xzf /root/backups/backup_YYYYMMDD_HHMMSS/www-data.tar.gz -C /

# 4. Restaurar configuración Apache
cp -r /root/backups/backup_YYYYMMDD_HHMMSS/apache_conf/* /etc/httpd/conf.d/

# 5. Reiniciar Apache
systemctl restart httpd
```

---

## 🚨 DISASTER RECOVERY (Si vuelves a cagarla)

### Script de Despliegue Completo desde Cero

```bash
# 1. BACKUP LOCAL PRIMERO (desde tu Mac)
cd /Users/javi/aso-rank-guard
tar -czf ~/Desktop/aso-backup-$(date +%Y%m%d).tar.gz .

# 2. Reinstalar servidor si es necesario (Panel IONOS)
# 3. Configurar firewall en IONOS: 22, 80, 443, 8443, 8447

# 4. Conectar al servidor nuevo
ssh root@NUEVA_IP

# 5. Instalar dependencias
yum install -y epel-release python3 python3-pip httpd git htop
pip3 install -q requests beautifulsoup4 pyyaml pandas

# 6. Desactivar SELinux
setenforce 0
sed -i 's/^SELINUX=enforcing/SELINUX=permissive/' /etc/selinux/config

# 7. Subir proyecto desde tu Mac
scp ~/Desktop/aso-backup-*.tar.gz root@NUEVA_IP:/root/

# 8. Desplegar en servidor
cd /root
tar -xzf aso-backup-*.tar.gz -C /root/aso-rank-guard/
python3 /root/aso-rank-guard/src/dashboard_generator.py
mkdir -p /var/www/aso-rank-guard
cp /root/aso-rank-guard/web/dashboard-interactive.html /var/www/aso-rank-guard/index.html
chmod 644 /var/www/aso-rank-guard/index.html

# 9. Configurar Apache
cat > /etc/httpd/conf.d/aso-rank-guard.conf << 'APACHE'
Listen 8447
<VirtualHost *:8447>
    DocumentRoot /var/www/aso-rank-guard
    DirectoryIndex index.html
    
    <Directory /var/www/aso-rank-guard>
        Options -Indexes
        AllowOverride None
        Require all granted
    </Directory>
</VirtualHost>
APACHE

systemctl enable httpd
systemctl start httpd

# 10. Configurar cron
(crontab -l 2>/dev/null; echo "0 16 * * * cd /root/aso-rank-guard && /usr/bin/python3 src/scheduler.py >> logs/cron.log 2>&1") | crontab -

# 11. VERIFICAR
curl -I http://localhost:8447
```

---

## ✅ Checklist Post-Despliegue

- [ ] Dashboard accesible: http://194.164.160.111:8447
- [ ] Apache corriendo: `systemctl status httpd`
- [ ] SELinux en Permissive: `getenforce`
- [ ] Firewall IONOS configurado (puerto 8447)
- [ ] Cron job configurado: `crontab -l`
- [ ] Backups automáticos: `/root/backup.sh` existe
- [ ] Logs funcionando: `tail -f /root/aso-rank-guard/logs/cron.log`

---

## 🔍 Troubleshooting

### Dashboard no carga
```bash
# 1. Verificar Apache
systemctl status httpd
journalctl -xeu httpd.service

# 2. Verificar puerto
ss -tlnp | grep 8447

# 3. Verificar SELinux
getenforce  # Debe ser "Permissive"

# 4. Verificar archivo existe
ls -lh /var/www/aso-rank-guard/index.html

# 5. Probar localmente
curl -I http://localhost:8447
```

### Puerto bloqueado
```bash
# Verificar desde tu Mac
curl -I --connect-timeout 5 http://194.164.160.111:8447

# Si da timeout → Revisar firewall IONOS
# Panel IONOS → Red → Políticas de firewall → "My firewall policy"
# Añadir regla: TCP puerto 8447
```

### Dashboard genera mal
```bash
cd /root/aso-rank-guard
python3 src/dashboard_generator.py
cp web/dashboard-interactive.html /var/www/aso-rank-guard/index.html
```

---

## 📞 CONTACTO EMERGENCIA

**Panel IONOS**: https://login.ionos.es/  
**Firewall**: Infraestructura → Red → Políticas de firewall  
**VNC Console**: Infraestructura → Servidores → [Servidor] → Consola  

**⚠️ NUNCA MÁS**:
- ❌ NO tocar configuración de seguridad sin backup
- ❌ NO borrar reglas de firewall/fail2ban sin saber qué hacen
- ❌ NO editar /etc/ssh/sshd_config sin acceso alternativo
- ❌ NO usar puertos bloqueados por firewall (8080)
- ❌ NO usar puertos de Plesk (80, 8443)
- ✅ SIEMPRE hacer backup antes de tocar config
- ✅ SIEMPRE verificar con `curl localhost:PUERTO` primero
- ✅ SIEMPRE revisar firewall IONOS antes de cambiar puertos

---

**Estado actual**: ✅ TODO FUNCIONANDO  
**Dashboard**: http://194.164.160.111:8447  
**Backups**: Diarios a las 02:00 UTC  
**Monitoreo**: Diario a las 16:00 UTC

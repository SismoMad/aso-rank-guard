# 🎛️ Notas sobre Plesk - ASO Rank Guard VPS

Tu servidor viene con **Plesk** preinstalado. Aquí tienes información importante:

---

## 🔐 Acceso a Plesk

### URL de acceso:
```
https://194.164.160.111:8443
```

### Credenciales iniciales:
- **Usuario:** admin o root
- **Contraseña:** La misma que SSH (`rCYRQdS6`)

**⚠️ Nota:** La primera vez que accedas, Plesk te pedirá configurar el panel.

---

## 🤔 ¿Usar Plesk o No?

### Ventajas de usar Plesk:
- ✅ Interfaz gráfica para gestionar todo
- ✅ Gestión fácil de dominios y SSL
- ✅ Backups automatizados integrados
- ✅ Monitoreo visual del servidor
- ✅ Firewall gráfico
- ✅ Gestor de bases de datos visual
- ✅ Logs accesibles desde web

### Desventajas de usar Plesk:
- ❌ Consume más recursos (RAM/CPU)
- ❌ Complejidad adicional para apps Node.js/Python
- ❌ Puede entrar en conflicto con Nginx manual
- ❌ Curva de aprendizaje si no lo conoces

---

## 💡 Recomendación para ASO Rank Guard

### Opción A: **NO usar Plesk** (Recomendado)
**Ventajas:**
- Más control manual
- Menos consumo de recursos
- Los scripts que creamos funcionan sin modificar
- Nginx configurado a medida

**Pasos:**
1. Ignora Plesk completamente
2. Usa los scripts shell que creamos
3. Gestiona todo por SSH

✅ **Esta es la opción recomendada** porque:
- Ya tienes scripts automatizados
- Mejor rendimiento (más RAM disponible)
- Configuración optimizada para tu stack

---

### Opción B: **Usar Plesk para algunas cosas**
Puedes usar Plesk solo para:
- Ver logs gráficamente
- Gestionar SSL de forma visual
- Monitoreo del servidor
- Backups automáticos

Pero sigue usando SSH para:
- Deploy de la aplicación
- PM2
- Cron jobs

---

## 🔧 Configuración si decides usar Plesk

### 1. Acceder a Plesk
```
https://194.164.160.111:8443
```

### 2. Crear un dominio/subdominio
Si tienes un dominio (ej: `asorankguard.com`):
1. En Plesk: **Websites & Domains** → **Add Domain**
2. Apuntar DNS del dominio a `194.164.160.111`
3. Configurar SSL desde Plesk (Let's Encrypt integrado)

### 3. Configurar Node.js App en Plesk
1. **Websites & Domains** → tu dominio → **Node.js**
2. Configurar:
   - **Application Root:** `/var/www/aso-rank-guard/web-app`
   - **Application Startup File:** `.next/standalone/server.js` (requiere cambios en Next.js)
   - **Application URL:** `/`

**⚠️ Problema:** Plesk no funciona bien con Next.js standalone. Es mejor usar PM2 manualmente.

### 4. Ver logs en Plesk
1. **Websites & Domains** → tu dominio → **Logs**
2. Puedes descargar logs de Nginx desde aquí

### 5. Configurar SSL en Plesk
1. **Websites & Domains** → tu dominio → **SSL/TLS Certificates**
2. Click en **Install** (Let's Encrypt)
3. Plesk lo configura automáticamente

---

## ⚙️ Conflictos Potenciales con Plesk

### Nginx
Plesk gestiona Nginx automáticamente. Si editas `/etc/nginx/conf.d/aso-rank-guard.conf` manualmente:

**Solución:**
1. Crea la configuración en `/etc/nginx/plesk.conf.d/` en vez de `/etc/nginx/conf.d/`
2. O usa "Additional Nginx directives" en Plesk panel

### Firewall
Plesk tiene su propio firewall. Si lo activas:
- Puede bloquear puertos que abriste con `firewall-cmd`
- Solución: Abre los puertos también en Plesk Firewall

### Cron Jobs
Puedes gestionar cron jobs desde Plesk:
1. **Tools & Settings** → **Scheduled Tasks**
2. Pero es más fácil usar `crontab -e` directamente

---

## 🎯 Configuración Recomendada (Híbrida)

### Usar Plesk para:
1. **Monitoreo visual:**
   - Ver CPU, RAM, disco
   - Ver logs de Nginx
   - Ver procesos corriendo

2. **SSL/HTTPS:**
   - Configurar certificados SSL de forma visual
   - Renovación automática incluida

3. **Backups:**
   - Configurar backups automáticos desde Plesk
   - Descargar backups fácilmente

### Usar SSH/Scripts para:
1. **Deploy de la aplicación:**
   - `./deploy-to-vps.sh`
   - `./quick-deploy.sh`

2. **Gestión de PM2:**
   - `pm2 status`
   - `pm2 logs`
   - `pm2 restart`

3. **Cron jobs:**
   - `crontab -e` para tracking automático

---

## 📊 Acceder a Funciones Útiles de Plesk

### Ver recursos del servidor
```
https://194.164.160.111:8443
→ Tools & Settings → Server Management → System Information
```

### Ver logs de Nginx
```
https://194.164.160.111:8443
→ Websites & Domains → tu-dominio → Logs
```

### Configurar SSL
```
https://194.164.160.111:8443
→ Websites & Domains → tu-dominio → SSL/TLS Certificates
```

### Backups automáticos
```
https://194.164.160.111:8443
→ Tools & Settings → Backup Manager
```

### Firewall
```
https://194.164.160.111:8443
→ Tools & Settings → Security → Firewall
```

---

## ⚠️ Cosas a Evitar en Plesk

### ❌ NO usar el gestor de aplicaciones Node.js de Plesk
- No funciona bien con Next.js
- Usa PM2 manualmente en su lugar

### ❌ NO modificar Nginx desde dos sitios
- Si usas Plesk para Nginx, NO edites archivos manualmente
- Si usas archivos manuales, NO uses panel Plesk para Nginx

### ❌ NO instalar bases de datos en Plesk
- Ya usas Supabase (cloud)
- No necesitas PostgreSQL/MySQL local

---

## 🔄 Desactivar Plesk (Opcional)

Si decides NO usar Plesk para ahorrar recursos:

```bash
# Detener servicios de Plesk
systemctl stop plesk-web-socket
systemctl stop psa
systemctl stop sw-cp-server
systemctl stop sw-engine

# Desactivar auto-inicio
systemctl disable plesk-web-socket
systemctl disable psa
systemctl disable sw-cp-server
systemctl disable sw-engine

# Esto liberará ~200-300MB de RAM
```

**⚠️ Solo hazlo si estás seguro de no necesitar Plesk**

Para reactivar:
```bash
systemctl start psa
systemctl enable psa
```

---

## 🎯 Decisión Final

### Para ASO Rank Guard, recomiendo:

#### Opción 1: **Ignorar Plesk completamente** ✅
- Usa solo SSH y scripts shell
- Mejor rendimiento
- Más control
- Scripts ya creados funcionan perfectamente

#### Opción 2: **Usar Plesk solo para monitoreo y SSL**
- Accede a Plesk solo para ver gráficos
- Configura SSL desde Plesk (más fácil)
- Deploy sigue siendo con scripts shell

---

## 📖 Documentación de Plesk

Si decides profundizar:
- **Documentación oficial:** https://docs.plesk.com/
- **Gestión Node.js:** https://docs.plesk.com/en-US/obsidian/administrator-guide/website-management/nodejs.79473/

---

## 💡 Resumen

**Para tu caso específico:**
1. ✅ **Ignora Plesk** para el deploy (usa scripts shell)
2. ✅ **Opcionalmente** usa Plesk para monitoreo visual
3. ✅ **Opcionalmente** usa Plesk para SSL (más fácil que certbot manual)
4. ❌ **No uses** Plesk para gestionar Node.js/Python apps
5. ❌ **No uses** Plesk para backups (ya tienes script de backup)

**Resultado:** Mejor rendimiento y configuración optimizada para tu stack.

---

**Próximo paso:** Ejecuta `./deploy-to-vps.sh` sin preocuparte por Plesk 🚀

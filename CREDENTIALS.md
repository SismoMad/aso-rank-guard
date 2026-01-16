# 🔐 Credenciales de Acceso - ASO Rank Guard

## 🌐 **Dashboard Web**

**URL**: http://194.164.160.111

### **Autenticación HTTP Basic**
```
Usuario: asoguard
Password: BibleNow2026
```

**Nota**: El navegador te pedirá estas credenciales la primera vez que accedas. Después las recordará automáticamente.

---

## 📡 **API REST**

**Base URL**: http://194.164.160.111/api

### **Acceso con Autenticación**

```bash
# Con curl
curl -u asoguard:BibleNow2026 http://194.164.160.111/api/stats

# Con JavaScript (desde navegador ya autenticado)
fetch('http://194.164.160.111/api/stats')
  .then(r => r.json())
  .then(console.log)

# Con Python
import requests
from requests.auth import HTTPBasicAuth

auth = HTTPBasicAuth('asoguard', 'BibleNow2026')
response = requests.get('http://194.164.160.111/api/stats', auth=auth)
print(response.json())
```

---

## 🔒 **Seguridad Implementada**

### ✅ **Protecciones Activas**
1. **HTTP Basic Authentication** - Usuario + contraseña requeridos
2. **Rate Limiting** - 60 requests/min por IP en la API
3. **CORS Restrictivo** - Solo IPs autorizadas
4. **GZip Compression** - Respuestas comprimidas
5. **Logging completo** - Todos los accesos registrados

### 📊 **Qué está protegido**
- ✅ Dashboard (/)
- ✅ API endpoints (/api/*)
- ✅ Health check (/health)
- ✅ Metrics (/metrics)
- ✅ Todo el sitio completo

---

## 🔄 **Cambiar Contraseña**

```bash
# Conectar al servidor
ssh root@194.164.160.111

# Cambiar contraseña
htpasswd -c /etc/nginx/.htpasswd asoguard

# Recargar nginx
systemctl reload nginx
```

---

## 👥 **Añadir Más Usuarios**

```bash
# Añadir usuario adicional (sin -c para no sobrescribir)
htpasswd /etc/nginx/.htpasswd nombre_usuario

# Recargar nginx
systemctl reload nginx
```

---

## 🚨 **Acceso de Emergencia**

Si olvidas la contraseña:

```bash
# Conectar al servidor
ssh root@194.164.160.111

# Crear nueva contraseña
htpasswd -cb /etc/nginx/.htpasswd asoguard "NuevaPassword123"

# Recargar nginx
systemctl reload nginx
```

---

## 🌍 **Restricción Adicional por IP (Opcional)**

Si quieres permitir solo desde tu casa/oficina:

```bash
# Editar nginx config
nano /etc/nginx/conf.d/aso-rank-guard.conf

# Añadir dentro de server {}:
allow TU_IP_PUBLICA;
deny all;

# Recargar
systemctl reload nginx
```

Para saber tu IP pública: https://ifconfig.me

---

## 📝 **Registro de Accesos**

```bash
# Ver logs de acceso
tail -f /var/log/nginx/access.log

# Ver intentos de acceso fallidos
grep "401" /var/log/nginx/access.log

# Ver accesos API
grep "/api" /var/log/nginx/access.log
```

---

## ⚠️ **IMPORTANTE**

- ✅ Guarda este archivo en un lugar seguro
- ✅ No compartas las credenciales por email/chat sin cifrar
- ✅ Cambia la contraseña cada 3-6 meses
- ✅ Si sospechas que alguien tiene acceso, cámbiala inmediatamente

---

**Última actualización**: 16 enero 2026  
**Nivel de seguridad**: 🟢 ALTO

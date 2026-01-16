# 🚨 SECURITY.md - Guía de Seguridad

## 🔐 Reporte de Vulnerabilidades

Si encuentras una vulnerabilidad de seguridad, **NO** abras un issue público.

**Contacta directamente:**
- Email: [TU_EMAIL_AQUI]
- Telegram: @tu_usuario

Responderé en menos de 48 horas.

---

## 🛡️ Mejores Prácticas de Seguridad

### 1. Credenciales

**❌ NUNCA hacer:**
```python
# Hardcodear credenciales en código
BOT_TOKEN = "8531462519:AAFvX5PPyB..."
PASSWORD = "mi_password_123"
```

**✅ SÍ hacer:**
```python
# Usar variables de entorno
import os
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
PASSWORD = os.getenv('HTTP_PASSWORD')
```

**Cómo configurar:**
```bash
# En el servidor
echo 'export TELEGRAM_BOT_TOKEN="tu_token"' >> ~/.bashrc
echo 'export HTTP_PASSWORD="tu_password"' >> ~/.bashrc
source ~/.bashrc
```

### 2. Archivos sensibles

**Archivos que NUNCA deben ir a Git:**
- `config/config.yaml` (contiene tokens)
- `CREDENTIALS.md` (contraseñas)
- `bot.log` (puede tener info sensible)
- `data/*.csv` (datos privados)
- `.env` (variables de entorno)

**Verifica tu `.gitignore`:**
```bash
cat .gitignore
# Debe incluir todos los archivos de arriba
```

**Si ya commiteaste algo sensible:**
```bash
# Eliminar del historial de Git
git rm --cached archivo_sensible.txt
git commit -m "Remove sensitive file"
git push

# IMPORTANTE: Cambiar las credenciales expuestas
# porque siguen en el historial de GitHub
```

### 3. HTTPS/SSL

**Estado actual:** ⚠️ HTTP (sin cifrado)

**Cómo añadir HTTPS gratis:**
```bash
# Conectar al servidor
ssh root@194.164.160.111

# Instalar certbot
yum install -y certbot python3-certbot-nginx

# Obtener certificado (GRATIS)
certbot --nginx -d tu-dominio.com

# Renovación automática
echo "0 3 * * * certbot renew --quiet" | crontab -
```

**Beneficios:**
- 🔒 Cifrado de datos
- ✅ Navegadores no muestran "No seguro"
- 📈 Mejor SEO (si expones públicamente)

### 4. Firewall

**Estado actual:** ⚠️ Todos los puertos abiertos

**Cómo proteger:**
```bash
# En AlmaLinux con firewalld
firewall-cmd --permanent --add-service=http
firewall-cmd --permanent --add-service=https
firewall-cmd --permanent --add-service=ssh
firewall-cmd --permanent --remove-service=dhcpv6-client
firewall-cmd --reload

# Verificar
firewall-cmd --list-all
```

**Resultado:** Solo puertos 80 (HTTP), 443 (HTTPS) y 22 (SSH) abiertos.

### 5. SSH Hardening

**Deshabilitar password login (solo SSH keys):**
```bash
# En el servidor
nano /etc/ssh/sshd_config

# Cambiar:
PasswordAuthentication no
PermitRootLogin prohibit-password
PubkeyAuthentication yes

# Reiniciar SSH
systemctl restart sshd
```

**⚠️ ANTES de hacer esto:** Asegúrate de tener tu SSH key configurada o te quedarás sin acceso.

```bash
# En tu Mac
ssh-copy-id root@194.164.160.111
# Introduce password por última vez
# Ya puedes conectar sin password
```

### 6. Fail2ban (anti brute-force)

**Proteger contra ataques:**
```bash
# Instalar
yum install -y epel-release
yum install -y fail2ban

# Configurar
cat > /etc/fail2ban/jail.local << EOF
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5

[sshd]
enabled = true

[nginx-limit-req]
enabled = true
filter = nginx-limit-req
logpath = /var/log/nginx/error.log

[nginx-http-auth]
enabled = true
filter = nginx-http-auth
logpath = /var/log/nginx/error.log
EOF

# Iniciar
systemctl enable --now fail2ban
```

**Resultado:** IPs bloqueadas automáticamente tras 5 intentos fallidos.

### 7. Rate Limiting

**Ya implementado en API v2.0** ✅

```python
# slowapi limita a 60 req/min por IP
@limiter.limit("60/minute")
def get_stats():
    ...
```

**Para aumentar protección:**
```python
# Limitar endpoints sensibles aún más
@limiter.limit("10/minute")  # Solo 10/min
def export_csv():
    ...
```

### 8. Input Validation

**Siempre validar datos del usuario:**
```python
# ❌ MAL - vulnerable a injection
keyword = request.args.get('keyword')
df = df[df['keyword'] == keyword]

# ✅ BIEN - validado
from fastapi import Query
keyword: str = Query(..., regex="^[a-zA-Z0-9 ]{1,50}$")
```

### 9. Actualizaciones de dependencias

**Mantener paquetes actualizados:**
```bash
# Cada mes, revisar vulnerabilidades
pip list --outdated

# Actualizar
pip install --upgrade fastapi uvicorn pandas

# Actualizar requirements.txt
pip freeze > requirements.txt
```

**Herramientas recomendadas:**
```bash
# Safety - detecta vulnerabilidades conocidas
pip install safety
safety check

# Bandit - análisis estático de seguridad
pip install bandit
bandit -r src/
```

### 10. Backups cifrados

**Cifrar backups antes de subirlos:**
```bash
# Backup con cifrado GPG
tar -czf backup.tar.gz /var/www/aso-rank-guard/data
gpg --symmetric --cipher-algo AES256 backup.tar.gz
# Crea backup.tar.gz.gpg cifrado

# Subir a cloud
rclone copy backup.tar.gz.gpg gdrive:backups/

# Para restaurar:
gpg --decrypt backup.tar.gz.gpg > backup.tar.gz
tar -xzf backup.tar.gz
```

---

## 🔍 Checklist de Seguridad

**Al desplegar (primera vez):**
- [ ] Cambiar contraseñas por defecto
- [ ] Configurar `.gitignore` correctamente
- [ ] Usar variables de entorno para secretos
- [ ] Verificar que archivos sensibles NO están en Git
- [ ] Configurar HTTPS/SSL
- [ ] Activar firewall
- [ ] Configurar SSH keys (deshabilitar password)

**Mantenimiento mensual:**
- [ ] Rotar contraseñas
- [ ] Actualizar dependencias
- [ ] Revisar logs de acceso sospechoso
- [ ] Verificar que backups funcionan
- [ ] Ejecutar `safety check` para vulnerabilidades

**Si hay incidente:**
- [ ] Cambiar TODAS las credenciales inmediatamente
- [ ] Revisar logs para identificar breach
- [ ] Regenerar tokens de Telegram Bot
- [ ] Notificar a usuarios si aplica
- [ ] Documentar lecciones aprendidas

---

## 📚 Recursos Adicionales

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [Python Security Best Practices](https://snyk.io/blog/python-security-best-practices-cheat-sheet/)
- [Let's Encrypt](https://letsencrypt.org/)

---

**Última revisión:** 16 enero 2026  
**Nivel de seguridad actual:** 🟡 MEDIO (mejorable)  
**Objetivo:** 🟢 ALTO

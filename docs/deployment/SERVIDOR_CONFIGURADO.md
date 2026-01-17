# ✅ Servidor Configurado - ASO Rank Guard

## 🖥️ Información del Servidor

**Proveedor:** IONOS VPS  
**IP:** 194.164.160.111  
**Sistema:** Alma Linux 9 + Plesk  
**Acceso SSH:** root@194.164.160.111 (contraseña: 43GRAvsq)

---

## 🌐 URLs Activas

### Producción
- **Landing Page:** http://194.164.160.111/index.html
- **Login:** http://194.164.160.111/login.html
- **Precios:** http://194.164.160.111/pricing.html
- **Dashboard:** http://194.164.160.111/dashboard.html

### Panel de Control
- **Plesk:** https://194.164.160.111:8443
  - Usuario: root
  - Contraseña: 43GRAvsq

---

## 📂 Estructura en Servidor

```
/var/www/html/
├── index.html       (14KB) - Landing page
├── login.html       (14KB) - Autenticación
├── pricing.html     (20KB) - Planes y precios
└── dashboard.html   (31KB) - App SaaS
```

---

## 🚀 Comandos Útiles

### Subir archivos actualizados
```bash
scp web/index.html root@194.164.160.111:/var/www/html/
scp web/login.html root@194.164.160.111:/var/www/html/
scp web/pricing.html root@194.164.160.111:/var/www/html/
scp web/dashboard.html root@194.164.160.111:/var/www/html/
```

### Conectar por SSH
```bash
ssh root@194.164.160.111
```

### Ver logs del servidor web
```bash
ssh root@194.164.160.111 "tail -f /var/log/httpd/access_log"
```

### Reiniciar servidor web
```bash
ssh root@194.164.160.111 "systemctl restart httpd"
```

---

## 🔧 Configuración Recomendada

### 1. Configurar Dominio Personalizado

En Plesk (https://194.164.160.111:8443):
1. Websites & Domains → Add Domain
2. Nombre: `aso-rank-guard.com` (o tu dominio)
3. Document Root: `/var/www/html`
4. SSL/TLS: Let's Encrypt (gratis)

### 2. Configurar HTTPS

```bash
# Instalar Certbot
ssh root@194.164.160.111 "dnf install certbot python3-certbot-apache -y"

# Obtener certificado SSL
ssh root@194.164.160.111 "certbot --apache -d tudominio.com"
```

### 3. Configurar Apache/Nginx

Crear archivo de configuración:
```bash
ssh root@194.164.160.111 "cat > /etc/httpd/conf.d/aso-rank-guard.conf << 'EOF'
<VirtualHost *:80>
    ServerName 194.164.160.111
    DocumentRoot /var/www/html
    
    <Directory /var/www/html>
        Options Indexes FollowSymLinks
        AllowOverride All
        Require all granted
    </Directory>
    
    # SPA routing (URLs limpias)
    <IfModule mod_rewrite.c>
        RewriteEngine On
        RewriteBase /
        RewriteRule ^index\.html$ - [L]
        RewriteCond %{REQUEST_FILENAME} !-f
        RewriteCond %{REQUEST_FILENAME} !-d
        RewriteRule . /index.html [L]
    </IfModule>
</VirtualHost>
EOF"

# Reiniciar Apache
ssh root@194.164.160.111 "systemctl restart httpd"
```

---

## 🔒 Seguridad

### Cambiar puerto SSH (opcional)
```bash
ssh root@194.164.160.111 "sed -i 's/#Port 22/Port 2222/' /etc/ssh/sshd_config && systemctl restart sshd"
```

### Configurar Firewall
```bash
ssh root@194.164.160.111 "firewall-cmd --permanent --add-service=http"
ssh root@194.164.160.111 "firewall-cmd --permanent --add-service=https"
ssh root@194.164.160.111 "firewall-cmd --reload"
```

### Actualizar sistema
```bash
ssh root@194.164.160.111 "dnf update -y"
```

---

## 📊 Monitoreo

### Ver uso de recursos
```bash
ssh root@194.164.160.111 "htop"
```

### Ver espacio en disco
```bash
ssh root@194.164.160.111 "df -h"
```

### Ver estadísticas de Apache
```bash
ssh root@194.164.160.111 "systemctl status httpd"
```

---

## 🐛 Troubleshooting

### La página no carga
1. Verificar que Apache esté corriendo:
   ```bash
   ssh root@194.164.160.111 "systemctl status httpd"
   ```

2. Verificar que los archivos existan:
   ```bash
   ssh root@194.164.160.111 "ls -la /var/www/html/"
   ```

3. Ver logs de error:
   ```bash
   ssh root@194.164.160.111 "tail -50 /var/log/httpd/error_log"
   ```

### Error 403 Forbidden
```bash
ssh root@194.164.160.111 "chmod 755 /var/www/html && chmod 644 /var/www/html/*.html"
```

### Error 500 Internal Server Error
```bash
ssh root@194.164.160.111 "tail -50 /var/log/httpd/error_log"
```

---

## 📱 Configuración de Supabase en Producción

Los archivos HTML ya están configurados con:
- **URL:** https://bidqxydrybpuwyskrarh.supabase.co
- **Anon Key:** eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

✅ Todo funciona directamente desde el navegador (no necesita backend)

---

## 🎯 Próximos Pasos

1. **Testear todo el flujo:**
   - [ ] Abrir http://194.164.160.111/
   - [ ] Hacer clic en "Prueba Gratis"
   - [ ] Registrar usuario nuevo
   - [ ] Login exitoso
   - [ ] Dashboard carga correctamente
   - [ ] Agregar app funciona
   - [ ] Ver rankings

2. **Dominio personalizado:**
   - [ ] Comprar dominio (ej: Namecheap, GoDaddy)
   - [ ] Configurar DNS apuntando a 194.164.160.111
   - [ ] Configurar en Plesk
   - [ ] Instalar SSL (Let's Encrypt)

3. **Optimizaciones:**
   - [ ] Habilitar compresión GZIP
   - [ ] Configurar cache headers
   - [ ] CDN para assets estáticos (Cloudflare)
   - [ ] Google Analytics

4. **Backup:**
   - [ ] Configurar backups automáticos en Plesk
   - [ ] Backup de base de datos Supabase

---

## 📞 Soporte

**Servidor:** IONOS VPS  
**Panel:** Plesk (https://194.164.160.111:8443)  
**Base de Datos:** Supabase (https://app.supabase.com)

---

_Última actualización: 17 enero 2026_

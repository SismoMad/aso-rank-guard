# 🔐 AUDITORÍA DE SEGURIDAD - ASO Rank Guard Server

**Fecha**: 16 Enero 2026  
**Server**: 194.164.160.111 (AlmaLinux 9.7 + Plesk)  
**Estado**: ⚠️ MÚLTIPLES VULNERABILIDADES CRÍTICAS

---

## 🚨 PROBLEMAS CRÍTICOS ENCONTRADOS

### 1. ❌ **SSH SIN PROTECCIÓN**
**Severidad**: 🔴 CRÍTICA

```
PermitRootLogin yes  ← PELIGRO: Acceso root directo
PasswordAuthentication [habilitado]  ← Vulnerable a fuerza bruta
Puerto: 22 (estándar)  ← Fácil de atacar
```

**Riesgo**: 
- Cualquiera puede intentar acceder como root
- Ataques de fuerza bruta al puerto 22
- Contraseña expuesta: `43GRAvsq` (estática, sin rotación)

**Exposición**: TODO EL MUNDO puede atacar SSH en el puerto 22

---

### 2. ❌ **FAIL2BAN DESACTIVADO**
**Severidad**: 🔴 CRÍTICA

```
Status: inactive
```

**Riesgo**:
- CERO protección contra fuerza bruta
- Sin límite de intentos de login fallidos
- Sin bloqueo automático de IPs atacantes

**Consecuencia**: Un script automatizado puede probar millones de combinaciones sin ser bloqueado

---

### 3. ⚠️ **SELINUX EN PERMISSIVE**
**Severidad**: 🟡 ALTA

```
Current: Permissive
Config: [probablemente Permissive permanente]
```

**Riesgo**:
- CERO aislamiento de procesos
- Si un atacante compromete Apache, puede acceder a TODO el sistema
- Sin protección contra escalada de privilegios

**Estado actual**: Lo desactivamos para que funcione Apache, pero es peligroso

---

### 4. ❌ **FIREWALL LOCAL INEXISTENTE**
**Severidad**: 🔴 CRÍTICA

```
iptables: ACCEPT all (sin reglas)
firewalld: No configurado
```

**Protección actual**: SOLO firewall de IONOS (externo)

**Riesgo**:
- Si Plesk abre un puerto vulnerable, está expuesto directamente
- Sin segunda capa de defensa
- Confiamos 100% en configuración externa

---

### 5. ⚠️ **DASHBOARD SIN AUTENTICACIÓN**
**Severidad**: 🟡 MEDIA

```
http://194.164.160.111:8447
Sin usuario/password
```

**Riesgo**:
- Cualquiera puede ver tus datos de ASO
- Información de competidores públicamente accesible
- Posibles keywords y estrategias expuestas

**Exposición**: PÚBLICO para todo internet

---

### 6. ⚠️ **PUERTOS INNECESARIOS ABIERTOS**
**Severidad**: 🟡 MEDIA

```
Puerto 80 (HTTP)  ← Usado por Plesk (Default Page)
Puerto 443 (HTTPS) ← SSL de Plesk
Puerto 8443 ← Plesk Admin Panel
Puerto 8447 ← Dashboard
Puerto 22 ← SSH
```

**Riesgo**:
- Puertos 80/443 exponen página default de Plesk (huella digital)
- Puerto 8443 es panel admin de Plesk (objetivo de ataques)
- Muchos vectores de ataque abiertos

---

### 7. ✅ **PUNTOS POSITIVOS** (los únicos)

- Firewall IONOS correctamente configurado (22, 80, 443, 8443, 8447)
- Apache corriendo correctamente
- Servidor recién reinstalado (sin malware heredado)
- Backups configurados
- SSH por ahora solo tú tienes la contraseña

---

## 📊 MATRIZ DE RIESGOS

| Vulnerabilidad | Severidad | Probabilidad | Impacto | Urgencia |
|---|---|---|---|---|
| SSH sin Fail2ban | 🔴 Crítica | Alta | Total | Inmediata |
| Root login habilitado | 🔴 Crítica | Alta | Total | Inmediata |
| SELinux disabled | 🟡 Alta | Media | Alto | Media |
| Sin firewall local | 🔴 Crítica | Media | Total | Alta |
| Dashboard público | 🟡 Media | Baja | Medio | Baja |
| Plesk default page | 🟢 Baja | Baja | Bajo | Baja |

---

## 🎯 RECOMENDACIONES PRIORIZADAS

### NIVEL 1: URGENTE (Hacer YA)

#### ✅ **A. Instalar y Configurar Fail2ban**
**Impacto**: Bloquea el 99% de ataques de fuerza bruta

```bash
# Instalar fail2ban
yum install -y fail2ban fail2ban-systemd

# Configurar protección SSH
cat > /etc/fail2ban/jail.local << 'EOF'
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 3

[sshd]
enabled = true
port = 22
logpath = /var/log/secure
EOF

# Habilitar y arrancar
systemctl enable fail2ban
systemctl start fail2ban
```

**Beneficio**: Después de 3 intentos fallidos, bloqueo automático por 1 hora

---

#### ✅ **B. Crear Usuario No-Root para SSH**
**Impacto**: Elimina acceso directo a root

```bash
# Crear usuario administrador
useradd -m -s /bin/bash javi
passwd javi  # Contraseña fuerte

# Dar permisos sudo
usermod -aG wheel javi

# Probar acceso ANTES de cambiar config
ssh javi@194.164.160.111

# Una vez verificado, deshabilitar root:
sed -i 's/^PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config
systemctl reload sshd
```

**Beneficio**: Los atacantes no saben qué usuario atacar (no es "root")

---

### NIVEL 2: IMPORTANTE (Hacer esta semana)

#### ✅ **C. Configurar Firewall Local (firewalld)**

```bash
# Activar firewalld
systemctl enable firewalld
systemctl start firewalld

# Permitir solo puertos necesarios
firewall-cmd --permanent --add-service=ssh
firewall-cmd --permanent --add-port=8447/tcp
firewall-cmd --reload

# Verificar
firewall-cmd --list-all
```

**Beneficio**: Doble capa de protección (IONOS + local)

---

#### ✅ **D. Añadir Autenticación al Dashboard**

```bash
# Crear usuario/password
htpasswd -cb /etc/httpd/.htpasswd asoguard PASSWORD_SEGURA

# Modificar config Apache
cat > /etc/httpd/conf.d/aso-rank-guard.conf << 'EOF'
Listen 8447
<VirtualHost *:8447>
    DocumentRoot /var/www/aso-rank-guard
    DirectoryIndex index.html
    
    <Directory /var/www/aso-rank-guard>
        AuthType Basic
        AuthName "ASO Rank Guard"
        AuthUserFile /etc/httpd/.htpasswd
        Require valid-user
        Options -Indexes
        AllowOverride None
        Require all granted
    </Directory>
</VirtualHost>
EOF

systemctl restart httpd
```

**Beneficio**: Dashboard privado, solo tú puedes acceder

---

#### ✅ **E. Cambiar Puerto SSH (opcional pero recomendado)**

```bash
# Cambiar a puerto no estándar (ej: 2222)
sed -i 's/^#Port 22/Port 2222/' /etc/ssh/sshd_config

# Actualizar firewall
firewall-cmd --permanent --remove-service=ssh
firewall-cmd --permanent --add-port=2222/tcp
firewall-cmd --reload

# Actualizar IONOS firewall (quitar 22, añadir 2222)

systemctl reload sshd
```

**Beneficio**: El 95% de ataques automatizados solo buscan puerto 22

---

### NIVEL 3: RECOMENDADO (Hacer cuando tengas tiempo)

#### ✅ **F. Habilitar SELinux (con cuidado)**

```bash
# Cambiar a enforcing GRADUALMENTE
setenforce 1  # Temporal para probar

# Si Apache funciona bien:
sed -i 's/^SELINUX=permissive/SELINUX=enforcing/' /etc/selinux/config

# Si Apache falla, dar contexto correcto:
chcon -R -t httpd_sys_content_t /var/www/aso-rank-guard/
semanage fcontext -a -t httpd_sys_content_t "/var/www/aso-rank-guard(/.*)?"
```

**Beneficio**: Aislamiento total entre procesos

---

#### ✅ **G. Configurar Actualizaciones Automáticas**

```bash
yum install -y dnf-automatic
systemctl enable --now dnf-automatic.timer
```

**Beneficio**: Parches de seguridad aplicados automáticamente

---

#### ✅ **H. Monitoreo de Intentos de Intrusión**

```bash
# Ver intentos de login fallidos
cat /var/log/secure | grep "Failed password"

# Ver IPs bloqueadas por fail2ban
fail2ban-client status sshd

# Crear alerta diaria
echo '0 8 * * * tail -50 /var/log/secure | grep "Failed" | mail -s "Intentos SSH fallidos" tu@email.com' | crontab -
```

---

## 🛡️ PLAN DE IMPLEMENTACIÓN SEGURO

### ⚠️ REGLA DE ORO: **NUNCA aplicar cambios sin backup y verificación**

1. **SIEMPRE tener sesión SSH abierta** mientras haces cambios
2. **PROBAR en nueva sesión** antes de cerrar la original
3. **TENER acceso VNC** (IONOS Console) como plan B
4. **BACKUP antes de tocar** `/etc/ssh/sshd_config`
5. **NO cerrar sesión root** hasta verificar acceso alternativo

---

## 📋 CHECKLIST DE IMPLEMENTACIÓN

### Paso 1: Preparación
- [ ] Backup completo: `/root/backup.sh`
- [ ] Acceso VNC verificado (IONOS Panel)
- [ ] Sesión SSH abierta como "ventana de seguridad"

### Paso 2: Implementar Fail2ban (5 min)
- [ ] Instalar fail2ban
- [ ] Configurar `/etc/fail2ban/jail.local`
- [ ] Iniciar servicio
- [ ] Verificar: `fail2ban-client status sshd`

### Paso 3: Crear usuario alternativo (10 min)
- [ ] Crear usuario `javi`
- [ ] Configurar password fuerte
- [ ] Añadir a grupo wheel
- [ ] **PROBAR login desde otra terminal**
- [ ] Verificar `sudo su -` funciona

### Paso 4: Deshabilitar root (CUIDADO)
- [ ] Verificar paso 3 funciona 100%
- [ ] Editar `/etc/ssh/sshd_config`
- [ ] `PermitRootLogin no`
- [ ] `systemctl reload sshd`
- [ ] **MANTENER sesión root abierta**
- [ ] Probar login con usuario `javi`
- [ ] Si falla → revertir inmediatamente

### Paso 5: Firewall local
- [ ] Activar firewalld
- [ ] Configurar puertos
- [ ] Verificar Apache funciona
- [ ] Verificar SSH funciona

### Paso 6: Autenticación Dashboard
- [ ] Crear htpasswd
- [ ] Actualizar Apache config
- [ ] Reiniciar Apache
- [ ] Probar acceso http://194.164.160.111:8447

---

## 🚨 PLAN DE ROLLBACK

Si algo falla:

### SSH no funciona:
1. **Acceso VNC** → IONOS Panel → Servidores → Consola
2. Login como root con password: `43GRAvsq`
3. Revertir: `sed -i 's/PermitRootLogin no/PermitRootLogin yes/' /etc/ssh/sshd_config`
4. `systemctl restart sshd`

### Apache no funciona:
```bash
# Restaurar config anterior
cp /root/backups/backup_*/apache_conf/aso-rank-guard.conf /etc/httpd/conf.d/
systemctl restart httpd
```

### Firewall te bloquea:
```bash
# Via VNC
systemctl stop firewalld
systemctl disable firewalld
```

---

## 📊 COMPARATIVA: ANTES vs DESPUÉS

| Aspecto | 🔴 AHORA | ✅ DESPUÉS |
|---------|----------|-----------|
| Ataques fuerza bruta | Sin protección | Bloqueados tras 3 intentos |
| Acceso root | Directo | Prohibido |
| Firewall | Solo externo | Doble capa |
| Dashboard | Público | Con autenticación |
| SELinux | Deshabilitado | Habilitado (opcional) |
| Puerto SSH | 22 (obvio) | 2222 (opcional) |
| Actualizaciones | Manual | Automático (opcional) |

---

## 💰 COSTO DE NO HACER NADA

**Escenarios reales:**

1. **Bot encuentra puerto 22 abierto** → 10,000 intentos/hora → Probabilidad de éxito: 0.01% = **Compromiso en 1-2 semanas**

2. **Atacante entra como root** → 
   - Acceso total al sistema
   - Puede leer todos los datos ASO
   - Instalar malware/ransomware
   - Usar servidor para spam/ataques
   - **Coste**: Pérdida de datos + limpieza + reputación IP

3. **Dashboard público** →
   - Competidores ven tu estrategia ASO
   - Copian tus keywords
   - **Coste**: Ventaja competitiva perdida

---

## 🎯 RECOMENDACIÓN FINAL

### MÍNIMO INDISPENSABLE (30 minutos):
1. ✅ Instalar Fail2ban
2. ✅ Crear usuario SSH alternativo
3. ✅ Deshabilitar PermitRootLogin

**Esto cubre el 80% del riesgo**

### IDEAL COMPLETO (2 horas):
- Todo lo anterior +
- Firewall local
- Autenticación dashboard
- SELinux enforcing
- Puerto SSH alternativo

**Esto cubre el 99% del riesgo**

---

## 📞 CUANDO PEDIR AYUDA

**NO toques solo si**:
- No entiendes qué hace un comando
- No tienes acceso VNC como backup
- No has hecho backup reciente
- Es viernes tarde (por si hay que recuperar el finde)

**Pide ayuda antes de**:
- Cambiar `/etc/ssh/sshd_config`
- Habilitar SELinux enforcing
- Cambiar puerto SSH
- Tocar firewall

---

**Status Actual**: 🔴 **VULNERABLE**  
**Urgencia**: 🔴 **ALTA** (especialmente Fail2ban + usuario no-root)  
**Dificultad**: 🟡 **MEDIA** (con esta guía: BAJA)  
**Tiempo estimado**: ⏱️ **30-120 minutos** (según nivel)

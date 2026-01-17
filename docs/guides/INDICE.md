# 📚 Índice de Documentación - Despliegue VPS

## 🎯 Inicio Rápido

**Si es tu primera vez, empieza aquí:**

1. **[DEPLOY_RESUMEN.md](DEPLOY_RESUMEN.md)** - 📋 Resumen de todos los archivos creados
2. **[DEPLOY_QUICK_START.md](DEPLOY_QUICK_START.md)** - ⚡ Guía rápida de 3 pasos
3. **Ejecutar:** `./deploy-to-vps.sh`

---

## 📖 Documentación Completa

### Guías Paso a Paso

| Archivo | Descripción | Cuándo usar |
|---------|-------------|-------------|
| **[DEPLOY_VPS_GUIA.md](DEPLOY_VPS_GUIA.md)** | Guía completa y detallada (17K) | Primera vez o troubleshooting |
| **[DEPLOY_QUICK_START.md](DEPLOY_QUICK_START.md)** | Quick start en 3 pasos (3.8K) | Deploy rápido |
| **[DEPLOY_CHECKLIST.md](DEPLOY_CHECKLIST.md)** | Checklist por fases (9.5K) | Durante el proceso |
| **[DEPLOY_RESUMEN.md](DEPLOY_RESUMEN.md)** | Resumen de archivos (6K) | Entender qué hay |

### Información Técnica

| Archivo | Descripción | Cuándo usar |
|---------|-------------|-------------|
| **[ARQUITECTURA.md](ARQUITECTURA.md)** | Diagramas completos del sistema | Entender cómo funciona |
| **[COMANDOS_UTILES.md](COMANDOS_UTILES.md)** | Referencia de comandos (8.1K) | Mantenimiento diario |
| **[PLESK_NOTES.md](PLESK_NOTES.md)** | Notas sobre Plesk | Si usas Plesk panel |

---

## 🤖 Scripts Automatizados

### Scripts de Despliegue

| Script | Descripción | Uso |
|--------|-------------|-----|
| **[vps-initial-setup.sh](vps-initial-setup.sh)** | Setup inicial del servidor | Ejecutar EN el servidor (solo 1 vez) |
| **[deploy-to-vps.sh](deploy-to-vps.sh)** | Deploy completo | Desde tu Mac (primera vez + updates) |
| **[quick-deploy.sh](quick-deploy.sh)** | Deploy rápido (solo código) | Desde tu Mac (updates rápidos) |
| **[monitor-vps.sh](monitor-vps.sh)** | Monitoreo remoto | Desde tu Mac (verificar estado) |

### Cómo Ejecutar

```bash
# 1. Setup inicial del servidor (solo primera vez)
ssh root@194.164.160.111
bash vps-initial-setup.sh
exit

# 2. Deploy de la aplicación (desde tu Mac)
./deploy-to-vps.sh

# 3. Actualizaciones posteriores
./quick-deploy.sh        # Rápido (solo código)
./deploy-to-vps.sh       # Completo (con dependencias)

# 4. Monitoreo
./monitor-vps.sh         # Ver estado sin SSH
```

---

## 📂 Estructura de la Documentación

```
aso-rank-guard/
│
├── 📚 DOCUMENTACION DE DESPLIEGUE
│   │
│   ├── 📋 INDICE.md                    # ← Estás aquí
│   ├── 📖 DEPLOY_VPS_GUIA.md          # Guía completa (17K)
│   ├── ⚡ DEPLOY_QUICK_START.md       # Quick start (3.8K)
│   ├── ✅ DEPLOY_CHECKLIST.md         # Checklist (9.5K)
│   ├── 📊 DEPLOY_RESUMEN.md           # Resumen archivos (6K)
│   ├── 🏗️ ARQUITECTURA.md             # Diagramas técnicos
│   ├── 🔧 COMANDOS_UTILES.md          # Referencia comandos
│   └── 🎛️ PLESK_NOTES.md             # Notas sobre Plesk
│
├── 🤖 SCRIPTS DE DESPLIEGUE
│   │
│   ├── vps-initial-setup.sh           # Setup servidor
│   ├── deploy-to-vps.sh               # Deploy completo
│   ├── quick-deploy.sh                # Deploy rápido
│   └── monitor-vps.sh                 # Monitoreo
│
└── 📚 DOCUMENTACION PROYECTO
    │
    ├── README.md                       # README principal
    ├── .github/copilot-instructions.md # Instrucciones Copilot
    ├── SAAS_GUIA.md                   # Guía SaaS
    └── docs/                          # Más documentación
        ├── ARQUITECTURA_SUPABASE.md
        └── ...
```

---

## 🎯 Flujo de Lectura Recomendado

### Para Principiantes (nunca has desplegado un servidor)

1. **[ARQUITECTURA.md](ARQUITECTURA.md)** → Entender cómo funciona (15 min)
2. **[DEPLOY_VPS_GUIA.md](DEPLOY_VPS_GUIA.md)** → Leer guía completa (30 min)
3. **[DEPLOY_CHECKLIST.md](DEPLOY_CHECKLIST.md)** → Seguir checklist (hacer)
4. Ejecutar `vps-initial-setup.sh` en servidor
5. Ejecutar `./deploy-to-vps.sh` desde tu Mac
6. **[COMANDOS_UTILES.md](COMANDOS_UTILES.md)** → Guardar como referencia

**Tiempo estimado:** 1-2 horas (primera vez)

---

### Para Usuarios con Experiencia

1. **[DEPLOY_QUICK_START.md](DEPLOY_QUICK_START.md)** → Quick start (5 min)
2. Ejecutar `./deploy-to-vps.sh`
3. **[COMANDOS_UTILES.md](COMANDOS_UTILES.md)** → Referencia rápida

**Tiempo estimado:** 15-20 minutos

---

### Solo para Consulta Rápida

- **Ver comandos PM2:** [COMANDOS_UTILES.md](COMANDOS_UTILES.md#pm2-process-manager)
- **Ver comandos Nginx:** [COMANDOS_UTILES.md](COMANDOS_UTILES.md#nginx)
- **Troubleshooting:** [DEPLOY_VPS_GUIA.md](DEPLOY_VPS_GUIA.md#troubleshooting)
- **Notas sobre Plesk:** [PLESK_NOTES.md](PLESK_NOTES.md)

---

## 🔍 Buscar Información Específica

### Por Tema

| Tema | Documento |
|------|-----------|
| **Setup inicial** | [DEPLOY_VPS_GUIA.md](DEPLOY_VPS_GUIA.md#paso-1-preparar-el-servidor) |
| **Nginx config** | [DEPLOY_VPS_GUIA.md](DEPLOY_VPS_GUIA.md#paso-6-configurar-nginx) |
| **PM2 config** | [DEPLOY_VPS_GUIA.md](DEPLOY_VPS_GUIA.md#paso-5-configurar-pm2-process-manager) |
| **Cron jobs** | [DEPLOY_VPS_GUIA.md](DEPLOY_VPS_GUIA.md#paso-7-configurar-cron-jobs-tracking-automático) |
| **SSL/HTTPS** | [DEPLOY_VPS_GUIA.md](DEPLOY_VPS_GUIA.md#paso-8-sslhttps-opcional-pero-recomendado) |
| **Variables .env** | [DEPLOY_VPS_GUIA.md](DEPLOY_VPS_GUIA.md#paso-3-configurar-variables-de-entorno) |
| **Backups** | [DEPLOY_VPS_GUIA.md](DEPLOY_VPS_GUIA.md#92-configurar-monitoreo-con-monitor-vpssh) |
| **Arquitectura** | [ARQUITECTURA.md](ARQUITECTURA.md) |
| **Plesk** | [PLESK_NOTES.md](PLESK_NOTES.md) |

### Por Comando

| Comando | Documento |
|---------|-----------|
| `pm2 logs` | [COMANDOS_UTILES.md](COMANDOS_UTILES.md#pm2-process-manager) |
| `nginx -t` | [COMANDOS_UTILES.md](COMANDOS_UTILES.md#nginx) |
| `systemctl restart` | [COMANDOS_UTILES.md](COMANDOS_UTILES.md#nginx) |
| `crontab -e` | [COMANDOS_UTILES.md](COMANDOS_UTILES.md#cron-jobs) |
| `certbot renew` | [COMANDOS_UTILES.md](COMANDOS_UTILES.md#sslhttps-lets-encrypt) |
| `du -sh` | [COMANDOS_UTILES.md](COMANDOS_UTILES.md#monitoreo-del-sistema) |

---

## 🆘 Solución Rápida de Problemas

| Problema | Solución |
|----------|----------|
| **App no carga** | `./monitor-vps.sh` → Ver estado<br>`ssh root@194.164.160.111 'pm2 restart all'` |
| **Error 502** | Ver [Troubleshooting](DEPLOY_VPS_GUIA.md#problema-nginx-retorna-502-bad-gateway) |
| **PM2 no arranca** | Ver [Troubleshooting](DEPLOY_VPS_GUIA.md#problema-pm2-no-inicia-aplicaciones) |
| **Variables .env faltantes** | Ver [Troubleshooting](DEPLOY_VPS_GUIA.md#problema-nextjs-no-encuentra-variables-de-entorno) |
| **Módulo Python no encontrado** | Ver [Troubleshooting](DEPLOY_VPS_GUIA.md#problema-python-no-encuentra-módulos) |

---

## 📞 Información del Servidor

**Datos de acceso:**
```
IP:        194.164.160.111
Usuario:   root
Password:  rCYRQdS6
SSH:       ssh root@194.164.160.111
Plesk:     https://194.164.160.111:8443
```

**Especificaciones:**
```
CPU:       2 vCores
RAM:       2 GB
Disco:     80 GB NVMe SSD
SO:        Alma Linux 9
Panel:     Plesk
Ubicación: España
```

---

## ✅ Checklist Rápido

Antes de empezar, verifica que tienes:

- [ ] Acceso SSH al servidor (probado)
- [ ] Contraseña root guardada
- [ ] Tu Mac tiene `rsync` instalado
- [ ] Leíste al menos el Quick Start

Después del despliegue, verifica:

- [ ] `http://194.164.160.111` carga la web
- [ ] `http://194.164.160.111/health` responde OK
- [ ] `./monitor-vps.sh` muestra todo "online"
- [ ] PM2 auto-arranca en boot
- [ ] Cron jobs configurados

---

## 🎓 Recursos Adicionales

### Documentación Oficial

- **PM2:** https://pm2.keymetrics.io/docs/
- **Nginx:** https://nginx.org/en/docs/
- **Next.js:** https://nextjs.org/docs
- **FastAPI:** https://fastapi.tiangolo.com/
- **Supabase:** https://supabase.com/docs
- **Plesk:** https://docs.plesk.com/

### Tutoriales Recomendados

- **Deploy Next.js con PM2:** https://pm2.io/blog/2018/09/19/Manage-Next-js-Application-with-PM2/
- **Nginx Reverse Proxy:** https://docs.nginx.com/nginx/admin-guide/web-server/reverse-proxy/
- **Supabase Auth:** https://supabase.com/docs/guides/auth

---

## 📝 Notas Finales

### ¿Qué archivo leer primero?

**Si tienes 5 minutos:**
→ [DEPLOY_QUICK_START.md](DEPLOY_QUICK_START.md)

**Si tienes 30 minutos:**
→ [DEPLOY_VPS_GUIA.md](DEPLOY_VPS_GUIA.md)

**Si quieres entender cómo funciona:**
→ [ARQUITECTURA.md](ARQUITECTURA.md)

**Si ya desplegaste y necesitas ayuda:**
→ [COMANDOS_UTILES.md](COMANDOS_UTILES.md)

---

### Orden Recomendado de Ejecución

```bash
# 1. Leer documentación (15-30 min)
open DEPLOY_QUICK_START.md

# 2. Setup servidor (10 min)
ssh root@194.164.160.111
bash vps-initial-setup.sh
exit

# 3. Deploy aplicación (5 min)
./deploy-to-vps.sh

# 4. Verificar (2 min)
./monitor-vps.sh
open http://194.164.160.111

# 5. Configurar SSL (5 min)
ssh root@194.164.160.111
certbot --nginx -d 194.164.160.111

# 6. Configurar cron jobs (5 min)
# Ver DEPLOY_VPS_GUIA.md paso 7

# TOTAL: ~40 minutos
```

---

## 🎉 ¡Listo para Desplegar!

Tienes toda la documentación necesaria. **Próximo paso:**

```bash
./deploy-to-vps.sh
```

**¡Buena suerte! 🚀**

---

**Última actualización:** 17 de enero de 2026  
**Versión:** 1.0  
**Mantenedor:** @javi

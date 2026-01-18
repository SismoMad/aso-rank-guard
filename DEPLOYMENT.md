# 🚀 ASO Rank Guard - Deployment Guide

## ✅ Estado Actual del Servidor

**Servidor:** 194.164.160.111 (Ubuntu 24.04 + Plesk)

### Servicios Activos

- ✅ **Next.js Frontend:** Puerto 3000 (PM2)
- ✅ **Apache (Plesk):** Puerto 80
- ⏸️ **FastAPI Backend:** Pendiente de configuración
- ⏸️ **PostgreSQL (Supabase):** Cloud

---

## 🌐 Acceso a la Aplicación

**URL Principal:** http://194.164.160.111:3000

**Panel de Login:** http://194.164.160.111:3000/login

**Dashboard:** http://194.164.160.111:3000/dashboard

---

## 📦 Stack Tecnológico

### Frontend (Desplegado)
- **Framework:** Next.js 14 (App Router)
- **Styling:** TailwindCSS
- **Auth:** Supabase Auth
- **Process Manager:** PM2
- **Server:** Ubuntu 24.04

### Backend (Pendiente)
- **API:** FastAPI (Python 3.12)
- **Database:** Supabase PostgreSQL
- **Queue:** BullMQ + Redis (futuro)
- **Payments:** Stripe (futuro)

---

## 🔧 Mantenimiento del Servidor

### Ver logs en tiempo real
```bash
ssh root@194.164.160.111 'pm2 logs nextjs-app'
```

### Ver estado de los procesos
```bash
ssh root@194.164.160.111 'pm2 list'
```

### Reiniciar la aplicación
```bash
ssh root@194.164.160.111 'pm2 restart nextjs-app'
```

### Detener la aplicación
```bash
ssh root@194.164.160.111 'pm2 stop nextjs-app'
```

### Iniciar la aplicación
```bash
ssh root@194.164.160.111 'pm2 start nextjs-app'
```

---

## 🔄 Actualizar la Aplicación

### Opción 1: Script Automático (Recomendado)
```bash
./scripts/update-server-app.sh
```

Este script:
1. Copia archivos de Next.js al servidor
2. Copia configuración de producción
3. Reinstala dependencias
4. Recompila la aplicación
5. Reinicia PM2

### Opción 2: Manual
```bash
# 1. Copiar archivos
rsync -avz --exclude 'node_modules' --exclude '.next' \
  -e "ssh -o StrictHostKeyChecking=no" \
  ./web-app/ root@194.164.160.111:/root/aso-rank-guard/web-app/

# 2. Recompilar en servidor
ssh root@194.164.160.111 << 'EOF'
cd /root/aso-rank-guard/web-app
npm install
npm run build
pm2 restart nextjs-app
pm2 save
EOF
```

---

## ⚙️ Variables de Entorno

### Producción (.env.production)
```bash
# Supabase
NEXT_PUBLIC_SUPABASE_URL=https://bidqxydrybpuwyskrarh.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Backend API (cuando se despliegue)
NEXT_PUBLIC_API_URL=http://194.164.160.111:8000

# App
NEXT_PUBLIC_APP_NAME=ASO Rank Guard
NEXT_PUBLIC_APP_URL=http://194.164.160.111:3000
```

**⚠️ IMPORTANTE:** Nunca commitear claves secretas al repositorio.

---

## 🔒 Seguridad

### Firewall (UFW)
Puertos abiertos:
- `22/tcp` - SSH
- `80/tcp` - HTTP (Apache/Plesk)
- `443/tcp` - HTTPS (Apache/Plesk)
- `3000/tcp` - Next.js
- `8443/tcp` - Plesk Panel

### Backup
- PM2 guarda automáticamente la configuración en `/root/.pm2/dump.pm2`
- Los archivos del proyecto están en `/root/aso-rank-guard/`

---

## 🚧 Próximos Pasos (To-Do)

### Fase 1: Completar Frontend ✅
- [x] Desplegar Next.js
- [x] Configurar PM2
- [ ] Configurar dominio personalizado
- [ ] Configurar HTTPS/SSL

### Fase 2: Backend API
- [ ] Desplegar FastAPI en puerto 8000
- [ ] Configurar PM2 para FastAPI
- [ ] Conectar con Supabase
- [ ] Migrar lógica de Python a API

### Fase 3: Automatización
- [ ] Configurar cron jobs para tracking
- [ ] Implementar BullMQ workers
- [ ] Configurar alertas de Telegram

### Fase 4: Producción
- [ ] Configurar Nginx como proxy reverso
- [ ] Implementar rate limiting
- [ ] Configurar CDN (Cloudflare)
- [ ] Integrar Stripe para pagos
- [ ] Configurar backups automáticos

---

## 📊 Monitoreo

### Recursos del Servidor
```bash
# Ver uso de CPU/RAM
ssh root@194.164.160.111 'htop'

# Ver uso de disco
ssh root@194.164.160.111 'df -h'

# Ver procesos Node.js
ssh root@194.164.160.111 'ps aux | grep node'
```

### PM2 Monitoring
```bash
# Dashboard interactivo
ssh root@194.164.160.111 'pm2 monit'

# Métricas
ssh root@194.164.160.111 'pm2 describe nextjs-app'
```

---

## 🆘 Troubleshooting

### La app no responde
```bash
# Verificar si PM2 está corriendo
ssh root@194.164.160.111 'pm2 list'

# Ver logs de errores
ssh root@194.164.160.111 'pm2 logs nextjs-app --err'

# Reiniciar
ssh root@194.164.160.111 'pm2 restart nextjs-app'
```

### Puerto 3000 ocupado
```bash
# Ver qué proceso usa el puerto
ssh root@194.164.160.111 'lsof -i :3000'

# Matar proceso
ssh root@194.164.160.111 'kill -9 <PID>'
```

### Problemas de memoria
```bash
# Ver uso de memoria
ssh root@194.164.160.111 'free -h'

# Reiniciar PM2 si consume mucha RAM
ssh root@194.164.160.111 'pm2 restart all'
```

---

## 📝 Changelog

### 2026-01-18 - Initial Deployment
- ✅ Instalado Node.js 20 LTS
- ✅ Instalado PM2
- ✅ Desplegado Next.js Frontend
- ✅ Configurado PM2 para auto-restart
- ✅ Abierto puerto 3000 en firewall

---

## 📞 Contacto

**Desarrollador:** @javi  
**Servidor:** IONOS Ubuntu 24.04  
**Panel:** Plesk 18.0.75  

---

## 🔗 Links Útiles

- [Documentación Next.js](https://nextjs.org/docs)
- [Documentación PM2](https://pm2.keymetrics.io/docs/usage/quick-start/)
- [Documentación Supabase](https://supabase.com/docs)
- [Documentación Plesk](https://docs.plesk.com/)

---

**Última actualización:** 18 de enero de 2026

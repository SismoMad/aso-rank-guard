# 🚀 Despliegue Rápido - ASO Rank Guard VPS

## 📋 Información del Servidor

- **IP:** 194.164.160.111
- **Usuario:** root
- **SO:** Alma Linux 9 + Plesk
- **Recursos:** 2 vCPU, 2GB RAM, 80GB SSD

---

## ⚡ Quick Start (3 pasos)

### 1️⃣ Setup inicial del servidor (solo primera vez)

```bash
# Conectar al servidor
ssh root@194.164.160.111
# Contraseña: rCYRQdS6

# Copiar el script de setup
# (lo puedes copiar/pegar manualmente o subirlo)

# Ejecutar setup
bash vps-initial-setup.sh

# Salir del servidor
exit
```

### 2️⃣ Desplegar aplicación (desde tu Mac)

```bash
# En tu Mac, desde /Users/javi/aso-rank-guard
./deploy-to-vps.sh
```

Este script hace AUTOMÁTICAMENTE:
- ✅ Sincroniza código con rsync
- ✅ Crea archivos .env
- ✅ Instala dependencias Python
- ✅ Instala y buildea Next.js
- ✅ Configura PM2
- ✅ Inicia aplicaciones

### 3️⃣ Verificar que funciona

```bash
# Ver estado
./monitor-vps.sh

# O visitar directamente:
open http://194.164.160.111
```

---

## 🔄 Actualizaciones posteriores

### Deploy completo (con reinstalación de dependencias)
```bash
./deploy-to-vps.sh
```

### Quick deploy (solo código, más rápido)
```bash
./quick-deploy.sh
```

### Ver estado y logs
```bash
./monitor-vps.sh
```

---

## 📊 URLs de tu aplicación

Una vez desplegado:

- **Web App:** http://194.164.160.111
- **API:** http://194.164.160.111/api
- **Health Check:** http://194.164.160.111/health
- **API Docs:** http://194.164.160.111/docs (FastAPI Swagger)

---

## 🔧 Comandos útiles SSH

```bash
# Conectar al servidor
ssh root@194.164.160.111

# Ver estado de aplicaciones
pm2 status

# Ver logs en tiempo real
pm2 logs

# Reiniciar aplicaciones
pm2 restart all

# Ver recursos del sistema
htop

# Ver espacio en disco
df -h
```

---

## 🆘 Troubleshooting

### La app no arranca
```bash
# Ver logs de PM2
ssh root@194.164.160.111 'pm2 logs --err'

# Reiniciar servicios
ssh root@194.164.160.111 'pm2 restart all'
```

### Error 502 Bad Gateway
```bash
# Verificar que PM2 esté corriendo
ssh root@194.164.160.111 'pm2 status'

# Reiniciar Nginx
ssh root@194.164.160.111 'systemctl restart nginx'
```

### Cambios no se reflejan
```bash
# Hacer rebuild completo
ssh root@194.164.160.111 << 'EOF'
cd /var/www/aso-rank-guard/web-app
npm run build
pm2 restart all
EOF
```

---

## 📁 Estructura en el servidor

```
/var/www/aso-rank-guard/
├── .env                    # Variables backend
├── venv/                   # Entorno Python
├── api/                    # Backend FastAPI
├── web-app/                # Frontend Next.js
│   ├── .env.production     # Variables frontend
│   └── .next/              # Build de Next.js
├── logs/                   # Logs de PM2 y tracking
└── ecosystem.config.js     # Configuración PM2
```

---

## 🔒 Próximos pasos recomendados

### 1. Configurar SSL/HTTPS (recomendado)
```bash
ssh root@194.164.160.111
certbot --nginx -d 194.164.160.111
```

### 2. Configurar tracking automático
```bash
ssh root@194.164.160.111
crontab -e

# Añadir (tracking diario a las 9 AM):
0 9 * * * cd /var/www/aso-rank-guard && source venv/bin/activate && python src/rank_tracker_supabase.py
```

### 3. Configurar backups automáticos
```bash
ssh root@194.164.160.111
crontab -e

# Añadir (backup diario a las 2 AM):
0 2 * * * tar -czf /var/backups/aso-$(date +\%Y\%m\%d).tar.gz /var/www/aso-rank-guard/data/
```

---

## 📖 Documentación completa

- **Guía detallada:** [DEPLOY_VPS_GUIA.md](DEPLOY_VPS_GUIA.md)
- **Copilot Instructions:** [.github/copilot-instructions.md](.github/copilot-instructions.md)
- **README principal:** [README.md](README.md)

---

## 🎉 ¡Listo!

Tu aplicación debería estar funcionando en:
**http://194.164.160.111**

Para cualquier problema, consulta [DEPLOY_VPS_GUIA.md](DEPLOY_VPS_GUIA.md) o revisa los logs con `./monitor-vps.sh`

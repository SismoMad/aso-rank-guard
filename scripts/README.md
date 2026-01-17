# 🔧 Scripts de Mantenimiento y Deployment

Esta carpeta contiene scripts auxiliares para administración del sistema.

## 📜 Scripts Disponibles

### 🚀 Setup y Configuración

#### `quick_start.sh`
**Propósito**: Setup inicial completo del proyecto  
**Uso**: `./scripts/quick_start.sh`  
**Hace**:
- Verifica Python instalado
- Instala dependencias
- Ejecuta wizard de configuración
- Opcionalmente ejecuta test inicial

**Cuándo usar**: Primera vez que configuras el proyecto

---

#### `setup_automation.sh`
**Propósito**: Configurar automatización diaria con cron  
**Uso**: `./scripts/setup_automation.sh`  
**Hace**:
- Configura cron job para ejecuciones diarias
- Permite elegir hora de ejecución
- Valida configuración

**Cuándo usar**: Cuando quieres automatizar el tracking diario

---

### 🖥️ Deployment

#### `server_setup.sh`
**Propósito**: Setup completo del servidor de producción  
**Uso**: `./scripts/server_setup.sh`  
**Hace**:
- Sube código al servidor (194.164.160.111)
- Instala dependencias en servidor
- Configura servicios systemd
- Configura cron jobs en servidor
- Setup nginx y dashboard

**Cuándo usar**: Primera configuración del servidor o updates mayores

**Pre-requisitos**: Acceso SSH al servidor

---

#### `deploy_to_server.sh`
**Propósito**: Deploy rápido de cambios al servidor  
**Uso**: `./scripts/deploy_to_server.sh`  
**Hace**:
- Sube solo archivos modificados
- Reinicia servicios necesarios
- Valida que todo funcione

**Cuándo usar**: Después de hacer cambios en código que quieres subir a producción

**Diferencia con server_setup.sh**: Este es incremental, server_setup.sh es completo

---

### 💾 Backups

#### `backup.sh`
**Propósito**: Crear backup de datos importantes  
**Uso**: `./scripts/backup.sh`  
**Hace**:
- Backup de `data/ranks.csv`
- Backup de `config/config.yaml`
- Backup de logs importantes
- Crea archivo comprimido con timestamp

**Cuándo usar**: Antes de cambios importantes o periódicamente

**Output**: `backups/backup_YYYYMMDD_HHMMSS.tar.gz`

---

## 🎯 Workflows Comunes

### Primera Instalación
```bash
# 1. Quick start
./scripts/quick_start.sh

# 2. Configurar automatización (opcional)
./scripts/setup_automation.sh
```

### Configurar Servidor Nuevo
```bash
# 1. Setup completo del servidor
./scripts/server_setup.sh

# 2. Verificar que funciona
ssh root@194.164.160.111 'crontab -l'
```

### Actualizar Código en Servidor
```bash
# 1. Hacer backup primero
./scripts/backup.sh

# 2. Deploy cambios
./scripts/deploy_to_server.sh

# 3. Verificar logs
ssh root@194.164.160.111 'tail -f /root/aso-rank-guard/logs/api.log'
```

### Backup Regular
```bash
# Ejecutar manualmente
./scripts/backup.sh

# O configurar en cron (diario a las 2 AM)
0 2 * * * cd /Users/javi/aso-rank-guard && ./scripts/backup.sh
```

---

## ⚠️ Notas Importantes

### Scripts que Requieren Configuración

**server_setup.sh** y **deploy_to_server.sh** requieren:
- SSH configurado para `root@194.164.160.111`
- Clave SSH sin contraseña (recomendado) o contraseña guardada

**Configurar SSH sin contraseña**:
```bash
# En tu Mac
ssh-copy-id root@194.164.160.111
```

### Scripts Deprecados (ya no en uso)

Los siguientes scripts fueron removidos porque su funcionalidad está integrada:
- ~~`fix_critical.sh`~~ - Fixes temporales ya aplicados
- ~~`update_dashboard.sh`~~ - Funcionalidad en `pro.sh`

---

## 📝 Modificar Scripts

Todos los scripts están en bash y pueden editarse según necesites.

**Consejos**:
- Siempre haz backup antes de modificar
- Prueba cambios localmente antes de subir al servidor
- Mantén los scripts simples y documentados

---

## 🔗 Ver También

- **Comandos principales**: `../run.sh` y `../pro.sh` en root
- **Documentación**: [../docs/](../docs/)
- **Configuración**: [../config/config.yaml](../config/config.yaml)

---

**Última actualización**: 17 enero 2026

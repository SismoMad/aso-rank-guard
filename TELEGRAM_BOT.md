# 🚀 Bot de Telegram - Migración a Supabase

## 📋 Estado Actual

Tu bot de Telegram **YA funciona perfectamente** con CSV. Los mensajes tardan ~4 minutos porque está procesando 83 keywords.

## 🎯 Opciones Disponibles

### Opción 1: Seguir con CSV (Actual)
```bash
# Bot actual (ya corriendo)
python src/telegram_bot.py
```

✅ **Ventajas:**
- Ya funciona
- No requiere cambios
- Datos locales

❌ **Desventajas:**
- No multi-usuario
- Limitado por archivos CSV
- Difícil de escalar

### Opción 2: Migrar a Supabase (Recomendado)
```bash
# 1. Migrar datos existentes
python migrate_csv_to_supabase.py

# 2. Detener bot actual
pkill -f "telegram_bot.py"

# 3. Iniciar bot híbrido (auto-detecta Supabase)
python bot_telegram_hybrid.py
```

✅ **Ventajas:**
- Multi-usuario (RLS)
- Base de datos escalable
- Realtime updates
- Sin límites de CSV
- Listo para SaaS

❌ **Desventajas:**
- Requiere migración única
- Dependencia de internet

---

## 🔧 Cómo Migrar (Paso a Paso)

### 1. Verificar Configuración

Asegúrate que tu `.env` tiene:

```bash
SUPABASE_URL=https://bidqxydrybpuwyskrarh.supabase.co
SUPABASE_SERVICE_ROLE_KEY=tu_service_role_key_aqui
ADMIN_EMAIL=tu-email@ejemplo.com
TELEGRAM_BOT_TOKEN=8531462519:AAFvX5PPyB177DUzylwgC8LMIUztrWPYfbI
TELEGRAM_ALLOWED_CHATS=722751828
```

### 2. Migrar Datos de CSV

```bash
# Esto copia todo el historial de data/ranks.csv a Supabase
python migrate_csv_to_supabase.py
```

**Lo que hace:**
- ✅ Crea usuario admin en Supabase
- ✅ Crea app "Audio Bible Stories & Chat"
- ✅ Crea 83 keywords con países
- ✅ Migra TODO el historial de rankings

### 3. Detener Bot Actual

```bash
# Ver proceso actual
ps aux | grep telegram_bot

# Detener bot CSV
pkill -f "telegram_bot.py"
```

### 4. Iniciar Bot Híbrido

```bash
# Auto-detecta si usar CSV o Supabase
python bot_telegram_hybrid.py
```

El bot automáticamente usará Supabase si detecta `SUPABASE_URL` y `SUPABASE_SERVICE_ROLE_KEY` en `.env`.

---

## 📱 Uso del Bot

### Comandos Disponibles

```
/start   - Ver menú principal
/track   - Ejecutar tracking de keywords (4 min)
/status  - Ver estado actual
/help    - Ver ayuda
```

### Flujo Normal

1. **Enviar `/track`** al bot
2. **Esperar ~4 minutos** (83 keywords × 3 segundos)
3. **Ver confirmación** con resumen
4. **Usar `/status`** para ver detalles

---

## 🐛 Solución de Problemas

### Bot no responde

```bash
# Ver logs en tiempo real
tail -f logs/bot.log
```

### Error de conexión a Supabase

```bash
# Verificar variables de entorno
env | grep SUPABASE

# Verificar conectividad
curl https://bidqxydrybpuwyskrarh.supabase.co/rest/v1/
```

### Bot envia mensajes tarde

**Esto es normal**. El tracking tarda ~4 minutos:
- 83 keywords
- 3 segundos por keyword
- = 249 segundos (~4 min)

El bot responde cuando termina todo el proceso.

---

## 📊 Comparación de Modos

| Feature | CSV (Actual) | Supabase (Nuevo) |
|---------|--------------|------------------|
| Multi-usuario | ❌ | ✅ |
| Tiempo real | ❌ | ✅ |
| Escalabilidad | ❌ | ✅ |
| Web dashboard | ⚠️ Limitado | ✅ Full |
| Costo | Gratis | Gratis (250k filas) |
| Setup | Ya hecho | 1 comando |

---

## 🎯 Recomendación

**Si planeas hacer esto un SaaS → Migra a Supabase ahora**

Razones:
1. Multi-usuario desde el inicio
2. Dashboard Next.js ya configurado
3. RLS implementado
4. Sin límites de CSV
5. Migración es simple (1 comando)

**Si solo es para uso personal → CSV funciona perfecto**

Tu bot actual está funcionando bien, solo tarda porque está haciendo su trabajo correctamente.

---

## 📞 Soporte

Si tienes dudas, revisa:
- [SECURITY.md](SECURITY.md) - Guía de seguridad
- [DEPLOYMENT.md](DEPLOYMENT.md) - Guía de despliegue
- [supabase/SCHEMA_DESIGN.md](supabase/SCHEMA_DESIGN.md) - Schema de BD

---

**Última actualización:** 18 enero 2026

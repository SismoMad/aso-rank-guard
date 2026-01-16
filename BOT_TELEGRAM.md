# 🤖 Bot de Telegram - Guía de Uso

## 🚀 Iniciar el Bot

```bash
./run.sh bot
```

El bot se quedará activo esperando comandos desde Telegram.

---

## 📱 Comandos Disponibles en Telegram

Una vez que el bot esté corriendo, abre Telegram y envía estos comandos:

### `/start` o `/help`
Muestra la lista de comandos disponibles

### `/analyze` 
🔍 Ejecuta el **análisis PRO** con los datos actuales (sin tracking nuevo)
- Usa los datos existentes en `data/ranks.csv`
- Genera reporte completo con scores
- Te envía el análisis en el mismo chat

### `/track`
📊 Ejecuta **solo el tracking** de las 83 keywords (sin análisis)
- Tarda ~4 minutos
- Guarda los datos en `data/ranks.csv`
- **NUEVO:** Muestra volume (📊) y difficulty (🔴🟡🟢) para cada keyword
- Te confirma cuando termina

**Leyenda de emojis:**
- Volume: 🔥=Alto · 📊=Medio · 📉=Bajo
- Difficulty: 🔴=High · 🟡=Medium · 🟢=Low

### `/full`
🚀 **Workflow completo**: Tracking + Análisis
- Primero hace tracking de todas las keywords
- Luego genera y envía el análisis PRO
- Es como ejecutar `./run.sh monitor` pero desde Telegram

### `/status`
📈 Muestra el **estado actual** sin ejecutar nada:
- Última actualización
- Keywords totales y visibles
- Distribución (top 10, top 30)
- Mejor keyword
- Número de tracking dates

---

## 💡 Ejemplo de Uso Típico

**Caso 1: Ver análisis rápido (con datos de hoy)**
```
/analyze
```
→ Recibes el análisis PRO en ~5 segundos

**Caso 2: Tracking completo nuevo**
```
/full
```
→ Esperas ~4 minutos
→ Recibes tracking confirmado
→ Recibes análisis PRO actualizado

**Caso 3: Solo quiero ver el estado**
```
/status
```
→ Recibes resumen instantáneo

---

## 🛑 Detener el Bot

Presiona `Ctrl + C` en la terminal donde está corriendo

---

## 🔐 Seguridad

- El bot **solo responde** a tu chat_id configurado
- Otros usuarios recibirán "❌ No autorizado"
- El chat_id está en `config/config.yaml`

---

## ⚙️ Ejecutar en Background (Opcional)

Si quieres que el bot corra siempre en background:

```bash
# Con nohup
nohup ./run.sh bot > logs/bot.log 2>&1 &

# Ver si está corriendo
ps aux | grep telegram_bot

# Detener
pkill -f telegram_bot.py
```

---

## 🐛 Troubleshooting

**El bot no responde:**
1. Verifica que esté corriendo: `ps aux | grep telegram_bot`
2. Revisa que el bot_token sea correcto en `config/config.yaml`
3. Verifica que tu chat_id sea correcto

**Error "No autorizado":**
- Tu chat_id no coincide con el configurado
- Obtén tu chat_id: envía un mensaje al bot y revisa los logs

**El comando /full tarda mucho:**
- Es normal, tarda ~4 minutos en hacer tracking de 83 keywords
- No cierres el bot mientras esté procesando

---

## 📊 Workflow Recomendado

**Diario (automático con scheduler):**
```bash
./run.sh schedule
```
→ Se ejecuta automáticamente a las 8:00 AM

**Bajo demanda desde Telegram:**
- Mañana: `/status` (ver cómo va)
- Mediodía: `/analyze` (análisis rápido)
- Tarde: `/full` (tracking + análisis nuevo si hubo cambios)

---

**✅ El bot está listo para usar!**

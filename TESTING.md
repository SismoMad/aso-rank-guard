# 🧪 Guía de Testing - ASO Rank Guard

## Tests disponibles

### 1. Test básico de configuración

Verifica que `config.yaml` se carga correctamente:

```bash
python3 -c "import yaml; print(yaml.safe_load(open('config/config.yaml')))"
```

### 2. Test de iTunes Search API

Verificar que la API funciona y tu app aparece:

```bash
python3 << EOF
import requests

app_id = 6749528117
keyword = "audio bible stories"
country = "US"

url = f"https://itunes.apple.com/search"
params = {
    'term': keyword,
    'country': country,
    'entity': 'software',
    'limit': 50
}

response = requests.get(url, params=params)
data = response.json()

print(f"Resultados para '{keyword}' en {country}:")
for idx, app in enumerate(data['results'], 1):
    if app['trackId'] == app_id:
        print(f"  ✅ Tu app aparece en posición #{idx}")
        print(f"     Nombre: {app['trackName']}")
        break
else:
    print(f"  ❌ Tu app NO aparece en top 50")
EOF
```

### 3. Test de Telegram (sin enviar mensaje)

Verificar que el bot token es válido:

```bash
python3 << EOF
import requests

bot_token = "TU_BOT_TOKEN_AQUI"  # Reemplaza con tu token real
url = f"https://api.telegram.org/bot{bot_token}/getMe"

response = requests.get(url)
if response.status_code == 200:
    bot_info = response.json()
    print(f"✅ Bot válido: {bot_info['result']['username']}")
else:
    print(f"❌ Bot token inválido")
EOF
```

### 4. Test completo de alertas

Enviar mensaje de prueba real:

```bash
cd /Users/javi/aso-rank-guard
python3 src/telegram_alerts.py
```

### 5. Test de tracking (sin guardar)

Rastrear keywords y mostrar resultados sin guardar en CSV:

```bash
python3 << EOF
import sys
sys.path.insert(0, 'src')

from rank_tracker import RankTracker

tracker = RankTracker()
results = tracker.track_all_keywords()

print("\n📊 RESULTADOS DEL TRACKING:\n")
for _, row in results.iterrows():
    rank_str = f"#{row['rank']}" if row['rank'] < 250 else "No visible"
    print(f"  {row['keyword']} ({row['country']}): {rank_str}")

# NO guardar: tracker.save_results(results)
EOF
```

### 6. Test de Google Trends (si está instalado)

```bash
cd /Users/javi/aso-rank-guard
python3 src/trend_analyzer.py
```

### 7. Test del scheduler (modo dry-run)

Verificar que el scheduler funciona sin ejecutar checks reales:

```bash
python3 << EOF
import schedule
import time

def test_job():
    print("✅ Job ejecutado correctamente")

schedule.every().minute.do(test_job)

print("⏰ Esperando 1 minuto para test...")
print("(Presiona Ctrl+C para cancelar)")

for i in range(65):
    schedule.run_pending()
    time.sleep(1)
    
print("\n✅ Scheduler funciona correctamente")
EOF
```

## Tests de integración

### Test completo end-to-end

Ejecutar workflow completo en modo test (sin alertas reales):

1. Editar `config/config.yaml`:
```yaml
debug:
  test_mode: true
```

2. Ejecutar:
```bash
python3 src/run_monitor.py
```

Verás en logs las alertas que se enviarían sin enviarlas realmente.

## Troubleshooting común

### Error: "No module named 'telegram'"

```bash
pip3 install python-telegram-bot
```

### Error: "No module named 'pandas'"

```bash
pip3 install pandas
```

### Error: "App no aparece en rankings"

Posibles causas:
- El keyword es muy competitivo (prueba keywords más específicos)
- Tu app no está optimizada para ese keyword
- El país no es correcto
- La app está fuera del top 250

### Error: "Telegram bot not found"

Verifica:
1. BOT_TOKEN está bien copiado (sin espacios)
2. El bot no fue eliminado en BotFather
3. Has iniciado conversación con el bot (envíale /start)

## Validación de datos

### Verificar que el CSV se crea correctamente

```bash
# Ejecutar un tracking
python3 src/rank_tracker.py

# Verificar CSV
cat data/ranks.csv | head -20
```

Deberías ver:
```
date,keyword,country,rank,app_id
2026-01-15 10:30:00,audio bible stories,ES,42,6749528117
...
```

## Performance testing

### Medir tiempo de ejecución

```bash
time python3 src/rank_tracker.py
```

Tiempo esperado: 1-3 minutos para 10-20 keywords × 2 países

## Clean up después de tests

Borrar datos de prueba:

```bash
rm data/ranks.csv
rm logs/*.log
```

## Tests automatizados (opcional)

Crear archivo `tests/test_tracker.py`:

```python
import pytest
from src.rank_tracker import RankTracker

def test_tracker_initialization():
    tracker = RankTracker()
    assert tracker.app_id == 6749528117
    assert len(tracker.keywords) > 0

def test_get_rank():
    tracker = RankTracker()
    rank = tracker.get_rank_for_keyword("bible", "US")
    assert rank is None or isinstance(rank, int)

# Ejecutar con: pytest tests/
```

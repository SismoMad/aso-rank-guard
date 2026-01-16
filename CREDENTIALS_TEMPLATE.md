# 🔐 Credenciales de Acceso - ASO Rank Guard

⚠️ **NOTA DE SEGURIDAD**: Este archivo NO debe subirse a GitHub.
Los datos sensibles se guardan localmente en `CREDENTIALS.md`.

## 🌐 Dashboard Web

**URL**: http://TU_IP_DEL_SERVIDOR

### Autenticación HTTP Basic
```
Usuario: tu_usuario
Password: tu_contraseña
```

## 📡 API REST

**Base URL**: http://TU_IP_DEL_SERVIDOR/api

### Acceso con Autenticación

```bash
# Con curl
curl -u usuario:contraseña http://TU_IP_DEL_SERVIDOR/api/stats

# Con Python
import requests
from requests.auth import HTTPBasicAuth

auth = HTTPBasicAuth('usuario', 'contraseña')
response = requests.get('http://TU_IP_DEL_SERVIDOR/api/stats', auth=auth)
```

---

## 🔄 Configuración Inicial

1. Copia `config/config.example.yaml` a `config/config.yaml`
2. Rellena tus credenciales de Telegram
3. Configura tus keywords y app ID
4. Crea un archivo `CREDENTIALS.md` local con tus datos reales

---

## ⚠️ Archivos Excluidos de Git

Por seguridad, estos archivos NO se sincronizan con GitHub:
- `config/config.yaml` - Configuración con tokens
- `CREDENTIALS.md` - Credenciales de acceso
- `bot.log` - Logs que pueden contener información sensible
- `data/*.csv` - Datos de rankings

Consulta `.gitignore` para ver la lista completa.

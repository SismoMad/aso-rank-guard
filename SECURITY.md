# 🔒 Guía de Seguridad - ASO Rank Guard

## ⚠️ PROBLEMAS DETECTADOS Y SOLUCIONADOS

### ✅ Estado Actual (18 enero 2026)

- ✅ `.env` **NO** está trackeado en Git
- ✅ `.gitignore` configurado correctamente
- ✅ Claves hardcodeadas **ELIMINADAS** de archivos HTML
- ✅ Permisos de archivos sensibles ajustados (600)
- ⚠️ **PENDIENTE**: Claves antiguas en historial de Git

---

## 🚨 ACCIÓN REQUERIDA INMEDIATA

### 1. Rotar Claves de Supabase

Las claves actuales han sido expuestas en archivos HTML públicos y posiblemente en el historial de Git.

**Debes rotarlas AHORA:**

```bash
./scripts/rotate-keys.sh
```

Este script te guiará paso a paso para:
1. Generar nuevas claves en Supabase Dashboard
2. Actualizar `.env` local
3. Actualizar servidor de producción
4. (Opcional) Limpiar historial de Git

---

## 📋 Checklist de Seguridad

### Antes de Cada Commit

```bash
# Ejecutar auditoría de seguridad
./scripts/security-audit.sh
```

Si encuentra problemas, **NO COMMITEAR** hasta resolverlos.

### Antes de Push a GitHub

- [ ] `.env` **NO** está en `git status`
- [ ] No hay claves hardcodeadas en código
- [ ] Auditoría de seguridad pasa (exit code 0)
- [ ] Archivos sensibles tienen permisos 600

### Antes de Deploy a Producción

- [ ] Variables de entorno configuradas en servidor
- [ ] Claves diferentes para dev y producción
- [ ] HTTPS configurado (si aplicable)
- [ ] Firewall configurado correctamente

---

## 🔐 Gestión de Credenciales

### Dónde van las Claves

| Tipo de Clave | Local | Producción | Frontend | Backend |
|---------------|-------|------------|----------|---------|
| `SUPABASE_URL` | `.env` | Env vars | ✅ `NEXT_PUBLIC_` | ✅ |
| `ANON_KEY` | `.env` | Env vars | ✅ `NEXT_PUBLIC_` | ✅ |
| `SERVICE_ROLE_KEY` | `.env` | Env vars | ❌ **NUNCA** | ✅ |
| `TELEGRAM_BOT_TOKEN` | `.env` | Env vars | ❌ | ✅ |

### Prefijos de Variables de Entorno

**Next.js:**
- `NEXT_PUBLIC_*` → Expuestas en frontend (bundle público)
- Sin prefijo → Solo backend (Server Components, API Routes)

**Ejemplo correcto:**
```bash
# ✅ Seguro para frontend (protegido por RLS)
NEXT_PUBLIC_SUPABASE_URL=https://xxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJ...

# ❌ NUNCA en frontend (solo backend)
SUPABASE_SERVICE_ROLE_KEY=eyJ...
TELEGRAM_BOT_TOKEN=123:ABC...
```

---

## 🛡️ Reglas de Seguridad

### NUNCA HACER

1. ❌ Commitear `.env` a Git
2. ❌ Hardcodear credenciales en código fuente
3. ❌ Exponer `SERVICE_ROLE_KEY` en frontend
4. ❌ Compartir claves por Slack/Email/Discord
5. ❌ Usar las mismas claves en dev y producción
6. ❌ Dejar archivos con permisos 644/777

### SIEMPRE HACER

1. ✅ Usar variables de entorno (`.env`)
2. ✅ Diferentes claves para dev/staging/prod
3. ✅ Rotar claves si se exponen
4. ✅ Permisos 600 en archivos sensibles
5. ✅ Auditar antes de cada commit
6. ✅ Usar `.env.example` sin valores reales

---

## 🔄 Cómo Rotar Claves (Post-Breach)

Si expusiste claves accidentalmente:

### Opción 1: Script Automático (Recomendado)

```bash
./scripts/rotate-keys.sh
```

### Opción 2: Manual

1. **Generar nuevas claves en Supabase:**
   - https://app.supabase.com/project/_/settings/api
   - Click "Reset" en cada clave

2. **Actualizar local:**
   ```bash
   nano .env  # Pegar nuevas claves
   ```

3. **Actualizar producción:**
   ```bash
   ssh root@194.164.160.111
   cd /root/aso-rank-guard/web-app
   nano .env.production  # Pegar nuevas claves
   pm2 restart nextjs-app
   ```

4. **Limpiar historial Git (opcional):**
   ```bash
   # Instalar BFG
   brew install bfg
   
   # Crear archivo con claves antiguas
   echo "CLAVE_ANTIGUA_AQUI" > passwords.txt
   
   # Limpiar
   bfg --replace-text passwords.txt
   git reflog expire --expire=now --all
   git gc --prune=now --aggressive
   
   # ⚠️ CUIDADO: Reescribe historial
   git push --force
   ```

---

## 🧰 Herramientas de Seguridad

### Scripts Disponibles

```bash
# Auditoría completa de seguridad
./scripts/security-audit.sh

# Rotar claves de Supabase
./scripts/rotate-keys.sh

# Limpiar secretos del historial Git (legacy)
./scripts/fix-security-breach.sh
```

### Auditoría Manual

```bash
# Buscar claves en código
grep -r "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9" . --exclude-dir=node_modules --exclude-dir=venv

# Verificar que .env no esté en Git
git ls-files | grep "^\.env$"  # Debe estar VACÍO

# Ver archivos trackeados
git ls-tree -r HEAD --name-only | grep -E "\.(env|key|pem|p12|crt)$"
```

---

## 📖 Recursos Adicionales

### Documentación

- [Supabase Security Best Practices](https://supabase.com/docs/guides/auth/security-advisories)
- [Next.js Environment Variables](https://nextjs.org/docs/basic-features/environment-variables)
- [OWASP Secrets Management](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)

### Servicios de Escaneo

- [GitGuardian](https://www.gitguardian.com/) - Detecta secretos en repos
- [TruffleHog](https://github.com/trufflesecurity/trufflehog) - Escanea historial Git
- [GitHub Secret Scanning](https://docs.github.com/en/code-security/secret-scanning) - Automático en repos privados

---

## 🆘 En Caso de Breach

### Paso 1: Contener (Inmediato)

```bash
# 1. Rotar claves AHORA
./scripts/rotate-keys.sh

# 2. Revisar logs de Supabase
# https://app.supabase.com/project/_/logs

# 3. Verificar accesos sospechosos
# https://app.supabase.com/project/_/auth/users
```

### Paso 2: Investigar

- [ ] ¿Qué claves se expusieron?
- [ ] ¿Cuándo se expusieron? (commit date)
- [ ] ¿Están en repositorio público?
- [ ] ¿Hay accesos sospechosos en logs?

### Paso 3: Remediar

- [ ] Rotar todas las claves expuestas
- [ ] Limpiar historial Git si es necesario
- [ ] Notificar al equipo
- [ ] Documentar el incidente

### Paso 4: Prevenir

- [ ] Configurar pre-commit hooks
- [ ] Activar GitHub Secret Scanning
- [ ] Training de seguridad al equipo
- [ ] Revisar .gitignore

---

## 📞 Contactos de Emergencia

**Supabase Support:**
- Dashboard: https://app.supabase.com/support
- Discord: https://discord.supabase.com

**GitHub Security:**
- Advisory: https://github.com/[repo]/security/advisories
- Support: https://support.github.com/

---

**Última actualización:** 18 enero 2026  
**Próxima auditoría:** Antes de cada release  
**Responsable:** @javi

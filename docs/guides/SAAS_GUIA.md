# 🚀 ASO Rank Guard SaaS - Guía de Implementación

## ✅ ¿Qué Tenemos Ahora?

Un dashboard **multi-tenant** completo que permite:

1. ✅ **Login/Signup** con Supabase Auth
2. ✅ **Multi-usuario**: Cada usuario ve solo SUS apps
3. ✅ **Multi-app**: Cada usuario puede tener múltiples apps
4. ✅ **Onboarding**: Formulario para agregar apps fácilmente
5. ✅ **RLS activado**: Supabase protege los datos automáticamente

---

## 📁 Archivo Creado

**`web/saas_dashboard.html`** - Dashboard SaaS completo y funcional

---

## 🎯 Características Implementadas

### 1. Autenticación
- Login con email/password
- Registro de nuevos usuarios
- Logout
- Sesión persistente (cookies seguras)

### 2. Gestión de Apps
- Selector visual de apps
- Botón "Agregar App" siempre visible
- Cada app tiene:
  - Nombre
  - App Store ID
  - País
  - Usuario propietario (automático)

### 3. Dashboard por App
- Stats personalizadas (keywords, top 10, top 50, promedio)
- Tabla de keywords con rankings actuales
- Gráfico de evolución (últimos 7 días)
- Todo filtrado automáticamente por el app seleccionada

### 4. Seguridad (RLS)
- **Ya está configurado en Supabase**
- Cada usuario solo puede:
  - Ver sus propias apps
  - Ver keywords de sus apps
  - Ver rankings de sus keywords
- ✅ Sin código adicional necesario (RLS se encarga)

---

## 🚀 Cómo Usar

### Desarrollo Local

1. Abre el archivo en tu navegador:
```bash
open web/saas_dashboard.html
```

2. **Registra tu primera cuenta**
   - Email: tu@email.com
   - Password: (mínimo 6 caracteres)

3. **Agrega tu primera app**
   - Click en "Agregar App"
   - Nombre: "Audio Bible Stories"
   - App Store ID: 6749528117
   - País: US

4. **¡Listo!** Ya puedes ver tus datos

---

### Subir a Tu Servidor (194.164.160.111:8447)

**Opción 1: Reemplazar dashboard actual**

```bash
# Backup del actual
ssh usuario@194.164.160.111
mv /var/www/html/dashboard.html /var/www/html/dashboard_old.html

# Subir nuevo
scp web/saas_dashboard.html usuario@194.164.160.111:/var/www/html/dashboard.html

# Acceder
http://194.164.160.111:8447/
```

**Opción 2: URL separada (recomendado para testear)**

```bash
# Subir como nuevo archivo
scp web/saas_dashboard.html usuario@194.164.160.111:/var/www/html/saas.html

# Acceder
http://194.164.160.111:8447/saas.html
```

---

## 🔐 Configuración de RLS (Ya está hecho)

Las políticas RLS ya están en Supabase:

```sql
-- apps: usuarios solo ven sus apps
CREATE POLICY "Users can view own apps"
  ON apps FOR SELECT
  USING (user_id = auth.uid());

-- keywords: usuarios solo ven keywords de sus apps
CREATE POLICY "Users can view own keywords"
  ON keywords FOR SELECT
  USING (app_id IN (
    SELECT id FROM apps WHERE user_id = auth.uid()
  ));

-- rankings: usuarios solo ven rankings de sus keywords
CREATE POLICY "Users can view own rankings"
  ON rankings FOR SELECT
  USING (keyword_id IN (
    SELECT k.id FROM keywords k
    JOIN apps a ON k.app_id = a.id
    WHERE a.user_id = auth.uid()
  ));
```

✅ **No necesitas hacer nada - ya está activado**

---

## 👥 Flujo de Usuario Nuevo

### Primera Vez

1. **Accede**: http://194.164.160.111:8447/saas.html
2. **Registro**: Click en "Regístrate"
   - Email: cliente@empresa.com
   - Password: MiPassword123
3. **Confirmación**: Supabase envía email (opcional: puedes desactivar)
4. **Login**: Inicia sesión con las credenciales
5. **Bienvenida**: Pantalla vacía con botón "Agregar Mi Primera App"
6. **Onboarding**:
   - Nombre de app
   - App Store ID
   - País
7. **Dashboard**: ¡Ya puede ver sus rankings!

---

## 📊 Tracking de Keywords

Los usuarios pueden agregar apps, pero ¿cómo agregan keywords?

### Opción 1: Por ahora, tú las agregas (Admin)

Desde Supabase SQL Editor:

```sql
-- Ver apps del usuario
SELECT * FROM apps WHERE user_id = 'ID_DEL_USUARIO';

-- Agregar keywords para esa app
INSERT INTO keywords (app_id, keyword, country, is_active)
VALUES
  ('ID_DE_LA_APP', 'bible stories kids', 'US', true),
  ('ID_DE_LA_APP', 'audio bible', 'US', true),
  ('ID_DE_LA_APP', 'sleep bible', 'US', true);
```

### Opción 2: Formulario de Keywords (próximo paso)

Agregar modal similar al de apps:

```javascript
function showAddKeywordModal() {
    // Similar a showAddAppModal()
    // Campos: keyword, country
    // INSERT en tabla keywords
}
```

---

## 🎨 Personalización por Tier

Ahora mismo todos los usuarios tienen acceso igual. Para SaaS real:

### Límites por Tier

En `profiles` table tienes:
- `max_apps`: 10
- `max_keywords_per_app`: 200

**Validar antes de INSERT:**

```javascript
async function addApp() {
    // 1. Check limit
    const { data: profile } = await supabase
        .from('profiles')
        .select('max_apps')
        .eq('user_id', currentUser.id)
        .single();
    
    const { count } = await supabase
        .from('apps')
        .select('*', { count: 'exact', head: true })
        .eq('user_id', currentUser.id);
    
    if (count >= profile.max_apps) {
        alert('¡Límite alcanzado! Mejora tu plan para más apps');
        return;
    }
    
    // 2. Create app
    // ... código actual
}
```

---

## 💰 Integración con Stripe (Siguiente Paso)

### 1. Planes

```javascript
const PLANS = {
    free: {
        max_apps: 1,
        max_keywords_per_app: 10,
        price: 0
    },
    pro: {
        max_apps: 5,
        max_keywords_per_app: 100,
        price: 29
    },
    enterprise: {
        max_apps: 20,
        max_keywords_per_app: 500,
        price: 99
    }
};
```

### 2. Botón de Upgrade

```html
<button onclick="upgradePlan('pro')">
    Upgrade a Pro - $29/mes
</button>
```

### 3. Webhook de Stripe

Cuando el pago se confirma, actualizar `profiles`:

```sql
UPDATE profiles
SET subscription_tier = 'pro',
    max_apps = 5,
    max_keywords_per_app = 100
WHERE user_id = 'XXX';
```

---

## 🔧 Próximos Pasos Recomendados

### Corto Plazo (Esta Semana)

1. ✅ Subir `saas_dashboard.html` a tu servidor
2. ✅ Testear con 2-3 usuarios de prueba
3. ✅ Agregar página de "Agregar Keywords"
4. ✅ Validar límites de tier antes de INSERT

### Medio Plazo (Este Mes)

1. Landing page (explicando el SaaS)
2. Página de precios
3. Integración básica con Stripe
4. Email de bienvenida automático

### Largo Plazo (Próximos Meses)

1. Alertas configurables por usuario
2. Reportes exportables (PDF, Excel)
3. Comparativas entre competidores
4. API pública para integraciones
5. Dashboard de admin (ver todos los usuarios, stats)

---

## 📈 Métricas a Monitorear

Desde Supabase Dashboard:

```sql
-- Total usuarios registrados
SELECT COUNT(*) FROM auth.users;

-- Usuarios activos (últimos 30 días)
SELECT COUNT(DISTINCT user_id) 
FROM apps 
WHERE created_at > NOW() - INTERVAL '30 days';

-- Apps creadas por día
SELECT DATE(created_at), COUNT(*)
FROM apps
GROUP BY DATE(created_at)
ORDER BY DATE(created_at) DESC;

-- Keywords trackeadas
SELECT COUNT(*) FROM keywords WHERE is_active = true;

-- Rankings guardados (últimos 7 días)
SELECT COUNT(*) FROM rankings
WHERE tracked_at > NOW() - INTERVAL '7 days';
```

---

## 🐛 Troubleshooting

### "No puedo registrarme"

**Causa**: Email confirmation requerido

**Solución**: En Supabase Dashboard:
1. Authentication → Settings
2. Desactiva "Enable email confirmations"
3. (Opcional) Configura SMTP para enviar emails

### "No veo mis apps"

**Causa**: RLS bloqueando datos

**Solución**: Verificar que:
1. `user_id` en `apps` coincide con `auth.uid()`
2. RLS policies están activas
3. Usuario está logueado correctamente

### "Error: Row Level Security"

**Causa**: Intentando INSERT sin policy de INSERT

**Solución**: Crear policy:

```sql
CREATE POLICY "Users can insert own apps"
  ON apps FOR INSERT
  WITH CHECK (user_id = auth.uid());
```

---

## ✅ Checklist de Lanzamiento

- [ ] Dashboard subido al servidor
- [ ] RLS policies verificadas
- [ ] Registro de usuarios funcionando
- [ ] Agregar apps funcionando
- [ ] Datos filtrando correctamente por usuario
- [ ] Límites de tier implementados
- [ ] Landing page creada
- [ ] Precios definidos
- [ ] Stripe configurado
- [ ] Email de bienvenida
- [ ] Soporte básico (email/chat)

---

## 🎉 Resumen

**Tienes:**
- ✅ SaaS multi-tenant funcional
- ✅ Login/Signup completo
- ✅ Gestión de apps por usuario
- ✅ Dashboard con datos en tiempo real
- ✅ Seguridad RLS activada

**Siguiente paso:**
1. Sube `saas_dashboard.html` a tu servidor
2. Crea 2 cuentas de prueba
3. Agrega apps diferentes para cada una
4. Verifica que cada usuario ve solo SUS datos

**¿Listo para monetizar?**
- Define tus planes (Free, Pro, Enterprise)
- Crea landing page
- Integra Stripe
- ¡A vender!

---

_Última actualización: 17 enero 2026_

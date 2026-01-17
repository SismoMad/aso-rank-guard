# 🗺️ ASO Rank Guard - Estructura de Navegación SaaS

## 📁 Estructura de Archivos Web

```
web/
├── index.html       → Landing Page (home/marketing)
├── login.html       → Login & Signup
├── pricing.html     → Planes y Precios
├── dashboard.html   → App SaaS (área privada)
└── old_html/        → Versión anterior (legacy)
```

---

## 🔄 Flujo de Navegación

### 1️⃣ Visitante Nuevo (No Autenticado)

```
index.html (Landing)
    ↓
    ├─→ pricing.html (Ver Precios)
    │       ↓
    │   login.html?signup=true
    │
    └─→ login.html (Login/Signup)
            ↓
        dashboard.html (App SaaS)
```

### 2️⃣ Usuario Registrado

```
login.html
    ↓ (autenticación exitosa)
dashboard.html
    ↓
    ├─→ Selector de Apps
    ├─→ Agregar Nueva App
    ├─→ Ver Rankings/Stats
    └─→ Logout → index.html
```

---

## 📄 Páginas Detalladas

### **index.html** - Landing Page

**Propósito:** Página de marketing y ventas

**Secciones:**
- 🎯 Hero con propuesta de valor
- ⭐ Características principales (6 features)
- 💰 Precios resumidos (3 planes)
- 📞 CTA final
- 🔗 Footer con enlaces

**Enlaces clave:**
- `login.html` - Iniciar Sesión
- `login.html?signup=true` - Registrarse
- `pricing.html` - Ver Precios Completos
- `#features` - Ancla a características

**Target:** Visitantes nuevos, SEO, conversión

---

### **login.html** - Autenticación

**Propósito:** Login y Registro de usuarios

**Funcionalidades:**
- 🔐 Tabs: Login vs Signup
- 📧 Email + Password
- ✅ Validación de contraseñas
- 🔄 Creación automática de perfil
- ↩️ Redirección a `dashboard.html` tras login exitoso
- 🔗 Link de retorno a `index.html`

**Parámetros URL:**
- `?signup=true` - Abre directamente en tab de registro

**Integración:**
- Supabase Auth (email/password)
- Auto-creación en tabla `profiles`
- Sesión persistente con cookies

**Target:** Nuevos usuarios y usuarios existentes

---

### **pricing.html** - Planes y Precios

**Propósito:** Información detallada de planes

**Secciones:**
- 💳 Toggle Mensual/Anual (-20% anual)
- 📊 3 Cards de planes (Free, Pro, Enterprise)
- 📋 Tabla comparativa completa
- ❓ FAQ (6 preguntas frecuentes)
- 📞 CTA final

**Planes:**

| Plan | Precio | Apps | Keywords | Tracking |
|------|--------|------|----------|----------|
| Free | $0/mes | 1 | 10 | Diario |
| Pro | $29/mes | 5 | 100 | 6 horas |
| Enterprise | $99/mes | 20 | 500 | 1 hora |

**CTA:** Todos los botones llevan a `login.html?signup=true`

**Target:** Usuarios evaluando opciones, conversión

---

### **dashboard.html** - Aplicación SaaS

**Propósito:** App principal (área privada)

**Protección:** 
- ✅ Requiere autenticación (redirect a login si no hay sesión)
- ✅ RLS activo (usuarios solo ven SUS datos)

**Componentes:**

1. **Header**
   - Logo
   - Título de la app
   - User info (email) + Logout

2. **App Selector**
   - Cards de apps del usuario
   - Botón "Agregar App"
   - Filtro automático por `user_id`

3. **Dashboard Stats**
   - Total keywords
   - Top 10
   - Top 50
   - Promedio de ranking

4. **Gráfico de Evolución**
   - Chart.js (últimos 7 días)
   - Rankings por keyword

5. **Tabla de Keywords**
   - Keyword | País | Ranking | Cambio
   - Filtrada por `app_id` seleccionada

**Estados:**
- 🟢 Sin apps → Modal "Agregar Primera App"
- 🟡 Apps sin keywords → Mensaje informativo
- 🔵 Funcionamiento normal → Stats + Gráficos

**Target:** Usuarios autenticados, uso diario

---

## 🔐 Seguridad y Sesiones

### Flujo de Autenticación

```javascript
// En login.html
supabase.auth.signInWithPassword() 
    → Crea sesión
    → Guarda en localStorage
    → Redirect a dashboard.html

// En dashboard.html (inicio)
supabase.auth.getSession()
    → Si session: Cargar app
    → Si NO session: Redirect a login.html

// Logout
supabase.auth.signOut()
    → Borra sesión
    → Redirect a index.html
```

### Row Level Security (RLS)

**Apps Table:**
```sql
SELECT * FROM apps WHERE user_id = auth.uid()
```

**Keywords Table:**
```sql
SELECT * FROM keywords WHERE app_id IN (
    SELECT id FROM apps WHERE user_id = auth.uid()
)
```

**Rankings Table:**
```sql
-- Heredan seguridad de keywords vía JOIN
```

---

## 🎨 Diseño Consistente

### Paleta de Colores

```css
/* Gradiente Principal */
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);

/* Colores Base */
--primary: #2563eb;
--primary-dark: #1d4ed8;
--success: #10b981;
--error: #ef4444;
--background: #f9fafb;
--text: #1a1a1a;
--text-light: #6b7280;
```

### Logo

```html
<a href="/" class="logo">ASO<span>RankGuard</span></a>
```

- "ASO" en #2563eb
- "RankGuard" en #1e40af

### Botones

- **Primary:** Gradiente púrpura/azul
- **Secondary:** Borde azul, fondo transparente
- **White:** Fondo blanco (sobre gradiente)

---

## 📱 Responsive Design

Todas las páginas son **mobile-first**:

```css
@media (max-width: 768px) {
    /* Ajustes para móvil */
    - Nav links ocultos
    - Grid a 1 columna
    - Texto más pequeño
    - Padding reducido
}
```

---

## 🚀 Deployment

### Estructura de URLs (Producción)

```
https://tudominio.com/
├── /                     → index.html (Landing)
├── /login                → login.html
├── /pricing              → pricing.html
└── /dashboard            → dashboard.html (protegida)
```

### Subir al Servidor

```bash
# Opción 1: Todo junto
scp web/*.html usuario@194.164.160.111:/var/www/html/

# Opción 2: Individual
scp web/index.html usuario@194.164.160.111:/var/www/html/
scp web/login.html usuario@194.164.160.111:/var/www/html/
scp web/pricing.html usuario@194.164.160.111:/var/www/html/
scp web/dashboard.html usuario@194.164.160.111:/var/www/html/
```

### Configuración Nginx (Opcional)

```nginx
server {
    listen 8447;
    server_name 194.164.160.111;
    root /var/www/html;

    # Landing page
    location / {
        try_files $uri $uri/ /index.html;
    }

    # SPA routing (dashboard)
    location /dashboard {
        try_files $uri /dashboard.html;
    }

    # Clean URLs
    location /login {
        try_files $uri /login.html;
    }

    location /pricing {
        try_files $uri /pricing.html;
    }
}
```

---

## ✅ Checklist Pre-Lanzamiento

### Contenido
- [ ] Textos finales en landing page
- [ ] Precios confirmados
- [ ] FAQs completadas
- [ ] Términos de servicio enlazados
- [ ] Política de privacidad enlazada

### Funcionalidad
- [ ] Signup funciona correctamente
- [ ] Login funciona correctamente
- [ ] Logout funciona correctamente
- [ ] Dashboard carga datos reales
- [ ] App selector muestra apps del usuario
- [ ] Modal "Agregar App" funcional
- [ ] RLS bloqueando datos de otros usuarios

### Diseño
- [ ] Responsive en móvil
- [ ] Responsive en tablet
- [ ] Todos los enlaces funcionan
- [ ] Botones tienen hover effects
- [ ] No hay errores de consola

### Seguridad
- [ ] HTTPS habilitado (producción)
- [ ] SUPABASE_ANON_KEY correcto
- [ ] RLS policies activas
- [ ] Validación de inputs
- [ ] Error handling completo

### SEO
- [ ] Meta description en cada página
- [ ] Títulos únicos (<title>)
- [ ] Open Graph tags
- [ ] Favicon configurado
- [ ] Sitemap.xml creado

---

## 🔄 Flujo Completo de Usuario

### Primera Visita

```
1. Entra a https://tudominio.com/
2. Lee landing page (features, beneficios)
3. Click en "Ver Precios" → pricing.html
4. Evalúa planes
5. Click en "Prueba Gratis" → login.html?signup=true
6. Se registra con email/password
7. Auto-redirect a dashboard.html
8. Ve pantalla vacía con "Agregar Primera App"
9. Completa modal (nombre, app_store_id, país)
10. Ve su primera app en dashboard
11. [Necesitaría agregar keywords manualmente o vía script]
```

### Usuario Recurrente

```
1. Entra a https://tudominio.com/login
2. Ingresa credenciales
3. Redirect a dashboard.html
4. Ve selector con sus apps
5. Selecciona app
6. Ve stats, gráficos, tabla
7. Puede:
   - Cambiar de app
   - Agregar nueva app
   - Ver evolución de rankings
   - [Futuro: Exportar datos, configurar alertas]
```

---

## 📊 Próximos Pasos

### Corto Plazo (Semana 1-2)
1. ✅ Subir archivos al servidor
2. ✅ Testear flujo completo
3. ⏳ Agregar formulario de keywords en dashboard
4. ⏳ Implementar límites de tier (Free: 1 app, 10 keywords)

### Medio Plazo (Semana 3-4)
1. Integrar Stripe para pagos
2. Email de bienvenida automático
3. Recuperación de contraseña
4. Página de perfil/configuración

### Largo Plazo (Mes 2+)
1. Blog para SEO
2. Documentación/API docs
3. Dashboard de admin
4. Analytics de uso

---

## 🆘 Troubleshooting

### "No me redirige al dashboard después de login"

**Causa:** Sesión no se guarda

**Solución:**
1. Verificar que `supabase.auth.signInWithPassword()` retorna `data.session`
2. Comprobar que no hay errores en consola
3. Limpiar localStorage y reintentar

---

### "Veo datos de otros usuarios"

**Causa:** RLS no está activo

**Solución:**
```sql
-- Verificar RLS
SELECT tablename, rowsecurity 
FROM pg_tables 
WHERE schemaname = 'public';

-- Activar si está OFF
ALTER TABLE apps ENABLE ROW LEVEL SECURITY;
ALTER TABLE keywords ENABLE ROW LEVEL SECURITY;
ALTER TABLE rankings ENABLE ROW LEVEL SECURITY;
```

---

### "No carga el logo/estilos"

**Causa:** Rutas relativas incorrectas

**Solución:**
- Usar rutas absolutas: `/assets/logo.png`
- O rutas relativas desde raíz: `./assets/logo.png`

---

## 📞 Soporte

Para preguntas sobre esta estructura:
- 📧 Email: soporte@tuemail.com
- 💬 Telegram: @tu_usuario
- 📚 Docs: /docs

---

_Última actualización: 17 enero 2026_

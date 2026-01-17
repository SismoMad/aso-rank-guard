# ASO Rank Guard - Web Application

## ✅ Flujo End-to-End Completado

### 🎯 Flujo de Usuario

```
1. Homepage (/) 
   → Landing page con info del producto
   
2. Login/Signup (/login)
   → Autenticación con Supabase
   → Crear cuenta gratuita
   
3. Dashboard Principal (/dashboard)
   → Ver todas tus apps
   → Estadísticas globales
   → Botón "Nueva App"
   → Onboarding automático para nuevos usuarios
   
4. Seleccionar App (/dashboard/[appId])
   → Dashboard específico de la app
   → Keywords y rankings
   → Botón "Añadir Keywords"
   → Estadísticas detalladas por app
   → Tabs: Keywords, Histórico, Competidores, A/B Testing, Análisis
```

## 🚀 Componentes Creados

### 1. **AddAppModal** (`/components/AddAppModal.tsx`)
Modal para añadir nuevas apps:
- Nombre de la app
- Bundle ID / Package Name
- Plataforma (iOS/Android)
- País
- Categoría
- Validación de límites según plan

### 2. **AddKeywordsModal** (`/components/AddKeywordsModal.tsx`)
Modal para añadir keywords:
- Importación masiva (pegar lista)
- Añadir individualmente
- Campos: keyword, volumen, dificultad
- Validación de límites por app

### 3. **Onboarding** (`/components/Onboarding.tsx`)
Tutorial inicial para nuevos usuarios:
- 3 pasos explicativos
- Se muestra solo una vez
- Skip opcional
- Al finalizar, abre modal de añadir app

## 📁 Páginas Dinámicas

### Homepage (`/app/page.tsx`)
- Landing page estática
- Links a login/signup
- Features del producto

### Login (`/app/login/page.tsx`)
- Tabs: Login / Signup
- Integración con Supabase Auth
- Redirección a dashboard tras login exitoso

### Dashboard Principal (`/app/dashboard/page.tsx`)
**Cliente Component** - Totalmente dinámico:
- ✅ Carga datos del usuario autenticado
- ✅ Muestra onboarding si es nuevo usuario
- ✅ Lista todas las apps del usuario
- ✅ Estadísticas globales (keywords, rankings, top 10)
- ✅ Modal para añadir nueva app
- ✅ Click en app → Ir a dashboard específico

### Dashboard por App (`/app/dashboard/[appId]/page.tsx`)
**Cliente Component** - Dinámico por app:
- ✅ Carga datos de la app específica
- ✅ Solo muestra apps del usuario (RLS)
- ✅ Keywords y rankings de esa app
- ✅ Estadísticas por app
- ✅ Modal para añadir keywords
- ✅ Tabla con todas las keywords
- ✅ Si no hay keywords, botón para añadir

## 🔒 Seguridad (RLS)

Todas las queries usan Row Level Security:
- Usuario solo ve sus propias apps
- Usuario solo ve keywords de sus apps
- Validación en cliente Y servidor
- Service role solo en backend (cuando sea necesario)

## 🎨 Features Implementadas

### ✅ Multi-tenancy
- Cada usuario ve solo sus datos
- Apps aisladas por user_id
- Keywords aisladas por app_id

### ✅ Onboarding
- Aparece automáticamente para nuevos usuarios
- Se guarda en localStorage (no vuelve a aparecer)
- Guía paso a paso

### ✅ Modales Dinámicos
- AddApp: Se abre desde dashboard principal
- AddKeywords: Se abre desde dashboard de app
- Validación de límites según tier

### ✅ Validación de Límites
- Free tier: 1 app, 50 keywords/app
- Mensajes de error claros
- Check en tiempo real

### ✅ Estados Vacíos
- Dashboard sin apps: CTA para añadir primera app
- App sin keywords: CTA para añadir primera keyword
- Mensajes claros y accionables

## 🔄 Próximos Pasos

### Backend (Tracking)
- [ ] Worker para tracking automático de rankings
- [ ] Función para consultar rankings de App Store/Google Play
- [ ] Actualización automática cada hora

### Features Adicionales
- [ ] Editar app
- [ ] Eliminar app
- [ ] Editar keyword
- [ ] Eliminar keyword
- [ ] Gráficos de histórico de rankings
- [ ] Comparación de competidores
- [ ] Alertas de Telegram
- [ ] Exportar datos a CSV

### Subscripciones
- [ ] Integración con Stripe
- [ ] Página de pricing funcional
- [ ] Upgrade/downgrade de plan
- [ ] Webhooks de Stripe

## 🧪 Testing

Para probar el flujo completo:

1. **Nuevo Usuario:**
   ```
   1. Ir a http://localhost:3000
   2. Click "Start Free Trial"
   3. Registrarse con email/password
   4. Ver onboarding (3 pasos)
   5. Click "Empezar" → Se abre modal de añadir app
   6. Añadir app con datos de prueba
   7. Ver dashboard con la app
   8. Click en la app
   9. Ver dashboard de la app (vacío)
   10. Click "Añadir Keywords"
   11. Importar lista de keywords
   12. Ver tabla con keywords
   ```

2. **Usuario Existente:**
   ```
   1. Login
   2. Ver dashboard con apps
   3. Click en app existente
   4. Ver keywords
   5. Añadir más keywords
   ```

## 📝 Datos de Prueba

### App de Ejemplo:
```
Nombre: BiblieNow
Bundle ID: com.example.biblienow
Plataforma: iOS
País: España (es)
Categoría: Religión
```

### Keywords de Ejemplo:
```
biblia
biblia católica
estudio bíblico
devocional diario
lectura biblica
versículo del día
biblia en español
reina valera
```

## 🎯 Arquitectura

```
Homepage (/)
    ↓
Login (/login)
    ↓
Dashboard (/dashboard) → [AddAppModal]
    ↓                     ↓
    ↓                   Crear App
    ↓                     ↓
    └──→ App 1 (/dashboard/123) → [AddKeywordsModal]
    └──→ App 2 (/dashboard/456)     ↓
    └──→ App 3 (/dashboard/789)   Añadir Keywords
                                     ↓
                                  Ver Rankings
```

## 🔥 Demo Live

El servidor está corriendo en: **http://localhost:3000**

- Homepage: http://localhost:3000
- Login: http://localhost:3000/login
- Dashboard: http://localhost:3000/dashboard (requiere autenticación)

## 📊 Estado Actual

✅ **COMPLETADO** - Flujo end-to-end funcional
- Usuario puede registrarse
- Puede crear apps
- Puede añadir keywords
- Puede ver dashboard dinámico
- Todo es específico por usuario y por app
- RLS funcionando correctamente

🔜 **SIGUIENTE** - Implementar tracking automático de rankings

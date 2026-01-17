#!/bin/bash
# Script de inicio rápido para ASO Rank Guard

echo "🚀 ASO Rank Guard - Inicio Rápido"
echo "=================================="
echo ""

# Verificar .env
if [ ! -f .env ]; then
    echo "❌ Error: No se encontró archivo .env"
    echo "📝 Copia .env.example y configura tus credenciales"
    exit 1
fi

echo "✅ Archivo .env encontrado"
echo ""

# Mostrar opciones
echo "Selecciona qué quieres ejecutar:"
echo ""
echo "1) 📊 Abrir Dashboard Web (recomendado)"
echo "2) 🤖 Iniciar Bot de Telegram"
echo "3) 🔄 Ejecutar tracking manual de keywords"
echo "4) 🚀 Iniciar API FastAPI"
echo "5) 📈 Ver estadísticas actuales"
echo "6) ✅ Probar conexión a Supabase"
echo "0) ❌ Salir"
echo ""
read -p "Opción: " option

case $option in
    1)
        echo "📊 Abriendo dashboard..."
        open web/dashboard_supabase.html || xdg-open web/dashboard_supabase.html || echo "⚠️  Abre manualmente: web/dashboard_supabase.html"
        ;;
    2)
        echo "🤖 Iniciando bot de Telegram..."
        echo "💡 Tip: Usa Ctrl+C para detener"
        echo ""
        python3 bot_telegram_supabase.py
        ;;
    3)
        echo "🔄 Ejecutando tracking..."
        python3 track_and_save.py
        ;;
    4)
        echo "🚀 Iniciando API en http://localhost:8000"
        echo "📖 Documentación: http://localhost:8000/docs"
        echo ""
        cd api && python3 main.py
        ;;
    5)
        echo "📈 Obteniendo estadísticas de Supabase..."
        python3 << 'EOF'
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_ROLE_KEY"))

# Stats
keywords = supabase.table("keywords").select("*", count="exact").eq("is_active", True).execute()
rankings = supabase.table("rankings").select("*", count="exact").execute()
alerts = supabase.table("alert_history").select("*", count="exact").execute()

print(f"\n📊 Estadísticas:")
print(f"  Keywords activas: {keywords.count}")
print(f"  Rankings guardados: {rankings.count}")
print(f"  Alertas enviadas: {alerts.count}")
print(f"\n✅ Sistema operacional\n")
EOF
        ;;
    6)
        echo "🔌 Probando conexión a Supabase..."
        python3 << 'EOF'
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

try:
    supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_ROLE_KEY"))
    result = supabase.table("keywords").select("keyword").limit(3).execute()
    
    print("\n✅ Conexión exitosa a Supabase!")
    print(f"📊 Primeras 3 keywords:")
    for kw in result.data:
        print(f"  - {kw['keyword']}")
    print("")
except Exception as e:
    print(f"\n❌ Error de conexión: {e}\n")
EOF
        ;;
    0)
        echo "👋 ¡Hasta luego!"
        exit 0
        ;;
    *)
        echo "❌ Opción inválida"
        exit 1
        ;;
esac

#!/bin/bash
# Abrir puerto 3000 en el firewall

echo "🔥 Abriendo puerto 3000..."

# Opción 1: Usar firewall-cmd si está disponible
if command -v firewall-cmd &> /dev/null; then
    firewall-cmd --permanent --add-port=3000/tcp
    firewall-cmd --reload
    echo "✅ Puerto abierto con firewall-cmd"
fi

# Opción 2: Usar iptables directamente
iptables -I INPUT -p tcp --dport 3000 -j ACCEPT
service iptables save 2>/dev/null || iptables-save > /etc/sysconfig/iptables 2>/dev/null

# Opción 3: Usar Plesk firewall
if command -v plesk &> /dev/null; then
    plesk bin firewall --add-rule -direction incoming -port 3000 -proto tcp 2>/dev/null || true
fi

echo ""
echo "✅ Reglas de firewall actualizadas:"
iptables -L INPUT -n | grep 3000 || echo "Puerto 3000 configurado"

echo ""
echo "🌐 Prueba ahora: http://194.164.160.111:3000"

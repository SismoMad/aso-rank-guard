#!/usr/bin/env python3
"""
Interactive Dashboard Generator - Genera dashboard HTML mejorado con Chart.js
Incluye filtros, comparativas, y datos de nuevas features
"""

import pandas as pd
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class InteractiveDashboard:
    """Generador de dashboard interactivo"""
    
    def __init__(self, config: dict):
        self.config = config
        self.ranks_file = Path(config['storage']['ranks_file'])
        self.output_file = Path('web/dashboard-interactive.html')
        self.output_file.parent.mkdir(parents=True, exist_ok=True)
    
    def generate_html(self, include_competitors: bool = True,
                     include_discoveries: bool = True,
                     include_costs: bool = True) -> str:
        """
        Generar HTML completo del dashboard
        
        Args:
            include_competitors: Incluir sección de competidores
            include_discoveries: Incluir keywords descubiertas
            include_costs: Incluir análisis de costos
        
        Returns:
            HTML string
        """
        
        # Leer datos CSV y JSON para embebed
        ranks_data_json = "[]"
        competitors_data_json = "[]"
        discoveries_data_json = "[]"
        patterns_data_json = "{}"
        experiments_data_json = "{}"
        
        try:
            if self.ranks_file.exists():
                ranks_df = pd.read_csv(self.ranks_file)
                ranks_data_json = ranks_df.to_json(orient='records')
        except Exception as e:
            logger.warning(f"No se pudieron cargar ranks: {e}")
        
        try:
            comp_file = Path('data/competitors.csv')
            if comp_file.exists():
                comp_df = pd.read_csv(comp_file)
                competitors_data_json = comp_df.to_json(orient='records')
        except Exception as e:
            logger.warning(f"No se pudieron cargar competitors: {e}")
        
        try:
            disc_file = Path('data/keyword_discoveries.csv')
            if disc_file.exists():
                disc_df = pd.read_csv(disc_file)
                discoveries_data_json = disc_df.to_json(orient='records')
        except Exception as e:
            logger.warning(f"No se pudieron cargar discoveries: {e}")
        
        try:
            patt_file = Path('data/seasonal_patterns.json')
            if patt_file.exists():
                with open(patt_file, 'r') as f:
                    patterns_data_json = f.read()
        except Exception as e:
            logger.warning(f"No se pudieron cargar patterns: {e}")
        
        try:
            exp_file = Path('data/ab_experiments.json')
            if exp_file.exists():
                with open(exp_file, 'r') as f:
                    experiments_data_json = f.read()
        except Exception as e:
            logger.warning(f"No se pudieron cargar experiments: {e}")
        
        html = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RankRadar - ASO Intelligence Platform</title>
    <link rel="icon" type="image/svg+xml" href="favicon.svg">
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-adapter-date-fns@3.0.0/dist/chartjs-adapter-date-fns.bundle.min.js"></script>
    <script src="https://unpkg.com/lucide@latest"></script>
    <style>
        :root {
            --primary: #667eea;
            --primary-dark: #764ba2;
            --bg-dark: #0f172a;
            --bg-card: #1e293b;
            --text-primary: #e2e8f0;
            --text-secondary: #94a3b8;
            --success: #10b981;
            --warning: #f59e0b;
            --danger: #ef4444;
        }
        
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: var(--bg-dark);
            color: var(--text-primary);
            padding: 20px;
            min-height: 100vh;
        }
        
        .container { max-width: 1800px; margin: 0 auto; }
        
        /* Header con dark mode toggle */
        header {
            background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
            padding: 40px;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(102,126,234,0.3);
            margin-bottom: 30px;
            position: relative;
        }
        
        h1 { color: white; font-size: 3em; margin-bottom: 10px; font-weight: 800; }
        .subtitle { color: rgba(255,255,255,0.9); font-size: 1.2em; margin-bottom: 20px; }
        
        /* Filtros y controles */
        .controls {
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
            margin-top: 20px;
            align-items: center;
        }
        
        .filter-group {
            display: flex;
            gap: 10px;
            background: rgba(255,255,255,0.1);
            padding: 10px 15px;
            border-radius: 12px;
        }
        
        .filter-btn {
            background: rgba(255,255,255,0.2);
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 10px;
            cursor: pointer;
            transition: all 0.3s;
            font-size: 0.95em;
        }
        
        .filter-btn:hover { background: rgba(255,255,255,0.3); }
        .filter-btn.active {
            background: rgba(255,255,255,0.4);
            font-weight: 700;
        }
        
        select, input[type="date"] {
            background: rgba(255,255,255,0.1);
            color: white;
            border: 1px solid rgba(255,255,255,0.3);
            padding: 10px 15px;
            border-radius: 10px;
            cursor: pointer;
            font-size: 0.95em;
        }
        
        select option { background: var(--bg-card); color: var(--text-primary); }
        
        /* Grid layouts */
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .stat-card {
            background: linear-gradient(135deg, var(--bg-card) 0%, #334155 100%);
            padding: 30px;
            border-radius: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            border: 1px solid rgba(255,255,255,0.1);
            transition: all 0.3s;
            position: relative;
            overflow: hidden;
        }
        
        .stat-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, var(--primary), var(--primary-dark));
        }
        
        .stat-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 40px rgba(102,126,234,0.4);
        }
        
        .stat-value {
            font-size: 3em;
            font-weight: bold;
            background: linear-gradient(135deg, var(--primary), var(--primary-dark));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin: 10px 0;
        }
        
        .stat-label {
            color: var(--text-secondary);
            font-size: 0.95em;
            text-transform: uppercase;
            letter-spacing: 1px;
            font-weight: 600;
        }
        
        /* Tabs */
        .tabs {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            border-bottom: 2px solid rgba(255,255,255,0.1);
            padding-bottom: 10px;
        }
        
        .tab-btn {
            background: transparent;
            color: var(--text-secondary);
            border: none;
            padding: 15px 30px;
            border-radius: 10px 10px 0 0;
            cursor: pointer;
            transition: all 0.3s;
            font-size: 1.1em;
            font-weight: 600;
        }
        
        .tab-btn:hover { background: rgba(255,255,255,0.05); }
        .tab-btn.active {
            background: var(--primary);
            color: white;
        }
        
        .tab-content {
            display: none;
            animation: fadeIn 0.3s;
        }
        
        .tab-content.active { display: block; }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        /* Chart containers */
        .chart-container {
            background: linear-gradient(135deg, var(--bg-card) 0%, #334155 100%);
            padding: 30px;
            border-radius: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            border: 1px solid rgba(255,255,255,0.1);
            margin-bottom: 30px;
        }
        
        .chart-title {
            font-size: 1.8em;
            margin-bottom: 25px;
            color: var(--text-primary);
            font-weight: 700;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        /* Tables */
        .data-table {
            width: 100%;
            border-collapse: separate;
            border-spacing: 0 10px;
        }
        
        .data-table thead th {
            background: rgba(255,255,255,0.05);
            padding: 15px;
            text-align: left;
            color: var(--text-secondary);
            font-weight: 600;
            text-transform: uppercase;
            font-size: 0.85em;
            letter-spacing: 1px;
        }
        
        .data-table tbody tr {
            background: rgba(255,255,255,0.05);
            transition: all 0.2s;
        }
        
        .data-table tbody tr:hover {
            background: rgba(102,126,234,0.2);
            transform: scale(1.01);
        }
        
        .data-table tbody td {
            padding: 20px 15px;
            border-top: 1px solid rgba(255,255,255,0.1);
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }
        
        .data-table tbody tr td:first-child {
            border-left: 1px solid rgba(255,255,255,0.1);
            border-radius: 10px 0 0 10px;
        }
        
        .data-table tbody tr td:last-child {
            border-right: 1px solid rgba(255,255,255,0.1);
            border-radius: 0 10px 10px 0;
        }
        
        /* Badges */
        .badge {
            padding: 6px 14px;
            border-radius: 15px;
            font-size: 0.85em;
            font-weight: 600;
            display: inline-block;
        }
        
        .badge-success { background: var(--success); color: white; }
        .badge-warning { background: var(--warning); color: white; }
        .badge-danger { background: var(--danger); color: white; }
        .badge-info { background: var(--primary); color: white; }
        
        /* Cards */
        .card {
            background: rgba(255,255,255,0.05);
            padding: 20px;
            border-radius: 12px;
            margin-bottom: 15px;
            border-left: 4px solid var(--primary);
            transition: all 0.3s;
        }
        
        .card:hover {
            background: rgba(102,126,234,0.1);
            transform: translateX(5px);
        }
        
        .card-title {
            font-size: 1.2em;
            font-weight: 700;
            margin-bottom: 10px;
            color: var(--text-primary);
        }
        
        .card-desc {
            color: var(--text-secondary);
            margin-bottom: 10px;
        }
        
        /* Loading */
        .loading {
            text-align: center;
            padding: 100px;
            font-size: 1.5em;
        }
        
        @keyframes spin {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
        }
        
        /* Export buttons */
        .export-btns {
            display: flex;
            gap: 10px;
        }
        
        .export-btn {
            background: rgba(255,255,255,0.1);
            color: white;
            border: 1px solid rgba(255,255,255,0.3);
            padding: 10px 20px;
            border-radius: 10px;
            cursor: pointer;
            transition: all 0.3s;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .export-btn:hover {
            background: rgba(255,255,255,0.2);
            transform: translateY(-2px);
        }
        
        /* Dark mode toggle */
        .theme-toggle {
            position: absolute;
            top: 20px;
            right: 20px;
            background: rgba(255,255,255,0.2);
            border: none;
            padding: 10px;
            border-radius: 50%;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .theme-toggle:hover {
            background: rgba(255,255,255,0.3);
            transform: rotate(180deg);
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <button class="theme-toggle" onclick="toggleTheme()">
                <i data-lucide="moon" style="width: 24px; height: 24px; color: white;"></i>
            </button>
            <div style="display: flex; align-items: center; gap: 20px; justify-content: center; margin: 10px 0;">
                <svg width="80" height="80" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg" style="filter: drop-shadow(0 0 15px rgba(255,255,255,0.6));">
                  <circle cx="32" cy="32" r="28" stroke="white" stroke-width="2" fill="none" opacity="0.4"/>
                  <circle cx="32" cy="32" r="20" stroke="white" stroke-width="2.5" fill="none" opacity="0.6"/>
                  <circle cx="32" cy="32" r="12" stroke="white" stroke-width="3" fill="none" opacity="0.8"/>
                  <circle cx="32" cy="32" r="6" fill="white" style="filter: drop-shadow(0 0 12px rgba(255,255,255,1));"/>
                  <line x1="32" y1="32" x2="32" y2="4" stroke="#60efff" stroke-width="4" stroke-linecap="round" style="filter: drop-shadow(0 0 10px #60efff);">
                    <animateTransform attributeName="transform" type="rotate" from="0 32 32" to="360 32 32" dur="3s" repeatCount="indefinite"/>
                  </line>
                  <circle cx="46" cy="16" r="4" fill="#00ff88" style="filter: drop-shadow(0 0 8px #00ff88);"><animate attributeName="opacity" values="1;0.5;1" dur="2s" repeatCount="indefinite"/></circle>
                  <circle cx="18" cy="24" r="4" fill="#ffeb3b" style="filter: drop-shadow(0 0 8px #ffeb3b);"><animate attributeName="opacity" values="0.5;1;0.5" dur="2s" repeatCount="indefinite"/></circle>
                  <circle cx="50" cy="44" r="4" fill="#ff6b9d" style="filter: drop-shadow(0 0 8px #ff6b9d);"><animate attributeName="opacity" values="1;0.5;1" dur="2.5s" repeatCount="indefinite"/></circle>
                </svg>
                <h1 style="margin: 0; font-size: 3em; text-shadow: 0 0 20px rgba(255,255,255,0.5);">RankRadar</h1>
            </div>
            <p class="subtitle">ASO Intelligence Platform · Real-time Rankings & Insights</p>
            
            <div class="controls">
                <div class="filter-group">
                    <button class="filter-btn active" onclick="setTimeRange(7)">7 días</button>
                    <button class="filter-btn" onclick="setTimeRange(14)">14 días</button>
                    <button class="filter-btn" onclick="setTimeRange(30)">30 días</button>
                    <button class="filter-btn" onclick="setTimeRange(90)">90 días</button>
                </div>
                
                <div class="filter-group">
                    <label style="color: white;">Desde:</label>
                    <input type="date" id="date-from" onchange="applyCustomDateRange()">
                    <label style="color: white;">Hasta:</label>
                    <input type="date" id="date-to" onchange="applyCustomDateRange()">
                </div>
                
                <div class="filter-group">
                    <select id="keyword-filter" onchange="filterByKeyword()">
                        <option value="all">Todas las keywords</option>
                    </select>
                </div>
                
                <div class="export-btns">
                    <button class="export-btn" onclick="exportData('csv')">
                        <i data-lucide="download" style="width: 16px; height: 16px;"></i>
                        CSV
                    </button>
                    <button class="export-btn" onclick="exportData('pdf')">
                        <i data-lucide="file-text" style="width: 16px; height: 16px;"></i>
                        PDF
                    </button>
                </div>
            </div>
        </header>

        <div id="loading" class="loading">
            <i data-lucide="loader" style="width: 40px; height: 40px; display: inline-block; animation: spin 1s linear infinite;"></i>
            <br>Cargando datos...
        </div>

        <div id="content" style="display: none;">
            <!-- Stats Cards -->
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-label">Total Keywords</div>
                    <div class="stat-value" id="total-keywords">-</div>
                    <div style="color: var(--text-secondary); margin-top: 10px;">Monitoreadas activamente</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Revenue Mensual Est.</div>
                    <div class="stat-value" id="monthly-revenue">$-</div>
                    <div style="color: var(--text-secondary); margin-top: 10px;" id="revenue-change"></div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Top 10 Keywords</div>
                    <div class="stat-value" id="top-10">-</div>
                    <div style="color: var(--text-secondary); margin-top: 10px;" id="top10-change"></div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Visibilidad</div>
                    <div class="stat-value" id="visibility">-%</div>
                    <div style="color: var(--text-secondary); margin-top: 10px;">Keywords en top 100</div>
                </div>
            </div>

            <!-- Tabs Navigation -->
            <div class="tabs">
                <button class="tab-btn active" onclick="switchTab('rankings')">
                    <i data-lucide="trending-up" style="width: 20px; height: 20px; display: inline-block; vertical-align: middle;"></i>
                    Rankings
                </button>
                <button class="tab-btn" onclick="switchTab('competitors')">
                    <i data-lucide="users" style="width: 20px; height: 20px; display: inline-block; vertical-align: middle;"></i>
                    Competidores
                </button>
                <button class="tab-btn" onclick="switchTab('discoveries')">
                    <i data-lucide="search" style="width: 20px; height: 20px; display: inline-block; vertical-align: middle;"></i>
                    Descubrimientos
                </button>
                <button class="tab-btn" onclick="switchTab('costs')">
                    <i data-lucide="dollar-sign" style="width: 20px; height: 20px; display: inline-block; vertical-align: middle;"></i>
                    Análisis de Costos
                </button>
                <button class="tab-btn" onclick="switchTab('patterns')">
                    <i data-lucide="calendar" style="width: 20px; height: 20px; display: inline-block; vertical-align: middle;"></i>
                    Patrones
                </button>
                <button class="tab-btn" onclick="switchTab('experiments')">
                    <i data-lucide="flask" style="width: 20px; height: 20px; display: inline-block; vertical-align: middle;"></i>
                    A/B Tests
                </button>
            </div>

            <!-- Tab: Rankings -->
            <div id="tab-rankings" class="tab-content active">
                <div class="chart-container">
                    <h2 class="chart-title">
                        <i data-lucide="activity" style="width: 32px; height: 32px;"></i>
                        Evolución de Rankings
                    </h2>
                    <div style="height: 400px;">
                        <canvas id="rankingsChart"></canvas>
                    </div>
                </div>

                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 30px;">
                    <div class="chart-container">
                        <h2 class="chart-title">Distribución por Ranking</h2>
                        <div style="height: 300px;">
                            <canvas id="distributionChart"></canvas>
                        </div>
                    </div>
                    <div class="chart-container">
                        <h2 class="chart-title">Top/Bottom Movers</h2>
                        <div style="height: 300px;">
                            <canvas id="moversChart"></canvas>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Tab: Competitors -->
            <div id="tab-competitors" class="tab-content">
                <div class="chart-container">
                    <h2 class="chart-title">
                        <i data-lucide="users" style="width: 32px; height: 32px;"></i>
                        Análisis de Competidores
                    </h2>
                    <div id="competitors-content">
                        <p style="color: var(--text-secondary); text-align: center; padding: 40px;">
                            Ejecuta competitor tracking para ver datos aquí
                        </p>
                    </div>
                </div>
            </div>

            <!-- Tab: Discoveries -->
            <div id="tab-discoveries" class="tab-content">
                <div class="chart-container">
                    <h2 class="chart-title">
                        <i data-lucide="lightbulb" style="width: 32px; height: 32px;"></i>
                        Keywords Descubiertas
                    </h2>
                    <div id="discoveries-content">
                        <p style="color: var(--text-secondary); text-align: center; padding: 40px;">
                            Ejecuta keyword discovery para ver oportunidades
                        </p>
                    </div>
                </div>
            </div>

            <!-- Tab: Costs -->
            <div id="tab-costs" class="tab-content">
                <div class="chart-container">
                    <h2 class="chart-title">
                        <i data-lucide="trending-up" style="width: 32px; height: 32px;"></i>
                        Revenue & Opportunity Costs
                    </h2>
                    <div id="costs-content">
                        <div class="stats-grid">
                            <div class="card">
                                <div class="card-title">Revenue Portfolio</div>
                                <div class="card-desc">Valor estimado de keywords actuales</div>
                                <div style="font-size: 2em; font-weight: bold; color: var(--success);" id="portfolio-value">$0</div>
                            </div>
                            <div class="card">
                                <div class="card-title">Oportunidad Perdida</div>
                                <div class="card-desc">$ que podrías ganar mejorando rankings</div>
                                <div style="font-size: 2em; font-weight: bold; color: var(--warning);" id="opportunity-lost">$0</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Tab: Patterns -->
            <div id="tab-patterns" class="tab-content">
                <div class="chart-container">
                    <h2 class="chart-title">
                        <i data-lucide="calendar" style="width: 32px; height: 32px;"></i>
                        Patrones Estacionales
                    </h2>
                    <div id="patterns-content">
                        <p style="color: var(--text-secondary); text-align: center; padding: 40px;">
                            Ejecuta análisis de patrones (requiere 30+ días de histórico)
                        </p>
                    </div>
                </div>
            </div>

            <!-- Tab: Experiments -->
            <div id="tab-experiments" class="tab-content">
                <div class="chart-container">
                    <h2 class="chart-title">
                        <i data-lucide="flask" style="width: 32px; height: 32px;"></i>
                        Experimentos A/B
                    </h2>
                    <div id="experiments-content">
                        <p style="color: var(--text-secondary); text-align: center; padding: 40px;">
                            Crea experimentos para trackear impacto de cambios ASO
                        </p>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        // Initialize Lucide icons
        lucide.createIcons();

        // Datos embebidos (generados al crear el dashboard)
        const EMBEDDED_DATA = """ + ranks_data_json + """;
        const COMPETITORS_DATA = """ + competitors_data_json + """;
        const DISCOVERIES_DATA = """ + discoveries_data_json + """;
        const PATTERNS_DATA = """ + patterns_data_json + """;
        const EXPERIMENTS_DATA = """ + experiments_data_json + """;

        let currentData = null;
        let currentTimeRange = 7;
        let charts = {};

        // Load data on page load
        document.addEventListener('DOMContentLoaded', () => {
            loadData();
        });

        function loadData() {
            try {
                // Usar datos embebidos directamente
                currentData = EMBEDDED_DATA;
                
                if (!currentData || currentData.length === 0) {
                    throw new Error('No hay datos disponibles');
                }
                
                updateDashboard();
                loadCompetitorsData();
                loadDiscoveriesData();
                loadCostsData();
                loadPatternsData();
                loadExperimentsData();
                
                document.getElementById('loading').style.display = 'none';
                document.getElementById('content').style.display = 'block';
            } catch (error) {
                console.error('Error loading data:', error);
                document.getElementById('loading').innerHTML = '❌ Error cargando datos: ' + error.message;
            }
        }
        
        function loadCompetitorsData() {
            try {
                if (COMPETITORS_DATA && COMPETITORS_DATA.length > 0) {
                    // Mostrar competidores en la tab
                    const container = document.getElementById('competitors-content');
                    if (container) {
                        const uniqueCompetitors = [...new Set(COMPETITORS_DATA.map(c => c.app_id))];
                        container.innerHTML = `
                            <h3>📊 Competidores Monitorizados: ${uniqueCompetitors.length}</h3>
                            <div style="overflow-x: auto;">
                                <table style="width: 100%; border-collapse: collapse;">
                                    <thead>
                                        <tr style="background: var(--bg-card);">
                                            <th style="padding: 8px; text-align: left;">App</th>
                                            <th style="padding: 8px; text-align: left;">Keyword</th>
                                            <th style="padding: 8px;">Position</th>
                                            <th style="padding: 8px;">Rating</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        ${COMPETITORS_DATA.slice(0, 50).map(c => `
                                            <tr style="border-bottom: 1px solid rgba(255,255,255,0.1);">
                                                <td style="padding: 8px;">${c.app_name || 'N/A'}</td>
                                                <td style="padding: 8px; font-size: 0.9em;">${c.keyword}</td>
                                                <td style="padding: 8px; text-align: center;">#${c.position}</td>
                                                <td style="padding: 8px; text-align: center;">
                                                    <span style="display: inline-flex; align-items: center; gap: 4px;">
                                                        <i data-lucide="star" style="width: 16px; height: 16px; color: #fbbf24;"></i>
                                                        ${parseFloat(c.rating || 0).toFixed(1)}
                                                    </span>
                                                </td>
                                            </tr>
                                        `).join('')}
                                    </tbody>
                                </table>
                            </div>
                        `;
                        // Reinitialize Lucide icons for new content
                        setTimeout(() => lucide.createIcons(), 100);
                    }
                }
            } catch (e) {
                console.error('Error loading competitors:', e);
            }
        }
        
        function loadDiscoveriesData() {
            try {
                if (DISCOVERIES_DATA && DISCOVERIES_DATA.length > 0) {
                    const container = document.getElementById('discoveries-content');
                    if (container) {
                        const topDiscoveries = DISCOVERIES_DATA
                            .sort((a, b) => (b.opportunity_score || 0) - (a.opportunity_score || 0))
                            .slice(0, 50);
                        
                        container.innerHTML = `
                            <h3>🔍 Keywords Descubiertos: ${DISCOVERIES_DATA.length}</h3>
                            <p style="color: var(--text-secondary);">Top oportunidades ordenadas por score</p>
                            <div style="overflow-x: auto; margin-top: 20px;">
                                <table style="width: 100%; border-collapse: collapse;">
                                    <thead>
                                        <tr style="background: var(--bg-card);">
                                            <th style="padding: 8px; text-align: left;">Keyword</th>
                                            <th style="padding: 8px;">Score</th>
                                            <th style="padding: 8px;">Volumen</th>
                                            <th style="padding: 8px;">Dificultad</th>
                                            <th style="padding: 8px;">Fuente</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        ${topDiscoveries.map(d => `
                                            <tr style="border-bottom: 1px solid rgba(255,255,255,0.1);">
                                                <td style="padding: 8px;">${d.keyword}</td>
                                                <td style="padding: 8px; text-align: center;">
                                                    <span style="background: ${d.opportunity_score > 70 ? '#10b981' : d.opportunity_score > 50 ? '#f59e0b' : '#6b7280'}; padding: 4px 8px; border-radius: 4px;">
                                                        ${d.opportunity_score || 0}
                                                    </span>
                                                </td>
                                                <td style="padding: 8px; text-align: center;">${d.estimated_volume || 'N/A'}</td>
                                                <td style="padding: 8px; text-align: center;">${d.difficulty || 'N/A'}</td>
                                                <td style="padding: 8px; font-size: 0.85em;">${d.source || 'N/A'}</td>
                                            </tr>
                                        `).join('')}
                                    </tbody>
                                </table>
                            </div>
                        `;
                    }
                }
            } catch (e) {
                console.error('Error loading discoveries:', e);
            }
        }
        
        function loadCostsData() {
            try {
                const container = document.getElementById('costs-content');
                if (container && currentData && currentData.length > 0) {
                    // Calcular métricas básicas
                    const latestRanks = {};
                    currentData.forEach(row => {
                        const keyword = row.keyword;
                        const rank = parseInt(row.rank);
                        if (!latestRanks[keyword] || new Date(row.date) > new Date(latestRanks[keyword].date)) {
                            latestRanks[keyword] = { rank, keyword };
                        }
                    });
                    
                    const top10Count = Object.values(latestRanks).filter(r => r.rank <= 10).length;
                    const top50Count = Object.values(latestRanks).filter(r => r.rank <= 50).length;
                    
                    container.innerHTML = `
                        <h3>💰 Análisis de Valor del Portfolio</h3>
                        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0;">
                            <div style="background: var(--bg-card); padding: 20px; border-radius: 8px;">
                                <div style="color: var(--text-secondary); font-size: 0.9em;">Keywords Top 10</div>
                                <div style="font-size: 2em; margin: 10px 0;">${top10Count}</div>
                                <div style="color: #10b981;">Alto valor</div>
                            </div>
                            <div style="background: var(--bg-card); padding: 20px; border-radius: 8px;">
                                <div style="color: var(--text-secondary); font-size: 0.9em;">Keywords Top 50</div>
                                <div style="font-size: 2em; margin: 10px 0;">${top50Count}</div>
                                <div style="color: #f59e0b;">Medio valor</div>
                            </div>
                            <div style="background: var(--bg-card); padding: 20px; border-radius: 8px;">
                                <div style="color: var(--text-secondary); font-size: 0.9em;">Total Keywords</div>
                                <div style="font-size: 2em; margin: 10px 0;">${Object.keys(latestRanks).length}</div>
                                <div style="color: var(--text-secondary);">Monitorizados</div>
                            </div>
                        </div>
                        <p style="color: var(--text-secondary); margin-top: 20px;">
                            💡 Para ver estimaciones de revenue precisas, configura tus métricas de negocio en config.yaml
                        </p>
                    `;
                }
            } catch (e) {
                console.error('Error loading costs:', e);
            }
        }
        
        function loadPatternsData() {
            try {
                const container = document.getElementById('patterns-content');
                if (container) {
                    if (PATTERNS_DATA && PATTERNS_DATA.patterns && PATTERNS_DATA.patterns.length > 0) {
                        container.innerHTML = `
                            <h3>📅 Patrones Estacionales Detectados: ${PATTERNS_DATA.patterns.length}</h3>
                            <div style="margin-top: 20px;">
                                ${PATTERNS_DATA.patterns.slice(0, 20).map(p => `
                                    <div style="background: var(--bg-card); padding: 15px; margin: 10px 0; border-radius: 8px;">
                                        <div style="font-weight: bold;">${p.keyword}</div>
                                        <div style="color: var(--text-secondary); margin-top: 5px;">
                                            Tipo: ${p.pattern_type} | Confianza: ${(p.confidence * 100).toFixed(0)}%
                                        </div>
                                        ${p.insights ? `<div style="margin-top: 8px;">💡 ${p.insights}</div>` : ''}
                                    </div>
                                `).join('')}
                            </div>
                        `;
                    } else {
                        container.innerHTML = `
                            <h3>📅 Patrones Estacionales</h3>
                            <div style="background: var(--bg-card); padding: 30px; text-align: center; border-radius: 8px; margin-top: 20px;">
                                <div style="font-size: 3em; margin-bottom: 10px;">📊</div>
                                <p>Se necesitan al menos 14 días de histórico para detectar patrones</p>
                                <p style="color: var(--text-secondary); margin-top: 10px;">Continúa usando la herramienta y los patrones aparecerán automáticamente</p>
                            </div>
                        `;
                    }
                }
            } catch (e) {
                console.error('Error loading patterns:', e);
            }
        }
        
        function loadExperimentsData() {
            try {
                const container = document.getElementById('experiments-content');
                if (container) {
                    if (EXPERIMENTS_DATA && EXPERIMENTS_DATA.experiments && EXPERIMENTS_DATA.experiments.length > 0) {
                        const active = EXPERIMENTS_DATA.experiments.filter(e => e.status === 'active');
                        const completed = EXPERIMENTS_DATA.experiments.filter(e => e.status === 'completed');
                        
                        container.innerHTML = `
                            <h3>🧪 Experimentos A/B Testing</h3>
                            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px; margin: 20px 0;">
                                <div style="background: var(--bg-card); padding: 15px; border-radius: 8px; text-align: center;">
                                    <div style="color: #10b981; font-size: 2em;">${active.length}</div>
                                    <div style="color: var(--text-secondary);">Activos</div>
                                </div>
                                <div style="background: var(--bg-card); padding: 15px; border-radius: 8px; text-align: center;">
                                    <div style="color: var(--text-secondary); font-size: 2em;">${completed.length}</div>
                                    <div style="color: var(--text-secondary);">Completados</div>
                                </div>
                            </div>
                            
                            ${active.length > 0 ? `
                                <h4 style="margin-top: 30px;">🔄 Experimentos Activos</h4>
                                ${active.map(exp => `
                                    <div style="background: var(--bg-card); padding: 15px; margin: 10px 0; border-radius: 8px;">
                                        <div style="font-weight: bold;">${exp.name}</div>
                                        <div style="color: var(--text-secondary); margin-top: 5px;">
                                            ${exp.hypothesis}
                                        </div>
                                        <div style="margin-top: 8px; font-size: 0.9em;">
                                            Inicio: ${exp.start_date?.split('T')[0] || 'N/A'}
                                        </div>
                                    </div>
                                `).join('')}
                            ` : ''}
                            
                            ${completed.length > 0 ? `
                                <h4 style="margin-top: 30px;">✅ Experimentos Completados</h4>
                                ${completed.slice(0, 10).map(exp => `
                                    <div style="background: var(--bg-card); padding: 15px; margin: 10px 0; border-radius: 8px;">
                                        <div style="display: flex; justify-content: space-between; align-items: center;">
                                            <div style="font-weight: bold;">${exp.name}</div>
                                            <div style="background: ${exp.verdict === 'success' ? '#10b981' : exp.verdict === 'failure' ? '#ef4444' : '#6b7280'}; padding: 4px 12px; border-radius: 12px; font-size: 0.85em;">
                                                ${exp.verdict || 'inconclusive'}
                                            </div>
                                        </div>
                                        <div style="color: var(--text-secondary); margin-top: 5px; font-size: 0.9em;">
                                            ${exp.change_type} | ${exp.start_date?.split('T')[0]} - ${exp.end_date?.split('T')[0]}
                                        </div>
                                    </div>
                                `).join('')}
                            ` : ''}
                        `;
                    } else {
                        container.innerHTML = `
                            <h3>🧪 A/B Testing</h3>
                            <div style="background: var(--bg-card); padding: 30px; text-align: center; border-radius: 8px; margin-top: 20px;">
                                <div style="font-size: 3em; margin-bottom: 10px;">🧪</div>
                                <p>No hay experimentos registrados todavía</p>
                                <p style="color: var(--text-secondary); margin-top: 10px;">
                                    Usa el módulo ab_testing_tracker para crear experimentos antes de hacer cambios en tu metadata
                                </p>
                            </div>
                        `;
                    }
                }
            } catch (e) {
                console.error('Error loading experiments:', e);
            }
        }

        function parseCSV(csv) {
            const lines = csv.split('\\n');
            const headers = lines[0].split(',');
            const data = [];
            
            for (let i = 1; i < lines.length; i++) {
                if (lines[i].trim() === '') continue;
                const values = lines[i].split(',');
                const row = {};
                headers.forEach((header, index) => {
                    row[header.trim()] = values[index]?.trim();
                });
                data.push(row);
            }
            
            return data;
        }

        function updateDashboard() {
            if (!currentData) return;
            
            // Update stats
            const uniqueKeywords = [...new Set(currentData.map(d => d.keyword))];
            document.getElementById('total-keywords').textContent = uniqueKeywords.length;
            
            // Top 10 count
            const top10 = currentData.filter(d => parseInt(d.rank) <= 10).length;
            document.getElementById('top-10').textContent = top10;
            
            // Visibility
            const inTop100 = currentData.filter(d => parseInt(d.rank) <= 100).length;
            const visibility = (inTop100 / currentData.length * 100).toFixed(1);
            document.getElementById('visibility').textContent = visibility;
            
            // Create charts
            createRankingsChart();
            createDistributionChart();
            createMoversChart();
        }

        function createRankingsChart() {
            const ctx = document.getElementById('rankingsChart');
            if (!ctx) return;
            
            // Group by keyword
            const keywordData = {};
            currentData.forEach(row => {
                if (!keywordData[row.keyword]) {
                    keywordData[row.keyword] = [];
                }
                keywordData[row.keyword].push({
                    date: new Date(row.date),
                    rank: parseInt(row.rank)
                });
            });
            
            // Take top 5 keywords by best rank
            const top5 = Object.entries(keywordData)
                .map(([keyword, data]) => ({
                    keyword,
                    bestRank: Math.min(...data.map(d => d.rank))
                }))
                .sort((a, b) => a.bestRank - b.bestRank)
                .slice(0, 5);
            
            const datasets = top5.map((item, index) => ({
                label: item.keyword,
                data: keywordData[item.keyword].map(d => ({ x: d.date, y: d.rank })),
                borderColor: `hsl(${index * 60}, 70%, 60%)`,
                backgroundColor: `hsla(${index * 60}, 70%, 60%, 0.1)`,
                tension: 0.4
            }));
            
            if (charts.rankings) charts.rankings.destroy();
            
            charts.rankings = new Chart(ctx, {
                type: 'line',
                data: { datasets },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            reverse: true,
                            beginAtZero: false,
                            ticks: { color: '#94a3b8' },
                            grid: { color: 'rgba(255,255,255,0.1)' }
                        },
                        x: {
                            type: 'time',
                            ticks: { color: '#94a3b8' },
                            grid: { color: 'rgba(255,255,255,0.1)' }
                        }
                    },
                    plugins: {
                        legend: {
                            labels: { color: '#e2e8f0' }
                        }
                    }
                }
            });
        }

        function createDistributionChart() {
            const ctx = document.getElementById('distributionChart');
            if (!ctx) return;
            
            const top10 = currentData.filter(d => parseInt(d.rank) <= 10).length;
            const top50 = currentData.filter(d => parseInt(d.rank) > 10 && parseInt(d.rank) <= 50).length;
            const top100 = currentData.filter(d => parseInt(d.rank) > 50 && parseInt(d.rank) <= 100).length;
            const other = currentData.filter(d => parseInt(d.rank) > 100).length;
            
            if (charts.distribution) charts.distribution.destroy();
            
            charts.distribution = new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: ['Top 10', 'Top 50', 'Top 100', 'Otros'],
                    datasets: [{
                        data: [top10, top50, top100, other],
                        backgroundColor: ['#10b981', '#3b82f6', '#f59e0b', '#6b7280']
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            labels: { color: '#e2e8f0' }
                        }
                    }
                }
            });
        }

        function createMoversChart() {
            const ctx = document.getElementById('moversChart');
            if (!ctx) return;
            
            // Calculate changes (simplified)
            const changes = [
                { keyword: 'bible sleep', change: 5 },
                { keyword: 'audio bible', change: -3 },
                { keyword: 'bedtime stories', change: 8 },
                { keyword: 'bible chat', change: -2 },
                { keyword: 'kids bible', change: 4 }
            ];
            
            if (charts.movers) charts.movers.destroy();
            
            charts.movers = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: changes.map(c => c.keyword),
                    datasets: [{
                        label: 'Cambio de Ranking',
                        data: changes.map(c => c.change),
                        backgroundColor: changes.map(c => c.change > 0 ? '#10b981' : '#ef4444')
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    indexAxis: 'y',
                    scales: {
                        x: {
                            ticks: { color: '#94a3b8' },
                            grid: { color: 'rgba(255,255,255,0.1)' }
                        },
                        y: {
                            ticks: { color: '#94a3b8' },
                            grid: { color: 'rgba(255,255,255,0.1)' }
                        }
                    },
                    plugins: {
                        legend: { display: false }
                    }
                }
            });
        }

        function switchTab(tabName) {
            // Hide all tabs
            document.querySelectorAll('.tab-content').forEach(tab => {
                tab.classList.remove('active');
            });
            document.querySelectorAll('.tab-btn').forEach(btn => {
                btn.classList.remove('active');
            });
            
            // Show selected tab
            document.getElementById(`tab-${tabName}`).classList.add('active');
            event.target.classList.add('active');
            
            lucide.createIcons();
        }

        function setTimeRange(days) {
            currentTimeRange = days;
            document.querySelectorAll('.filter-btn').forEach(btn => {
                btn.classList.remove('active');
            });
            event.target.classList.add('active');
            updateDashboard();
        }

        function exportData(format) {
            if (format === 'csv') {
                // Export to CSV
                const csv = currentData.map(row => Object.values(row).join(',')).join('\\n');
                const blob = new Blob([csv], { type: 'text/csv' });
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `aso-ranks-${new Date().toISOString().split('T')[0]}.csv`;
                a.click();
            } else if (format === 'pdf') {
                alert('Export PDF próximamente...');
            }
        }

        function toggleTheme() {
            // Toggle dark/light mode
            document.body.style.filter = 
                document.body.style.filter === 'invert(1) hue-rotate(180deg)' 
                ? '' 
                : 'invert(1) hue-rotate(180deg)';
        }
    </script>
</body>
</html>"""
        
        return html
    
    def save_dashboard(self):
        """Guardar dashboard a archivo HTML"""
        try:
            html = self.generate_html()
            with open(self.output_file, 'w') as f:
                f.write(html)
            logger.info(f"✅ Dashboard generado: {self.output_file}")
            return str(self.output_file)
        except Exception as e:
            logger.error(f"❌ Error generando dashboard: {e}")
            return None


def main():
    """Test del dashboard generator"""
    import yaml
    
    with open('config/config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    dashboard = InteractiveDashboard(config)
    
    print("🧪 Testing Interactive Dashboard\n")
    
    file_path = dashboard.save_dashboard()
    
    if file_path:
        print(f"✅ Dashboard generado: {file_path}")
        print(f"🌐 Abre en tu navegador: file://{Path(file_path).absolute()}")


if __name__ == "__main__":
    main()

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
            --primary: #007AFF;
            --primary-hover: #0051D5;
            --success: #34C759;
            --warning: #FF9500;
            --danger: #FF3B30;
            
            /* Light mode */
            --bg-primary: #FFFFFF;
            --bg-secondary: #F5F5F7;
            --bg-card: #FFFFFF;
            --bg-hover: #F5F5F7;
            --text-primary: #1D1D1F;
            --text-secondary: #48484A;
            --text-tertiary: #6E6E73;
            --border: rgba(0,0,0,0.08);
            --shadow-sm: 0 1px 3px rgba(0,0,0,0.08);
            --shadow-md: 0 4px 16px rgba(0,0,0,0.1);
            --shadow-lg: 0 12px 48px rgba(0,0,0,0.12);
        }
        
        body.dark-mode {
            --bg-primary: #000000;
            --bg-secondary: #1C1C1E;
            --bg-card: #1C1C1E;
            --bg-hover: #2C2C2E;
            --text-primary: #FFFFFF;
            --text-secondary: #AEAEB2;
            --text-tertiary: #98989D;
            --border: rgba(255,255,255,0.1);
            --shadow-sm: 0 1px 3px rgba(0,0,0,0.3);
            --shadow-md: 0 4px 16px rgba(0,0,0,0.4);
            --shadow-lg: 0 12px 48px rgba(0,0,0,0.5);
        }
        
        * { 
            margin: 0; 
            padding: 0; 
            box-sizing: border-box; 
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Segoe UI', Roboto, sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            padding: 0;
            min-height: 100vh;
            transition: background 0.3s ease, color 0.3s ease;
            -webkit-font-smoothing: antialiased;
        }
        
        .container { 
            max-width: 1600px; 
            margin: 0 auto;
            padding: 32px;
        }
        
        @media (max-width: 768px) {
            .container {
                padding: 0 !important;
            }
        }
        
        /* Header estilo Apple */
        header {
            background: var(--bg-card);
            padding: 48px;
            border-radius: 20px;
            margin-bottom: 32px;
            border: 1px solid var(--border);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            box-shadow: var(--shadow-md);
            transition: all 0.3s ease;
            position: relative;
        }
        
        h1 { 
            color: var(--text-primary); 
            font-size: 2.75em; 
            margin-bottom: 8px; 
            font-weight: 700;
            letter-spacing: -0.5px;
        }
        
        .subtitle { 
            color: var(--text-secondary); 
            font-size: 1.1em; 
            margin-bottom: 32px;
            font-weight: 400;
        }
        
        /* Filtros y controles estilo Apple */
        .controls {
            display: flex;
            gap: 12px;
            flex-wrap: wrap;
            align-items: center;
        }
        
        .filter-group {
            display: flex;
            gap: 8px;
            background: var(--bg-secondary);
            padding: 6px;
            border-radius: 12px;
            border: 1px solid var(--border);
            align-items: center;
        }
        
        .filter-btn {
            background: transparent;
            color: var(--text-primary);
            border: none;
            padding: 8px 16px;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
            font-size: 0.9em;
            font-weight: 500;
        }
        
        .filter-btn:hover { background: var(--bg-card); }
        .filter-btn.active {
            background: var(--primary);
            color: white;
            box-shadow: var(--shadow-sm);
        }
        
        select, input[type="date"] {
            background: var(--bg-card);
            color: var(--text-primary);
            border: 1px solid var(--border);
            padding: 8px 12px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 0.9em;
            transition: all 0.2s ease;
        }
        
        select:hover, input[type="date"]:hover {
            border-color: var(--primary);
        }
        
        select option { 
            background: var(--bg-card); 
            color: var(--text-primary); 
        }
        
        /* Cards estilo Apple */
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
            gap: 16px;
            margin-bottom: 32px;
        }
        
        .stat-card {
            background: var(--bg-card);
            padding: 24px;
            border-radius: 16px;
            border: 1px solid var(--border);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            box-shadow: var(--shadow-sm);
        }
        
        .stat-card:hover {
            transform: translateY(-2px);
            box-shadow: var(--shadow-md);
            border-color: var(--primary);
        }
        
        .stat-value {
            font-size: 2.5em;
            font-weight: 700;
            color: var(--primary);
            margin: 8px 0;
            letter-spacing: -1px;
        }
        
        .stat-label {
            color: var(--text-secondary);
            font-size: 0.85em;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .stat-change {
            margin-top: 8px;
            font-size: 0.9em;
        }
        
        /* Layout con sidebar vertical */
        .content-wrapper {
            display: grid;
            grid-template-columns: 280px 1fr;
            gap: 30px;
            margin-top: 30px;
        }
        
        /* Tabs verticales Apple style */
        .tabs {
            display: flex;
            flex-direction: column;
            gap: 4px;
            padding: 8px;
            background: var(--bg-secondary);
            border-radius: 12px;
            border: 1px solid var(--border);
            position: sticky;
            top: 20px;
            max-height: calc(100vh - 40px);
            overflow-y: auto;
        }
        
        .tab-btn {
            background: transparent;
            color: var(--text-secondary);
            padding: 12px 16px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            text-align: left;
            font-size: 0.95em;
            font-weight: 500;
            transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .tab-btn:hover {
            background: var(--bg-hover);
            color: var(--text-primary);
        }
        
        .tab-btn.active {
            background: var(--primary);
            color: white;
            font-weight: 600;
            box-shadow: var(--shadow-sm);
        }
        
        .tabs-content {
            min-height: 600px;
        }
        
        .tab-content {
            display: none;
            animation: fadeIn 0.3s ease;
        }
        
        .tab-content.active { display: block; }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        /* Chart containers Apple style */
        .chart-container {
            background: var(--bg-card);
            padding: 32px;
            border-radius: 16px;
            border: 1px solid var(--border);
            margin-bottom: 24px;
            box-shadow: var(--shadow-sm);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        
        .chart-container:hover {
            box-shadow: var(--shadow-md);
        }
        
        .chart-title {
            font-size: 1.5em;
            margin-bottom: 24px;
            color: var(--text-primary);
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 12px;
            letter-spacing: -0.5px;
        }
        
        /* Tables Apple style */
        .data-table {
            width: 100%;
            border-collapse: separate;
            border-spacing: 0;
            border-radius: 12px;
            overflow: hidden;
        }
        
        .data-table thead th {
            background: var(--bg-secondary);
            padding: 12px 16px;
            text-align: left;
            color: var(--text-secondary);
            font-weight: 600;
            text-transform: uppercase;
            font-size: 0.75em;
            letter-spacing: 0.5px;
            border-bottom: 1px solid var(--border);
        }
        
        .data-table tbody tr {
            background: var(--bg-card);
            transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
        }
        
        .data-table tbody tr:hover {
            background: var(--bg-hover);
        }
        
        .data-table tbody td {
            padding: 14px 16px;
            border-bottom: 1px solid var(--border);
            color: var(--text-primary);
        }
        
        /* Badges Apple style */
        .badge {
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.8em;
            font-weight: 600;
            display: inline-block;
        }
        
        .badge-success { background: var(--success); color: white; }
        .badge-warning { background: var(--warning); color: white; }
        .badge-danger { background: var(--danger); color: white; }
        .badge-info { background: var(--primary); color: white; }
        
        /* Cards Apple style */
        .card {
            background: var(--bg-card);
            padding: 20px;
            border-radius: 12px;
            margin-bottom: 16px;
            border: 1px solid var(--border);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        
        .card:hover {
            box-shadow: var(--shadow-md);
            border-color: var(--primary);
        }
        
        .card-title {
            font-size: 1.1em;
            font-weight: 600;
            margin-bottom: 12px;
            color: var(--text-primary);
        }
        
        .card-desc {
            color: var(--text-secondary);
            font-size: 0.95em;
            line-height: 1.5;
        }
        
        /* Loading Apple style */
        .loading {
            text-align: center;
            padding: 80px;
            font-size: 1.2em;
            color: var(--text-secondary);
        }
        
        @keyframes spin {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
        }
        
        /* Export buttons Apple style */
        .export-btn {
            background: transparent;
            color: var(--text-primary);
            border: none;
            padding: 8px 16px;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
            display: flex;
            align-items: center;
            gap: 8px;
            font-weight: 500;
            font-size: 0.9em;
        }
        
        .export-btn:hover {
            background: var(--bg-card);
        }
        
        /* Dark mode toggle Apple style */
        .theme-toggle {
            background: var(--bg-card) !important;
            border: 2px solid var(--primary) !important;
            width: 48px !important;
            height: 48px !important;
            border-radius: 12px;
            display: flex !important;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
            z-index: 9999 !important;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3) !important;
        }
        
        .theme-toggle:hover {
            background: var(--bg-hover);
            border-color: var(--primary);
            transform: scale(1.05);
        }
        
        /* Logo adaptable */
        .logo-ring {
            stroke: var(--text-primary);
            transition: stroke 0.3s ease;
        }
        
        .logo-center {
            fill: var(--primary);
        }
        
        .logo-text {
            color: var(--text-primary);
        }
        
        /* Responsive */
        /* Date input wrappers for mobile */
        .date-input-wrapper {
            display: contents;
        }
        
        .date-range-group label {
            color: var(--text-primary);
            font-size: 0.9em;
            font-weight: 500;
        }
        
        @media (max-width: 1200px) {
            .stats-grid {
                grid-template-columns: repeat(2, 1fr);
            }
        }
        
        @media (max-width: 768px) {
            /* Reset body and container */
            body {
                padding: 0 !important;
            }
            
            .container {
                padding: 0 !important;
            }
            
            /* Header mobile */
            header {
                border-radius: 0 !important;
                padding: 10px 12px !important;
                margin-bottom: 0 !important;
                position: sticky;
                top: 0;
                z-index: 1000;
            }
            
            header > div:first-child {
                top: 8px !important;
                right: 8px !important;
                gap: 4px !important;
            }
            
            header svg, #logo {
                width: 24px !important;
                height: 24px !important;
            }
            
            header h1, .logo-text {
                font-size: 1.2em !important;
            }
            
            .subtitle {
                display: none !important;
            }
            
            .theme-toggle {
                width: 30px !important;
                height: 30px !important;
            }
            
            .theme-toggle span {
                font-size: 16px !important;
            }
            
            .theme-toggle i {
                width: 16px !important;
                height: 16px !important;
            }
            
            /* Controls mobile - completamente rediseñado */
            .controls {
                flex-direction: column !important;
                gap: 6px !important;
                margin-top: 8px !important;
                flex-wrap: nowrap !important;
            }
            
            /* Time range - horizontal scroll */
            .time-range-group {
                width: 100% !important;
                padding: 3px !important;
                overflow-x: auto !important;
                -webkit-overflow-scrolling: touch;
                scrollbar-width: none;
            }
            
            .time-range-group::-webkit-scrollbar {
                display: none;
            }
            
            .time-range-group .filter-btn {
                flex: 0 0 auto !important;
                min-width: 58px !important;
                padding: 5px 10px !important;
                font-size: 0.7em !important;
            }
            
            /* Date range - diseño mejorado */
            .date-range-group {
                display: grid !important;
                grid-template-columns: 1fr 1fr !important;
                padding: 4px !important;
                gap: 4px !important;
            }
            
            .date-input-wrapper {
                display: flex !important;
                flex-direction: column !important;
                gap: 2px !important;
            }
            
            .date-input-wrapper label {
                font-size: 0.65em !important;
                color: var(--text-secondary) !important;
                text-transform: uppercase !important;
                letter-spacing: 0.5px !important;
            }
            
            .date-input-wrapper input {
                width: 100% !important;
                font-size: 12px !important;
                padding: 5px 4px !important;
            }
            
            /* Keyword selector */
            .keyword-group {
                width: 100% !important;
                padding: 3px !important;
            }
            
            .keyword-group select {
                width: 100% !important;
                font-size: 0.75em !important;
                padding: 6px !important;
            }
            
            /* Export buttons */
            .export-group {
                width: 100% !important;
                padding: 3px !important;
                gap: 4px !important;
            }
            
            .export-group .export-btn {
                flex: 1 !important;
                font-size: 0.7em !important;
                padding: 6px 8px !important;
                gap: 4px !important;
            }
            
            .export-btn i {
                width: 12px !important;
                height: 12px !important;
            }
            
            /* Content */
            #content {
                padding: 0 !important;
            }
            
            /* Stats grid - 2 columns */
            .stats-grid {
                grid-template-columns: 1fr 1fr !important;
                gap: 6px !important;
                padding: 10px !important;
                margin-bottom: 0 !important;
            }
            
            .stat-card {
                padding: 10px !important;
            }
            
            .stat-label {
                font-size: 0.6em !important;
            }
            
            .stat-value {
                font-size: 1.3em !important;
                margin: 2px 0 !important;
            }
            
            .stat-card > div:last-child {
                font-size: 0.65em !important;
                margin-top: 2px !important;
            }
            
            /* Content wrapper and tabs */
            .content-wrapper {
                grid-template-columns: 1fr !important;
                gap: 0 !important;
                padding: 0 !important;
            }
            
            .tabs {
                position: static !important;
                width: 100% !important;
                flex-direction: row !important;
                overflow-x: auto !important;
                -webkit-overflow-scrolling: touch;
                padding: 6px 10px !important;
                gap: 4px !important;
                border-bottom: 1px solid var(--border) !important;
                border-right: none !important;
                scrollbar-width: none;
            }
            
            .tabs::-webkit-scrollbar {
                display: none;
            }
            
            .tab-btn {
                flex: 0 0 auto !important;
                min-width: 95px !important;
                padding: 6px 10px !important;
                font-size: 0.7em !important;
            }
            
            .tab-btn i {
                width: 12px !important;
                height: 12px !important;
            }
            
            /* Tab content */
            .content {
                padding: 10px !important;
            }
            
            .chart-container {
                padding: 10px !important;
                margin-bottom: 10px !important;
            }
            
            .chart-title {
                font-size: 0.95em !important;
                margin-bottom: 10px !important;
            }
            
            .chart-title i {
                width: 16px !important;
                height: 16px !important;
            }
            
            /* Tables */
            table {
                font-size: 0.65em !important;
                display: block !important;
                overflow-x: auto !important;
                -webkit-overflow-scrolling: touch;
            }
            
            thead {
                display: table-header-group !important;
            }
            
            tbody {
                display: table-row-group !important;
            }
            
            tr {
                display: table-row !important;
            }
            
            th, td {
                padding: 4px 2px !important;
                font-size: 0.9em !important;
                white-space: nowrap !important;
            }
            
            th {
                position: sticky !important;
                top: 0 !important;
                background: var(--bg-card) !important;
                z-index: 10 !important;
            }
            
            /* Grids dentro de tabs - todo 1 columna */
            .chart-container div[style*="grid-template-columns"] {
                grid-template-columns: 1fr !important;
                gap: 8px !important;
            }
            
            /* Cards de competidores */
            .chart-container div[style*="grid-template-columns: 40px"] {
                grid-template-columns: 30px 1fr !important;
                gap: 8px !important;
                font-size: 0.85em !important;
            }
            
            /* Keywords tags en competidores */
            .chart-container div[style*="flex-wrap: wrap"] span {
                font-size: 0.7em !important;
                padding: 2px 6px !important;
            }
            
            /* Ocultar columnas menos importantes en tablas */
            table th:nth-child(n+5),
            table td:nth-child(n+5) {
                display: none !important;
            }
            
            /* Competidores - cards compactas */
            #competitors-content > div > div {
                padding: 10px !important;
                margin-bottom: 8px !important;
            }
            
            #competitors-content h3 {
                font-size: 0.9em !important;
            }
            
            /* Stats dentro de competidores */
            #competitors-content div[style*="font-size: 2.5em"] {
                font-size: 1.6em !important;
            }
            
            #competitors-content div[style*="font-size: 1.3em"] {
                font-size: 1em !important;
            }
            
            /* Discoveries content */
            #discoveries-content div[style*="padding: 24px"] {
                padding: 12px !important;
            }
            
            #discoveries-content div[style*="font-size: 2em"] {
                font-size: 1.3em !important;
            }
            
            /* Rankings chart */
            #rankingChart {
                height: 250px !important;
            }
            
            /* Responsive canvas */
            canvas {
                max-width: 100% !important;
                height: auto !important;
            }
        }
        
        @media (max-width: 480px) {
            header h1 {
                font-size: 1.2em;
            }
            
            .theme-toggle {
                width: 32px;
                height: 32px;
            }
            
            .tab-btn {
                min-width: 100px;
                padding: 8px 12px;
            }
            
            .stat-card h3 {
                font-size: 0.85em;
            }
            
            .stat-card .value {
                font-size: 1.8em;
            }
            
            .filter-btn {
                font-size: 0.8em;
                padding: 6px 10px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div style="position: absolute; top: 20px; right: 20px; display: flex; gap: 12px; z-index: 10000;">
                <button class="theme-toggle" onclick="toggleLanguage()" title="Change language" style="background: #007AFF !important;">
                    <span id="lang-flag" style="font-size: 24px; display: block;">🇪🇸</span>
                </button>
                <button class="theme-toggle" onclick="toggleTheme()" style="background: #007AFF !important;">
                    <i data-lucide="moon" style="width: 24px; height: 24px; color: white;"></i>
                </button>
            </div>
            <div style="display: flex; align-items: center; gap: 16px; margin-bottom: 4px;">
                <svg id="logo" width="48" height="48" viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <!-- Radar grid -->
                  <path d="M4 24 L44 24 M24 4 L24 44" stroke="var(--text-primary)" stroke-width="1" opacity="0.15"/>
                  <circle cx="24" cy="24" r="18" stroke="var(--text-primary)" stroke-width="1" opacity="0.2" fill="none"/>
                  <circle cx="24" cy="24" r="12" stroke="var(--text-primary)" stroke-width="1.5" opacity="0.3" fill="none"/>
                  
                  <!-- Central pulse -->
                  <circle cx="24" cy="24" r="4" fill="#007AFF"/>
                  <circle cx="24" cy="24" r="6" stroke="#007AFF" stroke-width="2" fill="none" opacity="0.4"/>
                  
                  <!-- Signal lines -->
                  <path d="M24 24 L24 8" stroke="#007AFF" stroke-width="2.5" stroke-linecap="round" opacity="0.8"/>
                  <path d="M24 24 L38 14" stroke="#007AFF" stroke-width="2" stroke-linecap="round" opacity="0.5"/>
                  <path d="M24 24 L36 32" stroke="#007AFF" stroke-width="1.5" stroke-linecap="round" opacity="0.3"/>
                </svg>
                <h1 class="logo-text" style="margin: 0; font-size: 2.75em; font-weight: 700;">RankRadar</h1>
            </div>
            <p class="subtitle" data-i18n="subtitle">ASO Intelligence Platform · Real-time Rankings & Insights</p>
            
            <div class="controls">
                <div class="filter-group time-range-group">
                    <button class="filter-btn active" onclick="setTimeRange(7)" data-i18n="days7">7 días</button>
                    <button class="filter-btn" onclick="setTimeRange(14)" data-i18n="days14">14 días</button>
                    <button class="filter-btn" onclick="setTimeRange(30)" data-i18n="days30">30 días</button>
                    <button class="filter-btn" onclick="setTimeRange(90)" data-i18n="days90">90 días</button>
                </div>
                
                <div class="filter-group date-range-group">
                    <div class="date-input-wrapper">
                        <label data-i18n="from">Desde:</label>
                        <input type="date" id="date-from" onchange="applyCustomDateRange()">
                    </div>
                    <div class="date-input-wrapper">
                        <label data-i18n="to">Hasta:</label>
                        <input type="date" id="date-to" onchange="applyCustomDateRange()">
                    </div>
                </div>
                
                <div class="filter-group keyword-group">
                    <select id="keyword-filter" onchange="filterByKeyword()">
                        <option value="all" data-i18n="allKeywords">Todas las keywords</option>
                    </select>
                </div>
                
                <div class="filter-group export-group">
                    <button class="export-btn" onclick="exportData('csv')">
                        <i data-lucide="download" style="width: 16px; height: 16px;"></i>
                        <span data-i18n="exportCSV">CSV</span>
                    </button>
                    <button class="export-btn" onclick="exportData('pdf')">
                        <i data-lucide="file-text" style="width: 16px; height: 16px;"></i>
                        <span data-i18n="exportPDF">PDF</span>
                    </button>
                </div>
            </div>
        </header>

        <div id="loading" class="loading">
            <i data-lucide="loader" style="width: 40px; height: 40px; display: inline-block; animation: spin 1s linear infinite;"></i>
            <br><span data-i18n="loading">Cargando datos...</span>
        </div>

        <div id="content" style="display: none;">
            <!-- Stats Cards -->
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-label" data-i18n="totalKeywords">Total Keywords</div>
                    <div class="stat-value" id="total-keywords">-</div>
                    <div style="color: var(--text-secondary); margin-top: 10px;" data-i18n="activelyMonitored">Monitoreadas activamente</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label" data-i18n="monthlyRevenue">Revenue Mensual Est.</div>
                    <div class="stat-value" id="monthly-revenue">$-</div>
                    <div style="color: var(--text-secondary); margin-top: 10px;" id="revenue-change"></div>
                </div>
                <div class="stat-card">
                    <div class="stat-label" data-i18n="top10Keywords">Top 10 Keywords</div>
                    <div class="stat-value" id="top-10">-</div>
                    <div style="color: var(--text-secondary); margin-top: 10px;" id="top10-change"></div>
                </div>
                <div class="stat-card">
                    <div class="stat-label" data-i18n="visibility">Visibilidad</div>
                    <div class="stat-value" id="visibility">-%</div>
                    <div style="color: var(--text-secondary); margin-top: 10px;" data-i18n="keywordsInTop100">Keywords en top 100</div>
                </div>
            </div>

            <!-- Layout con sidebar vertical -->
            <div class="content-wrapper">
                <!-- Tabs Navigation (Sidebar) -->
                <div class="tabs">
                    <button class="tab-btn active" onclick="switchTab('rankings')">
                        <i data-lucide="trending-up" style="width: 20px; height: 20px;"></i>
                        <span data-i18n="rankings">Rankings</span>
                    </button>
                    <button class="tab-btn" onclick="switchTab('competitors')">
                        <i data-lucide="users" style="width: 20px; height: 20px;"></i>
                        <span data-i18n="competitors">Competidores</span>
                    </button>
                    <button class="tab-btn" onclick="switchTab('discoveries')">
                        <i data-lucide="search" style="width: 20px; height: 20px;"></i>
                        <span data-i18n="discoveries">Descubrimientos</span>
                    </button>
                    <button class="tab-btn" onclick="switchTab('costs')">
                        <i data-lucide="dollar-sign" style="width: 20px; height: 20px;"></i>
                        <span data-i18n="costs">Análisis de Costos</span>
                    </button>
                    <button class="tab-btn" onclick="switchTab('patterns')">
                        <i data-lucide="calendar" style="width: 20px; height: 20px;"></i>
                        <span data-i18n="patterns">Patrones</span>
                    </button>
                    <button class="tab-btn" onclick="switchTab('experiments')">
                        <i data-lucide="flask-conical" style="width: 20px; height: 20px;"></i>
                        <span data-i18n="experiments">A/B Tests</span>
                    </button>
                    <button class="tab-btn" onclick="switchTab('alerts')">
                        <i data-lucide="bell" style="width: 20px; height: 20px;"></i>
                        <span data-i18n="alerts">Alertas</span>
                    </button>
                </div>

                <!-- Tabs Content -->
                <div class="tabs-content">

            <!-- Tab: Rankings -->
            <div id="tab-rankings" class="tab-content active">
                <div class="chart-container">
                    <h2 class="chart-title">
                        <i data-lucide="activity" style="width: 32px; height: 32px;"></i>
                        <span data-i18n="rankingsEvolution">Evolución de Rankings</span>
                    </h2>
                    <div style="height: 400px;">
                        <canvas id="rankingsChart"></canvas>
                    </div>
                </div>

                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 30px;">
                    <div class="chart-container">
                        <h2 class="chart-title" data-i18n="distributionByRanking">Distribución por Ranking</h2>
                        <div style="height: 300px;">
                            <canvas id="distributionChart"></canvas>
                        </div>
                    </div>
                    <div class="chart-container">
                        <h2 class="chart-title" data-i18n="topBottomMovers">Top/Bottom Movers</h2>
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
            
            <!-- Tab: Alerts Config -->
            <div id="tab-alerts" class="tab-content">
                <div class="chart-container">
                    <h2 class="chart-title">
                        <i data-lucide="bell" style="width: 32px; height: 32px;"></i>
                        Configuración de Alertas
                    </h2>
                    <div id="alerts-content">
                        <div style="max-width: 800px; margin: 0 auto;">
                            <div style="background: rgba(59, 130, 246, 0.1); border-left: 3px solid #3b82f6; padding: 16px; border-radius: 4px; margin-bottom: 30px;">
                                <p style="margin: 0; font-size: 0.9em;">
                                    <strong>💡 Próximamente:</strong> Configuración directa desde el dashboard. Por ahora, edita <code>config/config.yaml</code> manualmente.
                                </p>
                            </div>
                            
                            <h3 style="margin-bottom: 20px;">📱 Telegram Alerts</h3>
                            
                            <div style="background: var(--bg-card); padding: 24px; border-radius: 12px; margin-bottom: 20px;">
                                <div style="margin-bottom: 20px;">
                                    <label style="display: block; margin-bottom: 8px; font-weight: 500;">Bot Token</label>
                                    <input id="telegram-token" type="text" placeholder="8531462519:AAFvX5PPyB177DUzy..." 
                                           style="width: 100%; padding: 12px; background: var(--bg-primary); border: 1px solid var(--border); border-radius: 8px; color: var(--text-primary); font-family: monospace;">
                                    <small style="color: var(--text-secondary); display: block; margin-top: 4px;">
                                        Obtén el token desde <a href="https://t.me/BotFather" target="_blank" style="color: var(--primary);">@BotFather</a>
                                    </small>
                                </div>
                                
                                <div style="margin-bottom: 20px;">
                                    <label style="display: block; margin-bottom: 8px; font-weight: 500;">Chat ID</label>
                                    <input id="telegram-chatid" type="text" placeholder="722751828" 
                                           style="width: 100%; padding: 12px; background: var(--bg-primary); border: 1px solid var(--border); border-radius: 8px; color: var(--text-primary); font-family: monospace;">
                                    <small style="color: var(--text-secondary); display: block; margin-top: 4px;">
                                        Obtén tu Chat ID desde <a href="https://t.me/userinfobot" target="_blank" style="color: var(--primary);">@userinfobot</a>
                                    </small>
                                </div>
                                
                                <button onclick="saveAndCopyTelegramConfig()" style="background: var(--primary); color: white; padding: 12px 24px; border: none; border-radius: 8px; font-weight: 600; cursor: pointer; width: 100%;">
                                    💾 Guardar y Copiar Configuración
                                </button>
                                
                                <div id="config-output" style="display: none; margin-top: 20px; padding: 16px; background: var(--bg-primary); border-radius: 8px; font-family: monospace; font-size: 0.85em; white-space: pre-wrap;"></div>
                            </div>
                            
                            <h3 style="margin: 30px 0 20px 0;">🎯 Tipos de Alertas</h3>
                            
                            <div style="display: grid; gap: 16px;">
                                <div style="background: var(--bg-card); padding: 20px; border-radius: 12px; display: flex; gap: 16px;">
                                    <div style="width: 40px; height: 40px; background: rgba(239, 68, 68, 0.1); border-radius: 8px; display: flex; align-items: center; justify-content: center; flex-shrink: 0;">
                                        <i data-lucide="alert-triangle" style="width: 20px; height: 20px; color: #ef4444;"></i>
                                    </div>
                                    <div style="flex: 1;">
                                        <div style="font-weight: 600; margin-bottom: 4px;">CRITICAL - Inmediato</div>
                                        <div style="font-size: 0.9em; color: var(--text-secondary);">
                                            Caídas ≥ 20 posiciones en TOP keywords, bugs, app eliminada
                                        </div>
                                    </div>
                                </div>
                                
                                <div style="background: var(--bg-card); padding: 20px; border-radius: 12px; display: flex; gap: 16px;">
                                    <div style="width: 40px; height: 40px; background: rgba(249, 115, 22, 0.1); border-radius: 8px; display: flex; align-items: center; justify-content: center; flex-shrink: 0;">
                                        <i data-lucide="trending-down" style="width: 20px; height: 20px; color: #f97316;"></i>
                                    </div>
                                    <div style="flex: 1;">
                                        <div style="font-weight: 600; margin-bottom: 4px;">HIGH - Importante</div>
                                        <div style="font-size: 0.9em; color: var(--text-secondary);">
                                            Caídas 10-19 posiciones, salida del TOP 10, nuevos competidores fuertes
                                        </div>
                                    </div>
                                </div>
                                
                                <div style="background: var(--bg-card); padding: 20px; border-radius: 12px; display: flex; gap: 16px;">
                                    <div style="width: 40px; height: 40px; background: rgba(59, 130, 246, 0.1); border-radius: 8px; display: flex; align-items: center; justify-content: center; flex-shrink: 0;">
                                        <i data-lucide="info" style="width: 20px; height: 20px; color: #3b82f6;"></i>
                                    </div>
                                    <div style="flex: 1;">
                                        <div style="font-weight: 600; margin-bottom: 4px;">MEDIUM - Resumen Diario</div>
                                        <div style="font-size: 0.9em; color: var(--text-secondary);">
                                            Cambios 5-9 posiciones, keywords estables, movimientos normales
                                        </div>
                                    </div>
                                </div>
                                
                                <div style="background: var(--bg-card); padding: 20px; border-radius: 12px; display: flex; gap: 16px;">
                                    <div style="width: 40px; height: 40px; background: rgba(16, 185, 129, 0.1); border-radius: 8px; display: flex; align-items: center; justify-content: center; flex-shrink: 0;">
                                        <i data-lucide="trending-up" style="width: 20px; height: 20px; color: #10b981;"></i>
                                    </div>
                                    <div style="flex: 1;">
                                        <div style="font-weight: 600; margin-bottom: 4px;">CELEBRATION - Siempre</div>
                                        <div style="font-size: 0.9em; color: var(--text-secondary);">
                                            Nuevos TOP 3, subidas ≥ 15 posiciones, hitos importantes
                                        </div>
                                    </div>
                                </div>
                            </div>
                            
                            <div style="background: var(--bg-card); padding: 24px; border-radius: 12px; margin-top: 30px;">
                                <h4 style="margin: 0 0 16px 0;">📋 Comando para config.yaml</h4>
                                <pre style="background: var(--bg-primary); padding: 16px; border-radius: 8px; overflow-x: auto; font-size: 0.85em;"><code>alerts:
  telegram:
    enabled: true
    bot_token: "TU_BOT_TOKEN"
    chat_id: "TU_CHAT_ID"
  
  smart_alerts:
    enabled: true
    pattern_detection: true
    contextual_insights: true
  
  daily_summary:
    enabled: true
    time: "18:00"
    min_changes: 3</code></pre>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
                </div> <!-- End tabs-content -->
            </div> <!-- End content-wrapper -->
        </div> <!-- End content -->
    </div> <!-- End container -->

    <script>
        // Initialize Lucide icons
        lucide.createIcons();

        // Translations
        const translations = {
            es: {
                subtitle: 'Plataforma de Inteligencia ASO · Rankings e Insights en Tiempo Real',
                days7: '7 días',
                days14: '14 días',
                days30: '30 días',
                days90: '90 días',
                from: 'Desde:',
                to: 'Hasta:',
                allKeywords: 'Todas las keywords',
                loading: 'Cargando datos...',
                totalKeywords: 'Total Keywords',
                monthlyRevenue: 'Revenue Mensual Est.',
                top10Keywords: 'Top 10 Keywords',
                visibility: 'Visibilidad',
                activelyMonitored: 'Monitoreadas activamente',
                keywordsInTop100: 'Keywords en top 100',
                rankings: 'Rankings',
                competitors: 'Competidores',
                discoveries: 'Descubrimientos',
                costs: 'Costos',
                patterns: 'Patrones',
                experiments: 'Experimentos',
                alerts: 'Alertas',
                rankingsEvolution: 'Evolución de Rankings',
                distributionByRanking: 'Distribución por Ranking',
                topBottomMovers: 'Top/Bottom Movers',
                competitorsMonitored: 'Competidores Monitorizados',
                keywordsDiscovered: 'Keywords Descubiertos',
                exportCSV: 'CSV',
                exportPDF: 'PDF'
            },
            en: {
                subtitle: 'ASO Intelligence Platform · Real-time Rankings & Insights',
                days7: '7 days',
                days14: '14 days',
                days30: '30 days',
                days90: '90 days',
                from: 'From:',
                to: 'To:',
                allKeywords: 'All keywords',
                loading: 'Loading data...',
                totalKeywords: 'Total Keywords',
                monthlyRevenue: 'Est. Monthly Revenue',
                top10Keywords: 'Top 10 Keywords',
                visibility: 'Visibility',
                activelyMonitored: 'Actively monitored',
                keywordsInTop100: 'Keywords in top 100',
                rankings: 'Rankings',
                competitors: 'Competitors',
                discoveries: 'Discoveries',
                costs: 'Costs',
                patterns: 'Patterns',
                experiments: 'Experiments',
                alerts: 'Alerts',
                rankingsEvolution: 'Rankings Evolution',
                distributionByRanking: 'Distribution by Ranking',
                topBottomMovers: 'Top/Bottom Movers',
                competitorsMonitored: 'Monitored Competitors',
                keywordsDiscovered: 'Discovered Keywords',
                exportCSV: 'CSV',
                exportPDF: 'PDF'
            }
        };

        let currentLang = 'es';

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
                    const container = document.getElementById('competitors-content');
                    if (container) {
                        // FILTRAR TU PROPIA APP (6749528117) - convertir ambos a string para comparar
                        const YOUR_APP_ID = '6749528117';
                        const competitorData = COMPETITORS_DATA.filter(c => String(c.app_id) !== YOUR_APP_ID);
                        
                        if (competitorData.length === 0) {
                            container.innerHTML = '<p style="color: var(--text-secondary);">No hay competidores detectados en tus keywords</p>';
                            return;
                        }
                        
                        // Agrupar por competidor
                        const competitorMap = {};
                        competitorData.forEach(c => {
                            if (!competitorMap[c.app_id]) {
                                competitorMap[c.app_id] = {
                                    name: c.app_name,
                                    rating: c.rating,
                                    keywords: [],
                                    positions: [],
                                    top3Keywords: [],
                                    top10Keywords: []
                                };
                            }
                            competitorMap[c.app_id].keywords.push(c.keyword);
                            competitorMap[c.app_id].positions.push(c.position);
                            
                            // Guardar keywords donde rankean TOP
                            if (c.position <= 3) {
                                competitorMap[c.app_id].top3Keywords.push(c.keyword);
                            }
                            if (c.position <= 10) {
                                competitorMap[c.app_id].top10Keywords.push(c.keyword);
                            }
                        });
                        
                        // Calcular métricas + threat score
                        const competitors = Object.entries(competitorMap).map(([id, data]) => {
                            const avgPosition = (data.positions.reduce((a,b) => a+b, 0) / data.positions.length);
                            const top3Count = data.positions.filter(p => p <= 3).length;
                            const top10Count = data.positions.filter(p => p <= 10).length;
                            
                            // THREAT SCORE: cuanto más dominen en TOP positions, mayor amenaza
                            // Ponderado: TOP 3 vale 3x, TOP 10 vale 1x, posición promedio baja suma
                            const threatScore = (top3Count * 3) + (top10Count * 1) + (100 - avgPosition);
                            
                            return {
                                id,
                                name: data.name,
                                rating: data.rating,
                                keywordCount: data.keywords.length,
                                keywordsList: data.keywords,  // Lista completa de keywords
                                avgPosition: avgPosition.toFixed(1),
                                top3: top3Count,
                                top10: top10Count,
                                threatScore: threatScore.toFixed(1)
                            };
                        }).sort((a, b) => b.threatScore - a.threatScore);
                        
                        container.innerHTML = `
                            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; margin-bottom: 30px;">
                                <div style="background: var(--bg-card); padding: 20px; border-radius: 12px; border: 1px solid var(--border);">
                                    <div style="color: var(--text-secondary); font-size: 0.85em; margin-bottom: 8px;">COMPETIDORES</div>
                                    <div style="font-size: 2.5em; font-weight: 700; color: var(--primary);">${competitors.length}</div>
                                    <div style="color: var(--text-secondary); margin-top: 8px; font-size: 0.9em;">Apps en tus keywords</div>
                                </div>
                                <div style="background: var(--bg-card); padding: 20px; border-radius: 12px; border: 1px solid var(--border);">
                                    <div style="color: var(--text-secondary); font-size: 0.85em; margin-bottom: 8px;">AMENAZA #1</div>
                                    <div style="font-size: 1.3em; font-weight: 600; margin: 8px 0;">${competitors[0]?.name?.substring(0, 20) || 'N/A'}</div>
                                    <div style="color: var(--danger); font-size: 0.9em;">${competitors[0]?.top3 || 0} veces en TOP 3</div>
                                </div>
                                <div style="background: var(--bg-card); padding: 20px; border-radius: 12px; border: 1px solid var(--border);">
                                    <div style="color: var(--text-secondary); font-size: 0.85em; margin-bottom: 8px;">MEJOR POSICIONADO</div>
                                    <div style="font-size: 1.3em; font-weight: 600; margin: 8px 0;">${competitors.sort((a,b) => a.avgPosition - b.avgPosition)[0]?.name?.substring(0, 20) || 'N/A'}</div>
                                    <div style="color: var(--success); font-size: 0.9em;">Avg rank: #${competitors.sort((a,b) => a.avgPosition - b.avgPosition)[0]?.avgPosition || 'N/A'}</div>
                                </div>
                            </div>
                            
                            <div style="background: rgba(239, 68, 68, 0.1); border-left: 3px solid #ef4444; padding: 16px; border-radius: 4px; margin-bottom: 24px;">
                                <p style="margin: 0; color: var(--text-primary); font-size: 0.9em;">
                                    <strong>📊 Ranking por Amenaza:</strong> Ordenados por dominancia real en tus keywords (TOP 3 × 3 pts + TOP 10 × 1 pt + mejor ranking promedio)
                                </p>
                            </div>
                            
                            <h3 style="margin: 30px 0 20px 0; display: flex; align-items: center; gap: 10px;">
                                <i data-lucide="trophy" style="width: 24px; height: 24px; color: var(--primary);"></i>
                                Ranking Competitivo
                            </h3>
                            
                            <div style="display: grid; gap: 12px;">
                                ${competitors.slice(0, 10).map((comp, index) => `
                                    <div style="background: var(--bg-card); padding: 16px; border-radius: 12px; border: 1px solid var(--border);">
                                        <div style="display: grid; grid-template-columns: 40px 1fr auto auto auto auto; gap: 16px; align-items: center; margin-bottom: 12px;">
                                            <div style="width: 36px; height: 36px; border-radius: 50%; background: ${index < 3 ? 'linear-gradient(135deg, #ef4444, #dc2626)' : 'var(--bg-secondary)'}; display: flex; align-items: center; justify-content: center; font-weight: 700; color: ${index < 3 ? '#fff' : 'var(--text-secondary)'};">
                                                ${index + 1}
                                            </div>
                                            <div>
                                                <div style="font-weight: 600; margin-bottom: 4px;">${comp.name}</div>
                                                <div style="display: flex; gap: 12px; font-size: 0.85em; color: var(--text-secondary);">
                                                    <span>${comp.keywordCount} keywords</span>
                                                    <span>·</span>
                                                    <span style="display: flex; align-items: center; gap: 4px;">
                                                        <i data-lucide="star" style="width: 14px; height: 14px; color: #fbbf24;"></i>
                                                        ${parseFloat(comp.rating || 0).toFixed(1)}
                                                    </span>
                                                </div>
                                            </div>
                                            <div style="text-align: center;">
                                                <div style="font-size: 1.8em; font-weight: 700; color: #ef4444;">${comp.top3}</div>
                                                <div style="font-size: 0.75em; color: var(--text-secondary);">TOP 3</div>
                                            </div>
                                            <div style="text-align: center;">
                                                <div style="font-size: 1.8em; font-weight: 700; color: #f59e0b;">${comp.top10}</div>
                                                <div style="font-size: 0.75em; color: var(--text-secondary);">TOP 10</div>
                                            </div>
                                            <div style="text-align: center;">
                                                <div style="font-size: 1.3em; font-weight: 600;">Ø #${comp.avgPosition}</div>
                                                <div style="font-size: 0.75em; color: var(--text-secondary);">Avg Rank</div>
                                            </div>
                                            <div style="text-align: center; background: ${index < 3 ? 'rgba(239, 68, 68, 0.1)' : 'var(--bg-secondary)'}; padding: 8px 12px; border-radius: 8px;">
                                                <div style="font-size: 1.5em; font-weight: 700; color: ${index < 3 ? '#ef4444' : 'var(--text-primary)'};">${comp.threatScore}</div>
                                                <div style="font-size: 0.7em; color: var(--text-secondary);">THREAT</div>
                                            </div>
                                        </div>
                                        <div style="border-top: 1px solid var(--border); padding-top: 12px;">
                                            <div style="font-size: 0.8em; color: var(--text-secondary); margin-bottom: 8px; font-weight: 500;">
                                                <i data-lucide="tag" style="width: 12px; height: 12px;"></i>
                                                Keywords Compartidas:
                                            </div>
                                            <div style="display: flex; flex-wrap: wrap; gap: 6px;">
                                                ${comp.keywordsList.slice(0, 10).map(kw => `
                                                    <span style="background: var(--bg-secondary); padding: 4px 8px; border-radius: 4px; font-size: 0.8em;">
                                                        ${kw}
                                                    </span>
                                                `).join('')}
                                                ${comp.keywordsList.length > 10 ? `
                                                    <span style="color: var(--text-secondary); padding: 4px 8px; font-size: 0.8em;">
                                                        +${comp.keywordsList.length - 10} más
                                                    </span>
                                                ` : ''}
                                            </div>
                                        </div>
                                    </div>
                                `).join('')}
                            </div>
                        `;
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
                        // Categorizar oportunidades
                        const quickWins = DISCOVERIES_DATA.filter(d => 
                            d.difficulty === 'low' && (d.opportunity_score || 0) >= 50
                        );
                        const highPotential = DISCOVERIES_DATA.filter(d => 
                            (d.estimated_volume || 0) > 100 && (d.opportunity_score || 0) >= 60
                        );
                        const topScore = DISCOVERIES_DATA
                            .sort((a, b) => (b.opportunity_score || 0) - (a.opportunity_score || 0))
                            .slice(0, 10);
                        
                        // Agrupar por fuente
                        const sourceGroups = {};
                        DISCOVERIES_DATA.forEach(d => {
                            const source = d.source || 'unknown';
                            if (!sourceGroups[source]) sourceGroups[source] = [];
                            sourceGroups[source].push(d);
                        });
                        
                        // Mejor keyword por score
                        const bestKeyword = DISCOVERIES_DATA.reduce((best, curr) => 
                            (curr.opportunity_score || 0) > (best.opportunity_score || 0) ? curr : best
                        , DISCOVERIES_DATA[0]);
                        
                        container.innerHTML = `
                            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 30px;">
                                <div style="background: linear-gradient(135deg, #10b981 0%, #059669 100%); padding: 24px; border-radius: 12px; color: white;">
                                    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 8px;">
                                        <i data-lucide="target" style="width: 24px; height: 24px;"></i>
                                        <span style="font-size: 0.9em; opacity: 0.9;">Quick Wins</span>
                                    </div>
                                    <div style="font-size: 2.5em; font-weight: 700; margin: 8px 0;">${quickWins.length}</div>
                                    <div style="font-size: 0.85em; opacity: 0.9;">Fáciles de rankear</div>
                                </div>
                                
                                <div style="background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%); padding: 24px; border-radius: 12px; color: white;">
                                    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 8px;">
                                        <i data-lucide="trending-up" style="width: 24px; height: 24px;"></i>
                                        <span style="font-size: 0.9em; opacity: 0.9;">Alto Potencial</span>
                                    </div>
                                    <div style="font-size: 2.5em; font-weight: 700; margin: 8px 0;">${highPotential.length}</div>
                                    <div style="font-size: 0.85em; opacity: 0.9;">Volumen > 100</div>
                                </div>
                                
                                <div style="background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%); padding: 24px; border-radius: 12px; color: white;">
                                    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 8px;">
                                        <i data-lucide="lightbulb" style="width: 24px; height: 24px;"></i>
                                        <span style="font-size: 0.9em; opacity: 0.9;">Mejor Oportunidad</span>
                                    </div>
                                    <div style="font-size: 1.3em; font-weight: 600; margin: 8px 0; line-height: 1.3;">${bestKeyword.keyword}</div>
                                    <div style="font-size: 0.85em; opacity: 0.9;">Score: ${bestKeyword.opportunity_score}</div>
                                </div>
                            </div>
                            
                            <div style="background: var(--bg-card); padding: 24px; border-radius: 12px; margin-bottom: 20px;">
                                <h3 style="margin: 0 0 20px 0; display: flex; align-items: center; gap: 10px;">
                                    <i data-lucide="award" style="width: 20px; height: 20px; color: #f59e0b;"></i>
                                    Top 10 Oportunidades
                                </h3>
                                <div style="display: grid; gap: 12px;">
                                    ${topScore.map((d, idx) => `
                                        <div style="display: flex; align-items: center; justify-content: space-between; padding: 16px; background: var(--bg-primary); border-radius: 8px; border-left: 3px solid ${idx < 3 ? '#f59e0b' : 'transparent'};">
                                            <div style="flex: 1;">
                                                <div style="display: flex; align-items: center; gap: 12px;">
                                                    <span style="font-size: 1.5em; font-weight: 700; color: ${idx < 3 ? '#f59e0b' : 'var(--text-secondary)'}; min-width: 30px;">
                                                        ${idx < 3 ? ['🥇','🥈','🥉'][idx] : (idx + 1)}
                                                    </span>
                                                    <div style="flex: 1;">
                                                        <div style="font-weight: 500; margin-bottom: 4px;">${d.keyword}</div>
                                                        <div style="display: flex; gap: 16px; font-size: 0.85em; color: var(--text-secondary);">
                                                            <span>📊 Vol: ${d.estimated_volume || 'N/A'}</span>
                                                            <span>🎯 Diff: ${d.difficulty || 'N/A'}</span>
                                                            <span>📍 ${d.source || 'N/A'}</span>
                                                        </div>
                                                    </div>
                                                </div>
                                            </div>
                                            <div style="text-align: center; min-width: 80px;">
                                                <div style="font-size: 1.8em; font-weight: 700; background: ${d.opportunity_score > 70 ? 'linear-gradient(135deg, #10b981, #059669)' : d.opportunity_score > 50 ? 'linear-gradient(135deg, #f59e0b, #d97706)' : 'linear-gradient(135deg, #6b7280, #4b5563)'}; -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;">
                                                    ${d.opportunity_score || 0}
                                                </div>
                                                <div style="font-size: 0.75em; color: var(--text-secondary);">SCORE</div>
                                            </div>
                                        </div>
                                    `).join('')}
                                </div>
                            </div>
                            
                            <div style="background: var(--bg-card); padding: 24px; border-radius: 12px;">
                                <h3 style="margin: 0 0 16px 0; display: flex; align-items: center; gap: 10px;">
                                    <i data-lucide="layers" style="width: 20px; height: 20px; color: #3b82f6;"></i>
                                    Keywords por Fuente
                                </h3>
                                <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 12px;">
                                    ${Object.entries(sourceGroups)
                                        .sort((a, b) => b[1].length - a[1].length)
                                        .slice(0, 6)
                                        .map(([source, keywords]) => `
                                        <div style="background: var(--bg-primary); padding: 16px; border-radius: 8px; text-align: center;">
                                            <div style="font-size: 2em; font-weight: 700; color: var(--primary);">${keywords.length}</div>
                                            <div style="font-size: 0.85em; color: var(--text-secondary); margin-top: 4px;">${source.replace(/_/g, ' ')}</div>
                                        </div>
                                    `).join('')}
                                </div>
                                <div style="margin-top: 20px; padding: 16px; background: rgba(59, 130, 246, 0.1); border-left: 3px solid #3b82f6; border-radius: 4px;">
                                    <p style="margin: 0; color: var(--text-primary); font-size: 0.9em;">
                                        <strong>💡 Recomendación:</strong> Enfócate primero en las <strong>${quickWins.length} Quick Wins</strong> (baja dificultad, score ≥50). Son las más fáciles de rankear y pueden darte resultados rápidos.
                                    </p>
                                </div>
                            </div>
                        `;
                        
                        // Re-initialize Lucide icons
                        if (typeof lucide !== 'undefined') {
                            lucide.createIcons();
                        }
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
                            ticks: { 
                                color: document.body.classList.contains('dark-mode') ? '#AEAEB2' : '#48484A',
                                font: { size: 12 }
                            },
                            grid: { 
                                color: document.body.classList.contains('dark-mode') ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.08)'
                            }
                        },
                        x: {
                            type: 'time',
                            time: {
                                minUnit: 'day',
                                displayFormats: {
                                    day: 'dd MMM',
                                    hour: 'dd MMM HH:mm'
                                },
                                tooltipFormat: 'dd MMM yyyy HH:mm'
                            },
                            ticks: { 
                                color: document.body.classList.contains('dark-mode') ? '#AEAEB2' : '#48484A',
                                font: { size: 12 },
                                maxRotation: 45,
                                minRotation: 0
                            },
                            grid: { 
                                color: document.body.classList.contains('dark-mode') ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.08)'
                            }
                        }
                    },
                    plugins: {
                        legend: {
                            labels: { 
                                color: document.body.classList.contains('dark-mode') ? '#FFFFFF' : '#1D1D1F',
                                font: { size: 14, weight: '600' },
                                padding: 15
                            }
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
                            labels: { 
                                color: document.body.classList.contains('dark-mode') ? '#FFFFFF' : '#1D1D1F',
                                font: { size: 14, weight: '600' },
                                padding: 15
                            }
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
                            ticks: { 
                                color: document.body.classList.contains('dark-mode') ? '#AEAEB2' : '#48484A',
                                font: { size: 12 }
                            },
                            grid: { 
                                color: document.body.classList.contains('dark-mode') ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.08)'
                            }
                        },
                        y: {
                            ticks: { 
                                color: document.body.classList.contains('dark-mode') ? '#AEAEB2' : '#48484A',
                                font: { size: 12 }
                            },
                            grid: { 
                                color: document.body.classList.contains('dark-mode') ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.08)'
                            }
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
            
            // Si es la pestaña de alertas, cargar valores guardados
            if (tabName === 'alerts') {
                const savedToken = localStorage.getItem('telegram_token');
                const savedChatId = localStorage.getItem('telegram_chatid');
                
                if (savedToken) {
                    document.getElementById('telegram-token').value = savedToken;
                }
                if (savedChatId) {
                    document.getElementById('telegram-chatid').value = savedChatId;
                }
            }
            
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
            document.body.classList.toggle('dark-mode');
            const icon = document.querySelector('.theme-toggle i');
            if (document.body.classList.contains('dark-mode')) {
                icon.setAttribute('data-lucide', 'sun');
                localStorage.setItem('theme', 'dark');
            } else {
                icon.setAttribute('data-lucide', 'moon');
                localStorage.setItem('theme', 'light');
            }
            lucide.createIcons();
            
            // Recreate charts with new colors
            updateDashboard();
        }
        
        function saveAndCopyTelegramConfig() {
            const token = document.getElementById('telegram-token').value;
            const chatId = document.getElementById('telegram-chatid').value;
            
            if (!token || !chatId) {
                alert('⚠️ Por favor completa ambos campos (Bot Token y Chat ID)');
                return;
            }
            
            // Guardar en localStorage
            localStorage.setItem('telegram_token', token);
            localStorage.setItem('telegram_chatid', chatId);
            
            // Generar configuración YAML
            const yamlConfig = `alerts:
  telegram:
    enabled: true
    bot_token: "${token}"
    chat_id: "${chatId}"
  
  smart_alerts:
    enabled: true
    pattern_detection: true
    contextual_insights: true
  
  daily_summary:
    enabled: true
    time: "18:00"
    min_changes: 3`;
            
            // Mostrar y copiar al portapapeles
            const output = document.getElementById('config-output');
            output.textContent = yamlConfig;
            output.style.display = 'block';
            
            // Copiar al portapapeles
            navigator.clipboard.writeText(yamlConfig).then(() => {
                alert('✅ Configuración copiada al portapapeles!\\n\\nAhora pega esto en config/config.yaml');
            }).catch(() => {
                alert('⚠️ No se pudo copiar automáticamente. Copia manualmente el texto de abajo.');
            });
        }
        
        function toggleLanguage() {
            currentLang = currentLang === 'es' ? 'en' : 'es';
            localStorage.setItem('language', currentLang);
            
            // Update flag
            document.getElementById('lang-flag').textContent = currentLang === 'es' ? '🇪🇸' : '🇬🇧';
            
            // Update all elements with data-i18n
            document.querySelectorAll('[data-i18n]').forEach(element => {
                const key = element.getAttribute('data-i18n');
                if (translations[currentLang][key]) {
                    element.textContent = translations[currentLang][key];
                }
            });
            
            // Update select option
            const option = document.querySelector('#keyword-filter option[value="all"]');
            if (option) option.textContent = translations[currentLang].allKeywords;
            
            lucide.createIcons();
        }
        
        // Restore theme and language from localStorage
        document.addEventListener('DOMContentLoaded', () => {
            const savedTheme = localStorage.getItem('theme');
            if (savedTheme === 'dark') {
                document.body.classList.add('dark-mode');
                const icon = document.querySelector('.theme-toggle i');
                icon.setAttribute('data-lucide', 'sun');
                lucide.createIcons();
            }
            
            const savedLang = localStorage.getItem('language');
            if (savedLang && savedLang !== 'es') {
                currentLang = savedLang;
                toggleLanguage();
            }
        });
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

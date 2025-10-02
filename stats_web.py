from flask import Flask, render_template, jsonify
import json
import os
from datetime import datetime

app = Flask(__name__)

# Función para leer estadísticas (se puede adaptar según como guardes los datos)
def get_bot_stats():
    # Esto sería mejor si guardas las stats en un archivo JSON
    # Por ahora simulo algunos datos
    return {
        "total_users": 5,
        "total_commands": 23,
        "uptime": "2 días, 3 horas",
        "recent_commands": [
            {"time": "14:23", "user": "@lu1qa", "command": "/aprs LU1ABC"},
            {"time": "14:20", "user": "@ham_radio", "command": "/wx LU2XYZ-13"},
            {"time": "14:15", "user": "@aprs_fan", "command": "/ssid LU3DEF"},
        ],
        "popular_commands": [
            {"command": "/aprs", "count": 15},
            {"command": "/wx", "count": 5},
            {"command": "/ssid", "count": 3},
        ]
    }

@app.route('/')
def dashboard():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>APRS Bot Stats</title>
        <meta charset="UTF-8">
        <style>
            body { 
                font-family: Arial, sans-serif; 
                background: #0d1117; 
                color: #c9d1d9; 
                margin: 0; 
                padding: 20px; 
            }
            .container { 
                max-width: 800px; 
                margin: 0 auto; 
            }
            .card { 
                background: #21262d; 
                border: 1px solid #30363d;
                border-radius: 8px; 
                padding: 20px; 
                margin-bottom: 20px; 
            }
            .stat-grid { 
                display: grid; 
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); 
                gap: 15px; 
                margin-bottom: 20px; 
            }
            .stat-box { 
                background: #0d1117; 
                padding: 15px; 
                border-radius: 6px; 
                text-align: center; 
            }
            .stat-number { 
                font-size: 2em; 
                font-weight: bold; 
                color: #58a6ff; 
            }
            .recent-command { 
                background: #0d1117; 
                padding: 8px 12px; 
                margin: 5px 0; 
                border-radius: 4px; 
                border-left: 3px solid #f85149; 
            }
            h1 { color: #58a6ff; }
            h3 { color: #7c3aed; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤖 APRS Bot - Estadísticas</h1>
            
            <div class="stat-grid">
                <div class="stat-box">
                    <div class="stat-number" id="totalUsers">-</div>
                    <div>Usuarios únicos</div>
                </div>
                <div class="stat-box">
                    <div class="stat-number" id="totalCommands">-</div>
                    <div>Total comandos</div>
                </div>
                <div class="stat-box">
                    <div class="stat-number" id="uptime">-</div>
                    <div>Tiempo activo</div>
                </div>
            </div>
            
            <div class="card">
                <h3>📝 Comandos recientes</h3>
                <div id="recentCommands">Cargando...</div>
            </div>
            
            <div class="card">
                <h3>🔥 Comandos más usados</h3>
                <div id="popularCommands">Cargando...</div>
            </div>
        </div>
        
        <script>
            function loadStats() {
                fetch('/api/stats')
                    .then(response => response.json())
                    .then(data => {
                        document.getElementById('totalUsers').textContent = data.total_users;
                        document.getElementById('totalCommands').textContent = data.total_commands;
                        document.getElementById('uptime').textContent = data.uptime;
                        
                        // Comandos recientes
                        let recentHtml = '';
                        data.recent_commands.forEach(cmd => {
                            recentHtml += `
                                <div class="recent-command">
                                    <strong>${cmd.time}</strong> - ${cmd.user}: <code>${cmd.command}</code>
                                </div>
                            `;
                        });
                        document.getElementById('recentCommands').innerHTML = recentHtml;
                        
                        // Comandos populares
                        let popularHtml = '';
                        data.popular_commands.forEach(cmd => {
                            popularHtml += `
                                <div class="recent-command">
                                    <code>${cmd.command}</code> - <strong>${cmd.count} veces</strong>
                                </div>
                            `;
                        });
                        document.getElementById('popularCommands').innerHTML = popularHtml;
                    });
            }
            
            loadStats();
            setInterval(loadStats, 30000); // Actualizar cada 30 segundos
        </script>
    </body>
    </html>
    '''

@app.route('/api/stats')
def api_stats():
    return jsonify(get_bot_stats())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False)
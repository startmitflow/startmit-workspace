"""
Elite Dangerous Trading Web App
Flask web interface for EDSM commodity searches

Run locally:
    python app.py
    
Deploy to Railway/Render/Heroku:
   1. Push to GitHub
    2. Connect to hosting provider
    3. Set start command: python app.py
"""

from flask import Flask, render_template_string, request, jsonify
import urllib.request
import json
import urllib.parse

app = Flask(__name__)

# EDSM API Base
EDSM_API = "https://www.edsm.net/api-system-v1"

def get_stations(system_name):
    """Get all stations in a system from EDSM"""
    url = f"{EDSM_API}/stations?systemName={urllib.parse.quote(system_name)}"
    try:
        with urllib.request.urlopen(url, timeout=30) as response:
            return json.loads(response.read().decode())
    except Exception as e:
        return {"error": str(e)}

def get_market_data(system_name, station_name):
    """Get market data for a station"""
    url = f"{EDSM_API}/stations/market?systemName={urllib.parse.quote(system_name)}&stationName={urllib.parse.quote(station_name)}"
    try:
        with urllib.request.urlopen(url, timeout=30) as response:
            return json.loads(response.read().decode())
    except Exception as e:
        return {"error": str(e)}

@app.route('/')
def index():
    """Main search page"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/search', methods=['GET'])
def search():
    """Search for commodity in a system"""
    commodity = request.args.get('commodity', '')
    system = request.args.get('system', '')
    
    if not commodity or not system:
        return jsonify({"error": "Both commodity and system are required"})
    
    # Get stations
    system_data = get_stations(system)
    if "error" in system_data:
        return jsonify({"error": system_data["error"]})
    
    stations = system_data.get("stations", [])
    if not stations:
        return jsonify({"error": "No stations found"})
    
    results = []
    for station in stations:
        if not station.get("haveMarket"):
            continue
        
        market = get_market_data(system, station["name"])
        if "error" in market:
            continue
        
        commodities = market.get("commodities", [])
        for comm in commodities:
            if comm.get("name") == commodity:
                results.append({
                    "station": station["name"],
                    "type": station.get("type", "Unknown"),
                    "distance": station.get("distanceToArrival", 0),
                    "buy": comm.get("buyPrice", 0),
                    "sell": comm.get("sellPrice", 0),
                    "stock": comm.get("stock", 0),
                    "demand": comm.get("demand", 0)
                })
    
    # Sort by buy price (lowest first)
    results.sort(key=lambda x: x["buy"])
    
    # Calculate average
    avg_price = sum(r["buy"] for r in results) / len(results) if results else 0
    
    return jsonify({
        "commodity": commodity,
        "system": system,
        "count": len(results),
        "average_price": round(avg_price),
        "results": results
    })

@app.route('/api/stations/<system>')
def api_stations(system):
    """API endpoint to get stations in a system"""
    data = get_stations(system)
    if "error" in data:
        return jsonify(data), 400
    return jsonify(data)

@app.route('/api/market/<system>/<station>')
def api_market(system, station):
    """API endpoint to get market data for a station"""
    data = get_market_data(system, station)
    if "error" in data:
        return jsonify(data), 400
    return jsonify(data)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Elite Trading Search</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { 
            font-family: 'Segoe UI', system-ui, sans-serif; 
            background: linear-gradient(135deg, #0a0a1a 0%, #1a1a3a 100%);
            min-height: 100vh;
            color: #fff;
            padding: 20px;
        }
        .container { max-width: 900px; margin: 0 auto; }
        h1 { 
            text-align: center; 
            color: #00d4ff; 
            margin-bottom: 30px;
            font-size: 2.5em;
            text-shadow: 0 0 20px rgba(0,212,255,0.5);
        }
        .search-box {
            background: rgba(255,255,255,0.1);
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 30px;
            border: 1px solid rgba(255,255,255,0.1);
        }
        .form-row {
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
        }
        .form-group {
            flex: 1;
            min-width: 200px;
        }
        label {
            display: block;
            margin-bottom: 8px;
            color: #aaa;
            font-size: 0.9em;
        }
        input, select {
            width: 100%;
            padding: 12px 15px;
            border-radius: 8px;
            border: 1px solid rgba(255,255,255,0.2);
            background: rgba(0,0,0,0.3);
            color: #fff;
            font-size: 1em;
        }
        input:focus, select:focus {
            outline: none;
            border-color: #00d4ff;
            box-shadow: 0 0 10px rgba(0,212,255,0.3);
        }
        button {
            background: linear-gradient(135deg, #00d4ff, #0066ff);
            color: #fff;
            border: none;
            padding: 15px 40px;
            border-radius: 8px;
            font-size: 1.1em;
            cursor: pointer;
            margin-top: 15px;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 20px rgba(0,212,255,0.4);
        }
        .results {
            background: rgba(255,255,255,0.05);
            border-radius: 15px;
            padding: 20px;
            border: 1px solid rgba(255,255,255,0.1);
        }
        .result-item {
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 10px;
            background: rgba(0,0,0,0.2);
            border-left: 4px solid #00d4ff;
        }
        .result-item.cheap { border-left-color: #00ff00; }
        .result-item.Station { font-weight: bold; color: #00d4ff; }
        .result-meta { color: #888; font-size: 0.9em; margin-top: 5px; }
        .price { font-size: 1.2em; font-weight: bold; }
        .price.buy { color: #ff6b6b; }
        .price.sell { color: #4ecdc4; }
        .stats {
            display: flex;
            justify-content: space-between;
            padding: 15px;
            background: rgba(0,212,255,0.1);
            border-radius: 10px;
            margin-bottom: 20px;
        }
        .stat { text-align: center; }
        .stat-value { font-size: 1.5em; font-weight: bold; color: #00d4ff; }
        .stat-label { color: #888; font-size: 0.8em; }
        .loading {
            text-align: center;
            padding: 40px;
            color: #888;
        }
        .error { color: #ff6b6b; padding: 20px; text-align: center; }
        .commodity-list {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-top: 10px;
        }
        .commodity-tag {
            background: rgba(0,212,255,0.2);
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            cursor: pointer;
            transition: background 0.2s;
        }
        .commodity-tag:hover { background: rgba(0,212,255,0.4); }
    </style>
</head>
<body>
    <div class="container">
        <h1>Elite Trading Search</h1>
        
        <div class="search-box">
            <form id="searchForm">
                <div class="form-row">
                    <div class="form-group">
                        <label>System</label>
                        <input type="text" id="system" placeholder="e.g. Sol, Lave, Shinrarta Dezhra" required>
                    </div>
                    <div class="form-group">
                        <label>Commodity</label>
                        <input type="text" id="commodity" placeholder="e.g. Gold, Silver, Tritium" required>
                    </div>
                </div>
                <button type="submit">Search</button>
            </form>
            
            <div class="commodity-list">
                <span class="commodity-tag" onclick="document.getElementById('commodity').value='Gold'">Gold</span>
                <span class="commodity-tag" onclick="document.getElementById('commodity').value='Silver'">Silver</span>
                <span class="commodity-tag" onclick="document.getElementById('commodity').value='Platinum'">Platinum</span>
                <span class="commodity-tag" onclick="document.getElementById('commodity').value='Palladium'">Palladium</span>
                <span class="commodity-tag" onclick="document.getElementById('commodity').value='Tritium'">Tritium</span>
                <span class="commodity-tag" onclick="document.getElementById('commodity').value='Bertrandite'">Bertrandite</span>
                <span class="commodity-tag" onclick="document.getElementById('commodity').value='Grain'">Grain</span>
                <span class="commodity-tag" onclick="document.getElementById('commodity').value='Coffee'">Coffee</span>
            </div>
        </div>
        
        <div id="results" class="results" style="display:none;"></div>
    </div>
    
    <script>
        document.getElementById('searchForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const system = document.getElementById('system').value;
            const commodity = document.getElementById('commodity').value;
            const resultsDiv = document.getElementById('results');
            
            resultsDiv.style.display = 'block';
            resultsDiv.innerHTML = '<div class="loading">Searching EDSM...</div>';
            
            try {
                const response = await fetch(`/search?system=${encodeURIComponent(system)}&commodity=${encodeURIComponent(commodity)}`);
                const data = await response.json();
                
                if (data.error) {
                    resultsDiv.innerHTML = `<div class="error">${data.error}</div>`;
                    return;
                }
                
                if (data.results.length === 0) {
                    resultsDiv.innerHTML = `<div class="error">No stations found selling ${data.commodity} in ${data.system}</div>`;
                    return;
                }
                
                const avg = data.average_price;
                let html = `
                    <div class="stats">
                        <div class="stat">
                            <div class="stat-value">${data.count}</div>
                            <div class="stat-label">Stations</div>
                        </div>
                        <div class="stat">
                            <div class="stat-value">${data.average_price.toLocaleString()}cr</div>
                            <div class="stat-label">Avg Price</div>
                        </div>
                        <div class="stat">
                            <div class="stat-value">${data.results[0].buy.toLocaleString()}cr</div>
                            <div class="stat-label">Lowest Price</div>
                        </div>
                    </div>
                    <h3 style="margin-bottom:15px;color:#00d4ff;">Stations Selling ${data.commodity}</h3>
                `;
                
                data.results.forEach(r => {
                    const isCheap = r.buy < avg;
                    html += `
                        <div class="result-item ${isCheap ? 'cheap' : ''}">
                            <div class="Station">${r.station} <span style="color:#888;font-weight:normal;">(${r.type})</span></div>
                            <div class="result-meta">Distance: ${r.distance}ls | Stock: ${r.stock.toLocaleString()} | Demand: ${r.demand.toLocaleString()}</div>
                            <div style="margin-top:8px;">
                                <span class="price buy">Buy: ${r.buy.toLocaleString()}cr</span>
                                <span style="margin-left:20px;" class="price sell">Sell: ${r.sell.toLocaleString()}cr</span>
                                ${isCheap ? '<span style="margin-left:20px;color:#00ff00;">CHEAP</span>' : ''}
                            </div>
                        </div>
                    `;
                });
                
                resultsDiv.innerHTML = html;
            } catch (err) {
                resultsDiv.innerHTML = `<div class="error">Search failed: ${err.message}</div>`;
            }
        });
    </script>
</body>
</html>
'''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

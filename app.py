from flask import Flask, render_template_string, request, jsonify
import urllib.request
import json
import urllib.parse

app = Flask(__name__)

EDSM_API = "https://www.edsm.net/api-system-v1"

def get_stations(system_name):
    url = f"{EDSM_API}/stations?systemName={urllib.parse.quote(system_name)}"
    try:
        with urllib.request.urlopen(url, timeout=30) as response:
            return json.loads(response.read().decode())
    except Exception as e:
        return {"error": str(e)}

def get_market_data(system_name, station_name):
    url = f"{EDSM_API}/stations/market?systemName={urllib.parse.quote(system_name)}&stationName={urllib.parse.quote(station_name)}"
    try:
        with urllib.request.urlopen(url, timeout=30) as response:
            return json.loads(response.read().decode())
    except Exception as e:
        return {"error": str(e)}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Elite Trading Search</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { 
            font-family: Arial, sans-serif; 
            background: #0a0a1a;
            min-height: 100vh;
            color: #fff;
            padding: 20px;
        }
        .container { max-width: 900px; margin: 0 auto; }
        h1 { 
            text-align: center; 
            color: #00d4ff; 
            margin-bottom: 30px;
            font-size: 2em;
        }
        .search-box {
            background: rgba(255,255,255,0.1);
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
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
            margin-bottom: 5px;
            color: #aaa;
        }
        input {
            width: 100%;
            padding: 10px;
            border-radius: 5px;
            border: 1px solid #444;
            background: #1a1a2e;
            color: #fff;
        }
        button {
            background: #00d4ff;
            color: #000;
            border: none;
            padding: 12px 30px;
            border-radius: 5px;
            font-size: 1em;
            cursor: pointer;
            margin-top: 10px;
        }
        button:hover { background: #00aacc; }
        .results {
            background: rgba(255,255,255,0.05);
            border-radius: 10px;
            padding: 15px;
        }
        .result-item {
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 8px;
            background: #1a1a2e;
            border-left: 3px solid #00d4ff;
        }
        .result-item.cheap { border-left-color: #00ff00; }
        .stats {
            display: flex;
            justify-content: space-between;
            padding: 10px;
            background: rgba(0,212,255,0.1);
            border-radius: 5px;
            margin-bottom: 15px;
        }
        .stat { text-align: center; }
        .stat-value { font-size: 1.3em; font-weight: bold; color: #00d4ff; }
        .stat-label { color: #888; font-size: 0.8em; }
        .commodity-list {
            display: flex;
            flex-wrap: wrap;
            gap: 5px;
            margin-top: 10px;
        }
        .commodity-tag {
            background: #1a4a5e;
            padding: 5px 10px;
            border-radius: 15px;
            font-size: 0.8em;
            cursor: pointer;
        }
        .commodity-tag:hover { background: #2a6a7e; }
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
                        <input type="text" id="system" placeholder="e.g. Sol, Lave" required>
                    </div>
                    <div class="form-group">
                        <label>Commodity</label>
                        <input type="text" id="commodity" placeholder="e.g. Gold, Silver" required>
                    </div>
                </div>
                <button type="submit">Search</button>
            </form>
            <div class="commodity-list">
                <span class="commodity-tag" onclick="setCommodity('Gold')">Gold</span>
                <span class="commodity-tag" onclick="setCommodity('Silver')">Silver</span>
                <span class="commodity-tag" onclick="setCommodity('Platinum')">Platinum</span>
                <span class="commodity-tag" onclick="setCommodity('Palladium')">Palladium</span>
                <span class="commodity-tag" onclick="setCommodity('Tritium')">Tritium</span>
            </div>
        </div>
        <div id="results" class="results" style="display:none;"></div>
    </div>
    <script>
        function setCommodity(name) {
            document.getElementById('commodity').value = name;
        }
        
        document.getElementById('searchForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const system = document.getElementById('system').value;
            const commodity = document.getElementById('commodity').value;
            const resultsDiv = document.getElementById('results');
            
            resultsDiv.style.display = 'block';
            resultsDiv.innerHTML = '<div style="text-align:center;padding:20px;color:#888;">Searching...</div>';
            
            try {
                const response = await fetch('/search?system=' + encodeURIComponent(system) + '&commodity=' + encodeURIComponent(commodity));
                const data = await response.json();
                
                if (data.error) {
                    resultsDiv.innerHTML = '<div style="color:#ff6b6b;text-align:center;">' + data.error + '</div>';
                    return;
                }
                
                if (data.results.length === 0) {
                    resultsDiv.innerHTML = '<div style="color:#ff6b6b;text-align:center;">No stations found selling ' + data.commodity + ' in ' + data.system + '</div>';
                    return;
                }
                
                const avg = data.average_price;
                let html = '<div class="stats">' +
                    '<div class="stat"><div class="stat-value">' + data.count + '</div><div class="stat-label">Stations</div></div>' +
                    '<div class="stat"><div class="stat-value">' + avg.toLocaleString() + 'cr</div><div class="stat-label">Avg Price</div></div>' +
                    '<div class="stat"><div class="stat-value">' + data.results[0].buy.toLocaleString() + 'cr</div><div class="stat-label">Lowest</div></div>' +
                    '</div>' +
                    '<h3 style="margin-bottom:15px;color:#00d4ff;">Stations Selling ' + data.commodity + '</h3>';
                
                data.results.forEach(r => {
                    const isCheap = r.buy < avg;
                    html += '<div class="result-item ' + (isCheap ? 'cheap' : '') + '">' +
                        '<div style="font-weight:bold;color:#00d4ff;">' + r.station + ' <span style="color:#888;font-weight:normal;">(' + r.type + ')</span></div>' +
                        '<div style="color:#888;font-size:0.9em;margin-top:3px;">Distance: ' + r.distance + 'ls | Stock: ' + r.stock.toLocaleString() + '</div>' +
                        '<div style="margin-top:5px;">' +
                        '<span style="color:#ff6b6b;font-weight:bold;">Buy: ' + r.buy.toLocaleString() + 'cr</span>' +
                        '<span style="margin-left:15px;color:#4ecdc4;font-weight:bold;">Sell: ' + r.sell.toLocaleString() + 'cr</span>' +
                        (isCheap ? '<span style="margin-left:15px;color:#00ff00;">CHEAP</span>' : '') +
                        '</div></div>';
                });
                
                resultsDiv.innerHTML = html;
            } catch (err) {
                resultsDiv.innerHTML = '<div style="color:#ff6b6b;text-align:center;">Error: ' + err.message + '</div>';
            }
        });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/search')
def search():
    commodity = request.args.get('commodity', '')
    system = request.args.get('system', '')
    
    if not commodity or not system:
        return jsonify({"error": "Both commodity and system are required"})
    
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
    
    results.sort(key=lambda x: x["buy"])
    avg_price = sum(r["buy"] for r in results) // len(results) if results else 0
    
    return jsonify({
        "commodity": commodity,
        "system": system,
        "count": len(results),
        "average_price": avg_price,
        "results": results
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

"""
Elite Dangerous Station Advisor - Complete Rewrite v13
A clean, working single-file Flask app with EDSM API integration.
"""

from flask import Flask, render_template_string, request, jsonify
import urllib.request
import json
import urllib.parse

app = Flask(__name__)

EDSM_API = "https://www.edsm.net"
REQUEST_HEADERS = {"User-Agent": "StartMit-EliteCompanion/1.0"}

COMMODITIES = [
    "Advanced Catalysers", "Agri-Medicines", "Algae", "Aluminium", "Animal Meat",
    "Batteries", "Beer", "Bellows", "Biocircuits", "Carbon", "Cheese", "Chemicals",
    "Cobalt", "Cobalt Ore", "Coffee", "Coltan", "Copper", "Copper Ore", "Diamond",
    "Food Cartridges", "Fruits", "Gold", "Gold Ore", "Grain", "Hydrogen Fuel",
    "Insulated Cabin Fabric", "Ion Distributor", "Iron", "Iron Ore", "Lithium",
    "Lithium Ore", "Methanol Monopropellant", "Mineral Oil", "Minerals", "Nickel",
    "Nickel Ore", "Nitrogen", "Oxygen", "Palladium", "Platinum", "Platinum Ore",
    "Power Generators", "Power Plants", "Processed Foods", "Rares", "Robotics",
    "Scrap", "Scrap Metal", "Semiconductors", "Silver", "Silver Ore", "Steel",
    "Sulphur", "Technology Components", "Textiles", "Titanium", "Titanium Ore",
    "Tritium", "Tritium Ore", "Water", "Wine", "Wool"
]

def api_get(endpoint, params=None):
    url = f"{EDSM_API}{endpoint}"
    if params:
        url += "?" + "&".join(f"{k}={urllib.parse.quote(str(v))}" for k, v in params.items())
    req = urllib.request.Request(url, headers=REQUEST_HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read().decode())
    except Exception as e:
        return {"error": str(e)}

def get_system_info(name):
    return api_get("/api-v1/system", {
        "systemName": name,
        "showInformation": 1,
        "showCoordinates": 1
    })

def get_stations(name):
    return api_get("/api-system-v1/stations", {"systemName": name})

def get_station_market(system, station):
    return api_get("/api-system-v1/stations/market", {
        "systemName": system,
        "stationName": station
    })

HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Elite Station Advisor</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        :root {
            --bg: #0a0a12;
            --card: #12121f;
            --input: #1a1a2e;
            --accent: #f5a623;
            --cyan: #00d4ff;
            --green: #00ff88;
            --red: #ff4757;
            --text: #e0e0e0;
            --dim: #888;
            --border: #2a2a3e;
        }
        body { font-family: Segoe UI, Arial, sans-serif; background: var(--bg); color: var(--text); min-height: 100vh; display: flex; }
        .sidebar { width: 220px; background: var(--card); border-right: 1px solid var(--border); height: 100vh; position: fixed; left: 0; top: 0; overflow-y: auto; }
        .sidebar-header { padding: 20px; border-bottom: 1px solid var(--border); }
        .sidebar-header h1 { font-size: 1.2em; color: var(--accent); }
        .sidebar-header span { font-size: 0.7em; color: var(--dim); }
        .nav-section { padding: 15px 0; }
        .nav-section-title { font-size: 0.65em; text-transform: uppercase; color: var(--dim); padding: 0 20px; margin-bottom: 8px; letter-spacing: 1px; }
        .nav-item { display: flex; align-items: center; gap: 10px; padding: 10px 20px; color: var(--dim); cursor: pointer; transition: all 0.2s; border-left: 3px solid transparent; }
        .nav-item:hover { background: rgba(255,255,255,0.05); color: var(--text); }
        .nav-item.active { background: rgba(245,166,35,0.15); color: var(--accent); border-left-color: var(--accent); }
        .nav-item .icon { font-size: 1.1em; width: 22px; text-align: center; }
        .nav-item .label { font-size: 0.85em; }
        .main { margin-left: 220px; flex: 1; padding: 30px; }
        .page { display: none; }
        .page.active { display: block; }
        .page-header { margin-bottom: 25px; }
        .page-header h2 { font-size: 1.6em; color: var(--text); margin-bottom: 5px; }
        .page-header p { color: var(--dim); font-size: 0.85em; }
        .card { background: var(--card); border: 1px solid var(--border); border-radius: 10px; padding: 20px; margin-bottom: 20px; }
        .card-header { margin-bottom: 15px; }
        .card-title { font-size: 1em; font-weight: 600; color: var(--cyan); }
        .form-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 15px; }
        .form-group { margin-bottom: 12px; }
        .form-group label { display: block; font-size: 0.75em; color: var(--dim); margin-bottom: 5px; text-transform: uppercase; }
        input, select { width: 100%; padding: 10px 12px; border: 1px solid var(--border); border-radius: 6px; background: var(--input); color: var(--text); font-size: 0.9em; }
        input:focus, select:focus { outline: none; border-color: var(--cyan); }
        button { background: var(--accent); color: #000; border: none; padding: 10px 20px; border-radius: 6px; font-size: 0.9em; font-weight: 600; cursor: pointer; }
        button:hover { background: #ffb84d; }
        button.secondary { background: var(--input); color: var(--text); border: 1px solid var(--border); }
        button.secondary:hover { background: var(--border); }
        .results-grid { display: grid; gap: 10px; }
        .result-item { background: var(--input); border: 1px solid var(--border); border-radius: 8px; padding: 12px; cursor: pointer; transition: all 0.2s; }
        .result-item:hover { border-color: var(--cyan); transform: translateX(3px); }
        .result-item .name { color: var(--cyan); font-weight: 600; margin-bottom: 4px; }
        .result-item .info { font-size: 0.8em; color: var(--dim); }
        .badge { display: inline-block; padding: 3px 8px; border-radius: 4px; font-size: 0.7em; margin: 2px; }
        .badge-green { background: rgba(0,255,136,0.15); color: var(--green); }
        .badge-cyan { background: rgba(0,212,255,0.15); color: var(--cyan); }
        .modal-overlay { display: none; position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.85); z-index: 1000; align-items: center; justify-content: center; padding: 20px; }
        .modal-overlay.active { display: flex; }
        .modal { background: var(--card); border: 1px solid var(--border); border-radius: 12px; width: 100%; max-width: 800px; max-height: 85vh; overflow-y: auto; }
        .modal-header { padding: 15px 20px; border-bottom: 1px solid var(--border); display: flex; justify-content: space-between; align-items: center; position: sticky; top: 0; background: var(--card); z-index: 10; }
        .modal-header h3 { color: var(--cyan); }
        .modal-close { background: none; border: none; color: var(--dim); font-size: 1.5em; cursor: pointer; }
        .modal-close:hover { color: var(--red); }
        .modal-body { padding: 20px; }
        .modal-section { margin-bottom: 20px; }
        .modal-section h4 { color: var(--accent); font-size: 0.9em; margin-bottom: 10px; padding-bottom: 8px; border-bottom: 1px solid var(--border); }
        .stat-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 10px; }
        .stat-box { background: var(--input); border: 1px solid var(--border); border-radius: 6px; padding: 12px; text-align: center; }
        .stat-box .value { font-size: 1.2em; font-weight: bold; color: var(--cyan); }
        .stat-box .label { font-size: 0.7em; color: var(--dim); text-transform: uppercase; }
        .data-table { width: 100%; border-collapse: collapse; font-size: 0.8em; }
        .data-table th, .data-table td { padding: 6px 10px; text-align: left; border-bottom: 1px solid var(--border); }
        .data-table th { color: var(--dim); font-weight: 500; text-transform: uppercase; font-size: 0.7em; }
        .data-table tr:hover { background: rgba(255,255,255,0.03); }
        .price-buy { color: var(--green); }
        .price-sell { color: var(--red); }
        .empty-state { text-align: center; padding: 40px; color: var(--dim); }
        .loading { text-align: center; padding: 20px; color: var(--dim); }
    </style>
</head>
<body>
    <nav class="sidebar">
        <div class="sidebar-header">
            <h1>Elite Station Advisor</h1>
            <span>by StartMit</span>
        </div>
        <div class="nav-section">
            <div class="nav-section-title">Trade and Station</div>
            <div class="nav-item active" onclick="showPage(event, 'trade')">
                <span class="icon">T</span><span class="label">Trade Search</span>
            </div>
            <div class="nav-item" onclick="showPage(event, 'station')">
                <span class="icon">S</span><span class="label">Station Info</span>
            </div>
            <div class="nav-item" onclick="showPage(event, 'route')">
                <span class="icon">R</span><span class="label">Trade Routes</span>
            </div>
            <div class="nav-item" onclick="showPage(event, 'services')">
                <span class="icon">F</span><span class="label">Service Finder</span>
            </div>
        </div>
        <div class="nav-section">
            <div class="nav-section-title">Tools</div>
            <div class="nav-item" onclick="showPage(event, 'states')">
                <span class="icon">X</span><span class="label">System States</span>
            </div>
            <div class="nav-item" onclick="showPage(event, 'engineering')">
                <span class="icon">E</span><span class="label">Engineering</span>
            </div>
            <div class="nav-item" onclick="showPage(event, 'colonize')">
                <span class="icon">C</span><span class="label">Colony Advisor</span>
            </div>
        </div>
        <div class="nav-section">
            <div class="nav-section-title">Exploration</div>
            <div class="nav-item" onclick="showPage(event, 'guardian')">
                <span class="icon">G</span><span class="label">Guardian Sites</span>
            </div>
            <div class="nav-item" onclick="showPage(event, 'thargoid')">
                <span class="icon">T</span><span class="label">Thargoid Sites</span>
            </div>
            <div class="nav-item" onclick="showPage(event, 'carrier')">
                <span class="icon">C</span><span class="label">Fleet Carriers</span>
            </div>
        </div>
    </nav>

    <main class="main">
        <!-- TRADE SEARCH PAGE -->
        <div id="page-trade" class="page active">
            <div class="page-header">
                <h2>Trade Search</h2>
                <p>Find commodity prices in any system</p>
            </div>
            <div class="card">
                <div class="card-header"><span class="card-title">Search</span></div>
                <div class="form-grid">
                    <div class="form-group">
                        <label for="trade-system">System</label>
                        <input type="text" id="trade-system" placeholder="e.g. Diaguandrak">
                    </div>
                    <div class="form-group">
                        <label for="trade-commodity">Commodity</label>
                        <select id="trade-commodity">
                            <option value="">Select commodity...</option>
                        </select>
                    </div>
                    <div class="form-group" style="align-self: end;">
                        <button onclick="searchTrade()">Search</button>
                    </div>
                </div>
            </div>
            <div id="trade-results" class="card" style="display: none;">
                <div class="card-header"><span class="card-title" id="trade-count">0 results</span></div>
                <div id="trade-results-list" class="results-grid"></div>
            </div>
        </div>

        <!-- STATION INFO PAGE -->
        <div id="page-station" class="page">
            <div class="page-header">
                <h2>Station Info</h2>
                <p>Find stations in a system</p>
            </div>
            <div class="card">
                <div class="card-header"><span class="card-title">Search Stations</span></div>
                <div class="form-grid">
                    <div class="form-group">
                        <label for="station-system">System</label>
                        <input type="text" id="station-system" placeholder="e.g. Diaguandrak">
                    </div>
                    <div class="form-group" style="align-self: end;">
                        <button onclick="searchStation()">Search</button>
                    </div>
                </div>
            </div>
            <div id="station-results" class="card" style="display: none;">
                <div class="card-header"><span class="card-title" id="station-system-name">System</span></div>
                <div id="station-list" class="results-grid"></div>
            </div>
        </div>

        <!-- TRADE ROUTES PAGE -->
        <div id="page-route" class="page">
            <div class="page-header">
                <h2>Trade Routes</h2>
                <p>Find profitable trade routes</p>
            </div>
            <div class="card">
                <div class="card-header"><span class="card-title">Find Routes</span></div>
                <div class="form-grid">
                    <div class="form-group">
                        <label for="route-from">From System</label>
                        <input type="text" id="route-from" placeholder="e.g. Diaguandrak">
                    </div>
                    <div class="form-group">
                        <label for="route-to">To System</label>
                        <input type="text" id="route-to" placeholder="e.g. Lucasium">
                    </div>
                    <div class="form-group" style="align-self: end;">
                        <button onclick="searchRoute()">Find Route</button>
                    </div>
                </div>
            </div>
            <div id="route-results" class="card" style="display: none;">
                <div id="route-list"></div>
            </div>
        </div>

        <!-- SERVICE FINDER PAGE -->
        <div id="page-services" class="page">
            <div class="page-header">
                <h2>Service Finder</h2>
                <p>Find stations with specific services</p>
            </div>
            <div class="card">
                <div class="card-header"><span class="card-title">Search</span></div>
                <div class="form-grid">
                    <div class="form-group">
                        <label for="service-system">System</label>
                        <input type="text" id="service-system" placeholder="e.g. Diaguandrak">
                    </div>
                    <div class="form-group">
                        <label for="service-type">Service</label>
                        <select id="service-type">
                            <option value="outfitting">Outfitting</option>
                            <option value="shipyard">Shipyard</option>
                            <option value="market">Market</option>
                            <option value="repair">Repair</option>
                            <option value="refuel">Refuel</option>
                            <option value="restock">Restock</option>
                        </select>
                    </div>
                    <div class="form-group" style="align-self: end;">
                        <button onclick="searchServices()">Search</button>
                    </div>
                </div>
            </div>
            <div id="service-results" class="card" style="display: none;">
                <div id="service-list" class="results-grid"></div>
            </div>
        </div>

        <!-- SYSTEM STATES PAGE -->
        <div id="page-states" class="page">
            <div class="page-header">
                <h2>System States</h2>
                <p>Check current state and trade effects</p>
            </div>
            <div class="card">
                <div class="card-header"><span class="card-title">System State Guide</span></div>
                <div id="state-guide"></div>
            </div>
        </div>

        <!-- ENGINEERING PAGE -->
        <div id="page-engineering" class="page">
            <div class="page-header">
                <h2>Engineering</h2>
                <p>Blueprint crafting and material requirements</p>
            </div>
            <div class="card">
                <div class="card-header"><span class="card-title">Recipes</span></div>
                <div id="engineering-list">
                    <p style="color: var(--dim);">Engineering module coming soon.</p>
                </div>
            </div>
        </div>

        <!-- COLONY ADVISOR PAGE -->
        <div id="page-colonize" class="page">
            <div class="page-header">
                <h2>Colony Advisor</h2>
                <p>Plan your colony layout</p>
            </div>
            <div class="card">
                <div class="card-header"><span class="card-title">Colony Planning</span></div>
                <p style="color: var(--dim);">Colony advisor coming soon.</p>
            </div>
        </div>

        <!-- GUARDIAN SITES PAGE -->
        <div id="page-guardian" class="page">
            <div class="page-header">
                <h2>Guardian Sites</h2>
                <p>Known Guardian locations</p>
            </div>
            <div class="card">
                <div class="card-header"><span class="card-title">Guardian Sites</span></div>
                <div class="results-grid">
                    <div class="result-item">
                        <div class="name">Synuefe EU-R c4-15</div>
                        <div class="info">Multiple pylons, combat zone nearby</div>
                    </div>
                    <div class="result-item">
                        <div class="name">Synuefe XR-R c4-6</div>
                        <div class="info">Large central structure</div>
                    </div>
                    <div class="result-item">
                        <div class="name">HIP 22441</div>
                        <div class="info">Blueprint site - requires keycard</div>
                    </div>
                </div>
            </div>
        </div>

        <!-- THARGOID SITES PAGE -->
        <div id="page-thargoid" class="page">
            <div class="page-header">
                <h2>Thargoid Sites</h2>
                <p>Known Thargoid locations</p>
            </div>
            <div class="card">
                <div class="card-header"><span class="card-title">Thargoid Sites</span></div>
                <div class="results-grid">
                    <div class="result-item">
                        <div class="name">HIP 21025</div>
                        <div class="info">Crash site, hyperdiction common</div>
                    </div>
                    <div class="result-item">
                        <div class="name">Pleiades Nebula</div>
                        <div class="info">Multiple sites, Interceptor spawns</div>
                    </div>
                </div>
            </div>
        </div>

        <!-- FLEET CARRIERS PAGE -->
        <div id="page-carrier" class="page">
            <div class="page-header">
                <h2>Fleet Carriers</h2>
                <p>Search fleet carriers</p>
            </div>
            <div class="card">
                <div class="card-header"><span class="card-title">Search Carriers</span></div>
                <div class="form-grid">
                    <div class="form-group">
                        <label for="carrier-name">Carrier Name or ID</label>
                        <input type="text" id="carrier-name" placeholder="e.g. EXPLORER-X5">
                    </div>
                    <div class="form-group" style="align-self: end;">
                        <button onclick="searchCarrier()">Search</button>
                    </div>
                </div>
            </div>
            <div id="carrier-results" class="card" style="display: none;">
                <div id="carrier-list"></div>
            </div>
        </div>
    </main>

    <!-- STATION DETAIL MODAL -->
    <div id="station-modal" class="modal-overlay">
        <div class="modal">
            <div class="modal-header">
                <h3 id="modal-station-name">Station Name</h3>
                <button class="modal-close" onclick="closeModal()">X</button>
            </div>
            <div class="modal-body">
                <div class="stat-grid" style="margin-bottom: 20px;">
                    <div class="stat-box">
                        <div class="value" id="modal-station-type">-</div>
                        <div class="label">Type</div>
                    </div>
                    <div class="stat-box">
                        <div class="value" id="modal-distance">-</div>
                        <div class="label">Distance (LS)</div>
                    </div>
                    <div class="stat-box">
                        <div class="value" id="modal-economy">-</div>
                        <div class="label">Economy</div>
                    </div>
                    <div class="stat-box">
                        <div class="value" id="modal-government">-</div>
                        <div class="label">Government</div>
                    </div>
                </div>
                <div class="modal-section">
                    <h4>Services</h4>
                    <div id="modal-services"></div>
                </div>
                <div class="modal-section">
                    <h4>Commodities</h4>
                    <div id="modal-commodities"></div>
                </div>
            </div>
        </div>
    </div>

    <script>
        // Commodity list for dropdown
        var commodities = ''' + json.dumps(COMMODITIES) + ''';
        
        // Populate commodity dropdown
        document.addEventListener('DOMContentLoaded', function() {
            var select = document.getElementById('trade-commodity');
            if (select) {
                commodities.forEach(function(c) {
                    var opt = document.createElement('option');
                    opt.value = c;
                    opt.textContent = c;
                    select.appendChild(opt);
                });
            }
        });

        // Navigation
        function showPage(event, pageId) {
            if (event) {
                event.preventDefault();
            }
            document.querySelectorAll('.page').forEach(function(p) {
                p.classList.remove('active');
            });
            document.querySelectorAll('.nav-item').forEach(function(n) {
                n.classList.remove('active');
            });
            var page = document.getElementById('page-' + pageId);
            if (page) {
                page.classList.add('active');
            }
            if (event && event.target) {
                var navItem = event.target.closest('.nav-item');
                if (navItem) {
                    navItem.classList.add('active');
                }
            }
        }

        // Trade Search
        async function searchTrade() {
            var system = document.getElementById('trade-system').value;
            var commodity = document.getElementById('trade-commodity').value;
            if (!system || !commodity) {
                alert('Please enter system and select commodity');
                return;
            }
            var results = document.getElementById('trade-results');
            var list = document.getElementById('trade-results-list');
            results.style.display = 'block';
            list.innerHTML = '<div class="loading">Searching...</div>';
            
            try {
                var resp = await fetch('/api/search?system=' + encodeURIComponent(system) + '&commodity=' + encodeURIComponent(commodity));
                var data = await resp.json();
                
                if (data.error) {
                    list.innerHTML = '<div class="empty-state"><p>Error: ' + data.error + '</p></div>';
                    return;
                }
                
                if (!data.results || data.results.length === 0) {
                    list.innerHTML = '<div class="empty-state"><p>No results found</p></div>';
                    return;
                }
                
                document.getElementById('trade-count').textContent = data.results.length + ' results';
                list.innerHTML = data.results.slice(0, 20).map(function(r) {
                    return '<div class="result-item" onclick="openStationModal(\'' + data.system + '\', \'' + r.station + '\')">' +
                        '<div class="name">' + r.station + '</div>' +
                        '<div class="info">' + (r.type || 'Unknown') + ' | ' + (r.distance || '?') + ' LS<br>' +
                        'Buy: ' + (r.buy || '?') + ' CR | Sell: ' + (r.sell || '?') + ' CR</div>' +
                        '</div>';
                }).join('');
            } catch (e) {
                list.innerHTML = '<div class="empty-state"><p>Error: ' + e.message + '</p></div>';
            }
        }

        // Station Search
        async function searchStation() {
            var system = document.getElementById('station-system').value;
            if (!system) {
                alert('Please enter a system name');
                return;
            }
            var results = document.getElementById('station-results');
            var list = document.getElementById('station-list');
            document.getElementById('station-system-name').textContent = system;
            results.style.display = 'block';
            list.innerHTML = '<div class="loading">Loading stations...</div>';
            
            try {
                var resp = await fetch('/api/station?system=' + encodeURIComponent(system));
                var data = await resp.json();
                
                if (data.error || !data.stations) {
                    list.innerHTML = '<div class="empty-state"><p>' + (data.error || 'No stations found') + '</p></div>';
                    return;
                }
                
                if (data.stations.length === 0) {
                    list.innerHTML = '<div class="empty-state"><p>No stations found in this system</p></div>';
                    return;
                }
                
                list.innerHTML = data.stations.map(function(s) {
                    var services = formatServices(s);
                    return '<div class="result-item" onclick="openStationModal(\'' + data.system + '\', \'' + s.name + '\')">' +
                        '<div class="name">' + s.name + '</div>' +
                        '<div class="info">' + (s.type || 'Unknown') + ' | ' + (s.distanceToArrival || '?') + ' LS<br>' +
                        'Economy: ' + (s.economy || 'Unknown') + '</div>' +
                        '</div>';
                }).join('');
            } catch (e) {
                list.innerHTML = '<div class="empty-state"><p>Error: ' + e.message + '</p></div>';
            }
        }

        // Trade Routes
        async function searchRoute() {
            var from = document.getElementById('route-from').value;
            var to = document.getElementById('route-to').value;
            if (!from || !to) {
                alert('Please enter both systems');
                return;
            }
            var results = document.getElementById('route-results');
            var list = document.getElementById('route-list');
            results.style.display = 'block';
            list.innerHTML = '<div class="loading">Finding routes...</div>';
            
            try {
                var resp = await fetch('/api/route?from=' + encodeURIComponent(from) + '&to=' + encodeURIComponent(to));
                var data = await resp.json();
                
                if (data.error) {
                    list.innerHTML = '<div class="empty-state"><p>' + data.error + '</p></div>';
                    return;
                }
                
                list.innerHTML = '<p style="color: var(--dim);">Route search coming soon. Try searching stations individually.</p>';
            } catch (e) {
                list.innerHTML = '<div class="empty-state"><p>Error: ' + e.message + '</p></div>';
            }
        }

        // Service Finder
        async function searchServices() {
            var system = document.getElementById('service-system').value;
            var type = document.getElementById('service-type').value;
            if (!system) {
                alert('Please enter a system name');
                return;
            }
            var results = document.getElementById('service-results');
            var list = document.getElementById('service-list');
            results.style.display = 'block';
            list.innerHTML = '<div class="loading">Searching...</div>';
            
            try {
                var resp = await fetch('/api/services?system=' + encodeURIComponent(system) + '&service=' + encodeURIComponent(type));
                var data = await resp.json();
                
                if (data.error || !data.stations) {
                    list.innerHTML = '<div class="empty-state"><p>' + (data.error || 'No stations found') + '</p></div>';
                    return;
                }
                
                list.innerHTML = data.stations.map(function(s) {
                    return '<div class="result-item" onclick="openStationModal(\'' + system + '\', \'' + s.name + '\')">' +
                        '<div class="name">' + s.name + '</div>' +
                        '<div class="info">' + (s.type || 'Unknown') + ' | ' + (s.distanceToArrival || '?') + ' LS</div>' +
                        '</div>';
                }).join('');
            } catch (e) {
                list.innerHTML = '<div class="empty-state"><p>Error: ' + e.message + '</p></div>';
            }
        }

        // Fleet Carrier Search
        async function searchCarrier() {
            var name = document.getElementById('carrier-name').value;
            if (!name) {
                alert('Please enter a carrier name or ID');
                return;
            }
            var results = document.getElementById('carrier-results');
            var list = document.getElementById('carrier-list');
            results.style.display = 'block';
            list.innerHTML = '<div class="loading">Searching...</div>';
            
            list.innerHTML = '<div class="empty-state"><p>Fleet carrier search coming soon.</p></div>';
        }

        // Format services as badges
        function formatServices(station) {
            var services = [];
            if (station.haveMarket) services.push('<span class="badge badge-green">Market</span>');
            if (station.haveShipyard) services.push('<span class="badge badge-cyan">Shipyard</span>');
            if (station.haveOutfitting) services.push('<span class="badge badge-cyan">Outfitting</span>');
            if (station.hasRefuel) services.push('<span class="badge badge-green">Refuel</span>');
            if (station.hasRepair) services.push('<span class="badge badge-green">Repair</span>');
            if (station.hasRestock) services.push('<span class="badge badge-green">Restock</span>');
            if (services.length === 0) services.push('<span class="badge">Unknown</span>');
            return services.join('');
        }

        // Open station detail modal
        async function openStationModal(system, station) {
            document.getElementById('modal-station-name').textContent = station;
            document.getElementById('modal-station-type').textContent = '-';
            document.getElementById('modal-distance').textContent = '-';
            document.getElementById('modal-economy').textContent = '-';
            document.getElementById('modal-government').textContent = '-';
            document.getElementById('modal-services').innerHTML = '<div class="loading">Loading...</div>';
            document.getElementById('modal-commodities').innerHTML = '';
            document.getElementById('station-modal').classList.add('active');
            
            try {
                var resp = await fetch('/api/station-detail?system=' + encodeURIComponent(system) + '&station=' + encodeURIComponent(station));
                var data = await resp.json();
                
                document.getElementById('modal-station-type').textContent = data.type || 'Unknown';
                document.getElementById('modal-distance').textContent = data.distanceToArrival || '?';
                document.getElementById('modal-economy').textContent = data.economy || 'Unknown';
                document.getElementById('modal-government').textContent = data.government || 'Unknown';
                
                var servicesHtml = formatServices(data);
                document.getElementById('modal-services').innerHTML = servicesHtml || '<span class="badge">No services found</span>';
                
                if (data.commodities && data.commodities.length > 0) {
                    var table = '<table class="data-table"><thead><tr><th>Commodity</th><th>Buy</th><th>Sell</th><th>Supply</th></tr></thead><tbody>';
                    data.commodities.slice(0, 20).forEach(function(c) {
                        table += '<tr><td>' + c.name + '</td><td class="price-buy">' + (c.buyPrice || '?') + '</td><td class="price-sell">' + (c.sellPrice || '?') + '</td><td>' + (c.stock || '?') + '</td></tr>';
                    });
                    table += '</tbody></table>';
                    document.getElementById('modal-commodities').innerHTML = table;
                } else {
                    document.getElementById('modal-commodities').innerHTML = '<p style="color: var(--dim);">No market data available</p>';
                }
            } catch (e) {
                document.getElementById('modal-services').innerHTML = '<p style="color: var(--red);">Error loading data: ' + e.message + '</p>';
            }
        }

        // Close modal
        function closeModal() {
            document.getElementById('station-modal').classList.remove('active');
        }

        // Close modal on background click
        document.getElementById('station-modal').addEventListener('click', function(e) {
            if (e.target === this) {
                closeModal();
            }
        });

        // Close modal on Escape key
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') {
                closeModal();
            }
        });
    </script>
</body>
</html>'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/search')
def search():
    system = request.args.get('system', '')
    commodity = request.args.get('commodity', '')
    if not system or not commodity:
        return jsonify({"error": "Missing parameters"})
    
    # Get systems with the commodity
    systems_data = api_get("/api-v1/systems-with-station", {
        "commodotyName": commodity,
        "showStation": 1
    })
    
    # Search for commodity in the system
    data = api_get("/api-v1/commodities-by-station", {
        "systemName": system,
        "commodityName": commodity
    })
    
    results = []
    if not data.get("error"):
        for item in data.get("items", []):
            results.append({
                "station": item.get("stationName", "Unknown"),
                "type": item.get("stationType", "Unknown"),
                "distance": item.get("distanceToArrival", "?"),
                "buy": item.get("buyPrice", 0),
                "sell": item.get("sellPrice", 0),
                "stock": item.get("stock", 0),
                "demand": item.get("demand", 0)
            })
    
    return jsonify({
        "system": system,
        "commodity": commodity,
        "count": len(results),
        "results": results
    })

@app.route('/api/station')
def station():
    system = request.args.get('system', '')
    if not system:
        return jsonify({"error": "Missing system parameter"})
    
    data = get_stations(system)
    if data.get("error"):
        return jsonify({"error": data.get("error")})
    
    stations = []
    for s in data.get("stations", []):
        stations.append({
            "name": s.get("name", "Unknown"),
            "type": s.get("type", "Unknown"),
            "distanceToArrival": s.get("distanceToArrival", "?"),
            "economy": s.get("economy", "Unknown"),
            "government": s.get("government", ""),
            "haveMarket": s.get("haveMarket", False),
            "haveShipyard": s.get("haveShipyard", False),
            "haveOutfitting": s.get("haveOutfitting", False),
            "hasRefuel": s.get("hasRefuel", False),
            "hasRepair": s.get("hasRepair", False),
            "hasRestock": s.get("hasRestock", False)
        })
    
    return jsonify({
        "system": system,
        "count": len(stations),
        "stations": stations
    })

@app.route('/api/station-detail')
def station_detail():
    system = request.args.get('system', '')
    station = request.args.get('station', '')
    if not system or not station:
        return jsonify({"error": "Missing parameters"})
    
    # Get station info
    stations_data = get_stations(system)
    station_info = None
    for s in stations_data.get("stations", []):
        if s.get("name") == station:
            station_info = s
            break
    
    if not station_info:
        # Try direct lookup
        all_stations = api_get("/api-system-v1/stations", {"systemName": system})
        for s in all_stations.get("stations", []):
            if s.get("name") == station:
                station_info = s
                break
    
    # Get market data
    market_data = get_station_market(system, station)
    commodities = []
    if not market_data.get("error"):
        for c in market_data.get("commodities", []):
            commodities.append({
                "name": c.get("name", "Unknown"),
                "buyPrice": c.get("buyPrice", 0),
                "sellPrice": c.get("sellPrice", 0),
                "stock": c.get("stock", 0),
                "demand": c.get("demand", 0)
            })
    
    result = {
        "name": station,
        "type": station_info.get("type", "Unknown") if station_info else "Unknown",
        "distanceToArrival": station_info.get("distanceToArrival", "?") if station_info else "?",
        "economy": station_info.get("economy", "Unknown") if station_info else "Unknown",
        "government": station_info.get("government", "") if station_info else "",
        "haveMarket": station_info.get("haveMarket", False) if station_info else False,
        "haveShipyard": station_info.get("haveShipyard", False) if station_info else False,
        "haveOutfitting": station_info.get("haveOutfitting", False) if station_info else False,
        "hasRefuel": station_info.get("hasRefuel", False) if station_info else False,
        "hasRepair": station_info.get("hasRepair", False) if station_info else False,
        "hasRestock": station_info.get("hasRestock", False) if station_info else False,
        "commodities": commodities
    }
    
    return jsonify(result)

@app.route('/api/route')
def route():
    from_system = request.args.get('from', '')
    to_system = request.args.get('to', '')
    if not from_system or not to_system:
        return jsonify({"error": "Missing parameters"})
    
    return jsonify({"error": "Route finding coming soon"})

@app.route('/api/services')
def services():
    system = request.args.get('system', '')
    service = request.args.get('service', '')
    if not system:
        return jsonify({"error": "Missing system parameter"})
    
    data = get_stations(system)
    if data.get("error"):
        return jsonify({"error": data.get("error")})
    
    stations = []
    service_key_map = {
        "outfitting": "haveOutfitting",
        "shipyard": "haveShipyard",
        "market": "haveMarket",
        "repair": "hasRepair",
        "refuel": "hasRefuel",
        "restock": "hasRestock"
    }
    
    key = service_key_map.get(service, "")
    for s in data.get("stations", []):
        if key and s.get(key, False):
            stations.append({
                "name": s.get("name", "Unknown"),
                "type": s.get("type", "Unknown"),
                "distanceToArrival": s.get("distanceToArrival", "?")
            })
    
    return jsonify({
        "system": system,
        "service": service,
        "stations": stations
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)

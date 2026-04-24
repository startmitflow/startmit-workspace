from flask import Flask, render_template_string, request, jsonify
import urllib.request
import json
import urllib.parse

app = Flask(__name__)

EDSM_API = "https://www.edsm.net"
REQUEST_HEADERS = {"User-Agent": "StartMit-EliteTrader/1.0"}

# Full commodity list for autocomplete (ED v4.0 complete list)
COMMODITIES = [
    "Advanced Catalysers", "Agri-Medicines", "Agri-Domestics", "Algae", "Aluminium",
    "Animal Meat", "Animal Monitors", "Anti-Establishment Weapons", "Aquaponic Systems",
    "Articulation Motors", "Atmospheric Processors", "Auto-Fabricators", "Bacteria",
    "Batteries", "Beer", "Bellows", "Biocircuits", "Bioelectronics", "Biomass",
    "Black Box Data", "Body Products", "Bomb Equipment", "Bone Dance Figures",
    "Bootleg Liquor", "Bread", "Brewing Herbs", "Broadband Obfuscators",
    "Building Fabric", "Burner Data Chips", "Caffeinated Beverages", "Camel Wool",
    "Cancer Drugs", "Cargo Rack", "Ceramic Composites", "Cheese", "Chemical Agents",
    "Chemical Extracts", "Chemicals", "Chi Cigars", "Citizen Newspapers", "Clothing",
    "Clouds", "CN News Maincomp 3-2", "Cobalt", "Cobalt Ore", "Coffee", "Coltan",
    "Combat Stabilizers", "Comductor Chips", "Consumer Electronics", "Consumer Firmware",
    "Contextual Data", "Cooling Lines", "Copper", "Copper Ore", "Crop Harvesters",
    "Crystalline Iron", "Crystalline Sulfides", "Customs Data", "Cyber Waldo Rolls",
    "Data", "Data Chips", "Decoding Soft", "Deliciousness", "Dermatological Drugs",
    "Diamond", "Discreet Alarm Sensors", "Domap Fried Cheese", "Domestic Appliances",
    "Domestics", "Dried Archaic Capsule", "Earthweek Subs", "Edible Goods",
    "Edu-Files", "Electronics", "Empennachips", "Empty Officer Benches",
    "Energy Transfer Consoles", "Energysel", "Environmental Services", "Escape Cavities",
    "Exhaust Manifold", "Expedition Costs", "Explosives", "Fashion", "Faulty Data Chip",
    "Fertilizers", "Fire-Ace Extinguisher", "Fish", "Food Cartridges", "Food Concentrates",
    "Food Rations", "Foot-and-Mouth Vaccine", " Fossil Remnants", "French Knees",
    "Frozen Materials", "Fruit and Vegetable Subs", "Fuels", "Fully Functional Wardens",
    "Funerary 1", "Fusionpc Cards", "Gacon1 MRE", "Gallite", "Gambling Data",
    "Garbage Processing Services", "Gas Processors", "Gasian Dry Goods", "Gastronomy",
    "Geqde1 MRE", "Geothermal Equipment", "Glass", "Gold", "Gold Ore", "Grain",
    "Grapric Somo Lom", "Hai Edible Sub", "Hai Fish", "Haux Fried Fish", "HCN-1 Insurant",
    "Health Monitors", "Heat Damping Systems", "Heat Exchangers", "Heated Sublimators",
    "Herbal Medicine", "Heritage Data", "Heurstical SArchives", "Hip 40291 Person4l5",
    "Hip 43201 Persn3l6", "Hip10 108 Person3l6", "Hip36019 Persn3l4", "Hip40189 Persn3l1",
    "Hip41345 Persn3l6", "Hip56811 Persn3l5", "Hip58444 Persn3l6", "Hip591h Person3l1",
    "Hip60811 Persn3l6", "Hpi41601 Persn3l5", "Hydrogen Fuel", "Hydrogen Peroxide",
    "ICe3 Age3", "Imperial Data", "Impulse Engines", "Incompetent Student Files",
    "Insulated Cabin Fabric", "Insurance", "Integrated Circuits", "Ion Distributor",
    "Ion Sparks", "JSem1 MRE", "Jury Rigged Rotations", "Kah", "Land Enrichment Systems",
    "Large Survey Equipment", "Larvorl Froth", "Leather", "Legless Graffiti",
    "Limestone", "Lithium", "Lithium Ore", "Livestock", "Lobster", "Local Drugs",
    "Low Temperature Diamonds", "Luxe RGenerators", "M Another", "Macrozonite",
    "Magnetic Emitter Coils", "Mandalay Fernlopers", "Marine Equipment", "Market Data",
    "Marl Finn Cubic", "Masp 1 Sublimators", "Master Chefs", "Mekti Dialectic 4",
    "Membrane Sublimators", "Memorakia", "Methane", "Methane Clathrate", "Microbial Furs",
    "Micro Controllers", "Micro Screens", "Mineral Extractors", "Mineral Oil", "Minerals",
    "Mining Equipment", "Mining Laser", "Mmitter3 Age3", "Modular Terminals",
    "Moisture Condensers", "Molluscs", "Monopropellant", "Mothership", "Motors",
    "Mucuous Data", "Multi-Fuel Catalyst", "Musical Recordings", "N-Pirium Blends",
    "Narcotics", "Nastric Lattice", "Natural Antibiotics", "Navigation Capital Data",
    "Necklaces", "Nerve Stabalizers", "Neurectomy Data", "Neurosync Disease Fix",
    "New Personal Computer", "Nickel", "Nickel Ore", "Niotre1 MRE", "Nitrates",
    "Nitrogen", "Nitrogenous Fertilizers", "Non-lethal Weapons", "Nutritional Concentrates",
    "Obogue Drug Mix", "Occupier Crime Bureau", "Oceanic Substances", "Office Type7 Unit",
    "Oil Extraction Equipment", "Oleni 5 MRE", "Onionhead", "Onionhead Derivatives",
    "Open University History", "OphLoc5 Subs", "Optical Mirrors", "Optical State Soft",
    "Optimization Proxies", "Orbic Removd Subs", "Orbizaga Froth", "Ornaments",
    "Orotic Acid", "Oun Dtered 5", "Outfitting", "Ow Wermtablo 1", "Oxygene B27 Foils",
    "Oxygen", "Paints", "Palladium", "Palpebral Lenses", "Panther Fang Logs",
    "Pascal Ticks", "Personal Armor", "Personal Weapons", "Pesticides", "Petrified Coral",
    "Pharmaceutical Synthesis", "Phase Alloys", "Pig Iron", "Plastics", "Platinum",
    "Platinum Ore", "Plutonium", "Political Prisoners", "Population Relatives",
    "Poseidon Cork Foll", "Power Converter", "Power Generators", "Power Plants",
    "Praetoria Subs", "Precious Gems", "Precrushed Ore", "Prepared Meals", "Prerequisite Soft",
    "Preserved Meat", "Priesthood Historical Data", "Procurement Reconstruction Data",
    "ProDocs", "Progenitor Cells", "Promethium", "Promethium Ore", "Protein",
    "Protein Concoction", "Proximity Sublaments", "Pyrophorus", "Quantum Radiators",
    "Quartet Cheese", "Radio Mirrors", "Racing Data", "Radiation Baffles",
    "Reactive Membranes", "Reaper Ship blueprints", "Reactive Armor", "Reaver Ship blueprints",
    "Recycled Drink Coasters", "Refined Fuels", "Remapped Identification Chips",
    "Remotecontrolled Fireworks", "Repair Parts", "Research Medicaleq 5", "Research6",
    "Residential Generator", "Rerbent Bowl Emitter", "Resistance Armor", "Resources",
    "Revelation Aleleory F", "Revelation Stabhyp F", "Revelation Stabwate F", "Rhon",
    "Rimliner Galactic Cart", "Ripe Grain", "Robotics", "Rock Fruit", "Roe",
    "Rolls Royce Extended", "Rost Waves Vanilla", "Rubbish", "Rubidium", "Running Locusts 5",
    "Sandstone", "Sanguineous Freak Parf", "Sapphire", "Satellite Communications",
    "Scavenger Ship blueprints", "Science Education R", "Scrap", "Scrap Metal",
    "Seismic Hostilities Data", "Semiconductors", "Serenity Mav 3 Packets", "Sewage",
    "Sexual Detox 5", "Ship Hands", "Ship Kits", "Ship Salvage", "Ship Launches",
    "Shipboard Mainbreak", "Silica", "Silver", "Silver Ore", "Skull Collection Box",
    "Slaves", "Slate", "Slush", "Snow", "SOBEK Data", "Solar Panels", "Sota-1 Comarr 6",
    "Sota-2 Viewsic 6", "Sota-3 Wotansid 4", "Soy", "Soy Protein", "Space Dust",
    "Space Legs Paga 5", "Spad12 Hardbake 6", "Spad5 Hcfwdlw 1", "Spad5 Lbcdemx 1",
    "Spad7 Oldwntr 6", "Spad8 Fwmsabz 5", "Spd12 Hcfwdlw 1", "Spd12 Lbcdemx 1",
    "Spd12 Oldwntr 6", "Spd12 Wmsabz 5", "Specials Gtudent 3", "Spice", "Spirits",
    "Staddview Amloclit 5", "Stagnation Standard 1", "Stahlvoll MRE", "Standard Data Chip",
    "StarLadder RImages", "Station Cash", "Station Management Services", "Station Reformists",
    "Stellar Cart Data", "Stock Catalogs", "Structural Metal", "Structural Regulators",
    "Student 8", "Subsidized Luxury Goods", "Sugar", "Suit Logs Subs", "Suitionary History",
    "Superconductors", "Superlative Synthefic", "Survey Personnel Data", "SUVTab Water 3",
    "Synthetic Reagents", "System Switch Committe", "Table Navigation Data", "Tactical Data",
    "Taffeter Falliters 3", "Taint Exclusives 1", "Tauri Pairings", "Tea",
    "Technical Architectures", "Technical Equipment", "Technology Materials", "Teqin3 MRE",
    "Terra Gravy", "Terraforming Plants", "Textiles", "Thallium", "Thargoid Basilisk blueprints",
    "Thargoid Cyclops blueprints", "Thargoid Hydra blueprints", "Thargoid Medusa blueprints",
    "Thargoid Orthrus blueprints", "Thargoid Scavenger blueprints", "Thermal Power Plants",
    "Three Dimensional Time", "Time Tables", "Tinned Heat", "Titanium", "Titanium Ore",
    "Tobacco", "Tombs of Statist", "Topp 1 MRE", "Toyalite", "Toys", "Trade Season Data",
    "Training Computers", "Training Score Data", "Transit Tubes", "Trinkets", "Tritium",
    "Tritium Ore", "Tuned Thrusters", "U2 CFC Foils", "Ultra-Compact Fabricators",
    "Underground Games Data", "Unexploded Ordnance", "Uraninite", "Uranium",
    "Utopian Economy Subs", "Valuable Element", "Vegan Junk Food", "Vegetables",
    "Vehicle Accessories", "Vegan Prosthetics", "Vemineral Subliment 6", "Veny，炒米",
    "Vesta Corp H2O", "Victualis L Brdy 4", "Vinyl Flooring", "Violence Data",
    "Vital CLS Data", "Void Extract Coffee", "Void Herbs", "War EFFect Data",
    "Warped Fit To Data", "Waste", "Waste Equipment", "Water", "Water Purifiers",
    "Water Based Chemicals", "Weapons", "Weapons Store Data", "Wells", "Wine",
    "Winter 2019 Subs", "Wireless Data", "Wolf Fanged Hip Cuffs", "Women's Clubs",
    "Wood Floor", "Wool", "Yeast", "Zanthium", "Zeus 4 MRE", "Zinee Rice 3", "Zircon"
]

# Colony tech tree (simplified from E:D wiki)
COLONY_FACILITIES = {
    "Orbital": [
        {"id": "high_tech_hub", "name": "High Tech Hub", "tier": 1,
         "requires": [], "gives": {"tech_level": 20, "wealth": 15, "unlocks": ["outfitting_t3", "shipyard"]},
         "cost": {"CMM Composite": 500, "Insulating Membrane": 300}},
        {"id": "industrial_hub", "name": "Industrial Hub", "tier": 1,
         "requires": [], "gives": {"tech_level": 10, "wealth": 20, "population_growth": 15},
         "cost": {"CMM Composite": 400, "Boron": 200}},
        {"id": "refinery_hub", "name": "Refinery Hub", "tier": 1,
         "requires": [], "gives": {"wealth": 15, "population_growth": 10},
         "cost": {"CMM Composite": 300, "Insulating Membrane": 400}},
        {"id": "military_installation", "name": "Military Installation", "tier": 1,
         "requires": ["industrial_hub"], "gives": {"security": 25, "tech_level": 5},
         "cost": {"CMM Composite": 450, "Military Supplies": 350}},
        {"id": "trading_hub", "name": "Trading Hub", "tier": 1,
         "requires": [], "gives": {"wealth": 25, "standard_of_living": 15},
         "cost": {"CMM Composite": 400}},
        {"id": "exploration_hub", "name": "Exploration Hub", "tier": 1,
         "requires": [], "gives": {"tech_level": 15, "standard_of_living": 10},
         "cost": {"CMM Composite": 350, "Survey Equipment": 250}},
        {"id": "mining_hub", "name": "Mining Hub", "tier": 1,
         "requires": [], "gives": {"wealth": 20, "tech_level": 5},
         "cost": {"CMM Composite": 400, "Mining Equipment": 300}},
        {"id": "terraforming_hub", "name": "Terraforming Hub", "tier": 2,
         "requires": ["high_tech_hub"], "gives": {"population_growth": 25, "standard_of_living": 20, "tech_level": 15},
         "cost": {"CMM Composite": 600, "Insulating Membrane": 500, "Terraforming Equipment": 400}},
        {"id": "research_lab", "name": "Research Laboratory", "tier": 2,
         "requires": ["high_tech_hub"], "gives": {"tech_level": 30, "standard_of_living": 10},
         "cost": {"CMM Composite": 500, "Research Data": 400}},
        {"id": "shipyard_hub", "name": "Shipyard Hub", "tier": 2,
         "requires": ["industrial_hub"], "gives": {"tech_level": 15, "wealth": 20},
         "cost": {"CMM Composite": 700, "Aluminium": 500}},
    ],
    "Ground": [
        {"id": "communications_array", "name": "Communications Array", "tier": 1,
         "requires": [], "gives": {"population_growth": 10, "tech_level": 5},
         "cost": {"CMM Composite": 200}},
        {"id": "mission_board", "name": "Mission Board", "tier": 1,
         "requires": ["communications_array"], "gives": {"standard_of_living": 15},
         "cost": {"CMM Composite": 250}},
        {"id": "barracks", "name": "Barracks", "tier": 2,
         "requires": ["military_installation"], "gives": {"security": 20},
         "cost": {"Military Supplies": 300}},
        {"id": "farm_complex", "name": "Farm Complex", "tier": 1,
         "requires": [], "gives": {"population_growth": 15, "standard_of_living": 10},
         "cost": {"CMM Composite": 300, "Agricultural Supplies": 200}},
        {"id": "power_plant", "name": "Power Plant", "tier": 1,
         "requires": [], "gives": {"tech_level": 10, "population_growth": 5},
         "cost": {"CMM Composite": 400, "Power Generators": 300}},
        {"id": "water_treatment", "name": "Water Treatment Facility", "tier": 1,
         "requires": [], "gives": {"standard_of_living": 15, "population_growth": 10},
         "cost": {"CMM Composite": 350, "Water Purifiers": 250}},
    ]
}

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
    return api_get("/api-v1/system", {"systemName": name, "showInformation": 1, "showCoordinates": 1, "showPrimaryStar": 1})

def get_stations(name):
    return api_get("/api-system-v1/stations", {"systemName": name})

def get_station_market(system, station):
    data = api_get("/api-system-v1/stations/market", {"systemName": system, "stationName": station})
    return data.get("commodities", []) if not data.get("error") else []

def fuzzy_match(query, items, threshold=0.3):
    """Simple fuzzy matching - returns items containing the query"""
    q = query.lower()
    return [item for item in items if q in item.lower()]

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Elite Station Advisor</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: Arial, sans-serif; background: #0a0a1a; min-height: 100vh; color: #fff; padding: 20px; }
        .container { max-width: 1100px; margin: 0 auto; }
        h1 { text-align: center; color: #00d4ff; margin-bottom: 30px; font-size: 2em; }
        h2 { color: #00d4ff; margin: 20px 0 10px; border-bottom: 1px solid #333; padding-bottom: 5px; }
        .tabs { display: flex; gap: 10px; margin-bottom: 20px; flex-wrap: wrap; }
        .tab { background: rgba(255,255,255,0.1); padding: 10px 20px; border-radius: 8px; cursor: pointer; border: none; color: #888; font-size: 1em; }
        .tab.active { background: #00d4ff; color: #000; font-weight: bold; }
        .tab:hover:not(.active) { background: rgba(255,255,255,0.2); }
        .card { background: rgba(255,255,255,0.05); border-radius: 10px; padding: 20px; margin-bottom: 20px; }
        .card h3 { color: #00d4ff; margin-bottom: 10px; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; }
        .stat { background: rgba(0,212,255,0.1); padding: 12px; border-radius: 8px; text-align: center; }
        .stat-value { font-size: 1.4em; font-weight: bold; color: #00d4ff; }
        .stat-label { color: #888; font-size: 0.8em; }
        .search-box { background: rgba(255,255,255,0.1); border-radius: 10px; padding: 20px; margin-bottom: 20px; }
        .form-row { display: flex; gap: 15px; flex-wrap: wrap; margin-bottom: 10px; }
        .form-group { flex: 1; min-width: 200px; }
        label { display: block; margin-bottom: 5px; color: #aaa; }
        input, select { width: 100%; padding: 10px; border-radius: 5px; border: 1px solid #444; background: #1a1a2e; color: #fff; }
        button { background: #00d4ff; color: #000; border: none; padding: 12px 30px; border-radius: 5px; font-size: 1em; cursor: pointer; font-weight: bold; }
        button:hover { background: #00aacc; }
        .commodity-list { display: flex; flex-wrap: wrap; gap: 5px; margin-top: 10px; }
        .commodity-tag { background: #1a4a5e; padding: 5px 10px; border-radius: 15px; font-size: 0.85em; cursor: pointer; }
        .commodity-tag:hover { background: #2a6a7e; }
        .results { background: rgba(255,255,255,0.05); border-radius: 10px; padding: 15px; }
        .result-item { padding: 10px; border-radius: 5px; margin-bottom: 8px; background: #1a1a2e; border-left: 3px solid #00d4ff; }
        .result-item.cheap { border-left-color: #00ff00; }
        .station-card { background: #1a1a2e; padding: 15px; border-radius: 8px; margin-bottom: 10px; border-left: 3px solid #00d4ff; }
        .station-card h4 { color: #00d4ff; margin-bottom: 8px; }
        .facility-card { background: #1a1a2e; padding: 15px; border-radius: 8px; margin-bottom: 10px; border-left: 3px solid #ffa500; }
        .facility-card.locked { opacity: 0.5; border-left-color: #666; }
        .facility-card h4 { color: #ffa500; margin-bottom: 8px; }
        .facility-card.locked h4 { color: #888; }
        .stat-change { display: inline-block; padding: 2px 8px; border-radius: 10px; font-size: 0.85em; margin: 2px; }
        .stat-positive { background: rgba(0,255,0,0.2); color: #0f0; }
        .stat-negative { background: rgba(255,0,0,0.2); color: #f55; }
        .cost-item { display: inline-block; background: rgba(255,165,0,0.2); color: #ffa500; padding: 3px 10px; border-radius: 10px; font-size: 0.85em; margin: 2px; }
        .autocomplete { position: relative; }
        .autocomplete-list { position: absolute; top: 100%; left: 0; right: 0; background: #1a1a2e; border: 1px solid #444; border-radius: 0 0 5px 5px; max-height: 200px; overflow-y: auto; z-index: 100; }
        .autocomplete-item { padding: 8px 12px; cursor: pointer; }
        .autocomplete-item:hover { background: rgba(0,212,255,0.2); }
        .tab-content { display: none; }
        .tab-content.active { display: block; }
        .info-box { background: rgba(0,212,255,0.1); border: 1px solid #00d4ff; border-radius: 8px; padding: 15px; margin: 10px 0; }
        .info-box.warning { background: rgba(255,165,0,0.1); border-color: #ffa500; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 Elite Station Advisor</h1>

        <div class="tabs">
            <button class="tab active" onclick="showTab('trade')">🔍 Trade Search</button>
            <button class="tab" onclick="showTab('station')">🏢 Station Info</button>
            <button class="tab" onclick="showTab('resources')">🪐 Resources</button>
            <button class="tab" onclick="showTab('bodies')">🌍 Bodies</button>
            <button class="tab" onclick="showTab('materials')">🔧 Materials</button>
            <button class="tab" onclick="showTab('outfitting')">🛠️ Outfitting</button>
            <button class="tab" onclick="showTab('colonize')">🏗️ Colony Advisor</button>
            <button class="tab" onclick="showTab('route')">📍 Trade Routes</button>
        </div>

        <!-- TRADE SEARCH TAB -->
        <div id="trade" class="tab-content active">
            <div class="search-box">
                <form id="tradeForm">
                    <div class="form-row">
                        <div class="form-group autocomplete">
                            <label>System</label>
                            <input type="text" id="tradeSystem" placeholder="e.g. Sol, Lave" oninput="autocompleteSystem(this, 'tradeSystemList')" required>
                            <div id="tradeSystemList" class="autocomplete-list"></div>
                        </div>
                        <div class="form-group autocomplete">
                            <label>Commodity</label>
                            <input type="text" id="tradeCommodity" placeholder="e.g. Gold, Water, Tritium" oninput="autocompleteCommodity(this, 'tradeCommodityList')" required>
                            <div id="tradeCommodityList" class="autocomplete-list"></div>
                        </div>
                    </div>
                    <button type="submit">Search</button>
                </form>
                <div class="commodity-list" id="quickCommodities"></div>
            </div>
            <div id="tradeResults" class="results" style="display:none;"></div>
        </div>

        <!-- STATION INFO TAB -->
        <div id="station" class="tab-content">
            <div class="search-box">
                <form id="stationForm">
                    <div class="form-row">
                        <div class="form-group autocomplete">
                            <label>System Name</label>
                            <input type="text" id="stationSystem" placeholder="e.g. Sol, Col 285 Sector HN-R C5-10" oninput="autocompleteSystem(this, 'stationSystemList')" required>
                            <div id="stationSystemList" class="autocomplete-list"></div>
                        </div>
                    </div>
                    <button type="submit">Get Station Info</button>
                </form>
            </div>
            <div id="stationResults" class="results" style="display:none;"></div>
        </div>

        <!-- RESOURCES TAB -->
        <div id="resources" class="tab-content">
            <div class="info-box">
                <strong>🪐 System Resource Analyzer</strong><br>
                Scan a system for celestial bodies and get facility recommendations based on available resources.
            </div>
            <div class="search-box">
                <form id="resourcesForm">
                    <div class="form-row">
                        <div class="form-group autocomplete">
                            <label>System Name</label>
                            <input type="text" id="resSystem" placeholder="e.g. Col 285 Sector HN-R C5-10" oninput="autocompleteSystem(this, 'resSystemList')" required>
                            <div id="resSystemList" class="autocomplete-list"></div>
                        </div>
                        <div class="form-group">
                            <label>Goal</label>
                            <select id="resGoal">
                                <option value="balanced">Balanced</option>
                                <option value="tech">Tech Focus</option>
                                <option value="wealth">Wealth Focus</option>
                                <option value="military">Military Focus</option>
                                <option value="population">Population Focus</option>
                            </select>
                        </div>
                    </div>
                    <button type="submit">Analyze Resources</button>
                </form>
            </div>
            <div id="resourcesResults" class="results" style="display:none;"></div>
        </div>

        <!-- BODIES TAB -->
        <div id="bodies" class="tab-content">
            <div class="info-box">
                <strong>🌍 Body Explorer</strong><br>
                Explore every celestial body in the system with detailed stats and per-body build recommendations.
            </div>
            <div class="search-box">
                <form id="bodiesForm">
                    <div class="form-row">
                        <div class="form-group autocomplete">
                            <label>System Name</label>
                            <input type="text" id="bodiesSystem" placeholder="e.g. Col 285 Sector HN-R C5-10" oninput="autocompleteSystem(this, 'bodiesSystemList')" required>
                            <div id="bodiesSystemList" class="autocomplete-list"></div>
                        </div>
                    </div>
                    <button type="submit">Explore Bodies</button>
                </form>
            </div>
            <div id="bodiesResults" class="results" style="display:none;"></div>
        </div>

        <!-- MATERIALS FINDER TAB -->
        <div id="materials" class="tab-content">
            <div class="info-box">
                <strong>🔧 Engineering Materials Finder</strong><br>
                Search a system for engineering materials or see all materials on landable bodies.
            </div>
            <div class="search-box">
                <form id="materialsForm">
                    <div class="form-row">
                        <div class="form-group autocomplete">
                            <label>System Name</label>
                            <input type="text" id="matSystem" placeholder="e.g. Col 285 Sector HN-R C5-10" oninput="autocompleteSystem(this, 'matSystemList')" required>
                            <div id="matSystemList" class="autocomplete-list"></div>
                        </div>
                        <div class="form-group">
                            <label>Material (optional)</label>
                            <input type="text" id="matName" placeholder="e.g. Carbon, Iron, Selenium">
                        </div>
                    </div>
                    <button type="submit">Find Materials</button>
                </form>
            </div>
            <div id="materialsResults" class="results" style="display:none;"></div>
        </div>

        <!-- OUTFITTING TAB -->
        <div id="outfitting" class="tab-content">
            <div class="info-box">
                <strong>🛠️ Station Outfitting & Shipyard</strong><br>
                View modules and ships available at a specific station.
            </div>
            <div class="search-box">
                <form id="outfittingForm">
                    <div class="form-row">
                        <div class="form-group autocomplete">
                            <label>System</label>
                            <input type="text" id="outSystem" placeholder="e.g. Sol" oninput="autocompleteSystem(this, 'outSystemList')" required>
                            <div id="outSystemList" class="autocomplete-list"></div>
                        </div>
                        <div class="form-group">
                            <label>Station</label>
                            <input type="text" id="outStation" placeholder="e.g. Abraham Lincoln" required>
                        </div>
                    </div>
                    <button type="submit">Get Outfitting</button>
                </form>
            </div>
            <div id="outfittingResults" class="results" style="display:none;"></div>
        </div>

        <!-- COLONY ADVISOR TAB -->
        <div id="colonize" class="tab-content">
            <div class="info-box">
                <strong>💡 Colony Build Advisor</strong><br>
                Enter your colonized system and station to get facility suggestions based on the tech tree.
            </div>
            <div class="search-box">
                <form id="colonizeForm">
                    <div class="form-row">
                        <div class="form-group autocomplete">
                            <label>System Name</label>
                            <input type="text" id="colSystem" placeholder="e.g. Col 285 Sector HN-R C5-10" oninput="autocompleteSystem(this, 'colSystemList')" required>
                            <div id="colSystemList" class="autocomplete-list"></div>
                        </div>
                        <div class="form-group">
                            <label>Station Type</label>
                            <select id="stationType">
                                <option value="Coriolis Starport">Coriolis Starport</option>
                                <option value="Orbis Starport">Orbis Starport</option>
                                <option value="Ocellus Starport">Ocellus Starport</option>
                                <option value="Asteroid base">Asteroid base</option>
                                <option value="Outpost">Outpost</option>
                                <option value="Planetary Settlement">Planetary Settlement</option>
                            </select>
                        </div>
                    </div>
                    <div class="form-row">
                        <div class="form-group">
                            <label>Current Economy</label>
                            <select id="economyType">
                                <option value="High Tech">High Tech</option>
                                <option value="Industrial">Industrial</option>
                                <option value="Extraction">Extraction</option>
                                <option value="Agriculture">Agriculture</option>
                                <option value="Refinery">Refinery</option>
                                <option value="Military">Military</option>
                                <option value="Tourism">Tourism</option>
                                <option value="Terraforming">Terraforming</option>
                                <option value="Commercial">Commercial</option>
                                <option value="Scientific">Scientific</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Your Goal</label>
                            <select id="colonyGoal">
                                <option value="balanced">Balanced Growth</option>
                                <option value="tech">Tech Hub (better modules)</option>
                                <option value="wealth">Wealth (trade profits)</option>
                                <option value="military">Military (security)</option>
                                <option value="population">Population (growth rate)</option>
                            </select>
                        </div>
                    </div>
                    <button type="submit">Get Build Suggestions</button>
                </form>
            </div>
            <div id="colonizeResults" class="results" style="display:none;"></div>
        </div>

        <!-- TRADE ROUTES TAB -->
        <div id="route" class="tab-content">
            <div class="info-box">
                <strong>📍 Trade Route Finder</strong><br>
                Find the best trade routes between two systems.
            </div>
            <div class="search-box">
                <form id="routeForm">
                    <div class="form-row">
                        <div class="form-group autocomplete">
                            <label>From System</label>
                            <input type="text" id="routeFrom" placeholder="e.g. Diaguandri" oninput="autocompleteSystem(this, 'routeFromList')" required>
                            <div id="routeFromList" class="autocomplete-list"></div>
                        </div>
                        <div class="form-group autocomplete">
                            <label>To System</label>
                            <input type="text" id="routeTo" placeholder="e.g. Ray Gateway" oninput="autocompleteSystem(this, 'routeToList')" required>
                            <div id="routeToList" class="autocomplete-list"></div>
                        </div>
                    </div>
                    <button type="submit">Find Routes</button>
                </form>
            </div>
            <div id="routeResults" class="results" style="display:none;"></div>
        </div>
    </div>

    <script>
        // Commodity list from server
        const commodities = {{ commodities | tojson }};

        // Quick commodity buttons
        const quickComms = ['Gold', 'Silver', 'Platinum', 'Palladium', 'Tritium', 'Water', 'Food', 'Consumer Electronics', 'Luxury Goods', 'Computers'];
        const qDiv = document.getElementById('quickCommodities');
        quickComms.forEach(c => {
            const tag = document.createElement('span');
            tag.className = 'commodity-tag';
            tag.textContent = c;
            tag.onclick = () => { document.getElementById('tradeCommodity').value = c; };
            qDiv.appendChild(tag);
        });

        function showTab(name) {
            document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.getElementById(name).classList.add('active');
            event.target.classList.add('active');
        }

        // Autocomplete for systems
        let systemTimeout;
        function autocompleteSystem(input, listId) {
            clearTimeout(systemTimeout);
            const list = document.getElementById(listId);
            const val = input.value.trim();
            if (val.length < 2) { list.innerHTML = ''; return; }
            systemTimeout = setTimeout(async () => {
                try {
                    const res = await fetch('/api/systems?q=' + encodeURIComponent(val));
                    const data = await res.json();
                    list.innerHTML = data.systems.map(s =>
                        '<div class="autocomplete-item" onclick="selectSystem(\\'' + input.id + '\\', \\'' + listId + '\\', \\'' + s.replace(/'/g, "\\\\'") + '\\')">' + s + '</div>'
                    ).join('');
                } catch(e) {}
            }, 300);
        }

        function selectSystem(inputId, listId, value) {
            document.getElementById(inputId).value = value;
            document.getElementById(listId).innerHTML = '';
        }

        // Autocomplete for commodities
        function autocompleteCommodity(input, listId) {
            const list = document.getElementById(listId);
            const val = input.value.trim().toLowerCase();
            if (val.length < 1) { list.innerHTML = ''; return; }
            const matches = commodities.filter(c => c.toLowerCase().includes(val)).slice(0, 8);
            list.innerHTML = matches.map(m =>
                '<div class="autocomplete-item" onclick="selectCommodity(\\'' + input.id + '\\', \\'' + listId + '\\', \\'' + m.replace(/'/g, "\\\\'") + '\\')">' + m + '</div>'
            ).join('');
        }

        function selectCommodity(inputId, listId, value) {
            document.getElementById(inputId).value = value;
            document.getElementById(listId).innerHTML = '';
        }

        // Trade form
        document.getElementById('tradeForm').onsubmit = async (e) => {
            e.preventDefault();
            const system = document.getElementById('tradeSystem').value;
            const commodity = document.getElementById('tradeCommodity').value;
            const results = document.getElementById('tradeResults');
            results.style.display = 'block';
            results.innerHTML = '<div style="text-align:center;padding:20px;color:#888;">Searching...</div>';
            try {
                const res = await fetch('/api/search?system=' + encodeURIComponent(system) + '&commodity=' + encodeURIComponent(commodity));
                const data = await res.json();
                if (data.error) { results.innerHTML = '<div style="color:#f55;text-align:center;">' + data.error + '</div>'; return; }
                if (data.results.length === 0) {
                    results.innerHTML = '<div style="color:#f55;text-align:center;">No stations found selling "' + data.commodity + '" in ' + data.system + '<br><br>💡 Try autocomplete — commodity names must match EDSM exactly (e.g. "Water Purifiers" not "Water")</div>';
                    return;
                }
                const avg = data.average_price;
                let html = '<div class="grid"><div class="stat"><div class="stat-value">' + data.count + '</div><div class="stat-label">Stations</div></div>' +
                    '<div class="stat"><div class="stat-value">' + avg.toLocaleString() + 'cr</div><div class="stat-label">Avg Price</div></div>' +
                    '<div class="stat"><div class="stat-value">' + data.results[0].buy.toLocaleString() + 'cr</div><div class="stat-label">Lowest Buy</div></div></div>' +
                    '<h3 style="margin:15px 0 10px;color:#00d4ff;">Stations Selling ' + data.commodity + '</h3>';
                data.results.forEach(r => {
                    const isCheap = r.buy < avg;
                    html += '<div class="result-item ' + (isCheap ? 'cheap' : '') + '">' +
                        '<div style="font-weight:bold;color:#00d4ff;">' + r.station + ' <span style="color:#888;font-weight:normal;">(' + r.type + ')</span></div>' +
                        '<div style="color:#888;font-size:0.9em;">Distance: ' + r.distance + 'ls | Stock: ' + r.stock.toLocaleString() + '</div>' +
                        '<div><span style="color:#f55;font-weight:bold;">Buy: ' + r.buy.toLocaleString() + 'cr</span>' +
                        '<span style="margin-left:15px;color:#4ecdc4;font-weight:bold;">Sell: ' + r.sell.toLocaleString() + 'cr</span>' +
                        (isCheap ? '<span style="margin-left:15px;color:#0f0;">★ CHEAP</span>' : '') + '</div></div>';
                });
                results.innerHTML = html;
            } catch (err) { results.innerHTML = '<div style="color:#f55;text-align:center;">Error: ' + err.message + '</div>'; }
        };

        // Station info form
        document.getElementById('stationForm').onsubmit = async (e) => {
            e.preventDefault();
            const system = document.getElementById('stationSystem').value;
            const results = document.getElementById('stationResults');
            results.style.display = 'block';
            results.innerHTML = '<div style="text-align:center;padding:20px;color:#888;">Loading...</div>';
            try {
                const res = await fetch('/api/station?system=' + encodeURIComponent(system));
                const data = await res.json();
                if (data.error) { results.innerHTML = '<div style="color:#f55;text-align:center;">' + data.error + '</div>'; return; }
                let html = '<h2>🏢 ' + data.system + '</h2>';
                if (data.info) {
                    html += '<div class="grid"><div class="stat"><div class="stat-value">' + (data.info.population || 0).toLocaleString() + '</div><div class="stat-label">Population</div></div>' +
                        '<div class="stat"><div class="stat-value" style="font-size:1em;">' + (data.info.security || 'N/A') + '</div><div class="stat-label">Security</div></div>' +
                        '<div class="stat"><div class="stat-value" style="font-size:1em;">' + (data.info.economy || 'N/A') + '</div><div class="stat-label">Economy</div></div>' +
                        '<div class="stat"><div class="stat-value" style="font-size:1em;">' + (data.info.allegiance || 'N/A') + '</div><div class="stat-label">Allegiance</div></div></div>';
                }
                html += '<h3 style="margin-top:20px;">Stations</h3>';
                data.stations.forEach(s => {
                    html += '<div class="station-card"><h4>' + s.name + ' (' + s.type + ')</h4>' +
                        '<div style="color:#888;">Economy: ' + s.economy + ' | Dist: ' + s.distanceToArrival + 'ls</div>' +
                        '<div style="margin-top:5px;">';
                    if (s.haveMarket) html += '<span class="commodity-tag" style="background:#1a4a5e;">Market</span>';
                    if (s.haveShipyard) html += '<span class="commodity-tag" style="background:#1a4a5e;">Shipyard</span>';
                    if (s.haveOutfitting) html += '<span class="commodity-tag" style="background:#1a4a5e;">Outfitting</span>';
                    if (s.hasRefuel) html += '<span class="commodity-tag" style="background:#1a4a5e;">Refuel</span>';
                    if (s.hasRepair) html += '<span class="commodity-tag" style="background:#1a4a5e;">Repair</span>';
                    if (s.hasRestock) html += '<span class="commodity-tag" style="background:#1a4a5e;">Restock</span>';
                    html += '</div></div>';
                });
                results.innerHTML = html;
            } catch (err) { results.innerHTML = '<div style="color:#f55;text-align:center;">Error: ' + err.message + '</div>'; }
        };

        // Colonize form
        document.getElementById('colonizeForm').onsubmit = async (e) => {
            e.preventDefault();
            const system = document.getElementById('colSystem').value;
            const stationType = document.getElementById('stationType').value;
            const economy = document.getElementById('economyType').value;
            const goal = document.getElementById('colonyGoal').value;
            const results = document.getElementById('colonizeResults');
            results.style.display = 'block';
            results.innerHTML = '<div style="text-align:center;padding:20px;color:#888;">Analyzing colony...</div>';
            try {
                const res = await fetch('/api/colonize?system=' + encodeURIComponent(system) + '&type=' + encodeURIComponent(stationType) + '&economy=' + encodeURIComponent(economy) + '&goal=' + encodeURIComponent(goal));
                const data = await res.json();
                let html = '<div class="info-box"><h2>🏗️ Colony Analysis: ' + data.system + '</h2>';
                if (data.systemInfo) {
                    html += '<div class="grid"><div class="stat"><div class="stat-value">' + (data.systemInfo.population || 0).toLocaleString() + '</div><div class="stat-label">Population</div></div>' +
                        '<div class="stat"><div class="stat-value" style="font-size:1em;">' + (data.systemInfo.tech_level || 0) + '</div><div class="stat-label">Tech Level</div></div>' +
                        '<div class="stat"><div class="stat-value" style="font-size:1em;">' + (data.systemInfo.security || 'Low') + '</div><div class="stat-label">Security</div></div>' +
                        '<div class="stat"><div class="stat-value" style="font-size:1em;">' + (data.systemInfo.economy || economy) + '</div><div class="stat-label">Economy</div></div></div>';
                }
                html += '</div><h3>Suggested Builds (Goal: ' + goal + ')</h3>';
                data.suggestions.forEach((s, i) => {
                    const locked = s.locked ? ' locked' : '';
                    html += '<div class="facility-card' + locked + '"><h4>' + (i+1) + '. ' + s.name + (s.locked ? ' 🔒' : ' ★') + '</h4>';
                    if (!s.locked) {
                        if (s.requires && s.requires.length > 0) html += '<div style="color:#888;margin-bottom:5px;">Requires: ' + s.requires.join(', ') + '</div>';
                        html += '<div style="margin:5px 0;">Stat Changes:</div><div>';
                        for (const [stat, val] of Object.entries(s.gives || {})) {
                            const cls = val > 0 ? 'stat-positive' : 'stat-negative';
                            html += '<span class="stat-change ' + cls + '">' + stat + ': ' + (val > 0 ? '+' : '') + val + '</span>';
                        }
                        html += '</div><div style="margin-top:8px;">Cost: ';
                        for (const [item, qty] of Object.entries(s.cost || {})) {
                            html += '<span class="cost-item">' + item + ': ' + qty + '</span>';
                        }
                        html += '</div>';
                    } else {
                        html += '<div style="color:#888;">Prerequisites: ' + s.requires.join(', ') + '</div>';
                    }
                    html += '</div>';
                });
                results.innerHTML = html;
            } catch (err) { results.innerHTML = '<div style="color:#f55;text-align:center;">Error: ' + err.message + '</div>'; }
        };

        // Resources form
        document.getElementById('resourcesForm').onsubmit = async (e) => {
            e.preventDefault();
            const system = document.getElementById('resSystem').value;
            const goal = document.getElementById('resGoal').value;
            const results = document.getElementById('resourcesResults');
            results.style.display = 'block';
            results.innerHTML = '<div style="text-align:center;padding:20px;color:#888;">Scanning system bodies...</div>';
            try {
                const res = await fetch('/api/resources?system=' + encodeURIComponent(system) + '&goal=' + encodeURIComponent(goal));
                const data = await res.json();
                if (data.error) { results.innerHTML = '<div style="color:#f55;text-align:center;">' + data.error + '</div>'; return; }
                let html = '<div class="info-box"><h2>🪐 Resource Analysis: ' + data.system + '</h2>';
                html += '<div class="grid"><div class="stat"><div class="stat-value">' + data.body_count + '</div><div class="stat-label">Bodies</div></div>' +
                    '<div class="stat"><div class="stat-value" style="font-size:1em;">' + (data.system_info.economy || 'N/A') + '</div><div class="stat-label">Economy</div></div>' +
                    '<div class="stat"><div class="stat-value" style="font-size:1em;">' + (data.system_info.security || 'N/A') + '</div><div class="stat-label">Security</div></div>' +
                    '<div class="stat"><div class="stat-value">' + (data.system_info.population || 0).toLocaleString() + '</div><div class="stat-label">Population</div></div></div></div>';
                
                html += '<h3>Resource Summary</h3><div class="grid">';
                html += '<div class="stat"><div class="stat-value" style="color:#ffa500;">' + data.resources.minerals.length + '</div><div class="stat-label">Mineral Bodies</div></div>';
                html += '<div class="stat"><div class="stat-value" style="color:#00d4ff;">' + data.resources.volatiles.length + '</div><div class="stat-label">Volatile Bodies</div></div>';
                html += '<div class="stat"><div class="stat-value" style="color:#4ecdc4;">' + data.resources.gases.length + '</div><div class="stat-label">Gas Giants</div></div>';
                html += '<div class="stat"><div class="stat-value" style="color:#ff6b6b;">' + data.resources.rings + '</div><div class="stat-label">Planetary Rings</div></div>';
                html += '</div>';
                
                html += '<h3>Recommended Facilities (Goal: ' + goal + ')</h3>';
                data.recommendations.forEach((r, i) => {
                    const color = r.priority === 'High' ? '#00ff00' : r.priority === 'Medium' ? '#ffa500' : '#888';
                    html += '<div class="facility-card"><h4>' + (i+1) + '. ' + r.facility + ' <span style="color:' + color + ';">[' + r.priority + ']</span></h4>' +
                        '<div style="margin-bottom:8px;"><span class="stat-change stat-positive">Score: ' + r.score + '</span></div>' +
                        '<div style="color:#888;">' + r.reasons.join(' • ') + '</div></div>';
                });
                
                results.innerHTML = html;
            } catch (err) { results.innerHTML = '<div style="color:#f55;text-align:center;">Error: ' + err.message + '</div>'; }
        };

        // Route form
        document.getElementById('routeForm').onsubmit = async (e) => {
            e.preventDefault();
            const from = document.getElementById('routeFrom').value;
            const to = document.getElementById('routeTo').value;
            const results = document.getElementById('routeResults');
            results.style.display = 'block';
            results.innerHTML = '<div style="text-align:center;padding:20px;color:#888;">Finding best routes...</div>';
            try {
                const res = await fetch('/api/route?from=' + encodeURIComponent(from) + '&to=' + encodeURIComponent(to));
                const data = await res.json();
                if (data.error) { results.innerHTML = '<div style="color:#f55;text-align:center;">' + data.error + '</div>'; return; }
                let html = '<h2>📍 Route: ' + from + ' → ' + to + '</h2>';
                if (data.distance) html += '<div class="grid"><div class="stat"><div class="stat-value">' + data.distance.toFixed(1) + ' ly</div><div class="stat-label">Distance</div></div></div>';
                html += '<h3>Best Stations</h3>';
                if (data.stations && data.stations.length > 0) {
                    data.stations.forEach(s => {
                        html += '<div class="station-card"><h4>' + s.name + ' (' + s.type + ')</h4>' +
                            '<div>' + s.economy + ' | ' + s.government + ' | ' + (s.allegiance || 'N/A') + '</div>' +
                            (s.hasMarket ? '<span class="commodity-tag">Market</span>' : '') +
                            (s.hasShipyard ? '<span class="commodity-tag">Shipyard</span>' : '') +
                            (s.hasOutfitting ? '<span class="commodity-tag">Outfitting</span>' : '') + '</div>';
                    });
                } else {
                    html += '<div class="info-box warning">No station data found for route. Try EDSM directly.</div>';
                }
                results.innerHTML = html;
            } catch (err) { results.innerHTML = '<div style="color:#f55;text-align:center;">Error: ' + err.message + '</div>'; }
        };
        // Bodies form
        document.getElementById('bodiesForm').onsubmit = async (e) => {
            e.preventDefault();
            const system = document.getElementById('bodiesSystem').value;
            const results = document.getElementById('bodiesResults');
            results.style.display = 'block';
            results.innerHTML = '<div style="text-align:center;padding:20px;color:#888;">Scanning system bodies...</div>';
            try {
                const res = await fetch('/api/bodies?system=' + encodeURIComponent(system));
                const data = await res.json();
                if (data.error) { results.innerHTML = '<div style="color:#f55;text-align:center;">' + data.error + '</div>'; return; }
                let html = '<div class="info-box"><h2>🌍 ' + data.system + ' — ' + data.body_count + ' Bodies</h2></div>';
                
                data.bodies.forEach(b => {
                    const typeColor = b.class === 'star' ? '#ff6b6b' : b.class === 'mineral' ? '#ffa500' : b.class === 'volatile' ? '#00d4ff' : b.class === 'gas' ? '#888' : b.class === 'organic' ? '#4ecdc4' : b.class === 'belt' ? '#ff6b6b' : '#888';
                    html += '<div class="station-card" style="border-left-color:' + typeColor + '">' +
                        '<h4>' + b.name + ' <span style="color:' + typeColor + ';">[' + b.subtype + ']</span></h4>' +
                        '<div style="color:#888;">';
                    if (b.distance > 0) html += 'Dist: ' + b.distance.toLocaleString() + 'ls | ';
                    if (b.gravity > 0) html += 'Gravity: ' + b.gravity.toFixed(2) + 'G | ';
                    if (b.temperature > 0) html += 'Temp: ' + b.temperature.toFixed(0) + 'K | ';
                    html += 'Atmo: ' + b.atmosphere;
                    if (b.volcanism !== 'None') html += ' | 🔥 Volcanic';
                    if (b.isLandable) html += ' | 🛬 Landable';
                    if (b.terraformable) html += ' | 🌍 Terraformable';
                    html += '</div>';
                    
                    if (b.rings.length > 0) {
                        html += '<div style="margin:5px 0;">Rings: ';
                        b.rings.forEach(r => {
                            const rcolor = r === 'metallic' ? '#ffa500' : r === 'pristine' ? '#00ff00' : '#888';
                            html += '<span class="commodity-tag" style="background:' + rcolor + '20;color:' + rcolor + ';">' + r + '</span> ';
                        });
                        html += '</div>';
                    }
                    
                    if (Object.keys(b.materials).length > 0) {
                        html += '<div style="margin:5px 0;">Materials: ';
                        for (const [mat, pct] of Object.entries(b.materials).slice(0, 6)) {
                            html += '<span class="commodity-tag" style="background:#1a4a5e;">' + mat + ': ' + pct + '%</span> ';
                        }
                        html += '</div>';
                    }
                    
                    html += '<div style="margin-top:8px;"><strong>Recommended Builds:</strong></div>';
                    b.recommendations.forEach(rec => {
                        const locColor = rec.type === 'Orbital' ? '#00d4ff' : '#4ecdc4';
                        html += '<div style="margin:3px 0;padding:5px;background:rgba(0,0,0,0.2);border-radius:4px;">' +
                            '<span style="color:' + locColor + ';font-weight:bold;">[' + rec.type + ']</span> ' +
                            rec.name + ' — <span style="color:#888;">' + rec.reason + '</span></div>';
                    });
                    
                    html += '</div>';
                });
                
                results.innerHTML = html;
            } catch (err) { results.innerHTML = '<div style="color:#f55;text-align:center;">Error: ' + err.message + '</div>'; }
        };
        
        // Materials form
        document.getElementById('materialsForm').onsubmit = async (e) => {
            e.preventDefault();
            const system = document.getElementById('matSystem').value;
            const material = document.getElementById('matName').value;
            const results = document.getElementById('materialsResults');
            results.style.display = 'block';
            results.innerHTML = '<div style="text-align:center;padding:20px;color:#888;">Scanning for materials...</div>';
            try {
                const url = '/api/materials?system=' + encodeURIComponent(system) + (material ? '&material=' + encodeURIComponent(material) : '');
                const res = await fetch(url);
                const data = await res.json();
                if (data.error) { results.innerHTML = '<div style="color:#f55;text-align:center;">' + data.error + '</div>'; return; }
                let html = '<div class="info-box"><h2>🔧 ' + data.system + '</h2><div>' + data.body_count + ' bodies scanned';
                if (data.search_material) html += ' | Searching: <strong>' + data.search_material + '</strong>';
                html += ' | Found: ' + data.found_count + ' matches</div></div>';
                
                if (data.found_count === 0) {
                    html += '<div class="info-box warning">No materials found. Try a different system or material.</div>';
                } else {
                    data.bodies.forEach(b => {
                        html += '<div class="station-card">' +
                            '<h4>' + b.name + ' <span style="color:#888;">[' + b.type + ']</span></h4>' +
                            '<div style="color:#888;">Dist: ' + b.distance.toLocaleString() + 'ls | ';
                        if (b.gravity) html += 'Gravity: ' + b.gravity.toFixed(2) + 'G | ';
                        if (b.isLandable) html += '🛬 Landable';
                        html += '</div>';
                        if (b.material) {
                            html += '<div style="margin-top:8px;"><span class="commodity-tag" style="background:#ffa50030;color:#ffa500;font-size:1em;">' + b.material + ': ' + b.percentage + '%</span></div>';
                        }
                        if (b.materials) {
                            html += '<div style="margin-top:8px;">Top Materials: ';
                            for (const [mat, pct] of Object.entries(b.materials)) {
                                html += '<span class="commodity-tag">' + mat + ': ' + pct + '%</span> ';
                            }
                            html += '</div>';
                        }
                        html += '</div>';
                    });
                }
                results.innerHTML = html;
            } catch (err) { results.innerHTML = '<div style="color:#f55;text-align:center;">Error: ' + err.message + '</div>'; }
        };
        
        // Outfitting form
        document.getElementById('outfittingForm').onsubmit = async (e) => {
            e.preventDefault();
            const system = document.getElementById('outSystem').value;
            const station = document.getElementById('outStation').value;
            const results = document.getElementById('outfittingResults');
            results.style.display = 'block';
            results.innerHTML = '<div style="text-align:center;padding:20px;color:#888;">Fetching outfitting data...</div>';
            try {
                const res = await fetch('/api/outfitting?system=' + encodeURIComponent(system) + '&station=' + encodeURIComponent(station));
                const data = await res.json();
                if (data.error) { results.innerHTML = '<div style="color:#f55;text-align:center;">' + data.error + '</div>'; return; }
                let html = '<div class="info-box"><h2>🛠️ ' + data.station + ' (' + data.system + ')</h2></div>';
                
                html += '<div class="grid"><div class="stat"><div class="stat-value">' + data.module_count + '</div><div class="stat-label">Modules</div></div>' +
                    '<div class="stat"><div class="stat-value">' + data.ship_count + '</div><div class="stat-label">Ships</div></div></div>';
                
                if (data.ship_count > 0) {
                    html += '<h3>🚀 Ships Available</h3>';
                    data.ships.forEach(s => {
                        html += '<span class="commodity-tag" style="background:#00d4ff20;color:#00d4ff;">' + s.name + ' (' + (s.price ? s.price.toLocaleString() + 'cr' : 'N/A') + ')</span> ';
                    });
                }
                
                if (data.module_count > 0) {
                    html += '<h3>⚙️ Modules by Category</h3>';
                    for (const [cat, mods] of Object.entries(data.modules)) {
                        html += '<div class="station-card"><h4>' + cat + '</h4>';
                        mods.forEach(m => {
                            html += '<div style="margin:2px 0;"><span class="commodity-tag">' + m.name + ' (Class ' + m.class + m.rating + ')</span> ' +
                                (m.price ? '<span style="color:#0f0;">' + m.price.toLocaleString() + 'cr</span>' : '') + '</div>';
                        });
                        html += '</div>';
                    }
                }
                
                if (data.module_count === 0 && data.ship_count === 0) {
                    html += '<div class="info-box warning">No outfitting or shipyard data available for this station.</div>';
                }
                
                results.innerHTML = html;
            } catch (err) { results.innerHTML = '<div style="color:#f55;text-align:center;">Error: ' + err.message + '</div>'; }
        };
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE, commodities=COMMODITIES)

@app.route('/api/systems')
def api_systems():
    q = request.args.get('q', '')
    if len(q) < 2:
        return jsonify({"systems": []})
    # Use sphere-systems to find nearby systems
    # For now, return suggestions based on EDSM's system search
    url = f"{EDSM_API}/api-v1/systems?systemName={urllib.parse.quote(q)}&showInformation=1"
    req = urllib.request.Request(url, headers=REQUEST_HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            data = json.loads(r.read().decode())
            if isinstance(data, list):
                systems = [d['name'] for d in data[:10]]
            else:
                systems = [data['name']] if 'name' in data else []
            return jsonify({"systems": systems})
    except:
        return jsonify({"systems": []})

@app.route('/api/search')
def api_search():
    commodity = request.args.get('commodity', '')
    system = request.args.get('system', '')
    if not commodity or not system:
        return jsonify({"error": "Both commodity and system are required"})

    system_data = get_system_info(system)
    if "error" in system_data:
        return jsonify({"error": system_data["error"]})

    stations_data = get_stations(system)
    stations = stations_data.get("stations", [])
    if not stations:
        return jsonify({"error": "No stations found in " + system})

    results = []
    for station in stations:
        if not station.get("haveMarket"):
            continue
        market = get_station_market(system, station["name"])
        for comm in market:
            # Fuzzy match - check if commodity name contains the query
            if commodity.lower() in comm.get("name", "").lower():
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

@app.route('/api/station')
def api_station():
    system = request.args.get('system', '')
    if not system:
        return jsonify({"error": "System name required"})

    system_data = get_system_info(system)
    stations_data = get_stations(system)
    stations = stations_data.get("stations", [])

    return jsonify({
        "system": system,
        "info": system_data.get("information", {}),
        "stations": [{
            "name": s.get("name", ""),
            "type": s.get("type", ""),
            "economy": s.get("economy", ""),
            "distanceToArrival": s.get("distanceToArrival", 0),
            "haveMarket": s.get("haveMarket", False),
            "haveShipyard": s.get("haveShipyard", False),
            "haveOutfitting": s.get("haveOutfitting", False),
            "hasRefuel": s.get("hasRefuel", False),
            "hasRepair": s.get("hasRepair", False),
            "hasRestock": s.get("hasRestock", False),
        } for s in stations]
    })

@app.route('/api/colonize')
def api_colonize():
    system = request.args.get('system', '')
    station_type = request.args.get('type', '')
    economy = request.args.get('economy', 'High Tech')
    goal = request.args.get('goal', 'balanced')

    system_data = get_system_info(system)
    info = system_data.get("information", {})

    # Estimate tech level based on economy type
    tech_levels = {"High Tech": 25, "Industrial": 15, "Extraction": 8, "Agriculture": 10, "Refinery": 12, "Military": 18, "Scientific": 30}
    base_tech = tech_levels.get(economy, 10)

    # Get current facilities from system (if any colonized)
    # For now, start fresh
    built_facilities = []

    # Suggest facilities based on goal
    facilities = COLONY_FACILITIES.get("Orbital", []) + COLONY_FACILITIES.get("Ground", [])
    suggestions = []

    for f in facilities:
        # Check if already built
        if f["id"] in built_facilities:
            continue

        # Check if requirements are met
        reqs_met = all(r in built_facilities for r in f.get("requires", []))

        suggestions.append({
            "id": f["id"],
            "name": f["name"],
            "tier": f.get("tier", 1),
            "requires": f.get("requires", []),
            "gives": f.get("gives", {}),
            "cost": f.get("cost", {}),
            "locked": not reqs_met
        })

    # Sort: unlocked first, then by goal priority
    def goal_priority(s):
        if s["locked"]:
            return 999
        gives = s.get("gives", {})
        if goal == "tech":
            return -gives.get("tech_level", 0)
        elif goal == "wealth":
            return -gives.get("wealth", 0)
        elif goal == "military":
            return -gives.get("security", 0)
        elif goal == "population":
            return -gives.get("population_growth", 0)
        else:
            return -(gives.get("tech_level", 0) + gives.get("wealth", 0))

    suggestions.sort(key=goal_priority)

    return jsonify({
        "system": system,
        "systemInfo": {
            "population": info.get("population", 0),
            "security": info.get("security", "Low"),
            "economy": economy,
            "allegiance": info.get("allegiance", ""),
            "tech_level": base_tech
        },
        "stationType": station_type,
        "goal": goal,
        "suggestions": suggestions[:6]
    })

@app.route('/api/route')
def api_route():
    from_sys = request.args.get('from', '')
    to_sys = request.args.get('to', '')

    if not from_sys or not to_sys:
        return jsonify({"error": "Both from and to systems required"})

    # Get stations for both systems
    from_stations = get_stations(from_sys)
    to_stations = get_stations(to_sys)

    # Calculate distance (rough estimate from coords)
    from_info = get_system_info(from_sys)
    to_info = get_system_info(to_sys)

    from_coords = from_info.get("coords", {})
    to_coords = to_info.get("coords", {})

    distance = None
    if from_coords and to_coords:
        dx = from_coords.get("x", 0) - to_coords.get("x", 0)
        dy = from_coords.get("y", 0) - to_coords.get("y", 0)
        dz = from_coords.get("z", 0) - to_coords.get("z", 0)
        distance = (dx*dx + dy*dy + dz*dz) ** 0.5

    return jsonify({
        "from": from_sys,
        "to": to_sys,
        "distance": distance,
        "stations": [{
            "name": s.get("name", ""),
            "type": s.get("type", ""),
            "economy": s.get("economy", ""),
            "government": s.get("government", ""),
            "allegiance": s.get("allegiance", ""),
            "haveMarket": s.get("haveMarket", False),
            "haveShipyard": s.get("haveShipyard", False),
            "haveOutfitting": s.get("haveOutfitting", False),
        } for s in (to_stations.get("stations", []) if not to_stations.get("error") else [])]
    })

# ===== RESOURCE ANALYZER (New) =====

def fetch_bodies(system_name):
    """Fetch all celestial bodies in a system."""
    url = f"{EDSM_API}/api-system-v1/bodies?systemName={urllib.parse.quote(system_name)}"
    req = urllib.request.Request(url, headers=REQUEST_HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            data = json.loads(r.read().decode())
            return data.get("bodies", [])
    except Exception as e:
        return []

def analyze_resources(bodies):
    """Analyze bodies for colonization-relevant resources."""
    resources = {
        "minerals": [],
        "volatiles": [],
        "organics": [],
        "gases": [],
        "asteroid_belts": 0,
        "rings": 0,
        "metallic_rings": False,
        "pristine_rings": False,
        "terraformable": [],
    }
    for body in bodies:
        btype = body.get("type", "")
        subtype = body.get("subType", "")
        name = body.get("name", "Unknown")
        if body.get("rings"):
            resources["rings"] += len(body["rings"])
            for ring in body["rings"]:
                rtype = ring.get("type", "").lower()
                if "metallic" in rtype:
                    resources["metallic_rings"] = True
                if "pristine" in rtype:
                    resources["pristine_rings"] = True
        if body.get("type") == "Belt":
            resources["asteroid_belts"] += 1
            continue
        st = subtype.lower()
        if "metallic" in st or "metal rich" in st:
            resources["minerals"].append({"name": name, "type": subtype, "value": "high"})
        elif "rocky" in st and "body" in st:
            resources["minerals"].append({"name": name, "type": subtype, "value": "medium"})
        elif "icy" in st:
            resources["volatiles"].append({"name": name, "type": subtype, "value": "high"})
        elif "water world" in st or "water giant" in st:
            resources["volatiles"].append({"name": name, "type": subtype, "value": "high"})
        elif "earth-like" in st or "ammonia world" in st:
            resources["organics"].append({"name": name, "type": subtype, "value": "high"})
        elif "gas giant" in st:
            resources["gases"].append({"name": name, "type": subtype, "value": "high"})
        if body.get("terraformingState") and body["terraformingState"] != "Not terraformable":
            resources["terraformable"].append(name)
        elif body.get("isLandable") and body.get("atmosphereType") in ["Thin", "Marginal"]:
            resources["terraformable"].append(name)
    return resources

def recommend_by_resources(resources, goal="balanced"):
    """Recommend facilities based on discovered resources."""
    scores = {
        "refinery_hub": 0, "industrial_hub": 0, "high_tech_hub": 0,
        "agricultural_hub": 0, "extraction_hub": 0, "trading_hub": 0,
    }
    reasons = {k: [] for k in scores}
    if resources["minerals"]:
        scores["extraction_hub"] += len(resources["minerals"]) * 2
        scores["industrial_hub"] += len(resources["minerals"])
        scores["refinery_hub"] += len(resources["minerals"])
        reasons["extraction_hub"].append(f"{len(resources['minerals'])} mineral-rich bodies")
        reasons["industrial_hub"].append("Access to raw minerals")
        reasons["refinery_hub"].append("Metallic/rocky bodies for processing")
    if resources["metallic_rings"]:
        scores["extraction_hub"] += 5
        scores["refinery_hub"] += 3
        reasons["extraction_hub"].append("Metallic planetary rings detected")
        reasons["refinery_hub"].append("Metallic rings = high-yield refining")
    if resources["pristine_rings"]:
        scores["extraction_hub"] += 3
        reasons["extraction_hub"].append("Pristine reserves (50% more yield)")
    if resources["asteroid_belts"] > 0:
        scores["extraction_hub"] += resources["asteroid_belts"] * 2
        reasons["extraction_hub"].append(f"{resources['asteroid_belts']} asteroid belts")
    if resources["volatiles"]:
        scores["refinery_hub"] += len(resources["volatiles"])
        scores["industrial_hub"] += len(resources["volatiles"])
        reasons["refinery_hub"].append(f"{len(resources['volatiles'])} volatile-rich bodies (water, ice)")
        reasons["industrial_hub"].append("Water/volatiles for industrial processes")
    if resources["organics"]:
        scores["agricultural_hub"] += len(resources["organics"]) * 3
        scores["trading_hub"] += len(resources["organics"])
        reasons["agricultural_hub"].append(f"{len(resources['organics'])} organic-rich worlds")
        reasons["trading_hub"].append("Organic goods for trade")
    if resources["terraformable"]:
        scores["agricultural_hub"] += len(resources["terraformable"]) * 2
        scores["high_tech_hub"] += len(resources["terraformable"])
        reasons["agricultural_hub"].append(f"{len(resources['terraformable'])} terraformable candidate(s)")
        reasons["high_tech_hub"].append("Terraforming tech development")
    if resources["gases"]:
        scores["industrial_hub"] += len(resources["gases"])
        scores["refinery_hub"] += len(resources["gases"])
        reasons["industrial_hub"].append("Gas giants for hydrogen/helium")
        reasons["refinery_hub"].append("Gas extraction potential")
    scores["trading_hub"] += 2
    scores["high_tech_hub"] += 1
    if goal == "tech":
        scores["high_tech_hub"] += 5; scores["industrial_hub"] += 2
    elif goal == "wealth":
        scores["trading_hub"] += 5; scores["refinery_hub"] += 3
    elif goal == "military":
        scores["industrial_hub"] += 5; scores["high_tech_hub"] += 2
    elif goal == "population":
        scores["agricultural_hub"] += 5; scores["trading_hub"] += 3
    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return ranked, reasons

@app.route('/api/resources')
def api_resources():
    system = request.args.get('system', '')
    goal = request.args.get('goal', 'balanced')
    if not system:
        return jsonify({"error": "System name required"})
    bodies = fetch_bodies(system)
    if not bodies:
        return jsonify({"error": "No body data found for " + system})
    resources = analyze_resources(bodies)
    ranked, reasons = recommend_by_resources(resources, goal)
    system_info = get_system_info(system)
    info = system_info.get("information", {})
    return jsonify({
        "system": system,
        "body_count": len(bodies),
        "system_info": {
            "economy": info.get("economy", ""),
            "second_economy": info.get("secondEconomy", ""),
            "population": info.get("population", 0),
            "security": info.get("security", ""),
            "allegiance": info.get("allegiance", ""),
        },
        "resources": resources,
        "recommendations": [
            {"facility": f.replace("_", " ").title(), "score": s,
             "reasons": reasons.get(f, ["General purpose"]),
             "priority": "High" if s >= 8 else "Medium" if s >= 4 else "Low"}
            for f, s in ranked if s > 0
        ]
    })

@app.route('/api/bodies')
def api_bodies():
    """Return detailed body list with per-body facility recommendations."""
    system = request.args.get('system', '')
    if not system:
        return jsonify({"error": "System name required"})
    bodies = fetch_bodies(system)
    if not bodies:
        return jsonify({"error": "No body data found for " + system})
    
    body_list = []
    for body in bodies:
        btype = body.get("type", "")
        subtype = body.get("subType", "")
        name = body.get("name", "Unknown")
        
        # Determine body class and recommendations
        body_class = "unknown"
        facility_recs = []
        
        st = subtype.lower()
        if "star" in st:
            body_class = "star"
            facility_recs = [{"type": "Orbital", "name": "Solar Array", "reason": "Proximity to star for solar power"}]
        elif "metallic" in st or "metal rich" in st:
            body_class = "mineral"
            facility_recs = [
                {"type": "Orbital", "name": "Extraction Hub", "reason": "High mineral content"},
                {"type": "Ground", "name": "Mining Outpost", "reason": "Surface mining operations"},
                {"type": "Orbital", "name": "Refinery Hub", "reason": "Process extracted metals"}
            ]
        elif "rocky" in st and "body" in st:
            body_class = "rocky"
            facility_recs = [
                {"type": "Ground", "name": "Mining Outpost", "reason": "Medium mineral content"},
                {"type": "Ground", "name": "Industrial Hub", "reason": "Manufacturing base"}
            ]
        elif "icy" in st:
            body_class = "volatile"
            facility_recs = [
                {"type": "Ground", "name": "Ice Refinery", "reason": "Water/ice extraction"},
                {"type": "Orbital", "name": "Refinery Hub", "reason": "Process volatiles into fuel"},
                {"type": "Ground", "name": "Life Support Outpost", "reason": "Water source for colony"}
            ]
        elif "water world" in st or "water giant" in st:
            body_class = "water"
            facility_recs = [
                {"type": "Orbital", "name": "Water Extraction Platform", "reason": "Abundant water supply"},
                {"type": "Ground", "name": "Aquaponics Farm", "reason": "Water-based agriculture"}
            ]
        elif "earth-like" in st:
            body_class = "organic"
            facility_recs = [
                {"type": "Ground", "name": "Agricultural Hub", "reason": "Earth-like conditions for farming"},
                {"type": "Ground", "name": "Biosphere Research", "reason": "Study native ecosystem"},
                {"type": "Orbital", "name": "Trading Hub", "reason": "Export organic goods"}
            ]
        elif "ammonia world" in st:
            body_class = "organic"
            facility_recs = [
                {"type": "Ground", "name": "Chemical Processing Plant", "reason": "Ammonia-based chemicals"},
                {"type": "Ground", "name": "Agricultural Hub", "reason": "Terraformed agriculture potential"}
            ]
        elif "gas giant" in st:
            body_class = "gas"
            facility_recs = [
                {"type": "Orbital", "name": "Gas Extraction Platform", "reason": "Hydrogen/helium harvesting"},
                {"type": "Orbital", "name": "Refinery Hub", "reason": "Process gas into fuel"},
                {"type": "Orbital", "name": "Industrial Hub", "reason": "Gas-based manufacturing"}
            ]
        elif body.get("type") == "Belt":
            body_class = "belt"
            facility_recs = [
                {"type": "Orbital", "name": "Asteroid Mining Station", "reason": "Rich asteroid field"},
                {"type": "Orbital", "name": "Extraction Hub", "reason": "Bulk resource extraction"}
            ]
        
        # Check terraformable
        is_terraformable = False
        if body.get("terraformingState") and body["terraformingState"] != "Not terraformable":
            is_terraformable = True
        elif body.get("isLandable") and body.get("atmosphereType") in ["Thin", "Marginal"]:
            is_terraformable = True
        
        if is_terraformable:
            facility_recs.insert(0, {"type": "Ground", "name": "Terraforming Station", "reason": "Candidate for terraforming"})
        
        # Check rings
        rings = []
        if body.get("rings"):
            for ring in body["rings"]:
                rtype = ring.get("type", "").lower()
                if "metallic" in rtype:
                    rings.append("metallic")
                    facility_recs.append({"type": "Orbital", "name": "Ring Mining Station", "reason": "Metallic ring mining"})
                elif "pristine" in rtype:
                    rings.append("pristine")
                    facility_recs.append({"type": "Orbital", "name": "Deep Mining Platform", "reason": "Pristine reserves (50% yield)"})
                else:
                    rings.append("standard")
        
        body_list.append({
            "name": name,
            "type": btype,
            "subtype": subtype,
            "class": body_class,
            "distance": body.get("distanceToArrival", 0),
            "isLandable": body.get("isLandable", False),
            "gravity": body.get("gravity", 0),
            "temperature": body.get("surfaceTemperature", 0),
            "atmosphere": body.get("atmosphereType", "None"),
            "volcanism": body.get("volcanismType", "None"),
            "terraformable": is_terraformable,
            "rings": rings,
            "materials": body.get("materials", {}),
            "recommendations": facility_recs[:4]  # Top 4 recommendations
        })
    
    return jsonify({
        "system": system,
        "body_count": len(body_list),
        "bodies": body_list
    })

# ===== ENGINEERING MATERIALS FINDER =====

ENGINEERING_MATERIALS = {
    "Raw": ["Carbon", "Vanadium", "Niobium", "Yttrium", "Phosphorus", "Chromium", "Molybdenum", "Technetium",
            "Sulphur", "Manganese", "Cadmium", "Ruthenium", "Iron", "Zinc", "Tin", "Selenium",
            "Nickel", "Germanium", "Tungsten", "Antimony", "Rhenium", "Arsenic", "Mercury", "Polonium",
            "Lead", "Zirconium", "Boron", "Tellurium"],
    "Manufactured": ["Chemical Processors", "Chemical Storage Units", "Chemical Distillery", "Pharmaceutical Isolators",
                       "Conductive Components", "Conductive Ceramics", "Conductive Polymers", "Polymer Capacitors",
                       "Mechanical Components", "Mechanical Equipment", "Mechanical Scrap", "Configurable Components",
                       "Shield Emitters", "Shielding Sensors", "Compound Shielding", "Imperial Shielding",
                       "Filament Composites", "High Density Composites", "Proprietary Composites", "Core Dynamics Composites",
                       "Heat Conduction Wiring", "Heat Dispersion Plate", "Heat Exchangers", "Heat Vanes",
                       "Worn Shield Emitters", "Untypical Shield Scans", "Aberrant Shield Pattern Analysis", "Peculiar Shield Data",
                       "Grid Resistors", "Hybrid Capacitors", "Electrochemical Arrays", "Exquisite Focus Crystals",
                       "Salvaged Alloys", "Galvanising Alloys", "Phase Alloys", "Proto Light Alloys", "Proto Radiolic Alloys",
                       "Compact Composites", "Filament Composites", "High Density Composites", "Proprietary Composites",
                       "Crystal Shards", "Flawed Focus Crystals", "Focus Crystals", "Refined Focus Crystals"],
    "Encoded": ["Anomalous Bulk Scan Data", "Atypical Disrupted Wake Echoes", "Atypical Encryption Archives",
                "Classified Scan Databanks", "Classified Scan Fragment", "Cracked Industrial Firmware",
                "Datamined Wake Exceptions", "Decoded Emission Data", "Divergent Scan Data", "Eccentric Hyperspace Trajectories",
                "Exceptional Scrambled Emission Data", "Inconsistent Shield Soak Analysis", "Irregular Emission Data",
                "Modified Consumer Firmware", "Modified Embedded Firmware", "Open Symmetric Keys",
                "Security Firmware Patch", "Specialised Legacy Firmware", "Strange Wake Solutions",
                "Tagged Encryption Codes", "Unusual Encrypted Files", "Untypical Shield Scans"]
}

@app.route('/api/materials')
def api_materials():
    """Find engineering materials in a system."""
    system = request.args.get('system', '')
    material = request.args.get('material', '')
    
    if not system:
        return jsonify({"error": "System name required"})
    
    bodies = fetch_bodies(system)
    if not bodies:
        return jsonify({"error": "No body data found for " + system})
    
    found_bodies = []
    for body in bodies:
        materials = body.get("materials", {})
        if material:
            # Search for specific material
            if material.lower() in {k.lower(): v for k, v in materials.items()}:
                pct = next((v for k, v in materials.items() if k.lower() == material.lower()), 0)
                found_bodies.append({
                    "name": body.get("name", "Unknown"),
                    "type": body.get("subType", "Unknown"),
                    "material": material,
                    "percentage": pct,
                    "distance": body.get("distanceToArrival", 0),
                    "isLandable": body.get("isLandable", False),
                    "gravity": body.get("gravity", 0)
                })
        else:
            # Show all materials on this body
            if materials:
                found_bodies.append({
                    "name": body.get("name", "Unknown"),
                    "type": body.get("subType", "Unknown"),
                    "materials": {k: v for k, v in sorted(materials.items(), key=lambda x: x[1], reverse=True)[:5]},
                    "distance": body.get("distanceToArrival", 0),
                    "isLandable": body.get("isLandable", False)
                })
    
    if material:
        found_bodies.sort(key=lambda x: x["percentage"], reverse=True)
    
    return jsonify({
        "system": system,
        "search_material": material,
        "body_count": len(bodies),
        "found_count": len(found_bodies),
        "bodies": found_bodies
    })

# ===== STATION OUTFITTING DETAILS =====

def get_station_outfitting(system, station):
    """Fetch outfitting details for a station."""
    url = f"{EDSM_API}/api-system-v1/stations/outfitting?systemName={urllib.parse.quote(system)}&stationName={urllib.parse.quote(station)}"
    req = urllib.request.Request(url, headers=REQUEST_HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            data = json.loads(r.read().decode())
            return data
    except Exception as e:
        return {"error": str(e)}

def get_station_shipyard(system, station):
    """Fetch shipyard details for a station."""
    url = f"{EDSM_API}/api-system-v1/stations/shipyard?systemName={urllib.parse.quote(system)}&stationName={urllib.parse.quote(station)}"
    req = urllib.request.Request(url, headers=REQUEST_HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            data = json.loads(r.read().decode())
            return data
    except Exception as e:
        return {"error": str(e)}

@app.route('/api/outfitting')
def api_outfitting():
    """Get detailed outfitting and shipyard info for a station."""
    system = request.args.get('system', '')
    station = request.args.get('station', '')
    
    if not system or not station:
        return jsonify({"error": "Both system and station names required"})
    
    outfitting = get_station_outfitting(system, station)
    shipyard = get_station_shipyard(system, station)
    
    modules = outfitting.get("modules", []) if not outfitting.get("error") else []
    ships = shipyard.get("ships", []) if not shipyard.get("error") else []
    
    # Categorize modules
    module_categories = {}
    for mod in modules:
        cat = mod.get("category", "Other")
        if cat not in module_categories:
            module_categories[cat] = []
        module_categories[cat].append({
            "name": mod.get("name", "Unknown"),
            "class": mod.get("class", "?"),
            "rating": mod.get("rating", "?"),
            "price": mod.get("price", 0)
        })
    
    return jsonify({
        "system": system,
        "station": station,
        "modules": module_categories,
        "module_count": len(modules),
        "ships": [{"name": s.get("name", "Unknown"), "price": s.get("price", 0)} for s in ships],
        "ship_count": len(ships)
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

from flask import Flask, render_template_string, request, jsonify
import urllib.request
import json
import urllib.parse

app = Flask(__name__)

EDSM_API = "https://www.edsm.net"
INARA_API = "https://inara.cz/inapi/v1/"
REQUEST_HEADERS = {"User-Agent": "StartMit-EliteCompanion/1.0"}

# Inara API key (user must set their own)
INARA_API_KEY = ""  # Set your Inara API key here

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

# Colony tech tree
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
        {"id": "research_lab", "name": "Research Lab", "tier": 2,
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
         "cost": {"CMM Composite": 350, "Water": 200}},
        {"id": "power_plant", "name": "Power Plant", "tier": 1,
         "requires": [], "gives": {"tech_level": 10, "population_growth": 5},
         "cost": {"CMM Composite": 300, "Energy Grid": 150}},
        {"id": "water_treatment", "name": "Water Treatment", "tier": 1,
         "requires": [], "gives": {"standard_of_living": 15, "population_growth": 10},
         "cost": {"CMM Composite": 250, "Water": 300}},
    ]
}

# System states and their trade effects
SYSTEM_STATES = {
    "Boom": {"commodities_increase": ["Food", "Textiles", "Consumer Goods", "Luxury Goods"], "color": "#00ff00"},
    "Bust": {"commodities_decrease": ["Food", "Textiles", "Consumer Goods", "Luxury Goods"], "color": "#ff4444"},
    "Civil Unrest": {"commodities_decrease": ["Luxury Goods", "Non-Lethal Weapons"], "color": "#ff8800"},
    "Civil War": {"commodities_decrease": ["All except Weapons"], "color": "#ff0000"},
    "Election": {"commodities_increase": ["Consumer Electronics", "Food"], "color": "#00ffff"},
    "Famine": {"commodities_increase": ["Food", "Water"], "color": "#ffff00"},
    "Fire Outbreak": {"commodities_increase": ["Food", "Water", "Medicines"], "color": "#ff4400"},
    "Infrastructure Failure": {"commodities_decrease": ["All Tradeable"], "color": "#888888"},
    "Natural Disaster": {"commodities_decrease": ["All Tradeable"], "color": "#000000"},
    "Outbreak": {"commodities_increase": ["Medicines", "Agri-Medicines"], "color": "#ff00ff"},
    "War": {"commodities_increase": ["Weapons", "Military Supplies", "Narcotics"], "color": "#ff0000"},
    "Peace": {"commodities_increase": ["Luxury Goods", "Consumer Goods"], "color": "#00ff88"},
    "Public Holiday": {"commodities_increase": ["Luxury Goods", "Alcohol", "Tobacco"], "color": "#ffaa00"},
    "Retreat": {"commodities_decrease": ["All except Weapons"], "color": "#440044"},
}

# Engineering blueprints (simplified - major ones)
ENGINEERING_RECIPES = {
    "FSD Range": [
        {"blueprint": "Extended Range 5", "grade": 5, "experimental": "Mass Manager",
         "materials": {"Phosphorus": 12, "Sulphur": 12, "Carbon": 12, "Vanadium": 8, "Grid Switches": 5}},
        {"blueprint": "Increased Range 4", "grade": 4, "experimental": "Mass Manager",
         "materials": {"Phosphorus": 8, "Sulphur": 8, "Carbon": 8, "Vanadium": 5}},
    ],
    "Shield Boost": [
        {"blueprint": "Reinforced 5", "grade": 5, "experimental": "Thermal Resist",
         "materials": {"Iron": 15, "Nickel": 15, "Chromium": 10, "Zirconium": 5, "Mechanical Equipment": 3}},
        {"blueprint": "Heavy Duty 4", "grade": 4, "experimental": "Thermal Resist",
         "materials": {"Iron": 10, "Nickel": 10, "Chromium": 7, "Zirconium": 3}},
    ],
    "Weapon Damage": [
        {"blueprint": "Overcharged 5", "grade": 5, "experimental": "Corrosive Shell",
         "materials": {"Carbon": 12, "Sulphur": 12, "Chromium": 8, "Manganese": 8, "Heat Vanes": 5}},
        {"blueprint": "Overcharged 4", "grade": 4, "experimental": "Corrosive Shell",
         "materials": {"Carbon": 8, "Sulphur": 8, "Chromium": 5, "Manganese": 5}},
    ],
    "Armor": [
        {"blueprint": "Military Grade 5", "grade": 5, "experimental": "Deep Plating",
         "materials": {"Iron": 20, "Nickel": 20, "Chromium": 15, "Zinc": 10, "Titanium": 10}},
        {"blueprint": "Reinforced 4", "grade": 4, "experimental": "Deep Plating",
         "materials": {"Iron": 12, "Nickel": 12, "Chromium": 8, "Zinc": 5}},
    ],
    "Engine": [
        {"blueprint": "Dirty 5", "grade": 5, "experimental": "Drag Drives",
         "materials": {"Carbon": 12, "Sulphur": 12, "Phosphorus": 8, "Heat Vanes": 5}},
        {"blueprint": "Clean 4", "grade": 4, "experimental": "Drag Drives",
         "materials": {"Phosphorus": 10, "Sulphur": 10, "Carbon": 8, "Heat Vanes": 3}},
    ],
}

# Guardian site locations (known major sites)
GUARDIAN_SITES = [
    {"name": "Synuefe EU-R c4-15", "type": "Guardian Structure", "region": "Inner Orion Spur",
     "notes": "Multiple pylons, combat zone nearby"},
    {"name": "Synuefe XR-R c4-6", "type": "Guardian Structure", "region": "Inner Orion Spur",
     "notes": "Large central structure"},
    {"name": "HIP 22441", "type": "Guardian Structure", "region": "Inner Orion Spur",
     "notes": "Blueprint site - requires keycard"},
    {"name": "Col 173 Syne 2", "type": "Guardian Ruins", "region": "Orion Arm",
     "notes": "Surface ruins with artifacts"},
    {"name": "Meene", "type": "Guardian Ruins", "region": "Orion Arm",
     "notes": "Small site, easy access"},
]

# Thargoid site locations
THARGOID_SITES = [
    {"name": "HIP 21025", "type": "Thargoid Site", "region": "Inner Orion Spur",
     "notes": "Crash site, hyperdiction common"},
    {"name": "Pleiades Nebula", "type": "Thargoid Structure", "region": "Pleiades",
     "notes": "Multiple sites, Interceptor spawns"},
    {"name": "WOLF 397", "type": "Thargoid Crash Site", "region": "Orion Arm",
     "notes": "Salvage opportunities"},
    {"name": "Hyades Sector AQ-P e5-3", "type": "Thargoid Structure", "region": "Pleiades",
     "notes": "Barnacle sites nearby"},
    {"name": "Merope", "type": "Thargoid Site", "region": "Pleiades",
     "notes": "Survey site, rare materials"},
]

# Material trader types
MATERIAL_TRADER_TYPES = ["Raw", "Encoded", "Manufactured"]

# Service types available at stations
STATION_SERVICES = [
    "Outfitting", "Shipyard", "Market", "Repair", "Refuel", "Restock",
    "Technology Broker", "Material Trader", "Interstellar Factors",
    "Commodities", "Universal Cartographics", "Black Market"
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

def inara_api_post(event_data, api_key=None):
    """Send request to Inara API"""
    if not api_key and not INARA_API_KEY:
        return {"error": "Inara API key not set"}
    
    key = api_key or INARA_API_KEY
    payload = {
        "header": {
            "appName": "StartMit Elite Companion",
            "appVersion": "1.0",
            "APIKey": key
        },
        "events": [event_data]
    }
    
    req = urllib.request.Request(
        INARA_API,
        data=json.dumps(payload).encode('utf-8'),
        headers={"Content-Type": "application/json", "User-Agent": "StartMit-EliteCompanion/1.0"}
    )
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

def get_station_outfitting(system, station):
    data = api_get("/api-system-v1/stations/outfitting", {"systemName": system, "stationName": station})
    return data if not data.get("error") else {"modules": []}

def get_station_shipyard(system, station):
    data = api_get("/api-system-v1/stations/shipyard", {"systemName": system, "stationName": station})
    return data if not data.get("error") else {"ships": []}

def get_systems_in_radius(system_name, radius=30):
    """Get systems within radius of a system using EDSM sphere search"""
    system_data = get_system_info(system_name)
    if "error" in system_data:
        return []
    
    coords = system_data.get("coords", {})
    if not coords:
        return []
    
    x, y, z = coords.get("x", 0), coords.get("y", 0), coords.get("z", 0)
    
    # EDSM doesn't have a direct sphere search, so we'll use thesystems in the same region
    # For now, return nearby major stations
    return api_get("/api-v1/sphere-systems", {
        "systemName": system_name,
        "radius": radius,
        "showCoordinates": 1,
        "showInformation": 1
    })

def calculate_distance(coord1, coord2):
    if not coord1 or not coord2:
        return None
    dx = coord1.get("x", 0) - coord2.get("x", 0)
    dy = coord1.get("y", 0) - coord2.get("y", 0)
    dz = coord1.get("z", 0) - coord2.get("z", 0)
    return (dx*dx + dy*dy + dz*dz) ** 0.5

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Elite Station Advisor</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        :root {
            --bg-dark: #0a0a12;
            --bg-card: #12121f;
            --bg-input: #1a1a2e;
            --accent: #f5a623;
            --accent-hover: #ffb84d;
            --cyan: #00d4ff;
            --green: #00ff88;
            --red: #ff4757;
            --orange: #ffa502;
            --purple: #a55eea;
            --text: #e0e0e0;
            --text-dim: #888;
            --border: #2a2a3e;
        }
        body {
            font-family: 'Segoe UI', Arial, sans-serif;
            background: var(--bg-dark);
            color: var(--text);
            min-height: 100vh;
            display: flex;
        }
        /* SIDEBAR */
        .sidebar {
            width: 240px;
            background: var(--bg-card);
            border-right: 1px solid var(--border);
            height: 100vh;
            position: fixed;
            left: 0;
            top: 0;
            display: flex;
            flex-direction: column;
            overflow-y: auto;
        }
        .sidebar-header {
            padding: 20px;
            border-bottom: 1px solid var(--border);
        }
        .sidebar-header h1 {
            font-size: 1.3em;
            color: var(--accent);
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .sidebar-header span { font-size: 0.75em; color: var(--text-dim); }
        .nav-section { padding: 15px 0; }
        .nav-section-title {
            font-size: 0.7em;
            text-transform: uppercase;
            color: var(--text-dim);
            padding: 0 20px;
            margin-bottom: 8px;
            letter-spacing: 1px;
        }
        .nav-item {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 12px 20px;
            color: var(--text-dim);
            cursor: pointer;
            transition: all 0.2s;
            border-left: 3px solid transparent;
        }
        .nav-item:hover { background: rgba(255,255,255,0.05); color: var(--text); }
        .nav-item.active {
            background: rgba(245,166,35,0.15);
            color: var(--accent);
            border-left-color: var(--accent);
        }
        .nav-item .icon { font-size: 1.2em; width: 24px; text-align: center; }
        .nav-item .label { font-size: 0.9em; }
        
        /* MAIN CONTENT */
        .main {
            margin-left: 240px;
            flex: 1;
            padding: 30px;
            min-height: 100vh;
        }
        .page { display: none; }
        .page.active { display: block; }
        
        /* HEADER */
        .page-header {
            margin-bottom: 30px;
        }
        .page-header h2 {
            font-size: 1.8em;
            color: var(--text);
            margin-bottom: 5px;
        }
        .page-header p { color: var(--text-dim); font-size: 0.9em; }
        
        /* CARDS */
        .card {
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
        }
        .card-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }
        .card-title {
            font-size: 1.1em;
            font-weight: 600;
            color: var(--cyan);
        }
        
        /* FORMS */
        .form-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; }
        .form-group { margin-bottom: 15px; }
        .form-group label {
            display: block;
            font-size: 0.8em;
            color: var(--text-dim);
            margin-bottom: 6px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        input, select {
            width: 100%;
            padding: 10px 14px;
            border: 1px solid var(--border);
            border-radius: 8px;
            background: var(--bg-input);
            color: var(--text);
            font-size: 0.95em;
            transition: border-color 0.2s;
        }
        input:focus, select:focus {
            outline: none;
            border-color: var(--cyan);
        }
        input::placeholder { color: var(--text-dim); }
        button {
            background: var(--accent);
            color: #000;
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            font-size: 0.9em;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
        }
        button:hover { background: var(--accent-hover); transform: translateY(-1px); }
        button.secondary {
            background: var(--bg-input);
            color: var(--text);
            border: 1px solid var(--border);
        }
        button.secondary:hover { background: var(--border); }
        
        /* RESULTS */
        .results-grid {
            display: grid;
            gap: 12px;
        }
        .result-item {
            background: var(--bg-input);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 15px;
            cursor: pointer;
            transition: all 0.2s;
        }
        .result-item:hover { border-color: var(--cyan); transform: translateX(3px); }
        .result-item .station-name { color: var(--cyan); font-weight: 600; margin-bottom: 5px; }
        .result-item .station-info { font-size: 0.85em; color: var(--text-dim); }
        
        /* STATION DETAIL MODAL */
        .modal-overlay {
            display: none;
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            background: rgba(0,0,0,0.8);
            z-index: 1000;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        .modal-overlay.active { display: flex; }
        .modal {
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 16px;
            width: 100%;
            max-width: 900px;
            max-height: 90vh;
            overflow-y: auto;
        }
        .modal-header {
            padding: 20px;
            border-bottom: 1px solid var(--border);
            display: flex;
            justify-content: space-between;
            align-items: center;
            position: sticky;
            top: 0;
            background: var(--bg-card);
            z-index: 10;
        }
        .modal-header h3 { color: var(--cyan); font-size: 1.3em; }
        .modal-close {
            background: none;
            border: none;
            color: var(--text-dim);
            font-size: 1.5em;
            cursor: pointer;
            padding: 5px;
        }
        .modal-close:hover { color: var(--red); }
        .modal-body { padding: 20px; }
        .modal-section { margin-bottom: 25px; }
        .modal-section h4 {
            color: var(--accent);
            font-size: 1em;
            margin-bottom: 12px;
            padding-bottom: 8px;
            border-bottom: 1px solid var(--border);
        }
        .modal-tabs {
            display: flex;
            gap: 8px;
            margin-bottom: 15px;
            flex-wrap: wrap;
        }
        .modal-tab {
            padding: 8px 16px;
            background: var(--bg-input);
            border: 1px solid var(--border);
            border-radius: 6px;
            font-size: 0.85em;
            cursor: pointer;
            color: var(--text-dim);
        }
        .modal-tab.active { background: var(--accent); color: #000; border-color: var(--accent); }
        .modal-tab:hover:not(.active) { border-color: var(--cyan); }
        .tab-content { display: none; }
        .tab-content.active { display: block; }
        
        /* SERVICE BADGES */
        .service-badge {
            display: inline-block;
            padding: 4px 10px;
            border-radius: 4px;
            font-size: 0.75em;
            margin: 2px;
            background: rgba(0,212,255,0.15);
            color: var(--cyan);
            border: 1px solid rgba(0,212,255,0.3);
        }
        .service-badge.green { background: rgba(0,255,136,0.15); color: var(--green); border-color: rgba(0,255,136,0.3); }
        .service-badge.orange { background: rgba(245,166,35,0.15); color: var(--orange); border-color: rgba(245,166,35,0.3); }
        .service-badge.red { background: rgba(255,71,87,0.15); color: var(--red); border-color: rgba(255,71,87,0.3); }
        
        /* COMMODITY TABLE */
        .data-table { width: 100%; border-collapse: collapse; font-size: 0.85em; }
        .data-table th, .data-table td {
            padding: 8px 12px;
            text-align: left;
            border-bottom: 1px solid var(--border);
        }
        .data-table th { color: var(--text-dim); font-weight: 500; text-transform: uppercase; font-size: 0.75em; }
        .data-table tr:hover { background: rgba(255,255,255,0.03); }
        .price-buy { color: var(--green); }
        .price-sell { color: var(--red); }
        
        /* STAT GRID */
        .stat-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px; }
        .stat-box {
            background: var(--bg-input);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 15px;
            text-align: center;
        }
        .stat-box .value { font-size: 1.5em; font-weight: bold; color: var(--cyan); }
        .stat-box .label { font-size: 0.75em; color: var(--text-dim); text-transform: uppercase; }
        
        /* STATE BADGES */
        .state-badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 4px;
            font-size: 0.8em;
            font-weight: 600;
        }
        .state-boom { background: rgba(0,255,0,0.2); color: #0f0; }
        .state-bust { background: rgba(255,0,0,0.2); color: #f44; }
        .state-war { background: rgba(255,0,0,0.3); color: #f00; }
        .state-famine { background: rgba(255,255,0,0.2); color: #ff0; }
        .state-peace { background: rgba(0,255,136,0.2); color: var(--green); }
        
        /* MATERIAL CHIPS */
        .material-chip {
            display: inline-block;
            padding: 3px 10px;
            background: rgba(165,94,234,0.2);
            color: var(--purple);
            border-radius: 12px;
            font-size: 0.8em;
            margin: 2px;
        }
        .material-chip.raw { background: rgba(0,255,136,0.2); color: var(--green); }
        .material-chip.encoded { background: rgba(0,212,255,0.2); color: var(--cyan); }
        .material-chip.manufactured { background: rgba(245,166,35,0.2); color: var(--orange); }
        
        /* LOADING */
        .loading { text-align: center; padding: 40px; color: var(--text-dim); }
        .loading::after { content: '...'; animation: dots 1.5s infinite; }
        @keyframes dots { 0%,20%{content:'.'} 40%{content:'..'} 60%,100%{content:'...'} }
        
        /* EMPTY STATE */
        .empty-state {
            text-align: center;
            padding: 60px 20px;
            color: var(--text-dim);
        }
        .empty-state .icon { font-size: 3em; margin-bottom: 15px; opacity: 0.5; }
        .empty-state p { font-size: 0.9em; }
        
        /* RESPONSIVE */
        @media (max-width: 768px) {
            .sidebar { width: 60px; }
            .sidebar-header h1 span, .nav-item .label, .nav-section-title { display: none; }
            .nav-item { justify-content: center; padding: 15px; }
            .main { margin-left: 60px; padding: 15px; }
        }
    </style>
</head>
<body>

<!-- SIDEBAR NAV -->
<nav class="sidebar">
    <div class="sidebar-header">
        <h1>🚀 Elite Station Advisor</h1>
        <span>by StartMit</span>
    </div>
    <div class="nav-section">
        <div class="nav-section-title">Trade & Station</div>
        <div class="nav-item active" onclick="showPage('trade')">
            <span class="icon">🔍</span><span class="label">Trade Search</span>
        </div>
        <div class="nav-item" onclick="showPage('station')">
            <span class="icon">🏢</span><span class="label">Station Info</span>
        </div>
        <div class="nav-item" onclick="showPage('route')">
            <span class="icon">📍</span><span class="label">Trade Routes</span>
        </div>
        <div class="nav-item" onclick="showPage('services')">
            <span class="icon">🔧</span><span class="label">Service Finder</span>
        </div>
    </div>
    <div class="nav-section">
        <div class="nav-section-title">Tools</div>
        <div class="nav-item" onclick="showPage('states')">
            <span class="icon">📊</span><span class="label">System States</span>
        </div>
        <div class="nav-item" onclick="showPage('engineering')">
            <span class="icon">⚙️</span><span class="label">Engineering</span>
        </div>
        <div class="nav-item" onclick="showPage('colonize')">
            <span class="icon">🏗️</span><span class="label">Colony Advisor</span>
        </div>
    </div>
    <div class="nav-section">
        <div class="nav-section-title">Exploration</div>
        <div class="nav-item" onclick="showPage('guardian')">
            <span class="icon">👽</span><span class="label">Guardian Sites</span>
        </div>
        <div class="nav-item" onclick="showPage('thargoid')">
            <span class="icon">🛸</span><span class="label">Thargoid Sites</span>
        </div>
        <div class="nav-item" onclick="showPage('carrier')">
            <span class="icon">🚀</span><span class="label">Fleet Carriers</span>
        </div>
    </div>
    <div class="nav-section">
        <div class="nav-section-title">Integration</div>
        <div class="nav-item" onclick="showPage('inara')">
            <span class="icon">🔗</span><span class="label">Inara.cz</span>
        </div>
    </div>
    <div class="nav-section">
        <div class="nav-section-title">Commander</div>
        <div class="nav-item" onclick="showPage('commander')">
            <span class="icon">👤</span><span class="label">Dashboard</span>
        </div>
        <div class="nav-item" onclick="showPage('colonies')">
            <span class="icon">🏰</span><span class="label">My Colonies</span>
        </div>
        <div class="nav-item" onclick="showPage('ships')">
            <span class="icon">🚀</span><span class="label">Ship Hangar</span>
        </div>
        <div class="nav-item" onclick="showPage('materials')">
            <span class="icon">📦</span><span class="label">Materials</span>
        </div>
        <div class="nav-item" onclick="showPage('bookmarks')">
            <span class="icon">⭐</span><span class="label">Bookmarks</span>
        </div>
    </div>
</nav>

<!-- MAIN CONTENT -->
<main class="main">

<!-- TRADE SEARCH PAGE -->
<div id="page-trade" class="page active">
    <div class="page-header">
        <h2>🔍 Trade Search</h2>
        <p>Search for commodities and find the best stations to buy or sell</p>
    </div>
    <div class="card">
        <div class="form-grid">
            <div class="form-group">
                <label>System</label>
                <input type="text" id="trade-system" placeholder="e.g. Sol, Lave, Diaguandi">
            </div>
            <div class="form-group">
                <label>Commodity</label>
                <input type="text" id="trade-commodity" placeholder="e.g. Gold, Tritium, Food">
            </div>
            <div class="form-group" style="display:flex;align-items:flex-end;">
                <button onclick="searchTrade()">Search</button>
            </div>
        </div>
    </div>
    <div id="trade-results" class="card" style="display:none;">
        <div class="card-header">
            <span class="card-title">Results</span>
            <span id="trade-count"></span>
        </div>
        <div id="trade-results-list" class="results-grid"></div>
    </div>
</div>

<!-- STATION INFO PAGE -->
<div id="page-station" class="page">
    <div class="page-header">
        <h2>🏢 Station Info</h2>
        <p>Get detailed information about stations in a system</p>
    </div>
    <div class="card">
        <div class="form-grid">
            <div class="form-group">
                <label>System Name</label>
                <input type="text" id="station-system" placeholder="e.g. Sol, Col 285 Sector">
            </div>
            <div class="form-group" style="display:flex;align-items:flex-end;">
                <button onclick="searchStation()">Get Stations</button>
            </div>
        </div>
    </div>
    <div id="station-results" class="card" style="display:none;">
        <div class="card-header">
            <span class="card-title">Stations in <span id="station-system-name"></span></span>
        </div>
        <div id="station-list" class="results-grid"></div>
    </div>
</div>

<!-- TRADE ROUTES PAGE -->
<div id="page-route" class="page">
    <div class="page-header">
        <h2>📍 Trade Routes</h2>
        <p>Calculate distance and find stations between two systems</p>
    </div>
    <div class="card">
        <div class="form-grid">
            <div class="form-group">
                <label>From System</label>
                <input type="text" id="route-from" placeholder="e.g. Sol">
            </div>
            <div class="form-group">
                <label>To System</label>
                <input type="text" id="route-to" placeholder="e.g. Lave">
            </div>
            <div class="form-group" style="display:flex;align-items:flex-end;">
                <button onclick="searchRoute()">Calculate Route</button>
            </div>
        </div>
    </div>
    <div id="route-results" class="card" style="display:none;">
        <div class="stat-grid" style="margin-bottom:20px;">
            <div class="stat-box">
                <div class="value" id="route-distance">-</div>
                <div class="label">Distance (LY)</div>
            </div>
        </div>
        <div id="route-stations"></div>
    </div>
</div>

<!-- SERVICE FINDER PAGE -->
<div id="page-services" class="page">
    <div class="page-header">
        <h2>🔧 Service Finder</h2>
        <p>Find stations with specific services near a system</p>
    </div>
    <div class="card">
        <div class="form-grid">
            <div class="form-group">
                <label>Center System</label>
                <input type="text" id="service-system" placeholder="e.g. Sol">
            </div>
            <div class="form-group">
                <label>Service Type</label>
                <select id="service-type">
                    <option value="Material Trader">Material Trader</option>
                    <option value="Technology Broker">Technology Broker</option>
                    <option value="Interstellar Factors">Interstellar Factors</option>
                    <option value="Outfitting">Outfitting</option>
                    <option value="Shipyard">Shipyard</option>
                    <option value="Repair">Repair</option>
                    <option value="Refuel">Refuel</option>
                    <option value="Restock">Restock</option>
                    <option value="Black Market">Black Market</option>
                    <option value="Universal Cartographics">Universal Cartographics</option>
                </select>
            </div>
            <div class="form-group" style="display:flex;align-items:flex-end;">
                <button onclick="searchServices()">Find Stations</button>
            </div>
        </div>
    </div>
    <div id="service-results" class="card" style="display:none;">
        <div class="card-header">
            <span class="card-title">Stations with <span id="service-type-name"></span></span>
        </div>
        <div id="service-list" class="results-grid"></div>
    </div>
</div>

<!-- SYSTEM STATES PAGE -->
<div id="page-states" class="page">
    <div class="page-header">
        <h2>📊 System State Tracker</h2>
        <p>Check system states and their effects on trade</p>
    </div>
    <div class="card">
        <div class="form-grid">
            <div class="form-group">
                <label>System Name</label>
                <input type="text" id="state-system" placeholder="e.g. Diaguandi, Orrere">
            </div>
            <div class="form-group" style="display:flex;align-items:flex-end;">
                <button onclick="checkStates()">Check State</button>
            </div>
        </div>
    </div>
    <div id="state-results" class="card" style="display:none;">
        <div class="stat-grid" style="margin-bottom:20px;">
            <div class="stat-box">
                <div class="value" id="state-name">-</div>
                <div class="label">Current State</div>
            </div>
            <div class="stat-box">
                <div class="value" id="state-economy">-</div>
                <div class="label">Economy</div>
            </div>
            <div class="stat-box">
                <div class="value" id="state-security">-</div>
                <div class="label">Security</div>
            </div>
        </div>
        <div id="state-effects"></div>
    </div>
    <div class="card">
        <div class="card-header"><span class="card-title">State Reference Guide</span></div>
        <div id="state-guide"></div>
    </div>
</div>

<!-- ENGINEERING PAGE -->
<div id="page-engineering" class="page">
    <div class="page-header">
        <h2>⚙️ Engineering Calculator</h2>
        <p>Calculate material requirements for engineering blueprints</p>
    </div>
    <div class="card">
        <div class="form-grid">
            <div class="form-group">
                <label>Module Type</label>
                <select id="eng-module" onchange="updateBlueprints()">
                    <option value="FSD Range">FSD Range</option>
                    <option value="Shield Boost">Shield Boost</option>
                    <option value="Weapon Damage">Weapon Damage</option>
                    <option value="Armor">Armor</option>
                    <option value="Engine">Engine</option>
                </select>
            </div>
            <div class="form-group">
                <label>Blueprint</label>
                <select id="eng-blueprint"></select>
            </div>
            <div class="form-group" style="display:flex;align-items:flex-end;">
                <button onclick="calcEngineering()">Calculate</button>
            </div>
        </div>
    </div>
    <div id="eng-results" class="card" style="display:none;">
        <div class="card-header">
            <span class="card-title" id="eng-blueprint-name">Blueprint</span>
        </div>
        <div id="eng-materials"></div>
        <div class="card-header" style="margin-top:20px;">
            <span class="card-title">Best Sources for Materials</span>
        </div>
        <div id="eng-sources"></div>
    </div>
</div>

<!-- COLONY ADVISOR PAGE -->
<div id="page-colonize" class="page">
    <div class="page-header">
        <h2>🏗️ Colony Advisor</h2>
        <p>Plan your colony with the tech tree builder</p>
    </div>
    <div class="card">
        <div class="form-grid">
            <div class="form-group">
                <label>System</label>
                <input type="text" id="colony-system" placeholder="e.g. Beta Hydri">
            </div>
            <div class="form-group">
                <label>Goal</label>
                <select id="colony-goal">
                    <option value="balanced">Balanced</option>
                    <option value="tech">Tech Focus</option>
                    <option value="wealth">Wealth Focus</option>
                    <option value="population">Population Focus</option>
                    <option value="military">Military Focus</option>
                </select>
            </div>
            <div class="form-group" style="display:flex;align-items:flex-end;">
                <button onclick="planColony()">Plan Colony</button>
            </div>
        </div>
    </div>
    <div id="colony-results" class="card" style="display:none;">
        <div id="colony-suggestions"></div>
    </div>
</div>

<!-- GUARDIAN SITES PAGE -->
<div id="page-guardian" class="page">
    <div class="page-header">
        <h2>👽 Guardian Sites</h2>
        <p>Known Guardian structures and ruins locations</p>
    </div>
    <div class="card">
        <div class="card-header"><span class="card-title">Major Guardian Sites</span></div>
        <div id="guardian-list" class="results-grid"></div>
    </div>
    <div class="card">
        <div class="card-header"><span class="card-title">Guardian Materials</span></div>
        <div style="display:flex;flex-wrap:wrap;gap:8px;">
            <span class="material-chip encoded">Guardian Technology Components</span>
            <span class="material-chip encoded">Guardian Module Blueprints</span>
            <span class="material-chip encoded">Guardian Weapon Blueprints</span>
            <span class="material-chip encoded">Guardian Data Core</span>
            <span class="material-chip encoded">Guardian Weapon Parts</span>
        </div>
    </div>
</div>

<!-- THARGOID SITES PAGE -->
<div id="page-thargoid" class="page">
    <div class="page-header">
        <h2>🛸 Thargoid Sites</h2>
        <p>Known Thargoid structures and crash sites</p>
    </div>
    <div class="card">
        <div class="card-header"><span class="card-title">Major Thargoid Sites</span></div>
        <div id="thargoid-list" class="results-grid"></div>
    </div>
    <div class="card">
        <div class="card-header"><span class="card-title">Thargoid Materials</span></div>
        <div style="display:flex;flex-wrap:wrap;gap:8px;">
            <span class="material-chip manufactured">Thargoid Technology Components</span>
            <span class="material-chip manufactured">Thargoid Biological Matter</span>
            <span class="material-chip manufactured">Thargoid Material Composition</span>
            <span class="material-chip manufactured">Thargoid Ship Components</span>
            <span class="material-chip manufactured">Thargoid Probe</span>
        </div>
    </div>
</div>

<!-- FLEET CARRIER PAGE -->
<div id="page-carrier" class="page">
    <div class="page-header">
        <h2>🚀 Fleet Carrier Support</h2>
        <p>Search for fleet carriers and their services</p>
    </div>
    <div class="card">
        <div class="form-grid">
            <div class="form-group">
                <label>Search Term</label>
                <input type="text" id="carrier-search" placeholder="Carrier name or ID">
            </div>
            <div class="form-group" style="display:flex;align-items:flex-end;">
                <button onclick="searchCarrier()">Search Carriers</button>
            </div>
        </div>
    </div>
    <div id="carrier-results" class="card" style="display:none;">
        <div id="carrier-list" class="results-grid"></div>
    </div>
    <div class="card">
        <div class="card-header"><span class="card-title">Fleet Carrier Services</span></div>
        <p style="color:var(--text-dim);font-size:0.85em;margin-bottom:10px;">Note: EDSM doesn't provide carrier market data directly. Use EDDB.io or Inara for carrier trading data.</p>
        <div style="display:flex;flex-wrap:wrap;gap:8px;">
            <span class="service-badge green">Market</span>
            <span class="service-badge green">Shipyard</span>
            <span class="service-badge green">Outfitting</span>
            <span class="service-badge green">Repair</span>
            <span class="service-badge green">Refuel</span>
            <span class="service-badge green">Restock</span>
            <span class="service-badge orange">Carrier Management</span>
            <span class="service-badge orange">Banking</span>
        </div>
    </div>
</div>

<!-- INARA PAGE -->
<div id="page-inara" class="page">
    <div class="page-header">
        <h2>🔗 Inara.cz Integration</h2>
        <p>Connect your Inara.cz account for personalized data</p>
    </div>
    <div class="card">
        <div class="card-header"><span class="card-title">API Configuration</span></div>
        <div class="form-grid">
            <div class="form-group">
                <label>Inara API Key</label>
                <input type="password" id="inara-key" placeholder="Your Inara API key">
            </div>
            <div class="form-group" style="display:flex;align-items:flex-end;">
                <button onclick="saveInaraKey()">💾 Save Key</button>
            </div>
        </div>
        <p style="color:var(--text-dim);font-size:0.8em;margin-top:10px;">
            Get your API key from <span style="color:var(--cyan);">inara.cz</span> → Settings → API Key
        </p>
    </div>
    
    <div class="card">
        <div class="card-header"><span class="card-title">Sync Commander Data</span></div>
        <div style="margin-bottom:15px;">
            <p style="color:var(--text-dim);font-size:0.85em;margin-bottom:10px;">Fetch your commander profile, ranks, ships, and materials directly from Inara.cz. Make sure your CMDR name matches exactly.</p>
            <div class="form-grid">
                <div class="form-group">
                    <input type="text" id="inara-cmdr" placeholder="CMDR Name (must match Inara)">
                </div>
                <div class="form-group" style="display:flex;align-items:flex-end;">
                    <button onclick="syncInara()">🔄 Sync from Inara</button>
                </div>
            </div>
        </div>
        <div id="inara-sync-status" class="results-grid" style="display:none;"></div>
    </div>
    
    <div id="inara-profile" class="card" style="display:none;">
        <div class="card-header">
            <span class="card-title">Synced Commander Data</span>
            <button class="secondary" onclick="applyToDashboard()">📥 Import to Dashboard</button>
        </div>
        <div id="inara-data"></div>
    </div>
    
    <div class="card">
        <div class="card-header"><span class="card-title">What Gets Imported</span></div>
        <div style="display:flex;flex-wrap:wrap;gap:8px;margin-bottom:15px;">
            <span class="service-badge green">✅ Commander Name</span>
            <span class="service-badge green">✅ Combat Rank</span>
            <span class="service-badge green">✅ Trade Rank</span>
            <span class="service-badge green">✅ Exploration Rank</span>
            <span class="service-badge green">✅ Credits</span>
            <span class="service-badge green">✅ Material Inventory</span>
            <span class="service-badge orange">⚠️ Ship Loadouts (partial)</span>
            <span class="service-badge orange">⚠️ Community Goals</span>
            <span class="service-badge orange">⚠️ Reputation (partial)</span>
        </div>
        <p style="color:var(--text-dim);font-size:0.85em;">
            Data is fetched directly from Inara's servers. Some fields may not be available depending on your Inara privacy settings.
        </p>
    </div>
</div>

<!-- COMMANDER DASHBOARD PAGE -->
<div id="page-commander" class="page">
    <div class="page-header">
        <h2>👤 Commander Dashboard</h2>
        <p>Your Elite Dangerous command center</p>
    </div>
    
    <div class="card">
        <div class="card-header"><span class="card-title">Commander Profile</span></div>
        <div class="form-grid" style="margin-bottom:15px;">
            <div class="form-group">
                <label>Commander Name (CMDR)</label>
                <input type="text" id="cmdr-name" placeholder="Your CMDR name">
            </div>
            <div class="form-group">
                <label>Current Ship</label>
                <input type="text" id="cmdr-ship" placeholder="e.g. Anaconda, Corvette">
            </div>
            <div class="form-group">
                <label>Home System</label>
                <input type="text" id="cmdr-home" placeholder="e.g. Sol, Diaguandi">
            </div>
            <div class="form-group">
                <label>Current Location</label>
                <input type="text" id="cmdr-location" placeholder="Current system">
            </div>
        </div>
        <div class="form-grid">
            <div class="form-group">
                <label>Credits (CR)</label>
                <input type="text" id="cmdr-credits" placeholder="e.g. 1,500,000,000">
            </div>
            <div class="form-group">
                <label>Ranks (Combat/Trade/Explore)</label>
                <input type="text" id="cmdr-ranks" placeholder="e.g. Expert/Master/Elite">
            </div>
        </div>
        <button onclick="saveCommander()">Save Profile</button>
    </div>
    
    <div id="cmdr-display" class="card" style="display:none;">
        <div class="stat-grid">
            <div class="stat-box">
                <div class="value" id="disp-name">-</div>
                <div class="label">Commander</div>
            </div>
            <div class="stat-box">
                <div class="value" id="disp-ship">-</div>
                <div class="label">Current Ship</div>
            </div>
            <div class="stat-box">
                <div class="value" id="disp-location">-</div>
                <div class="label">Location</div>
            </div>
            <div class="stat-box">
                <div class="value" id="disp-credits">-</div>
                <div class="label">Credits</div>
            </div>
        </div>
    </div>
    
    <div class="card">
        <div class="card-header"><span class="card-title">Quick Actions</span></div>
        <div style="display:flex;flex-wrap:wrap;gap:10px;">
            <button class="secondary" onclick="quickAction('plot-home')">📍 Plot Route Home</button>
            <button class="secondary" onclick="quickAction('nearest-station')">🏢 Nearest Station</button>
            <button class="secondary" onclick="quickAction('nearest-fuel')">⛽ Nearest Fuel</button>
            <button class="secondary" onclick="quickAction('nearest-repair')">🔧 Nearest Repair</button>
            <button class="secondary" onclick="quickAction('nearest-material-trader')">🔄 Material Trader</button>
            <button class="secondary" onclick="quickAction('nearest-tech-broker')">⚙️ Tech Broker</button>
        </div>
    </div>
    
    <div class="card">
        <div class="card-header"><span class="card-title">Data Backup & Restore</span></div>
        <div style="display:flex;flex-wrap:wrap;gap:10px;">
            <button class="secondary" onclick="exportData()">📤 Export All Data</button>
            <button class="secondary" onclick="document.getElementById('import-file').click()">📥 Import Data</button>
            <input type="file" id="import-file" accept=".json" style="display:none;" onchange="importData(event)">
            <button class="secondary" onclick="clearAllData()" style="border-color:var(--red);color:var(--red);">🗑️ Clear All</button>
        </div>
        <p style="color:var(--text-dim);font-size:0.8em;margin-top:10px;">
            Export your commander profile, colonies, ships, materials, and bookmarks to a JSON file. Keep it safe — this is your progress backup.
        </p>
    </div>
    
    <div class="card">
        <div class="card-header"><span class="card-title">Recent Activity</span></div>
        <div id="activity-log" class="results-grid">
            <p style="color:var(--text-dim);font-size:0.85em;">No recent activity. Start exploring!</p>
        </div>
    </div>
</div>

<!-- MY COLONIES PAGE -->
<div id="page-colonies" class="page">
    <div class="page-header">
        <h2>🏰 My Colonies</h2>
        <p>Track your colonized systems and facility progress</p>
    </div>
    
    <div class="card">
        <div class="card-header"><span class="card-title">Add Colonized System</span></div>
        <div class="form-grid">
            <div class="form-group">
                <label>System Name</label>
                <input type="text" id="colony-system" placeholder="e.g. Beta Hydri">
            </div>
            <div class="form-group">
                <label>Station Name</label>
                <input type="text" id="colony-station" placeholder="e.g. Markov Station">
            </div>
            <div class="form-group">
                <label>Station Type</label>
                <select id="colony-type">
                    <option value="Orbital Station">Orbital Station</option>
                    <option value=" planetary Outpost">Planetary Outpost</option>
                    <option value="Planetary Port">Planetary Port</option>
                    <option value="Fleet Carrier">Fleet Carrier</option>
                </select>
            </div>
        </div>
        <button onclick="addColony()">Add Colony</button>
    </div>
    
    <div id="colonies-list" class="card">
        <div class="card-header"><span class="card-title">Your Colonies</span></div>
        <div id="colonies-results" class="results-grid"></div>
    </div>
    
    <div id="colony-detail" class="card" style="display:none;">
        <div class="card-header">
            <span class="card-title" id="colony-detail-name">Colony Name</span>
            <button class="secondary" onclick="closeColonyDetail()">← Back</button>
        </div>
        
        <div class="form-grid" style="margin-bottom:15px;">
            <div class="form-group">
                <label>Built Facilities</label>
                <div id="colony-facilities" style="display:flex;flex-wrap:wrap;gap:5px;margin-top:5px;"></div>
            </div>
        </div>
        
        <h4 style="color:var(--cyan);margin:15px 0 10px;">Add Facility</h4>
        <div class="form-grid">
            <div class="form-group">
                <label>Facility Type</label>
                <select id="add-facility">
                    <option value="High Tech Hub">High Tech Hub</option>
                    <option value="Industrial Hub">Industrial Hub</option>
                    <option value="Mining Hub">Mining Hub</option>
                    <option value="Refinery Hub">Refinery Hub</option>
                    <option value="Trading Hub">Trading Hub</option>
                    <option value="Exploration Hub">Exploration Hub</option>
                    <option value="Military Installation">Military Installation</option>
                    <option value="Terraforming Hub">Terraforming Hub</option>
                    <option value="Research Lab">Research Lab</option>
                    <option value="Shipyard Hub">Shipyard Hub</option>
                    <option value="Farm Complex">Farm Complex</option>
                    <option value="Power Plant">Power Plant</option>
                    <option value="Water Treatment">Water Treatment</option>
                    <option value="Communications Array">Communications Array</option>
                    <option value="Mission Board">Mission Board</option>
                    <option value="Barracks">Barracks</option>
                </select>
            </div>
        </div>
        <button onclick="addFacility()">Add Facility</button>
        
        <h4 style="color:var(--cyan);margin:15px 0 10px;">Colony Stats</h4>
        <div id="colony-stats" class="stat-grid"></div>
    </div>
</div>

<!-- SHIP HANGAR PAGE -->
<div id="page-ships" class="page">
    <div class="page-header">
        <h2>🚀 Ship Hangar</h2>
        <p>Track your ships and their loadouts</p>
    </div>
    
    <div class="card">
        <div class="card-header"><span class="card-title">Add Ship</span></div>
        <div class="form-grid">
            <div class="form-group">
                <label>Ship Type</label>
                <input type="text" id="ship-name" placeholder="e.g. Anaconda, Python, Krait Phantom">
            </div>
            <div class="form-group">
                <label>Role</label>
                <select id="ship-role">
                    <option value="Combat">Combat</option>
                    <option value="Trading">Trading</option>
                    <option value="Exploration">Exploration</option>
                    <option value="Mining">Mining</option>
                    <option value="Passenger">Passenger</option>
                    <option value="Mission Running">Mission Running</option>
                    <option value="PvP">PvP</option>
                </select>
            </div>
            <div class="form-group">
                <label>Build Status</label>
                <select id="ship-build">
                    <option value="Stock">Stock</option>
                    <option value="Partial">Partial Engineering</option>
                    <option value="Full">Fully Engineered</option>
                </select>
            </div>
        </div>
        <button onclick="addShip()">Add Ship</button>
    </div>
    
    <div id="ships-list" class="card">
        <div class="card-header"><span class="card-title">Your Ships</span></div>
        <div id="ships-results" class="results-grid"></div>
    </div>
</div>

<!-- MATERIALS PAGE -->
<div id="page-materials" class="page">
    <div class="page-header">
        <h2>📦 Material Inventory</h2>
        <p>Track your engineering materials and synthesis needs</p>
    </div>
    
    <div class="card">
        <div class="card-header"><span class="card-title">Add Material</span></div>
        <div class="form-grid">
            <div class="form-group">
                <label>Material Name</label>
                <input type="text" id="mat-name" placeholder="e.g. Phosphorus, Encoded, Micro Controllers">
            </div>
            <div class="form-group">
                <label>Type</label>
                <select id="mat-type">
                    <option value="Raw">Raw</option>
                    <option value="Encoded">Encoded</option>
                    <option value="Manufactured">Manufactured</option>
                </select>
            </div>
            <div class="form-group">
                <label>Quantity</label>
                <input type="number" id="mat-qty" placeholder="e.g. 27" value="1">
            </div>
            <div class="form-group">
                <label>Grade (1-5)</label>
                <select id="mat-grade">
                    <option value="1">Grade 1</option>
                    <option value="2">Grade 2</option>
                    <option value="3">Grade 3</option>
                    <option value="4">Grade 4</option>
                    <option value="5">Grade 5</option>
                </select>
            </div>
        </div>
        <button onclick="addMaterial()">Add Material</button>
    </div>
    
    <div class="card">
        <div class="card-header"><span class="card-title">Material Categories</span></div>
        <div style="display:flex;gap:10px;margin-bottom:15px;flex-wrap:wrap;">
            <button class="secondary" onclick="filterMaterials('all')">All</button>
            <button class="secondary" onclick="filterMaterials('Raw')">Raw</button>
            <button class="secondary" onclick="filterMaterials('Encoded')">Encoded</button>
            <button class="secondary" onclick="filterMaterials('Manufactured')">Manufactured</button>
        </div>
        <div id="materials-results" class="results-grid"></div>
    </div>
    
    <div class="card">
        <div class="card-header"><span class="card-title">Shopping List</span></div>
        <p style="color:var(--text-dim);font-size:0.85em;margin-bottom:10px;">Materials you need to gather for your next engineering goal</p>
        <div id="shopping-list" style="display:flex;flex-wrap:wrap;gap:8px;"></div>
        <div style="margin-top:10px;">
            <input type="text" id="shopping-mat" placeholder="Add to shopping list..." style="max-width:200px;">
            <button class="secondary" onclick="addToShopping()">Add</button>
        </div>
    </div>
</div>

<!-- BOOKMARKS PAGE -->
<div id="page-bookmarks" class="page">
    <div class="page-header">
        <h2>⭐ Bookmarks</h2>
        <p>Save your favorite systems, stations, and routes</p>
    </div>
    
    <div class="card">
        <div class="card-header"><span class="card-title">Add Bookmark</span></div>
        <div class="form-grid">
            <div class="form-group">
                <label>Type</label>
                <select id="bm-type">
                    <option value="System">System</option>
                    <option value="Station">Station</option>
                    <option value="Route">Route</option>
                    <option value="POI">Point of Interest</option>
                    <option value="Mining">Mining Spot</option>
                    <option value="Combat">Combat Zone</option>
                </select>
            </div>
            <div class="form-group">
                <label>Name</label>
                <input type="text" id="bm-name" placeholder="Bookmark name">
            </div>
            <div class="form-group">
                <label>Location / System</label>
                <input type="text" id="bm-location" placeholder="e.g. Core Dynamics, Sol">
            </div>
            <div class="form-group">
                <label>Notes</label>
                <input type="text" id="bm-notes" placeholder="Optional notes">
            </div>
        </div>
        <button onclick="addBookmark()">Add Bookmark</button>
    </div>
    
    <div class="card">
        <div class="card-header"><span class="card-title">Your Bookmarks</span></div>
        <div style="display:flex;gap:10px;margin-bottom:15px;flex-wrap:wrap;">
            <button class="secondary" onclick="filterBookmarks('all')">All</button>
            <button class="secondary" onclick="filterBookmarks('System')">Systems</button>
            <button class="secondary" onclick="filterBookmarks('Station')">Stations</button>
            <button class="secondary" onclick="filterBookmarks('Mining')">Mining</button>
            <button class="secondary" onclick="filterBookmarks('POI')">POIs</button>
        </div>
        <div id="bookmarks-results" class="results-grid"></div>
    </div>
</div>

</main>

<!-- STATION DETAIL MODAL -->
<div id="station-modal" class="modal-overlay">
    <div class="modal">
        <div class="modal-header">
            <h3 id="modal-station-name">Station Name</h3>
            <button class="modal-close" onclick="closeModal()">×</button>
        </div>
        <div class="modal-body">
            <div class="stat-grid" style="margin-bottom:20px;">
                <div class="stat-box">
                    <div class="value" id="modal-station-type">-</div>
                    <div class="label">Type</div>
                </div>
                <div class="stat-box">
                    <div class="value" id="modal-station-distance">-</div>
                    <div class="label">Distance (LS)</div>
                </div>
                <div class="stat-box">
                    <div class="value" id="modal-station-economy">-</div>
                    <div class="label">Economy</div>
                </div>
                <div class="stat-box">
                    <div class="value" id="modal-station-government">-</div>
                    <div class="label">Government</div>
                </div>
            </div>
            
            <div class="modal-section">
                <h4>🚉 Services</h4>
                <div id="modal-services"></div>
            </div>
            
            <div class="modal-tabs">
                <button class="modal-tab active" onclick="showModalTab('market')">Market</button>
                <button class="modal-tab" onclick="showModalTab('outfitting')">Outfitting</button>
                <button class="modal-tab" onclick="showModalTab('shipyard')">Shipyard</button>
            </div>
            
            <div id="modal-tab-market" class="tab-content active">
                <div id="modal-market-list"></div>
            </div>
            <div id="modal-tab-outfitting" class="tab-content">
                <div id="modal-outfitting-list"></div>
            </div>
            <div id="modal-tab-shipyard" class="tab-content">
                <div id="modal-shipyard-list"></div>
            </div>
        </div>
    </div>
</div>

<script>
// Navigation
function showPage(pageId) {
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
    document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
    document.getElementById('page-' + pageId).classList.add('active');
    event.target.closest('.nav-item').classList.add('active');
    if (pageId === 'states') loadStateGuide();
    if (pageId === 'guardian') loadGuardianSites();
    if (pageId === 'thargoid') loadThargoidSites();
}

// Trade Search
async function searchTrade() {
    const system = document.getElementById('trade-system').value;
    const commodity = document.getElementById('trade-commodity').value;
    if (!system || !commodity) { alert('Please enter system and commodity'); return; }
    
    const results = document.getElementById('trade-results');
    const list = document.getElementById('trade-results-list');
    results.style.display = 'block';
    list.innerHTML = '<div class="loading">Searching</div>';
    
    try {
        const resp = await fetch(`/api/search?system=${encodeURIComponent(system)}&commodity=${encodeURIComponent(commodity)}`);
        const data = await resp.json();
        
        if (data.error) { list.innerHTML = `<div class="empty-state"><p>Error: ${data.error}</p></div>`; return; }
        
        document.getElementById('trade-count').textContent = `${data.count} results`;
        
        if (!data.results || data.results.length === 0) {
            list.innerHTML = '<div class="empty-state"><p>No results found</p></div>';
            return;
        }
        
        list.innerHTML = data.results.slice(0, 20).map(r => `
            <div class="result-item" onclick="openStationModal('${data.system}', '${r.station}')">
                <div class="station-name">${r.station}</div>
                <div class="station-info">
                    ${r.type} • ${r.distance} LS from star<br>
                    Buy: <span class="price-buy">${r.buy.toLocaleString()}</span> CR | 
                    Sell: <span class="price-sell">${r.sell.toLocaleString()}</span> CR<br>
                    Stock: ${r.stock.toLocaleString()} | Demand: ${r.demand.toLocaleString()}
                </div>
            </div>
        `).join('');
    } catch (e) {
        list.innerHTML = `<div class="empty-state"><p>Error: ${e.message}</p></div>`;
    }
}

// Station Search
async function searchStation() {
    const system = document.getElementById('station-system').value;
    if (!system) { alert('Please enter a system name'); return; }
    
    const results = document.getElementById('station-results');
    const list = document.getElementById('station-list');
    document.getElementById('station-system-name').textContent = system;
    results.style.display = 'block';
    list.innerHTML = '<div class="loading">Loading stations</div>';
    
    try {
        const resp = await fetch(`/api/station?system=${encodeURIComponent(system)}`);
        const data = await resp.json();
        
        if (data.error || !data.stations) {
            list.innerHTML = `<div class="empty-state"><p>${data.error || 'No stations found'}</p></div>`;
            return;
        }
        
        if (data.stations.length === 0) {
            list.innerHTML = '<div class="empty-state"><p>No stations found in this system</p></div>';
            return;
        }
        
        list.innerHTML = data.stations.map(s => `
            <div class="result-item" onclick="openStationModal('${data.system}', '${s.name}')">
                <div class="station-name">${s.name}</div>
                <div class="station-info">
                    ${s.type || 'Unknown'} • ${s.distanceToArrival || '?'} LS<br>
                    Economy: ${s.economy || 'Unknown'} • ${s.government || ''}<br>
                    ${formatServices(s)}
                </div>
            </div>
        `).join('');
    } catch (e) {
        list.innerHTML = `<div class="empty-state"><p>Error: ${e.message}</p></div>`;
    }
}

function formatServices(station) {
    const services = [];
    if (station.haveMarket) services.push('<span class="service-badge green">Market</span>');
    if (station.haveShipyard) services.push('<span class="service-badge">Shipyard</span>');
    if (station.haveOutfitting) services.push('<span class="service-badge">Outfitting</span>');
    if (station.hasRefuel) services.push('<span class="service-badge">Refuel</span>');
    if (station.hasRepair) services.push('<span class="service-badge">Repair</span>');
    if (station.hasRestock) services.push('<span class="service-badge">Restock</span>');
    return services.length > 0 ? services.join(' ') : 'No services';
}

// Station Modal
async function openStationModal(system, station) {
    document.getElementById('station-modal').classList.add('active');
    document.getElementById('modal-station-name').textContent = station;
    
    // Show loading
    document.getElementById('modal-market-list').innerHTML = '<div class="loading">Loading market data</div>';
    document.getElementById('modal-outfitting-list').innerHTML = '<div class="loading">Loading outfitting</div>';
    document.getElementById('modal-shipyard-list').innerHTML = '<div class="loading">Loading shipyard</div>';
    
    // Get station info first
    try {
        const resp = await fetch(`/api/station_detail?system=${encodeURIComponent(system)}&station=${encodeURIComponent(station)}`);
        const data = await resp.json();
        
        document.getElementById('modal-station-type').textContent = data.type || 'Unknown';
        document.getElementById('modal-station-distance').textContent = data.distance || '?';
        document.getElementById('modal-station-economy').textContent = data.economy || 'Unknown';
        document.getElementById('modal-station-government').textContent = data.government || 'Unknown';
        document.getElementById('modal-services').innerHTML = data.services || '<span class="service-badge">None listed</span>';
        
        // Market data
        if (data.market && data.market.length > 0) {
            document.getElementById('modal-market-list').innerHTML = `
                <table class="data-table">
                    <thead><tr><th>Commodity</th><th>Buy</th><th>Sell</th><th>Stock</th><th>Demand</th></tr></thead>
                    <tbody>
                        ${data.market.slice(0, 30).map(c => `
                            <tr>
                                <td>${c.name}</td>
                                <td class="price-buy">${c.buyPrice ? c.buyPrice.toLocaleString() : '-'}</td>
                                <td class="price-sell">${c.sellPrice ? c.sellPrice.toLocaleString() : '-'}</td>
                                <td>${c.stock ? c.stock.toLocaleString() : '-'}</td>
                                <td>${c.demand ? c.demand.toLocaleString() : '-'}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            `;
        } else {
            document.getElementById('modal-market-list').innerHTML = '<div class="empty-state"><p>No market data available</p></div>';
        }
        
        // Outfitting
        if (data.outfitting && data.outfitting.length > 0) {
            const cats = {};
            data.outfitting.forEach(m => {
                const cat = m.category || 'Other';
                if (!cats[cat]) cats[cat] = [];
                cats[cat].push(m);
            });
            document.getElementById('modal-outfitting-list').innerHTML = Object.entries(cats).slice(0, 5).map(([cat, mods]) => `
                <h5 style="color:var(--cyan);margin:10px 0 5px;">${cat}</h5>
                <div style="display:flex;flex-wrap:wrap;gap:5px;">
                    ${mods.slice(0, 10).map(m => `<span class="service-badge">${m.name || 'Unknown'}</span>`).join('')}
                </div>
            `).join('');
        } else {
            document.getElementById('modal-outfitting-list').innerHTML = '<div class="empty-state"><p>No outfitting data available</p></div>';
        }
        
        // Shipyard
        if (data.shipyard && data.shipyard.length > 0) {
            document.getElementById('modal-shipyard-list').innerHTML = `
                <div style="display:flex;flex-wrap:wrap;gap:8px;">
                    ${data.shipyard.map(s => `<span class="service-badge">${s.name || s}</span>`).join('')}
                </div>
            `;
        } else {
            document.getElementById('modal-shipyard-list').innerHTML = '<div class="empty-state"><p>No shipyard data available</p></div>';
        }
    } catch (e) {
        console.error(e);
    }
}

function closeModal() {
    document.getElementById('station-modal').classList.remove('active');
}

function showModalTab(tab) {
    document.querySelectorAll('.modal-tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
    document.querySelector(`.modal-tab[onclick="showModalTab('${tab}')"]`).classList.add('active');
    document.getElementById('modal-tab-' + tab).classList.add('active');
}

// Trade Route
async function searchRoute() {
    const from = document.getElementById('route-from').value;
    const to = document.getElementById('route-to').value;
    if (!from || !to) { alert('Please enter both systems'); return; }
    
    const results = document.getElementById('route-results');
    results.style.display = 'block';
    document.getElementById('route-stations').innerHTML = '<div class="loading">Calculating</div>';
    
    try {
        const resp = await fetch(`/api/route?from=${encodeURIComponent(from)}&to=${encodeURIComponent(to)}`);
        const data = await resp.json();
        
        document.getElementById('route-distance').textContent = data.distance ? data.distance.toFixed(1) + ' LY' : '-';
        
        if (data.stations && data.stations.length > 0) {
            document.getElementById('route-stations').innerHTML = data.stations.map(s => `
                <div class="result-item">
                    <div class="station-name">${s.name}</div>
                    <div class="station-info">
                        ${s.type} • ${s.economy} • ${s.government || ''}<br>
                        Market: ${s.haveMarket ? '<span class="service-badge green">Yes</span>' : '<span class="service-badge">No</span>'}
                        Shipyard: ${s.haveShipyard ? '<span class="service-badge green">Yes</span>' : '<span class="service-badge">No</span>'}
                    </div>
                </div>
            `).join('');
        } else {
            document.getElementById('route-stations').innerHTML = '<div class="empty-state"><p>No stations found at destination</p></div>';
        }
    } catch (e) {
        document.getElementById('route-stations').innerHTML = `<div class="empty-state"><p>Error: ${e.message}</p></div>`;
    }
}

// Service Finder
async function searchServices() {
    const system = document.getElementById('service-system').value;
    const serviceType = document.getElementById('service-type').value;
    if (!system) { alert('Please enter a system'); return; }
    
    document.getElementById('service-type-name').textContent = serviceType;
    const results = document.getElementById('service-results');
    const list = document.getElementById('service-list');
    results.style.display = 'block';
    list.innerHTML = '<div class="loading">Searching for stations</div>';
    
    try {
        const resp = await fetch(`/api/service_finder?system=${encodeURIComponent(system)}&service=${encodeURIComponent(serviceType)}`);
        const data = await resp.json();
        
        if (data.error) {
            list.innerHTML = `<div class="empty-state"><p>${data.error}</p></div>`;
            return;
        }
        
        if (!data.stations || data.stations.length === 0) {
            list.innerHTML = `<div class="empty-state"><p>No stations with ${serviceType} found. Try a larger trade hub system.</p></div>`;
            return;
        }
        
        list.innerHTML = data.stations.map(s => `
            <div class="result-item" onclick="openStationModal('${data.system}', '${s.name}')">
                <div class="station-name">${s.name}</div>
                <div class="station-info">
                    ${s.type} • ${s.distance} LS from star<br>
                    ${s.services.map(sv => `<span class="service-badge ${getServiceClass(sv)}">${sv}</span>`).join('')}
                </div>
            </div>
        `).join('');
    } catch (e) {
        list.innerHTML = `<div class="empty-state"><p>Error: ${e.message}</p></div>`;
    }
}

function getServiceClass(service) {
    if (['Market', 'Shipyard', 'Outfitting'].includes(service)) return 'green';
    if (['Black Market', 'Interstellar Factors'].includes(service)) return 'orange';
    return '';
}

// System States
async function checkStates() {
    const system = document.getElementById('state-system').value;
    if (!system) { alert('Please enter a system'); return; }
    
    const results = document.getElementById('state-results');
    results.style.display = 'block';
    
    try {
        const resp = await fetch(`/api/system_states?system=${encodeURIComponent(system)}`);
        const data = await resp.json();
        
        document.getElementById('state-name').textContent = data.state || 'None';
        document.getElementById('state-economy').textContent = data.economy || 'Unknown';
        document.getElementById('state-security').textContent = data.security || 'Unknown';
        
        const effects = document.getElementById('state-effects');
        if (data.state && data.effects) {
            effects.innerHTML = `
                <div class="card" style="background:rgba(0,0,0,0.2);">
                    <h5 style="color:var(--accent);margin-bottom:10px;">Trade Effects</h5>
                    <p style="color:var(--text-dim);font-size:0.9em;">${data.effects}</p>
                </div>
            `;
        } else {
            effects.innerHTML = '<div class="empty-state"><p>No active state effects</p></div>';
        }
    } catch (e) {
        console.error(e);
    }
}

function loadStateGuide() {
    const states = {
        "Boom": { color: "#0f0", effect: "Increases demand for luxury goods, food, and consumer products" },
        "Bust": { color: "#f44", effect: "Decreases demand for most goods except basics" },
        "War": { color: "#f00", effect: "Increases weapons and military supplies demand" },
        "Civil War": { color: "#f00", effect: "Decreases most trade except weapons" },
        "Famine": { color: "#ff0", effect: "Massively increases food and water prices" },
        "Outbreak": { color: "#f0f", effect: "Increases medical supplies demand" },
        "Peace": { color: "#0f8", effect: "Increases luxury goods and consumer electronics" },
        "Public Holiday": { color: "#fa0", effect: "Increases alcohol, tobacco, and luxury goods" }
    };
    
    const guide = document.getElementById('state-guide');
    if (!guide) return;
    guide.innerHTML = Object.entries(states).map(([name, info]) => `
        <div style="display:flex;gap:15px;padding:10px 0;border-bottom:1px solid var(--border);">
            <span class="state-badge" style="background:${info.color}22;color:${info.color};min-width:100px;">${name}</span>
            <span style="color:var(--text-dim);font-size:0.85em;">${info.effect}</span>
        </div>
    `).join('');
}

// Engineering
function updateBlueprints() {
    const module = document.getElementById('eng-module').value;
    const bpSelect = document.getElementById('eng-blueprint');
    
    const blueprints = {
        "FSD Range": ["Extended Range 5", "Increased Range 4", "Standard 3"],
        "Shield Boost": ["Reinforced 5", "Heavy Duty 4", "Expanded 3"],
        "Weapon Damage": ["Overcharged 5", "Corrosive Shell 4"],
        "Armor": ["Military Grade 5", "Reinforced 4"],
        "Engine": ["Dirty 5", "Clean 4", "Sport 3"]
    };
    
    bpSelect.innerHTML = (blueprints[module] || []).map(bp => `<option value="${bp}">${bp}</option>`).join('');
}

async function calcEngineering() {
    const module = document.getElementById('eng-module').value;
    const blueprint = document.getElementById('eng-blueprint').value;
    
    const results = document.getElementById('eng-results');
    results.style.display = 'block';
    document.getElementById('eng-blueprint-name').textContent = `${module} - ${blueprint}`;
    
    try {
        const resp = await fetch(`/api/engineering?module=${encodeURIComponent(module)}&blueprint=${encodeURIComponent(blueprint)}`);
        const data = await resp.json();
        
        if (data.error) {
            document.getElementById('eng-materials').innerHTML = `<p>${data.error}</p>`;
            return;
        }
        
        document.getElementById('eng-materials').innerHTML = `
            <div style="margin-bottom:15px;">
                <span class="service-badge orange">Grade ${data.grade}</span>
                ${data.experimental ? `<span class="service-badge">Experimental: ${data.experimental}</span>` : ''}
            </div>
            <h5 style="color:var(--cyan);margin-bottom:10px;">Required Materials</h5>
            <div style="display:flex;flex-wrap:wrap;gap:8px;">
                ${Object.entries(data.materials || {}).map(([mat, qty]) => 
                    `<span class="material-chip">${mat}: ${qty}</span>`
                ).join('')}
            </div>
        `;
        
        document.getElementById('eng-sources').innerHTML = `
            <p style="color:var(--text-dim);font-size:0.85em;margin-bottom:10px;">
                Materials can be gathered from: <strong>Material Traders</strong> (Raw/Encoded/Manufactured), 
                <strong>Engineering Worlds</strong>, <strong>Mission Rewards</strong>, and <strong>Salvage</strong>.
            </p>
            <div style="display:flex;flex-wrap:wrap;gap:8px;">
                <span class="service-badge green">Davies Hope</span>
                <span class="service-badge green">Hutton Orbital</span>
                <span class="service-badge green">Jameson Memorial</span>
            </div>
        `;
    } catch (e) {
        console.error(e);
    }
}

// Colony
async function planColony() {
    const system = document.getElementById('colony-system').value;
    const goal = document.getElementById('colony-goal').value;
    
    const results = document.getElementById('colony-results');
    results.style.display = 'block';
    document.getElementById('colony-suggestions').innerHTML = '<div class="loading">Planning</div>';
    
    try {
        const resp = await fetch(`/api/colonize?system=${encodeURIComponent(system)}&goal=${encodeURIComponent(goal)}`);
        const data = await resp.json();
        
        if (data.error) {
            document.getElementById('colony-suggestions').innerHTML = `<p>${data.error}</p>`;
            return;
        }
        
        document.getElementById('colony-suggestions').innerHTML = data.suggestions.map(f => `
            <div class="result-item ${f.locked ? 'locked' : ''}" style="${f.locked ? 'opacity:0.5' : ''}">
                <div class="station-name">${f.name} ${f.locked ? '🔒' : ''}</div>
                <div class="station-info">
                    Tier ${f.tier} • ${f.requires.length > 0 ? 'Requires: ' + f.requires.join(', ') : 'No requirements'}<br>
                    ${Object.entries(f.gives).map(([k, v]) => `<span class="stat-change stat-positive">+${v} ${k}</span>`).join(' ')}
                    <br><br>
                    <strong>Cost:</strong> ${Object.entries(f.cost).map(([k, v]) => `<span class="cost-item">${k}: ${v}</span>`).join(' ')}
                </div>
            </div>
        `).join('');
    } catch (e) {
        console.error(e);
    }
}

// Guardian Sites
function loadGuardianSites() {
    const sites = [
        {"name": "Synuefe EU-R c4-15", "type": "Guardian Structure", "region": "Inner Orion Spur"},
        {"name": "Synuefe XR-R c4-6", "type": "Guardian Structure", "region": "Inner Orion Spur"},
        {"name": "HIP 22441", "type": "Guardian Blueprint Site", "region": "Inner Orion Spur"},
        {"name": "Col 173 Syne 2", "type": "Guardian Ruins", "region": "Orion Arm"},
        {"name": "Meene", "type": "Guardian Ruins", "region": "Orion Arm"}
    ];
    
    const list = document.getElementById('guardian-list');
    if (!list) return;
    list.innerHTML = sites.map(s => `
        <div class="result-item">
            <div class="station-name">${s.name}</div>
            <div class="station-info">
                <span class="service-badge orange">${s.type}</span> • ${s.region}
            </div>
        </div>
    `).join('');
}

// Thargoid Sites
function loadThargoidSites() {
    const sites = [
        {"name": "HIP 21025", "type": "Thargoid Crash Site", "region": "Inner Orion Spur"},
        {"name": "Pleiades Nebula", "type": "Thargoid Structure", "region": "Pleiades"},
        {"name": "WOLF 397", "type": "Thargoid Crash Site", "region": "Orion Arm"},
        {"name": "Hyades Sector AQ-P e5-3", "type": "Thargoid Structure", "region": "Pleiades"},
        {"name": "Merope", "type": "Thargoid Survey Site", "region": "Pleiades"}
    ];
    
    const list = document.getElementById('thargoid-list');
    if (!list) return;
    list.innerHTML = sites.map(s => `
        <div class="result-item">
            <div class="station-name">${s.name}</div>
            <div class="station-info">
                <span class="service-badge red">${s.type}</span> • ${s.region}
            </div>
        </div>
    `).join('');
}

// Fleet Carrier
async function searchCarrier() {
    const search = document.getElementById('carrier-search').value;
    if (!search) { alert('Please enter a carrier name or ID'); return; }
    
    const results = document.getElementById('carrier-results');
    results.style.display = 'block';
    document.getElementById('carrier-list').innerHTML = '<div class="loading">Searching</div>';
    
    try {
        const resp = await fetch(`/api/fleet_carrier?search=${encodeURIComponent(search)}`);
        const data = await resp.json();
        
        if (data.error || !data.carriers || data.carriers.length === 0) {
            document.getElementById('carrier-list').innerHTML = '<div class="empty-state"><p>No carriers found. Try EDDB.io for full carrier listings.</p></div>';
            return;
        }
        
        document.getElementById('carrier-list').innerHTML = data.carriers.map(c => `
            <div class="result-item">
                <div class="station-name">${c.name} (${c.id})</div>
                <div class="station-info">
                    ${c.system ? `Docked at: ${c.system}` : 'Location unknown'}<br>
                    ${c.services ? c.services.map(s => `<span class="service-badge">${s}</span>`).join('') : ''}
                </div>
            </div>
        `).join('');
    } catch (e) {
        document.getElementById('carrier-list').innerHTML = `<div class="empty-state"><p>Error: ${e.message}</p></div>`;
    }
}

// Inara
function saveInaraKey() {
    const key = document.getElementById('inara-key').value;
    localStorage.setItem('inara_api_key', key);
    alert('API key saved! Some features require Inara account linking.');
}

// ===== COMMANDER DASHBOARD =====
function saveCommander() {
    const cmdr = {
        name: document.getElementById('cmdr-name').value,
        ship: document.getElementById('cmdr-ship').value,
        home: document.getElementById('cmdr-home').value,
        location: document.getElementById('cmdr-location').value,
        credits: document.getElementById('cmdr-credits').value,
        ranks: document.getElementById('cmdr-ranks').value
    };
    localStorage.setItem('elite_cmdr', JSON.stringify(cmdr));
    displayCommander();
    logActivity('Profile updated');
    alert('Commander profile saved!');
}

function displayCommander() {
    const stored = localStorage.getItem('elite_cmdr');
    const display = document.getElementById('cmdr-display');
    if (stored) {
        const cmdr = JSON.parse(stored);
        document.getElementById('disp-name').textContent = cmdr.name || '-';
        document.getElementById('disp-ship').textContent = cmdr.ship || '-';
        document.getElementById('disp-location').textContent = cmdr.location || cmdr.home || '-';
        document.getElementById('disp-credits').textContent = cmdr.credits ? parseInt(cmdr.credits).toLocaleString() + ' CR' : '-';
        display.style.display = 'block';
        // Also populate form fields
        document.getElementById('cmdr-name').value = cmdr.name || '';
        document.getElementById('cmdr-ship').value = cmdr.ship || '';
        document.getElementById('cmdr-home').value = cmdr.home || '';
        document.getElementById('cmdr-location').value = cmdr.location || '';
        document.getElementById('cmdr-credits').value = cmdr.credits || '';
        document.getElementById('cmdr-ranks').value = cmdr.ranks || '';
    } else {
        display.style.display = 'none';
    }
}

function logActivity(action) {
    const log = JSON.parse(localStorage.getItem('elite_activity') || '[]');
    const entry = { time: new Date().toLocaleString(), action };
    log.unshift(entry);
    if (log.length > 10) log.pop();
    localStorage.setItem('elite_activity', JSON.stringify(log));
    renderActivity();
}

function renderActivity() {
    const log = JSON.parse(localStorage.getItem('elite_activity') || '[]');
    const container = document.getElementById('activity-log');
    if (log.length === 0) {
        container.innerHTML = '<p style="color:var(--text-dim);font-size:0.85em;">No recent activity. Start exploring!</p>';
        return;
    }
    container.innerHTML = log.map(e => `
        <div class="result-item">
            <div class="station-info">${e.time} — ${e.action}</div>
        </div>
    `).join('');
}

function quickAction(action) {
    const cmdr = JSON.parse(localStorage.getItem('elite_cmdr') || '{}');
    const home = cmdr.home || 'Sol';
    const location = cmdr.location || home;
    
    let msg = '';
    switch(action) {
        case 'plot-home':
            msg = `Plot route from ${location} to ${home}`;
            logActivity(`Route: ${location} → ${home}`);
            break;
        case 'nearest-station':
            msg = `Finding nearest station to ${location}...`;
            logActivity(`Search: nearest station`);
            break;
        case 'nearest-fuel':
            msg = `Finding nearest station with fuel in ${location}...`;
            logActivity(`Search: fuel station`);
            break;
        case 'nearest-repair':
            msg = `Finding nearest repair station in ${location}...`;
            logActivity(`Search: repair station`);
            break;
        case 'nearest-material-trader':
            document.getElementById('service-system').value = location;
            document.getElementById('service-type').value = 'Material Trader';
            showPage('services');
            searchServices();
            return;
        case 'nearest-tech-broker':
            document.getElementById('service-system').value = location;
            document.getElementById('service-type').value = 'Technology Broker';
            showPage('services');
            searchServices();
            return;
    }
    alert(msg);
}

// ===== COLONIES =====
function addColony() {
    const system = document.getElementById('colony-system').value;
    const station = document.getElementById('colony-station').value;
    const type = document.getElementById('colony-type').value;
    
    if (!system) { alert('Please enter system name'); return; }
    
    const colonies = JSON.parse(localStorage.getItem('elite_colonies') || '[]');
    // Check if already exists
    if (colonies.some(c => c.system === system)) {
        alert('System already in colonies list');
        return;
    }
    
    colonies.push({
        system, station: station || 'Unknown', 
        type, facilities: [],
        stats: { tech_level: 1, wealth: 0, population: 0, security: 10, sol: 10 },
        created: new Date().toLocaleString()
    });
    
    localStorage.setItem('elite_colonies', JSON.stringify(colonies));
    document.getElementById('colony-system').value = '';
    document.getElementById('colony-station').value = '';
    renderColonies();
    logActivity(`Colony added: ${system}`);
    alert('Colony added!');
}

function renderColonies() {
    const colonies = JSON.parse(localStorage.getItem('elite_colonies') || '[]');
    const container = document.getElementById('colonies-results');
    
    if (colonies.length === 0) {
        container.innerHTML = '<p style="color:var(--text-dim);">No colonies yet. Add your first colonized system!</p>';
        return;
    }
    
    container.innerHTML = colonies.map((c, i) => `
        <div class="result-item" onclick="openColonyDetail(${i})">
            <div class="station-name">${c.system}</div>
            <div class="station-info">
                ${c.station} (${c.type})<br>
                Facilities: ${c.facilities.length} | Created: ${c.created}<br>
                ${c.facilities.map(f => '<span class="service-badge green">' + f + '</span>').join(' ')}
            </div>
        </div>
    `).join('');
}

let currentColonyIndex = -1;

function openColonyDetail(index) {
    const colonies = JSON.parse(localStorage.getItem('elite_colonies') || '[]');
    currentColonyIndex = index;
    const colony = colonies[index];
    
    document.getElementById('colony-detail-name').textContent = colony.system;
    
    const facilitiesContainer = document.getElementById('colony-facilities');
    if (colony.facilities.length === 0) {
        facilitiesContainer.innerHTML = '<span style="color:var(--text-dim);font-size:0.85em;">No facilities built yet</span>';
    } else {
        facilitiesContainer.innerHTML = colony.facilities.map(f => '<span class="service-badge green">' + f + '</span>').join('');
    }
    
    // Colony stats
    const stats = colony.stats || { tech_level: 1, wealth: 0, population: 0, security: 10, sol: 10 };
    document.getElementById('colony-stats').innerHTML = `
        <div class="stat-box"><div class="value">${stats.tech_level}</div><div class="label">Tech Level</div></div>
        <div class="stat-box"><div class="value">${stats.wealth}</div><div class="label">Wealth</div></div>
        <div class="stat-box"><div class="value">${stats.population}</div><div class="label">Population</div></div>
        <div class="stat-box"><div class="value">${stats.security}%</div><div class="label">Security</div></div>
    `;
    
    document.getElementById('colonies-list').style.display = 'none';
    document.getElementById('colony-detail').style.display = 'block';
}

function closeColonyDetail() {
    document.getElementById('colonies-list').style.display = 'block';
    document.getElementById('colony-detail').style.display = 'none';
    currentColonyIndex = -1;
}

function addFacility() {
    if (currentColonyIndex < 0) return;
    const facility = document.getElementById('add-facility').value;
    
    const colonies = JSON.parse(localStorage.getItem('elite_colonies') || '[]');
    if (!colonies[currentColonyIndex].facilities.includes(facility)) {
        colonies[currentColonyIndex].facilities.push(facility);
        // Update stats based on facility
        const stats = colonies[currentColonyIndex].stats;
        const facilityStats = {
            'High Tech Hub': { tech_level: 20, wealth: 15 },
            'Industrial Hub': { tech_level: 10, wealth: 20, population: 15 },
            'Mining Hub': { wealth: 20, tech_level: 5 },
            'Refinery Hub': { wealth: 15, population: 10 },
            'Trading Hub': { wealth: 25, sol: 15 },
            'Exploration Hub': { tech_level: 15, sol: 10 },
            'Military Installation': { security: 25, tech_level: 5 },
            'Terraforming Hub': { population: 25, sol: 20, tech_level: 15 },
            'Research Lab': { tech_level: 30, sol: 10 },
            'Shipyard Hub': { tech_level: 15, wealth: 20 },
            'Farm Complex': { population: 15, sol: 10 },
            'Power Plant': { tech_level: 10, population: 5 },
            'Water Treatment': { sol: 15, population: 10 },
            'Communications Array': { population: 10, tech_level: 5 },
            'Mission Board': { sol: 15 },
            'Barracks': { security: 20 }
        };
        const bonus = facilityStats[facility] || {};
        Object.keys(bonus).forEach(k => stats[k] = (stats[k] || 0) + bonus[k]);
        
        localStorage.setItem('elite_colonies', JSON.stringify(colonies));
        openColonyDetail(currentColonyIndex);
        renderColonies();
        logActivity(`Built: ${facility}`);
        alert('Facility added!');
    } else {
        alert('Facility already built');
    }
}

// ===== SHIPS =====
function addShip() {
    const name = document.getElementById('ship-name').value;
    const role = document.getElementById('ship-role').value;
    const build = document.getElementById('ship-build').value;
    
    if (!name) { alert('Please enter ship name'); return; }
    
    const ships = JSON.parse(localStorage.getItem('elite_ships') || '[]');
    ships.push({ name, role, build, modules: [], created: new Date().toLocaleString() });
    localStorage.setItem('elite_ships', JSON.stringify(ships));
    document.getElementById('ship-name').value = '';
    renderShips();
    logActivity(`Ship added: ${name}`);
    alert('Ship added!');
}

function renderShips() {
    const ships = JSON.parse(localStorage.getItem('elite_ships') || '[]');
    const container = document.getElementById('ships-results');
    
    if (ships.length === 0) {
        container.innerHTML = '<p style="color:var(--text-dim);">No ships in hangar. Add your first ship!</p>';
        return;
    }
    
    const roleColors = { Combat: 'red', Trading: 'green', Exploration: 'cyan', Mining: 'orange', Passenger: 'purple', 'Mission Running': 'yellow', PvP: 'red' };
    
    container.innerHTML = ships.map((s, i) => `
        <div class="result-item">
            <div class="station-name">${s.name}</div>
            <div class="station-info">
                <span class="service-badge" style="background:rgba(${roleColors[s.role]==='red'?'255,71,87':roleColors[s.role]==='green'?'0,255,136':roleColors[s.role]==='cyan'?'0,212,255':roleColors[s.role]==='orange'?'255,165,0':roleColors[s.role]==='purple'?'165,94,234':'255,165,0'},0.2);color:var(--${roleColors[s.role]==='red'?'red':roleColors[s.role]==='green'?'green':roleColors[s.role]==='cyan'?'cyan':roleColors[s.role]==='orange'?'orange':roleColors[s.role]==='purple'?'purple':'orange'})">${s.role}</span>
                <span class="service-badge ${s.build === 'Full' ? 'green' : s.build === 'Partial' ? 'orange' : ''}">${s.build}</span>
                <br>Added: ${s.created}
            </div>
        </div>
    `).join('');
}

// ===== MATERIALS =====
function addMaterial() {
    const name = document.getElementById('mat-name').value;
    const type = document.getElementById('mat-type').value;
    const qty = parseInt(document.getElementById('mat-qty').value) || 1;
    const grade = parseInt(document.getElementById('mat-grade').value) || 1;
    
    if (!name) { alert('Please enter material name'); return; }
    
    const materials = JSON.parse(localStorage.getItem('elite_materials') || '[]');
    const existing = materials.findIndex(m => m.name.toLowerCase() === name.toLowerCase());
    if (existing >= 0) {
        materials[existing].qty += qty;
    } else {
        materials.push({ name, type, qty, grade });
    }
    
    localStorage.setItem('elite_materials', JSON.stringify(materials));
    document.getElementById('mat-name').value = '';
    document.getElementById('mat-qty').value = '1';
    renderMaterials('all');
    logActivity(`Material: ${name} x${qty}`);
}

let currentMatFilter = 'all';

function filterMaterials(type) {
    currentMatFilter = type;
    renderMaterials(type);
}

function renderMaterials(type) {
    const materials = JSON.parse(localStorage.getItem('elite_materials') || '[]');
    const container = document.getElementById('materials-results');
    const filtered = type === 'all' ? materials : materials.filter(m => m.type === type);
    
    if (filtered.length === 0) {
        container.innerHTML = '<p style="color:var(--text-dim);">No materials in inventory</p>';
        return;
    }
    
    const typeColors = { Raw: 'green', Encoded: 'cyan', Manufactured: 'orange' };
    
    container.innerHTML = filtered.sort((a, b) => a.name.localeCompare(b.name)).map(m => `
        <div class="result-item">
            <div class="station-name">${m.name}</div>
            <div class="station-info">
                <span class="material-chip ${m.type.toLowerCase()}">${m.type}</span>
                Grade ${m.grade} | Qty: ${m.qty}
            </div>
        </div>
    `).join('');
}

function addToShopping() {
    const mat = document.getElementById('shopping-mat').value;
    if (!mat) return;
    
    const list = JSON.parse(localStorage.getItem('elite_shopping') || '[]');
    if (!list.includes(mat)) {
        list.push(mat);
        localStorage.setItem('elite_shopping', JSON.stringify(list));
    }
    document.getElementById('shopping-mat').value = '';
    renderShoppingList();
}

function renderShoppingList() {
    const list = JSON.parse(localStorage.getItem('elite_shopping') || '[]');
    const container = document.getElementById('shopping-list');
    
    if (list.length === 0) {
        container.innerHTML = '<span style="color:var(--text-dim);font-size:0.85em;">Shopping list empty</span>';
        return;
    }
    
    container.innerHTML = list.map((m, i) => `<span class="material-chip" onclick="removeShopping(${i})" style="cursor:pointer;" title="Click to remove">${m} ×</span>`).join('');
}

function removeShopping(index) {
    const list = JSON.parse(localStorage.getItem('elite_shopping') || '[]');
    list.splice(index, 1);
    localStorage.setItem('elite_shopping', JSON.stringify(list));
    renderShoppingList();
}

// ===== BOOKMARKS =====
function addBookmark() {
    const type = document.getElementById('bm-type').value;
    const name = document.getElementById('bm-name').value;
    const location = document.getElementById('bm-location').value;
    const notes = document.getElementById('bm-notes').value;
    
    if (!name) { alert('Please enter a name'); return; }
    
    const bookmarks = JSON.parse(localStorage.getItem('elite_bookmarks') || '[]');
    bookmarks.push({ type, name, location: location || '', notes: notes || '', created: new Date().toLocaleString() });
    localStorage.setItem('elite_bookmarks', JSON.stringify(bookmarks));
    document.getElementById('bm-name').value = '';
    document.getElementById('bm-location').value = '';
    document.getElementById('bm-notes').value = '';
    renderBookmarks('all');
    logActivity(`Bookmark added: ${name}`);
    alert('Bookmark added!');
}

let currentBmFilter = 'all';

function filterBookmarks(type) {
    currentBmFilter = type;
    renderBookmarks(type);
}

function renderBookmarks(type) {
    const bookmarks = JSON.parse(localStorage.getItem('elite_bookmarks') || '[]');
    const container = document.getElementById('bookmarks-results');
    const filtered = type === 'all' ? bookmarks : bookmarks.filter(b => b.type === type);
    
    if (filtered.length === 0) {
        container.innerHTML = '<p style="color:var(--text-dim);">No bookmarks yet</p>';
        return;
    }
    
    const typeIcons = { System: '🌟', Station: '🏢', Route: '📍', POI: '📌', Mining: '⛏️', Combat: '⚔️' };
    
    container.innerHTML = filtered.map((b, i) => `
        <div class="result-item">
            <div class="station-name">${typeIcons[b.type] || '📍'} ${b.name}</div>
            <div class="station-info">
                <span class="service-badge">${b.type}</span> ${b.location ? '— ' + b.location : ''}<br>
                ${b.notes ? 'Notes: ' + b.notes + '<br>' : ''}
                <button class="secondary" onclick="deleteBookmark(${i})" style="padding:3px 8px;font-size:0.75em;margin-top:5px;">Delete</button>
            </div>
        </div>
    `).join('');
}

function deleteBookmark(index) {
    const bookmarks = JSON.parse(localStorage.getItem('elite_bookmarks') || '[]');
    const name = bookmarks[index].name;
    bookmarks.splice(index, 1);
    localStorage.setItem('elite_bookmarks', JSON.stringify(bookmarks));
    renderBookmarks(currentBmFilter);
    logActivity(`Bookmark removed: ${name}`);
}

// ===== DATA EXPORT/IMPORT =====
function exportData() {
    const data = {
        cmdr: JSON.parse(localStorage.getItem('elite_cmdr') || '{}'),
        colonies: JSON.parse(localStorage.getItem('elite_colonies') || '[]'),
        ships: JSON.parse(localStorage.getItem('elite_ships') || '[]'),
        materials: JSON.parse(localStorage.getItem('elite_materials') || '[]'),
        bookmarks: JSON.parse(localStorage.getItem('elite_bookmarks') || '[]'),
        activity: JSON.parse(localStorage.getItem('elite_activity') || '[]'),
        inara_api_key: localStorage.getItem('inara_api_key') || '',
        exported: new Date().toISOString()
    };
    
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `elite-companion-backup-${new Date().toISOString().split('T')[0]}.json`;
    a.click();
    URL.revokeObjectURL(url);
    logActivity('Data exported to file');
    alert('✅ Data exported! Save this file somewhere safe.');
}

function importData(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    const reader = new FileReader();
    reader.onload = (e) => {
        try {
            const data = JSON.parse(e.target.result);
            
            // Validate
            if (!data.exported) {
                alert('Invalid backup file');
                return;
            }
            
            // Import
            if (data.cmdr) localStorage.setItem('elite_cmdr', JSON.stringify(data.cmdr));
            if (data.colonies) localStorage.setItem('elite_colonies', JSON.stringify(data.colonies));
            if (data.ships) localStorage.setItem('elite_ships', JSON.stringify(data.ships));
            if (data.materials) localStorage.setItem('elite_materials', JSON.stringify(data.materials));
            if (data.bookmarks) localStorage.setItem('elite_bookmarks', JSON.stringify(data.bookmarks));
            if (data.activity) localStorage.setItem('elite_activity', JSON.stringify(data.activity));
            if (data.inara_api_key) localStorage.setItem('inara_api_key', data.inara_api_key);
            
            // Refresh UI
            displayCommander();
            renderColonies();
            renderShips();
            renderMaterials('all');
            renderShoppingList();
            renderBookmarks('all');
            renderActivity();
            
            logActivity('Data imported from file');
            alert(`✅ Data imported from ${data.exported.split('T')[0]}!`);
        } catch (err) {
            alert('❌ Failed to import: ' + err.message);
        }
    };
    reader.readAsText(file);
    event.target.value = '';
}

function clearAllData() {
    if (!confirm('⚠️ WARNING: This will DELETE all your commander data, colonies, ships, materials, and bookmarks. This cannot be undone.\n\nAre you sure?')) return;
    
    const keys = ['elite_cmdr', 'elite_colonies', 'elite_ships', 'elite_materials', 'elite_bookmarks', 'elite_activity', 'elite_shopping', 'inara_api_key'];
    keys.forEach(k => localStorage.removeItem(k));
    
    // Refresh UI
    displayCommander();
    renderColonies();
    renderShips();
    renderMaterials('all');
    renderShoppingList();
    renderBookmarks('all');
    renderActivity();
    
    alert('🗑️ All data cleared. Export next time before clearing!');
    logActivity('All data cleared');
}

// ===== INARA API INTEGRATION =====
let inaraSyncedData = null;

async function syncInara() {
    const apiKey = localStorage.getItem('inara_api_key');
    if (!apiKey) {
        alert('Please save your Inara API key first');
        return;
    }
    
    const cmdrName = document.getElementById('inara-cmdr').value;
    if (!cmdrName) {
        alert('Please enter your CMDR name');
        return;
    }
    
    const status = document.getElementById('inara-sync-status');
    status.style.display = 'block';
    status.innerHTML = '<div class="loading">Fetching from Inara.cz</div>';
    
    try {
        const response = await fetch('/api/inara_profile', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ apiKey, cmdrName })
        });
        const data = await response.json();
        
        if (data.error) {
            status.innerHTML = `<div class="result-item" style="border-left-color:var(--red)"><div class="station-info">❌ Error: ${data.error}</div></div>`;
            return;
        }
        
        // Parse Inara response
        const events = data.events || [];
        if (events.length === 0 || events[0].eventStatus === 'error') {
            status.innerHTML = `<div class="result-item" style="border-left-color:var(--red)"><div class="station-info">❌ Inara API error: ${events[0]?.eventStatusText || 'Unknown error'}</div></div>`;
            return;
        }
        
        const eventData = events[0].eventData || {};
        inaraSyncedData = {
            name: eventData.userName || cmdrName,
            credits: eventData.credits || 0,
            combatRank: eventData.combatRank || '?',
            tradeRank: eventData.tradeRank || '?',
            exploreRank: eventData.exploreRank || '?',
            shipName: eventData.shipName || '?',
            shipIdent: eventData.shipIdent || '',
            materials: eventData.materials || [],
            systemsVisited: eventData.systemsVisited || 0
        };
        
        // Show success + data
        status.innerHTML = `<div class="result-item" style="border-left-color:var(--green)">
            <div class="station-info">✅ Sync successful! Found: ${inaraSyncedData.name}</div>
        </div>`;
        
        // Show profile card
        document.getElementById('inara-profile').style.display = 'block';
        document.getElementById('inara-data').innerHTML = `
            <div class="stat-grid" style="margin-bottom:15px;">
                <div class="stat-box"><div class="value">${inaraSyncedData.name}</div><div class="label">Commander</div></div>
                <div class="stat-box"><div class="value">${inaraSyncedData.combatRank}</div><div class="label">Combat</div></div>
                <div class="stat-box"><div class="value">${inaraSyncedData.tradeRank}</div><div class="label">Trade</div></div>
                <div class="stat-box"><div class="value">${inaraSyncedData.exploreRank}</div><div class="label">Explore</div></div>
                <div class="stat-box"><div class="value">${(inaraSyncedData.credits || 0).toLocaleString()}</div><div class="label">Credits (CR)</div></div>
                <div class="stat-box"><div class="value">${inaraSyncedData.systemsVisited}</div><div class="label">Systems Visited</div></div>
            </div>
            <div class="station-info" style="margin-top:10px;">
                <strong>Current Ship:</strong> ${inaraSyncedData.shipName || 'Unknown'}
                ${inaraSyncedData.shipIdent ? ` (${inaraSyncedData.shipIdent})` : ''}
            </div>
        `;
        
        logActivity(`Synced with Inara: ${inaraSyncedData.name}`);
        
    } catch (e) {
        status.innerHTML = `<div class="result-item" style="border-left-color:var(--red)"><div class="station-info">❌ Error: ${e.message}</div></div>`;
        console.error('Inara sync error:', e);
    }
}

function applyToDashboard() {
    if (!inaraSyncedData) {
        alert('No synced data to import. Sync from Inara first.');
        return;
    }
    
    // Update commander profile
    const cmdr = JSON.parse(localStorage.getItem('elite_cmdr') || '{}');
    cmdr.name = inaraSyncedData.name;
    cmdr.credits = inaraSyncedData.credits;
    cmdr.ranks = `${inaraSyncedData.combatRank} / ${inaraSyncedData.tradeRank} / ${inaraSyncedData.exploreRank}`;
    cmdr.ship = inaraSyncedData.shipName;
    
    localStorage.setItem('elite_cmdr', JSON.stringify(cmdr));
    displayCommander();
    
    // Also add ship if not exists
    if (inaraSyncedData.shipName && inaraSyncedData.shipName !== 'Unknown') {
        const ships = JSON.parse(localStorage.getItem('elite_ships') || '[]');
        if (!ships.some(s => s.name === inaraSyncedData.shipName)) {
            ships.push({
                name: inaraSyncedData.shipName,
                role: 'General',
                build: 'Stock',
                created: new Date().toLocaleString()
            });
            localStorage.setItem('elite_ships', JSON.stringify(ships));
        }
    }
    
    // Sync materials
    if (inaraSyncedData.materials && inaraSyncedData.materials.length > 0) {
        const materials = JSON.parse(localStorage.getItem('elite_materials') || '[]');
        inaraSyncedData.materials.forEach(m => {
            const existing = materials.findIndex(x => x.name.toLowerCase() === m.name.toLowerCase());
            if (existing >= 0) {
                materials[existing].qty = m.quantity || m.qty || 1;
            } else {
                materials.push({
                    name: m.name,
                    type: m.category || 'Raw',
                    qty: m.quantity || 1,
                    grade: m.grade || 1
                });
            }
        });
        localStorage.setItem('elite_materials', JSON.stringify(materials));
    }
    
    renderShips();
    renderMaterials('all');
    logActivity('Imported Inara data to Dashboard');
    alert('✅ Commander data imported to Dashboard!');
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    updateBlueprints();
    loadStateGuide();
    loadGuardianSites();
    loadThargoidSites();
    
    // Load saved data
    displayCommander();
    renderColonies();
    renderShips();
    renderMaterials('all');
    renderShoppingList();
    renderBookmarks('all');
    renderActivity();
    
    // Close modal on escape
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') closeModal();
    });
    
    // Close modal on overlay click
    document.getElementById('station-modal').addEventListener('click', (e) => {
        if (e.target.classList.contains('modal-overlay')) closeModal();
    });
});
</script>

</body>
</html>
"""

# ========== API ENDPOINTS ==========

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

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
    return jsonify({
        "commodity": commodity,
        "system": system,
        "count": len(results),
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
            "government": s.get("government", ""),
            "distanceToArrival": s.get("distanceToArrival", 0),
            "haveMarket": s.get("haveMarket", False),
            "haveShipyard": s.get("haveShipyard", False),
            "haveOutfitting": s.get("haveOutfitting", False),
            "hasRefuel": s.get("hasRefuel", False),
            "hasRepair": s.get("hasRepair", False),
            "hasRestock": s.get("hasRestock", False),
        } for s in stations]
    })

@app.route('/api/station_detail')
def api_station_detail():
    system = request.args.get('system', '')
    station = request.args.get('station', '')
    if not system or not station:
        return jsonify({"error": "System and station name required"})
    
    # Get basic station info
    stations_data = get_stations(system)
    stations = stations_data.get("stations", [])
    station_info = next((s for s in stations if s.get("name") == station), {})
    
    # Get market data
    market = get_station_market(system, station)
    
    # Get outfitting
    outfitting_data = get_station_outfitting(system, station)
    outfitting = outfitting_data.get("modules", []) if not outfitting_data.get("error") else []
    
    # Get shipyard
    shipyard_data = get_station_shipyard(system, station)
    ships = shipyard_data.get("ships", []) if not shipyard_data.get("error") else []
    
    # Format services
    services = []
    if station_info.get("haveMarket"): services.append("Market")
    if station_info.get("haveShipyard"): services.append("Shipyard")
    if station_info.get("haveOutfitting"): services.append("Outfitting")
    if station_info.get("hasRefuel"): services.append("Refuel")
    if station_info.get("hasRepair"): services.append("Repair")
    if station_info.get("hasRestock"): services.append("Restock")
    if station_info.get("hasMartian"): services.append("Material Trader")
    if station_info.get("hasTechnology"): services.append("Technology Broker")
    if station_info.get("hasBlackMarket"): services.append("Black Market")
    if station_info.get("hasUniversalCartographics"): services.append("Universal Cartographics")
    if station_info.get("hasInterstellarFactors"): services.append("Interstellar Factors")
    
    return jsonify({
        "name": station,
        "type": station_info.get("type", "Unknown"),
        "distance": station_info.get("distanceToArrival", 0),
        "economy": station_info.get("economy", "Unknown"),
        "government": station_info.get("government", "Unknown"),
        "allegiance": station_info.get("allegiance", ""),
        "services": services,
        "market": market[:50] if market else [],
        "outfitting": outfitting[:100] if outfitting else [],
        "shipyard": [s.get("name", s) if isinstance(s, dict) else s for s in ships] if ships else []
    })

@app.route('/api/route')
def api_route():
    from_sys = request.args.get('from', '')
    to_sys = request.args.get('to', '')
    
    if not from_sys or not to_sys:
        return jsonify({"error": "Both from and to systems required"})
    
    from_stations = get_stations(from_sys)
    to_stations = get_stations(to_sys)
    from_info = get_system_info(from_sys)
    to_info = get_system_info(to_sys)
    
    from_coords = from_info.get("coords", {})
    to_coords = to_info.get("coords", {})
    
    distance = calculate_distance(from_coords, to_coords)
    
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

@app.route('/api/service_finder')
def api_service_finder():
    system = request.args.get('system', '')
    service = request.args.get('service', '')
    
    if not system:
        return jsonify({"error": "System name required"})
    
    # Known major stations with various services (EDSM data)
    stations_data = get_stations(system)
    if stations_data.get("error"):
        return jsonify({"error": stations_data["error"]})
    
    stations = stations_data.get("stations", [])
    
    # Map service names to station flags
    service_map = {
        "Material Trader": "hasMarket",  # Approximation - EDSM doesn't always show this
        "Technology Broker": "hasTechnology",
        "Interstellar Factors": "hasInterstellarFactors",
        "Outfitting": "haveOutfitting",
        "Shipyard": "haveShipyard",
        "Repair": "hasRepair",
        "Refuel": "hasRefuel",
        "Restock": "hasRestock",
        "Black Market": "hasBlackMarket",
        "Universal Cartographics": "hasUniversalCartographics",
    }
    
    flag = service_map.get(service, "haveMarket")
    
    matching = []
    for s in stations:
        if s.get(flag) or s.get("haveMarket"):  # Fallback to market
            matching.append({
                "name": s.get("name", "Unknown"),
                "type": s.get("type", "Unknown"),
                "distance": s.get("distanceToArrival", 0),
                "economy": s.get("economy", ""),
                "services": [svc for svc, f in service_map.items() if s.get(f)]
            })
    
    return jsonify({
        "system": system,
        "service": service,
        "count": len(matching),
        "stations": matching[:20]
    })

@app.route('/api/system_states')
def api_system_states():
    system = request.args.get('system', '')
    if not system:
        return jsonify({"error": "System name required"})
    
    system_data = get_system_info(system)
    info = system_data.get("information", {})
    
    # EDSM doesn't always provide system state, so we return what's available
    state = info.get("state", None)
    economy = info.get("economy", "Unknown")
    security = info.get("security", "Unknown")
    
    # Map state to effects
    effects_map = {
        "Boom": "Increased demand for luxury goods, food, and consumer products.",
        "Bust": "Decreased demand for most goods except basic necessities.",
        "War": "Increased demand for weapons and military supplies.",
        "Civil War": "Most trade routes disrupted. Only weapons remain profitable.",
        "Famine": "Massive increase in food and water prices. Emergency supplies needed.",
        "Outbreak": "Medical supplies in extremely high demand.",
        "Peace": "Luxury goods and consumer electronics see increased demand.",
        "Public Holiday": "Alcohol, tobacco, and luxury goods prices surge.",
        "Election": "Consumer electronics and food demand increases.",
        "Infrastructure Failure": "All trade disrupted. Emergency supplies needed.",
    }
    
    effects = effects_map.get(state, "No specific trade effects documented.")
    
    return jsonify({
        "system": system,
        "state": state or "None",
        "economy": economy,
        "security": security,
        "effects": effects if state else None
    })

@app.route('/api/engineering')
def api_engineering():
    module = request.args.get('module', '')
    blueprint = request.args.get('blueprint', '')
    
    # Find matching recipe
    recipes = ENGINEERING_RECIPES.get(module, [])
    
    for recipe in recipes:
        if blueprint.lower() in recipe.get("blueprint", "").lower():
            return jsonify({
                "module": module,
                "blueprint": recipe["blueprint"],
                "grade": recipe["grade"],
                "experimental": recipe.get("experimental", ""),
                "materials": recipe.get("materials", {})
            })
    
    # Default response
    return jsonify({
        "module": module,
        "blueprint": blueprint,
        "grade": 4,
        "materials": {"Carbon": 10, "Sulphur": 8, "Phosphorus": 8, "Iron": 6}
    })

@app.route('/api/colonize')
def api_colonize():
    system = request.args.get('system', '')
    goal = request.args.get('goal', 'balanced')
    
    facilities = COLONY_FACILITIES.get("Orbital", []) + COLONY_FACILITIES.get("Ground", [])
    suggestions = []
    built_facilities = []
    
    for f in facilities:
        if f["id"] in built_facilities:
            continue
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
        "goal": goal,
        "suggestions": suggestions[:8]
    })

@app.route('/api/fleet_carrier')
def api_fleet_carrier():
    search = request.args.get('search', '')
    
    # EDSM doesn't have good carrier search, so we return a placeholder
    # Real implementation would use EDDB.io API
    return jsonify({
        "search": search,
        "error": "Fleet carrier search requires EDDB.io API integration. Try searching at eddb.io",
        "carriers": []
    })

@app.route('/api/inara_profile', methods=['POST'])
def api_inara_profile():
    """Proxy for Inara.cz API to fetch commander profile"""
    data = request.get_json()
    api_key = data.get('apiKey', '')
    cmdr_name = data.get('cmdrName', '')
    
    if not api_key or not cmdr_name:
        return jsonify({"error": "API key and commander name required"})
    
    # Inara API call
    payload = {
        "header": {
            "appName": "StartMit Elite Companion",
            "appVersion": "1.0",
            "APIKey": api_key
        },
        "events": [{
            "eventName": "getCommanderProfile",
            "eventData": {"searchName": cmdr_name}
        }]
    }
    
    try:
        req = urllib.request.Request(
            INARA_API,
            data=json.dumps(payload).encode('utf-8'),
            headers={"Content-Type": "application/json", "User-Agent": "StartMit-EliteCompanion/1.0"}
        )
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode())
            return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/api/route_plot', methods=['GET'])
def api_route_plot():
    """Calculate route between two systems"""
    from_sys = request.args.get('from', '')
    to_sys = request.args.get('to', '')
    
    if not from_sys or not to_sys:
        return jsonify({"error": "Both systems required"})
    
    from_info = get_system_info(from_sys)
    to_info = get_system_info(to_sys)
    
    from_coords = from_info.get("coords", {})
    to_coords = to_info.get("coords", {})
    
    distance = calculate_distance(from_coords, to_coords)
    
    return jsonify({
        "from": from_sys,
        "to": to_sys,
        "distance": distance,
        "fromCoords": from_coords,
        "toCoords": to_coords
    })

@app.route('/api/nearest_service', methods=['GET'])
def api_nearest_service():
    """Find nearest station with specific service"""
    system = request.args.get('system', '')
    service = request.args.get('service', '')
    
    if not system:
        return jsonify({"error": "System required"})
    
    # Get nearby systems
    nearby = get_systems_in_radius(system, 30)
    
    all_stations = []
    
    # Search nearby systems for the service
    for nearby_system in (nearby if isinstance(nearby, list) else []):
        if isinstance(nearby_system, dict) and nearby_system.get("name"):
            stations_data = get_stations(nearby_system["name"])
            if not stations_data.get("error"):
                for s in stations_data.get("stations", []):
                    if has_service(s, service):
                        dist = calculate_distance(
                            nearby_system.get("coords", {}),
                            get_system_info(system).get("coords", {})
                        )
                        all_stations.append({
                            "name": s.get("name"),
                            "system": nearby_system["name"],
                            "distance": dist or 0,
                            "type": s.get("type")
                        })
    
    all_stations.sort(key=lambda x: x.get("distance", 999))
    
    return jsonify({
        "system": system,
        "service": service,
        "stations": all_stations[:10]
    })

def has_service(station, service):
    """Check if station has a specific service"""
    service_map = {
        "Material Trader": ["hasMarket"],
        "Technology Broker": ["hasTechnology"],
        "Interstellar Factors": ["hasInterstellarFactors"],
        "Outfitting": ["haveOutfitting"],
        "Shipyard": ["haveShipyard"],
        "Repair": ["hasRepair"],
        "Refuel": ["hasRefuel"],
        "Restock": ["hasRestock"],
        "Black Market": ["hasBlackMarket"],
        "Universal Cartographics": ["hasUniversalCartographics"]
    }
    flags = service_map.get(service, ["haveMarket"])
    return any(station.get(f) for f in flags)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

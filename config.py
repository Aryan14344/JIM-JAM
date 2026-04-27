# Project Configuration
# List of curated subreddits for analysis

TARGET_SUBREDDITS = [
    # --- TECH & DEV CLUSTER (High Overlap) ---
    "programming", "python", "learnpython", "cscareerquestions", "webdev", 
    "reactjs", "javascript", "linux", "ubuntu", "sysadmin", "homelab", 
    "technology", "gadgets", "hardware", "buildapc", "pcmasterrace", 
    "machinelearning", "datascience", "artificial", "computerscience",
    
    # --- FINANCE & CRYPTO CLUSTER (High Activity) ---
    "personalfinance", "investing", "stocks", "options", "finance", 
    "financialindependence", "fatfire", "cryptocurrency", "bitcoin", 
    "ethereum", "btc", "ethtrader", "cryptomarkets",
    
    # --- SCIENCE & PHILOSOPHY (High Interdependence) ---
    "science", "askscience", "space", "physics", "biology", "chemistry", 
    "math", "astronomy", "history", "askhistorians", "psychology", 
    "sociology", "philosophy", "linguistics", "everythingscience",
    
    # --- LIFESTYLE & HOBBY (Niche Connectors) ---
    "fitness", "bodyweightfitness", "nutrition", "loseit", "keto", 
    "vegan", "eatcheapandhealthy", "mealprepsunday", "diy", "woodworking", 
    "3dprinting", "gardening", "houseplants", "photography", "drawing", 
    "art", "cooking", "recipes", "baking", "breadit", "seriouseats", 
    "askculinary", "travel", "camping", "hiking", "backpacking", "solotravel",
    
    # --- SPECIFIC GAMING (Better for Analysis than r/gaming) ---
    "patientgamers", "truegaming", "boardgames", "mmorpg", "rpg", "indiegaming"
]
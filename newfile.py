
from flask import Flask, request, redirect, render_template_string, send_from_directory
import requests
import os

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# Firebase Realtime Database URL
FIREBASE_URL = "https://limi-marketplace-default-rtdb.firebaseio.com/listings.json"

def get_firebase_listings():
    """ Helper to fetch clean listings array from Firebase """
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(FIREBASE_URL, headers=headers, timeout=10)
        if response.status_code != 200:
            return []
        data = response.json()
        listings = []
        if data and isinstance(data, dict):
            for k, v in data.items():
                if isinstance(v, dict):
                    v['id'] = k
                    listings.append(v)
            listings.reverse()
            return listings
        elif data and isinstance(data, list):
            clean_list = [item for item in data if isinstance(item, dict)]
            clean_list.reverse()
            return clean_list
        return []
    except Exception as e:
        print("Firebase Fetch Error:", e)
        return []
        
HTML_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>LIMI Marketplace</title>
    <link rel="manifest" href="/manifest.json">
    <meta name="theme-color" content="#0b132b">
    
    <meta name="google-site-verification" content="oetO7_cw4uwtMEnS6-Pthcs-tPpq-upX3x2JytIHZaw" />
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css">
    <style>
        :root {
            --app-dark: #0b132b;
            --app-accent: #00e599;
            --app-blue: #1c2541;
            --app-light-bg: #f4f6f9;
        }
        body { background-color: var(--app-light-bg); font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; padding-bottom: 85px; color: #1e293b; }
        
        #splashScreen {
            position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background: #0b132b; color: white; z-index: 9999;
            display: flex; flex-direction: column; justify-content: center; align-items: center;
            transition: opacity 0.5s ease, visibility 0.5s ease;
        }
        .splash-tag { font-size: 0.8rem; letter-spacing: 3px; color: var(--app-accent); text-transform: uppercase; font-weight: 800; margin-bottom: 6px; }
        .splash-title { font-size: 2.2rem; font-weight: 900; letter-spacing: -1px; }

        .brand-header { background: linear-gradient(135deg, #0b132b 0%, #1c2541 100%); color: white; border-bottom-left-radius: 20px; border-bottom-right-radius: 20px; box-shadow: 0 8px 20px rgba(11, 19, 43, 0.2); }
        .location-selector-btn { background: rgba(255, 255, 255, 0.08); backdrop-filter: blur(10px); border: 1px solid rgba(255, 255, 255, 0.15); color: #f8fafc; border-radius: 12px; font-size: 0.85rem; padding: 8px 12px; width: 100%; display: flex; justify-content: space-between; align-items: center; }
        .loc-badge-highlight { background: var(--app-accent); color: #0b132b; font-weight: 700; padding: 2px 8px; border-radius: 6px; font-size: 0.75rem; }
        
        .cat-scroll-container { display: flex; gap: 8px; overflow-x: auto; padding-bottom: 5px; scrollbar-width: none; }
        .cat-scroll-container::-webkit-scrollbar { display: none; }
        .cat-pill { background: white; border: 1px solid #cbd5e1; border-radius: 20px; padding: 6px 14px; white-space: nowrap; font-size: 0.82rem; font-weight: 600; color: #334155; text-decoration: none; }
        .cat-pill.active { background: #0b132b; color: white; border-color: #0b132b; }
        .cat-pill-more { background: var(--app-accent); color: #0b132b; border-color: var(--app-accent); font-weight: 700; }

        .ad-card { border: 1px solid #e2e8f0; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.03); background: white; }
        .ad-img { height: 140px; object-fit: cover; width: 100%; background-color: #f1f5f9; }

        .bottom-nav { position: fixed; bottom: 0; left: 0; right: 0; background: rgba(255, 255, 255, 0.96); backdrop-filter: blur(12px); height: 68px; border-top: 1px solid #e2e8f0; display: flex; justify-content: space-around; align-items: center; z-index: 1000; }
        .nav-item-custom { text-align: center; color: #64748b; text-decoration: none; font-size: 0.72rem; font-weight: 600; flex: 1; }
        .nav-item-custom i { font-size: 1.35rem; display: block; margin-bottom: 2px; color: #475569; }
        .nav-item-custom.active i, .nav-item-custom.active { color: #0b132b; font-weight: 700; }
        
        .sell-btn-wrapper { position: relative; top: -14px; text-decoration: none; text-align: center; }
        .sell-btn-circle { width: 56px; height: 56px; background: linear-gradient(135deg, #00e599 0%, #059669 100%); border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto; box-shadow: 0 6px 16px rgba(5, 150, 105, 0.35); border: 3px solid white; }
        .sell-btn-circle i { font-size: 1.7rem; color: #0b132b; }
    </style>
    </head>
<body>
    <div id="splashScreen">
        <div class="splash-tag">ULTIMATE DIRECTORY</div>
        <div class="splash-title">LIMI Marketplace</div>
        <div class="spinner-border text-success mt-4" style="width: 2.2rem; height: 2.2rem;" role="status"></div>
    </div>

    <div class="brand-header p-3 mb-3">
        <div class="d-flex justify-content-between align-items-center mb-2">
            <h3 class="fw-black m-0"><a href="/" class="text-white text-decoration-none">LIMI<span style="color: var(--app-accent);">.</span></a></h3>
            <span class="badge bg-light text-dark fw-bold px-2 py-1" style="font-size:0.7rem;">PRO MARKET</span>
        </div>
        <div class="mb-3">
            <button class="location-selector-btn" data-bs-toggle="modal" data-bs-target="#locationModal">
                <div class="d-flex align-items-center text-truncate me-2">
                    <i class="bi bi-geo-alt-fill me-2" style="color: var(--app-accent);"></i>
                    <div class="text-start text-truncate">
                        <div style="font-size: 0.62rem; color: #94a3b8; text-transform: uppercase;">Location Filter</div>
                        <div class="fw-bold text-white text-truncate" style="font-size: 0.85rem;">
                            {{ selected_loc if selected_loc else 'All India' }}
                        </div>
                    </div>
                </div>
                <span class="loc-badge-highlight">Change <i class="bi bi-chevron-right"></i></span>
            </button>
        </div>
        <form action="/" method="GET" class="row g-2">
            <input type="hidden" name="location" value="{{ selected_loc }}">
            <div class="col-12">
                <div class="input-group">
                    <input type="text" name="search" class="form-control border-0 ps-3" style="border-radius: 10px 0 0 10px; font-size: 0.88rem;" placeholder="Search Ads, Properties, Bikes, Jobs..." value="{{ search_query }}">
                    <button class="btn fw-bold px-3" style="background: var(--app-accent); color: #0b132b; border-radius: 0 10px 10px 0;" type="submit"><i class="bi bi-search"></i></button>
                    {% if selected_loc or search_query %}
                    <a href="/" class="btn btn-outline-light ms-2 text-white" style="border-radius: 10px; font-size: 0.8rem;">Clear</a>
                    {% endif %}
                </div>
            </div>
        </form>
    </div>

    <div class="container px-3">
        <div class="cat-scroll-container mb-3">
            <a href="/" class="cat-pill {{ 'active' if not current_cat else '' }}">🔥 All Ads</a>
            <a href="/category/Property %26 Land?location={{ selected_loc }}" class="cat-pill {{ 'active' if current_cat == 'Property & Land' else '' }}">🏠 Property & Land</a>
            <a href="/category/Cars?location={{ selected_loc }}" class="cat-pill {{ 'active' if current_cat == 'Cars' else '' }}">🚗 Cars</a>
            <a href="/category/Bikes?location={{ selected_loc }}" class="cat-pill {{ 'active' if current_cat == 'Bikes' else '' }}">🏍️ Bikes</a>
            <a href="/category/Mobiles?location={{ selected_loc }}" class="cat-pill {{ 'active' if current_cat == 'Mobiles' else '' }}">📱 Mobiles</a>
            <a href="/category/Jobs?location={{ selected_loc }}" class="cat-pill {{ 'active' if current_cat == 'Jobs' else '' }}">💼 Jobs</a>
            <a href="/category/Fashion?location={{ selected_loc }}" class="cat-pill {{ 'active' if current_cat == 'Fashion' else '' }}">👕 Fashion</a>
            <a href="/category/Electronics?location={{ selected_loc }}" class="cat-pill {{ 'active' if current_cat == 'Electronics' else '' }}">💻 Electronics</a>
            <a href="/category/Hostel %26 PG?location={{ selected_loc }}" class="cat-pill {{ 'active' if current_cat == 'Hostel & PG' else '' }}">🛏️ Hostels & PG</a>
            <a href="/category/Services?location={{ selected_loc }}" class="cat-pill {{ 'active' if current_cat == 'Services' else '' }}">🛠️ Services</a>
        </div>
        <div class="d-flex align-items-center justify-content-between mb-3">
            <h6 class="fw-bold text-dark m-0" style="font-size: 0.88rem;">
                {% if search_query %} Search Results for: "{{ search_query }}" {% elif current_cat %} Category: {{ current_cat }} {% else %} Top Recommendations {% endif %}
            </h6>
        </div>

        <div class="row g-3">
            {% for item in items %}
            <div class="col-6 col-md-4">
                <div class="card ad-card h-100">
                    {% if item.get('image') %}
                    <img src="{{ item.get('image') }}" class="ad-img" alt="Ad">
                    {% else %}
                    <div class="ad-img d-flex align-items-center justify-content-center text-muted fs-4"><i class="bi bi-box-seam"></i></div>
                    {% endif %}
                    <div class="p-2 d-flex flex-column justify-content-between flex-grow-1">
                        <div>
                            <div class="d-flex justify-content-between align-items-start">
                                <h5 class="fw-bold text-dark m-0" style="font-size: 1rem;">{{ item.get('price', '₹0') }}</h5>
                                <span class="badge bg-success-subtle text-success fw-bold" style="font-size: 0.65rem;">Verified</span>
                            </div>
                            <div class="text-truncate small fw-bold text-dark mt-1">{{ item.get('title', 'No Title') }}</div>
                            <div class="text-muted small text-truncate mt-1" style="font-size: 0.7rem;"><i class="bi bi-geo-alt-fill text-danger"></i> {{ item.get('location', 'India') }}</div>
                        </div>
                        <div class="d-flex gap-1 mt-2">
                            <a href="tel:{{ item.get('phone', '') }}" class="btn btn-sm flex-fill p-1 fw-bold border" style="font-size: 0.72rem;"><i class="bi bi-telephone-fill text-primary"></i> Call</a>
                            <a href="https://wa.me/91{{ item.get('phone', '') }}?text=Hi,%20I%20am%20interested%20in%20your%20ad" target="_blank" class="btn btn-sm flex-fill p-1 fw-bold border" style="font-size: 0.72rem; color: #166534;"><i class="bi bi-whatsapp text-success"></i> Chat</a>
                        </div>
                    </div>
                </div>
            </div>
            {% else %}
            <div class="col-12">
                <div class="alert text-center rounded-4 p-4 border bg-white">
                    <i class="bi bi-search fs-1 text-muted"></i>
                    <h6 class="mt-2 fw-bold">No Exact Matches Found!</h6>
                    <p class="small text-muted mb-2">Sirf wahi items show honge jo aapne search kiye hain.</p>
                    <a href="/" class="btn btn-sm fw-bold px-3 py-1" style="background: var(--app-accent); color: #0b132b;">View All Ads</a>
                </div>
            </div>
            {% endfor %}
        </div>
    </div>

    <div class="bottom-nav">
        <a href="/" class="nav-item-custom active"><i class="bi bi-house-door-fill"></i>Home</a>
        <a href="#" class="nav-item-custom"><i class="bi bi-chat-dots"></i>Chats</a>
        <a href="#" class="sell-btn-wrapper"><div class="sell-btn-circle"><i class="bi bi-plus-lg"></i></div></a>
        <a href="#" class="nav-item-custom"><i class="bi bi-journal-text"></i>My Ads</a>
        <a href="#" class="nav-item-custom"><i class="bi bi-person-circle"></i>Account</a>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        window.addEventListener('load', function() {
            setTimeout(function() {
                const splash = document.getElementById('splashScreen');
                if(splash) {
                    splash.style.opacity = '0';
                    splash.style.visibility = 'hidden';
                }
            }, 600);
        });
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    search_query = request.args.get('search', '').strip().lower()
    selected_loc = request.args.get('location', '').strip()
    
    all_items = get_firebase_listings()
    filtered = []
    
    for item in all_items:
        title = str(item.get('title', '')).lower()
        loc = str(item.get('location', '')).lower()
        
        # Location filter check
        if selected_loc and selected_loc.lower() not in loc:
            continue
            
        # Strict Search Logic
        if search_query and search_query not in title:
            continue
            
        filtered.append(item)
        
    return render_template_string(HTML_TEMPLATE, items=filtered, search_query=search_query, selected_loc=selected_loc, current_cat=None)

# --- PWA CRITICAL ROUTES (MANIFEST & ICONS) ---
@app.route('/manifest.json')
def manifest():
    return send_from_directory('.', 'manifest.json', mimetype='application/json')

@app.route('/icon-192.png')
def icon192():
    return send_from_directory('.', 'icon-192.png', mimetype='image/png')

@app.route('/icon-512.png')
def icon512():
    return send_from_directory('.', 'icon-512.png', mimetype='image/png')

@app.route('/robots.txt')
def robots():
    return send_from_directory('.', 'robots.txt')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)

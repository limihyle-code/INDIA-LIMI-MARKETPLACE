from flask import Flask, request, redirect, render_template_string
import requests

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
        
        /* UNIQUE ADVANCE LOADING SCREEN */
        #splashScreen {
            position: fixed;
            top: 0; left: 0; width: 100%; height: 100%;
            background: #0b132b;
            color: white;
            z-index: 9999;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            transition: opacity 0.5s ease, visibility 0.5s ease;
        }
        .splash-tag {
            font-size: 0.8rem;
            letter-spacing: 3px;
            color: var(--app-accent);
            text-transform: uppercase;
            font-weight: 800;
            margin-bottom: 6px;
        }
        .splash-title {
            font-size: 2.2rem;
            font-weight: 900;
            letter-spacing: -1px;
        }

        /* Clean Header */
        .brand-header { 
            background: linear-gradient(135deg, #0b132b 0%, #1c2541 100%); 
            color: white; 
            border-bottom-left-radius: 20px; 
            border-bottom-right-radius: 20px; 
            box-shadow: 0 8px 20px rgba(11, 19, 43, 0.2);
        }
        
        .location-selector-btn { 
            background: rgba(255, 255, 255, 0.08); 
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.15); 
            color: #f8fafc; 
            border-radius: 12px; 
            font-size: 0.85rem; 
            padding: 8px 12px; 
            width: 100%; 
            display: flex; 
            justify-content: space-between; 
            align-items: center; 
        }
        .loc-badge-highlight { background: var(--app-accent); color: #0b132b; font-weight: 700; padding: 2px 8px; border-radius: 6px; font-size: 0.75rem; }
        
        /* Category Pills horizontal scroll */
        .cat-scroll-container { display: flex; gap: 8px; overflow-x: auto; padding-bottom: 5px; scrollbar-width: none; }
        .cat-scroll-container::-webkit-scrollbar { display: none; }
        .cat-pill { background: white; border: 1px solid #cbd5e1; border-radius: 20px; padding: 6px 14px; white-space: nowrap; font-size: 0.82rem; font-weight: 600; color: #334155; text-decoration: none; }
        .cat-pill.active { background: #0b132b; color: white; border-color: #0b132b; }
        .cat-pill-more { background: var(--app-accent); color: #0b132b; border-color: var(--app-accent); font-weight: 700; }

        /* Product Cards */
        .ad-card { border: 1px solid #e2e8f0; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.03); background: white; }
        .ad-img { height: 140px; object-fit: cover; width: 100%; background-color: #f1f5f9; }

        /* Navigation Bar (5 Options Retained) */
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

    <!-- UNIQUE LOADING SCREEN -->
    <div id="splashScreen">
        <div class="splash-tag">ULTIMATE DIRECTORY</div>
        <div class="splash-title">LIMI Marketplace</div>
        <div class="spinner-border text-success mt-4" style="width: 2.2rem; height: 2.2rem;" role="status"></div>
    </div>

    <!-- Main Header -->
    <div class="brand-header p-3 mb-3">
        <div class="d-flex justify-content-between align-items-center mb-2">
            <h3 class="fw-black m-0"><a href="/" class="text-white text-decoration-none">LIMI<span style="color: var(--app-accent);">.</span></a></h3>
            <span class="badge bg-light text-dark fw-bold px-2 py-1" style="font-size:0.7rem;">PRO MARKET</span>
        </div>

        <!-- Location Button -->
        <div class="mb-3">
            <button class="location-selector-btn" data-bs-toggle="modal" data-bs-target="#locationModal">
                <div class="d-flex align-items-center text-truncate me-2">
                    <i class="bi bi-geo-alt-fill me-2" style="color: var(--app-accent);"></i>
                    <div class="text-start text-truncate">
                        <div style="font-size: 0.62rem; color: #94a3b8; text-transform: uppercase;">Location Filter</div>
                        <div class="fw-bold text-white text-truncate" style="font-size: 0.85rem;">
                            {% if selected_loc %}{{ selected_loc }}{% else %}All India{% endif %}
                        </div>
                    </div>
                </div>
                <span class="loc-badge-highlight">Change <i class="bi bi-chevron-right"></i></span>
            </button>
        </div>
        
        <!-- Main Search Form -->
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
        <!-- ALL CATEGORIES (OLX STYLE COMPLETE LIST) -->
        <div class="cat-scroll-container mb-3">
            <a href="/" class="cat-pill {% if not current_cat %}active{% endif %}">🔥 All Ads</a>
            <a href="/category/Property %26 Land?location={{ selected_loc }}" class="cat-pill {% if current_cat == 'Property & Land' %}active{% endif %}">🏠 Property & Land</a>
            <a href="/category/Cars?location={{ selected_loc }}" class="cat-pill {% if current_cat == 'Cars' %}active{% endif %}">🚗 Cars</a>
            <a href="/category/Bikes?location={{ selected_loc }}" class="cat-pill {% if current_cat == 'Bikes' %}active{% endif %}">🏍️ Bikes</a>
            <a href="/category/Mobiles?location={{ selected_loc }}" class="cat-pill {% if current_cat == 'Mobiles' %}active{% endif %}">📱 Mobiles</a>
            <a href="/category/Jobs?location={{ selected_loc }}" class="cat-pill {% if current_cat == 'Jobs' %}active{% endif %}">💼 Jobs</a>
            <a href="/category/Fashion?location={{ selected_loc }}" class="cat-pill {% if current_cat == 'Fashion' %}active{% endif %}">👕 Fashion</a>
            <a href="/category/Electronics?location={{ selected_loc }}" class="cat-pill {% if current_cat == 'Electronics' %}active{% endif %}">💻 Electronics</a>
            <a href="/category/Hostel %26 PG?location={{ selected_loc }}" class="cat-pill {% if current_cat == 'Hostel & PG' %}active{% endif %}">🛏️ Hostels & PG</a>
            <a href="/category/Services?location={{ selected_loc }}" class="cat-pill {% if current_cat == 'Services' %}active{% endif %}">🛠️ Services</a>
            <a href="/all-categories" class="cat-pill cat-pill-more">➕ More Options</a>
        </div>

        <!-- Filter Status Title -->
        <div class="d-flex align-items-center justify-content-between mb-3">
            <h6 class="fw-bold text-dark m-0" style="font-size: 0.88rem;">
                {% if search_query %} Search Results for: "{{ search_query }}" {% elif current_cat %} Category: {{ current_cat }} {% else %} Top Recommendations {% endif %}
            </h6>
            <span class="badge bg-white text-secondary border text-truncate" style="max-width: 150px; font-size: 0.72rem;">
                📍 {% if selected_loc %}{{ selected_loc }}{% else %}ALL INDIA{% endif %}
            </span>
        </div>

        <!-- Product Grid (Strict Search Logic) -->
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
                            <a href="https://wa.me/91{{ item.get('phone', '') }}?text=Hi,%20I%20am%20interested%20in%20your%20ad%20'{{ item.get('title', '') }}'" target="_blank" class="btn btn-sm flex-fill p-1 fw-bold border" style="font-size: 0.72rem; color: #166534;"><i class="bi bi-whatsapp text-success"></i> Chat</a>
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
    <!-- 5 Bottom Navigation Items Retained -->
    <div class="bottom-nav">
        <a href="/" class="nav-item-custom active"><i class="bi bi-house-door-fill"></i>Home</a>
        <a href="/chats" class="nav-item-custom"><i class="bi bi-chat-dots"></i>Chats</a>
        <a href="/post" class="sell-btn-wrapper"><div class="sell-btn-circle"><i class="bi bi-plus-lg"></i></div></a>
        <a href="/my-ads" class="nav-item-custom"><i class="bi bi-journal-text"></i>My Ads</a>
        <a href="/account" class="nav-item-custom"><i class="bi bi-person-circle"></i>Account</a>
    </div>

    <!-- Location Selector Modal -->
    <div class="modal fade" id="locationModal" tabindex="-1" aria-hidden="true">
        <div class="modal-dialog modal-dialog-scrollable modal-dialog-centered">
            <div class="modal-content shadow-lg border-0" style="border-radius: 20px;">
                <div class="modal-header bg-dark text-white d-flex justify-content-between align-items-center" style="padding: 16px 20px;">
                    <div>
                        <h6 class="fw-bold m-0" id="modalTitle">Select Location</h6>
                        <span class="small text-muted" style="font-size: 0.7rem;">Choose City, District or State</span>
                    </div>
                    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                
                <div class="p-3 bg-light border-bottom">
                    <button type="button" class="btn w-100 fw-bold mb-2 shadow-sm" style="background: var(--app-accent); color: #0b132b; border-radius: 10px;" onclick="getExactGPSLocation()">
                        <i class="bi bi-crosshair me-1"></i> Auto GPS Location
                    </button>
                    <div id="gpsStatus" class="small text-muted text-center" style="font-size: 0.75rem;"></div>

                    <input type="text" id="modalFilterInput" class="form-control mt-2" style="border-radius: 10px; font-size: 0.85rem;" placeholder="🔍 Quick Search Location..." onkeyup="filterLocationsInModal()">
                </div>

                <div class="modal-body p-0">
                    <div class="list-group list-group-flush border-bottom">
                        <a href="javascript:void(0)" class="list-group-item list-group-item-action fw-bold text-primary" onclick="applyLocation('')">
                            🌐 All India (Show All Ads)
                        </a>
                    </div>

                    <div id="stateListSection" class="list-group list-group-flush"></div>
                    
                    <div id="districtListSection" class="list-group list-group-flush d-none">
                        <button type="button" class="list-group-item list-group-item-action bg-dark text-white fw-bold py-2" onclick="showStateList()">
                            ← Back to States
                        </button>
                        <div id="districtsContainer"></div>
                    </div>

                    <div id="localityListSection" class="list-group list-group-flush d-none">
                        <button type="button" class="list-group-item list-group-item-action bg-dark text-white fw-bold py-2" onclick="backToDistricts()">
                            ← Back to Districts
                        </button>
                        <div id="localityContainer"></div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // Unique Splash Loader Hide
        window.addEventListener('load', function() {
            setTimeout(function() {
                const splash = document.getElementById('splashScreen');
                if(splash) {
                    splash.style.opacity = '0';
                    splash.style.visibility = 'hidden';
                }
            }, 600);
        });

        const indiaData = {
            "Bihar": {
                "Patna": ["Vijay Nagar - 800026", "Kankarbagh - 800020", "Boring Road - 800001", "Rajendra Nagar - 800016", "Patliputra - 800013", "Anisabad - 800002", "Bailey Road - 800014", "Danapur - 801503"],
                "Gaya": ["AP Colony - 823001", "Civil Lines - 823001", "Bodhgaya - 824231"],
                "Muzaffarpur": ["Brahmpura - 842003", "Kazi Mohammadpur - 842001", "Mithanpura - 842002"],
                "Bhagalpur": ["Tilka Manjhi - 812001", "Khanjarpur - 812001", "Zero Mile - 812002"],
                "Darbhanga": ["Laheriasarai - 846001", "Tower Chowk - 846004"]
            },
            "Uttar Pradesh": {
                "Lucknow": ["Hazratganj - 226001", "Gomti Nagar - 226010", "Alambagh - 226005"],
                "Varanasi": ["Lanka - 221005", "Godowlia - 221001", "Sigra - 221002"],
                "Noida": ["Sector 18 - 201301", "Sector 62 - 201309", "Greater Noida - 201310"]
            },
            "Delhi NCR": {
                "South Delhi": ["Saket - 110017", "Hauz Khas - 110016"],
                "Central Delhi": ["Connaught Place - 110001", "Karol Bagh - 110005"]
            },
            "Jharkhand": {
                "Ranchi": ["Lalpur - 834001", "Kanke Road - 834008", "Doranda - 834002"],
                "Jamshedpur": ["Bistupur - 831001", "Sakchi - 831001"]
            }
        };

        let currentSelectedState = "";

        function renderStates() {
            const container = document.getElementById('stateListSection');
            let html = '';
            for (let state in indiaData) {
                html += `<a href="javascript:void(0)" class="list-group-item list-group-item-action d-flex justify-content-between align-items-center loc-item-searchable" data-name="${state.toLowerCase()}" onclick="showDistricts('${state}')">
                            <span class="fw-semibold">${state}</span>
                            <i class="bi bi-chevron-right text-muted small"></i>
                         </a>`;
            }
            container.innerHTML = html;
        }

        function showDistricts(state) {
            currentSelectedState = state;
            document.getElementById('stateListSection').classList.add('d-none');
            document.getElementById('districtListSection').classList.remove('d-none');
            document.getElementById('localityListSection').classList.add('d-none');
            document.getElementById('modalTitle').innerText = `${state} (Districts)`;

            const container = document.getElementById('districtsContainer');
            let districts = Object.keys(indiaData[state] || {});
            
            let html = `<a href="javascript:void(0)" class="list-group-item list-group-item-action fw-bold text-success" onclick="applyLocation('${state}')">
                            📍 Entire ${state}
                        </a>`;
            
            districts.forEach(dist => {
                html += `<a href="javascript:void(0)" class="list-group-item list-group-item-action d-flex justify-content-between align-items-center loc-item-searchable" data-name="${dist.toLowerCase()}" onclick="showLocalities('${dist}')">
                            <span>${dist}</span>
                            <i class="bi bi-chevron-right text-muted small"></i>
                         </a>`;
            });
            container.innerHTML = html;
        }

        function showLocalities(district) {
            document.getElementById('districtListSection').classList.add('d-none');
            document.getElementById('localityListSection').classList.remove('d-none');
            document.getElementById('modalTitle').innerText = `${district} (Localities)`;

            const container = document.getElementById('localityContainer');
            let localities = (indiaData[currentSelectedState] && indiaData[currentSelectedState][district]) || [];
            
            let html = `<a href="javascript:void(0)" class="list-group-item list-group-item-action fw-bold text-success" onclick="applyLocation('${district}')">
                            📍 Entire ${district}
                        </a>`;
            
            localities.forEach(loc => {
                html += `<a href="javascript:void(0)" class="list-group-item list-group-item-action loc-item-searchable" data-name="${loc.toLowerCase()}" onclick="applyLocation('${loc}')">
                            🏠 ${loc}
                         </a>`;
            });
            container.innerHTML = html;
        }

        function filterLocationsInModal() {
            let input = document.getElementById('modalFilterInput').value.toLowerCase();
            let items = document.querySelectorAll('.loc-item-searchable');
            items.forEach(item => {
                let text = item.getAttribute('data-name') || '';
                item.style.display = text.includes(input) ? '' : 'none';
            });
        }

        function showStateList() {
            document.getElementById('districtListSection').classList.add('d-none');
            document.getElementById('localityListSection').classList.add('d-none');
            document.getElementById('stateListSection').classList.remove('d-none');
            document.getElementById('modalTitle').innerText = 'Select Location';
        }

        function backToDistricts() {
            showDistricts(currentSelectedState);
        }

        function applyLocation(locName) {
            window.location.href = "/?location=" + encodeURIComponent(locName);
        }

        function getExactGPSLocation() {
            const statusDiv = document.getElementById('gpsStatus');
            if (navigator.geolocation) {
                statusDiv.innerText = "Locating...";
                navigator.geolocation.getCurrentPosition(function(position) {
                    let lat = position.coords.latitude;
                    let lon = position.coords.longitude;
                    fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lon}`)
                    .then(res => res.json())
                    .then(data => {
                        let addr = data.address || {};
                        let city = addr.city || addr.town || addr.village || addr.subdistrict || '';
                        let pincode = addr.postcode ? ` - ${addr.postcode}` : '';
                        let fullLocationStr = city ? `${city}${pincode}` : 'Local Area';
                        applyLocation(fullLocationStr);
                    })
                    .catch(() => statusDiv.innerText = "Error decoding GPS address.");
                }, function() {
                    statusDiv.innerText = "Permission denied.";
                });
            }
        }

        renderStates();
    </script>
</body>
</html>"""
# --- ROUTING LOGIC WITH FULL CATEGORIES ---

@app.route('/')
def home():
    listings = get_firebase_listings()
    search_query = request.args.get('search', '').strip().lower()
    selected_loc = request.args.get('location', '').strip().lower()
    
    if selected_loc and selected_loc != 'all':
        keywords = [w.strip() for w in selected_loc.replace(',', ' ').split() if len(w.strip()) > 2]
        if keywords:
            listings = [i for i in listings if any(kw in str(i.get('location') or '').lower() for kw in keywords)]
        
    if search_query:
        listings = [
            i for i in listings 
            if search_query in str(i.get('title') or '').lower() 
            or search_query in str(i.get('category') or '').lower()
            or search_query in str(i.get('location') or '').lower()
        ]
        
    return render_template_string(HTML_TEMPLATE, items=listings, search_query=search_query, selected_loc=selected_loc, current_cat=None)

@app.route('/category/<cat_name>')
def category(cat_name):
    listings = get_firebase_listings()
    selected_loc = request.args.get('location', '').strip().lower()
    cat_items = [i for i in listings if str(i.get('category')).lower() == cat_name.lower()]
    
    if selected_loc and selected_loc != 'all':
        keywords = [w.strip() for w in selected_loc.replace(',', ' ').split() if len(w.strip()) > 2]
        if keywords:
            cat_items = [i for i in cat_items if any(kw in str(i.get('location') or '').lower() for kw in keywords)]
        
    return render_template_string(HTML_TEMPLATE, items=cat_items, search_query="", selected_loc=selected_loc, current_cat=cat_name)

@app.route('/all-categories')
def all_categories():
    categories_list = [
        ("🏠 Property & Land", "Property & Land"),
        ("🚗 Cars", "Cars"),
        ("🏍️ Bikes", "Bikes"),
        ("📱 Mobiles", "Mobiles"),
        ("💼 Jobs", "Jobs"),
        ("👕 Fashion", "Fashion"),
        ("💻 Electronics", "Electronics"),
        ("🛏️ Hostel & PG", "Hostel & PG"),
        ("📚 Libraries", "Library"),
        ("🎓 Coaching", "Coaching"),
        ("🛠️ Services", "Services")
    ]
    html = """<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1"><link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet"></head>
    <body class="p-3 bg-light" style="max-width:600px; margin:auto;"><div class="d-flex justify-content-between align-items-center mb-3"><h4 class="fw-bold m-0">All Categories</h4><a href="/" class="btn btn-sm btn-dark">← Back Home</a></div><div class="list-group shadow-sm border-0">"""
    for display_name, cat_val in categories_list:
        html += f'<a href="/category/{cat_val}" class="list-group-item list-group-item-action fw-bold py-3 fs-6">{display_name}</a>'
    html += "</div></body></html>"
    return html

@app.route('/post', methods=['GET', 'POST'])
def post_ad():
    if request.method == 'POST':
        new_item = {
            "title": request.form.get('title', ''),
            "category": request.form.get('category', ''),
            "price": "₹" + str(request.form.get('price', '0')),
            "location": request.form.get('location', ''),
            "phone": request.form.get('phone', ''),
            "image": request.form.get('image', ''),
            "verified": True
        }
        try:
            requests.post(FIREBASE_URL, json=new_item, timeout=10)
        except Exception as e:
            print("Post error:", e)
        return redirect('/')
        
    return """<!DOCTYPE html>
<html>
<head><meta name="viewport" content="width=device-width, initial-scale=1"><link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet"></head>
<body class="p-3 bg-light" style="max-width: 500px; margin: auto;">
    <div class="d-flex justify-content-between align-items-center mb-3">
        <h4 class="fw-bold">Post New Listing</h4>
        <a href="/" class="btn btn-sm btn-outline-secondary">← Home</a>
    </div>
    <form method="POST" class="card p-3 shadow-sm border-0" style="border-radius:16px;">
        <div class="mb-2"><label class="small fw-bold">Title</label><input type="text" name="title" class="form-control" placeholder="e.g. 2BHK Flat / iPhone 13 / Car" required></div>
        <div class="mb-2"><label class="small fw-bold">Category</label>
            <select name="category" class="form-select">
                <option>Property & Land</option>
                <option>Cars</option>
                <option>Bikes</option>
                <option>Mobiles</option>
                <option>Jobs</option>
                <option>Fashion</option>
                <option>Electronics</option>
                <option>Hostel & PG</option>
                <option>Library</option>
                <option>Coaching</option>
                <option>Services</option>
            </select>
        </div>
        <div class="mb-2"><label class="small fw-bold">Price (₹)</label><input type="number" name="price" class="form-control" placeholder="5000" required></div>
        <div class="mb-2"><label class="small fw-bold">Detailed Location (Area, City, State)</label>
            <input type="text" name="location" class="form-control" placeholder="e.g. Vijay Nagar, Patna, Bihar - 800026" required>
        </div>
        <div class="mb-2"><label class="small fw-bold">Mobile/WhatsApp Number</label><input type="tel" name="phone" class="form-control" placeholder="10-digit number" required></div>
        <div class="mb-3"><label class="small fw-bold">Image Link (Optional)</label><input type="url" name="image" class="form-control" placeholder="https://example.com/photo.jpg"></div>
        <button type="submit" class="btn btn-success w-100 fw-bold py-2" style="border-radius:10px;">POST AD NOW</button>
    </form>
</body>
</html>"""

@app.route('/my-ads')
def my_ads():
    listings = get_firebase_listings()
    return f"""<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1"><link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet"></head>
    <body class="p-3 bg-light"><div class="d-flex justify-content-between align-items-center mb-3"><h4>My Ads</h4><a href="/" class="btn btn-sm btn-outline-secondary">← Back</a></div>
    <div class="alert alert-info">Total Active Ads: <b>{len(listings)}</b></div></body></html>"""

@app.route('/chats')
def chats():
    return """<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1"><link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet"></head>
    <body class="p-3 bg-light"><div class="d-flex justify-content-between align-items-center mb-3"><h4>Chats & Contact</h4><a href="/" class="btn btn-sm btn-outline-secondary">← Back</a></div>
    <p class="text-muted">Direct WhatsApp Chat button har ad card par active hai.</p></body></html>"""

@app.route('/account')
def account():
    return """<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1"><link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet"></head>
    <body class="p-3 bg-light"><div class="d-flex justify-content-between align-items-center mb-3"><h4>My Account</h4><a href="/" class="btn btn-sm btn-outline-secondary">← Back</a></div>
    <div class="card p-3"><h5>User Profile</h5><p class="mb-0 text-muted">Status: Active</p></div></body></html>"""

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

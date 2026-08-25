from flask import Flask, request, redirect, render_template_string, jsonify, send_from_directory
import requests
import time
import os

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

FIREBASE_URL = "https://limi-marketplace-default-rtdb.firebaseio.com/listings.json"
FIREBASE_OFFERS_URL = "https://limi-marketplace-default-rtdb.firebaseio.com/offers.json"
FIREBASE_PROFILES_URL = "https://limi-marketplace-default-rtdb.firebaseio.com/profiles.json"

def get_firebase_listings():
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(FIREBASE_URL, headers=headers, timeout=3)
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

def get_user_profile(username):
    try:
        url = f"https://limi-marketplace-default-rtdb.firebaseio.com/profiles/{username}.json"
        res = requests.get(url, timeout=5)
        if res.status_code == 200 and res.json():
            return res.json()
    except:
        pass
    return {"likes": 0, "dislikes": 0, "reviews": []}

HTML_HEADER = """<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>LIMI Marketplace Pro</title>
    <link rel="manifest" href="/manifest.json">
    <meta name="theme-color" content="#0b132b">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css">
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>

    <script type="text/javascript">
        function googleTranslateElementInit() {
            new google.translate.TranslateElement({
                pageLanguage: 'en',
                includedLanguages: 'hi,en,bho,bn,mr,gu,pa,ta,te,kn,ml,ur',
                autoDisplay: false
           }, 'google_translate_element');     
      }
      function changeLanguage(langCode) {
           var selectEl = document.querySelector('.goog-te-combo');
           if (selectEl) {
               selectEl.value = langCode;
               selectEl.dispatchEvent(new Event('change'));
           }    
       }  
    </script>
   <script type="text/javascript" src="//translate.google.com/translate_a/element.js?cb=googleTranslateElementInit"></script>
   </head>
<body class="bg-light">
    <nav class="navbar navbar-dark bg-dark px-3 shadow-sm">
        <a class="navbar-brand fw-bold" href="/">LIMI Marketplace</a>
        <div class="dropdown">
            <button class="btn btn-sm btn-outline-light dropdown-toggle rounded-pill" type="button" data-bs-toggle="dropdown">
                🌐 Language
            </button>
            <ul class="dropdown-menu dropdown-menu-end shadow">
                <li><a class="dropdown-item" href="#" onclick="changeLanguage('hi')">🇮🇳 Hindi (हिंदी)</a></li>
                <li><a class="dropdown-item" href="#" onclick="changeLanguage('en')">🇬🇧 English</a></li>
                <li><a class="dropdown-item" href="#" onclick="changeLanguage('bho')">🇮🇳 Bhojpuri (भोजपुरी)</a></li>
                <li><a class="dropdown-item" href="#" onclick="changeLanguage('bn')">🇮🇳 Bengali (বাংলা)</a></li>
                <li><a class="dropdown-item" href="#" onclick="changeLanguage('mr')">🇮🇳 Marathi (मराठी)</a></li>
                <li><a class="dropdown-item" href="#" onclick="changeLanguage('gu')">🇮🇳 Gujarati (ગુજરાતી)</a></li>
                <li><a class="dropdown-item" href="#" onclick="changeLanguage('pa')">🇮🇳 Punjabi (પંજાબી)</a></li>
                <li><a class="dropdown-item" href="#" onclick="changeLanguage('ta')">🇮🇳 Tamil (தமிழ்)</a></li>
                <li><a class="dropdown-item" href="#" onclick="changeLanguage('te')">🇮🇳 Telugu (తెలుగు)</a></li>
                <li><a class="dropdown-item" href="#" onclick="changeLanguage('kn')">🇮🇳 Kannada (કન્નડ)</a></li>
                <li><a class="dropdown-item" href="#" onclick="changeLanguage('ml')">🇮🇳 Malayalam (മലയാളം)</a></li>
                <li><a class="dropdown-item" href="#" onclick="changeLanguage('ur')">🇮🇳 Urdu (اردو)</a></li>
            </ul>
        </div>
        <div id="google_translate_element" style="display:none;"></div>
    </nav>
    <style>
        :root { --app-dark: #0b132b; --app-accent: #00e599; --app-blue: #1c2541; --app-light-bg: #f4f6f9; }
        body { background-color: var(--app-light-bg); font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; padding-bottom: 85px; color: #1e293b; }
        .brand-header { background: linear-gradient(135deg, #0b132b 0%, #1c2541 100%); color: white; border-bottom-left-radius: 20px; border-bottom-right-radius: 20px; box-shadow: 0 8px 20px rgba(11, 19, 43, 0.2); }
        .ad-card { border: 1px solid #e2e8f0; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.03); background: white; position: relative; }
        .ad-img { height: 140px; object-fit: cover; width: 100%; background-color: #f1f5f9; }
        .urgent-badge { position: absolute; top: 8px; left: 8px; z-index: 10; background: #dc2626; color: white; font-size: 0.65rem; font-weight: 800; padding: 3px 8px; border-radius: 6px; }
        .price-drop-badge { position: absolute; top: 8px; left: 8px; z-index: 10; background: #059669; color: white; font-size: 0.65rem; font-weight: 800; padding: 3px 8px; border-radius: 6px; }
        .timer-box { background: #1e293b; color: #00e599; font-size: 0.68rem; font-weight: 700; padding: 2px 6px; border-radius: 4px; display: inline-block; margin-top: 4px; }
        .bottom-nav { position: fixed; bottom: 0; left: 0; right: 0; background: rgba(255, 255, 255, 0.96); backdrop-filter: blur(12px); height: 68px; border-top: 1px solid #e2e8f0; display: flex; justify-content: space-around; align-items: center; z-index: 1000; }
        .nav-item-custom { text-align: center; color: #64748b; text-decoration: none; font-size: 0.72rem; font-weight: 600; flex: 1; }
        .nav-item-custom i { font-size: 1.35rem; display: block; margin-bottom: 2px; color: #475569; }
        .nav-item-custom.active i, .nav-item-custom.active { color: #0b132b; font-weight: 700; }
        .sell-btn-wrapper { position: relative; top: -14px; text-decoration: none; text-align: center; }
        .sell-btn-circle { width: 56px; height: 56px; background: linear-gradient(135deg, #00e599 0%, #059669 100%); border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto; box-shadow: 0 6px 16px rgba(5, 150, 105, 0.35); border: 3px solid white; }
        .sell-btn-circle i { font-size: 1.7rem; color: #0b132b; }
        .star-gold { color: #f59e0b; }
    </style>
</head>
<body>
"""
@app.route('/')
def home():
    listings = get_firebase_listings()
    search_query = request.args.get('search', '').strip().lower()
    
    if search_query:
        listings = [i for i in listings if search_query in str(i.get('title', '')).lower()]

    return render_template_string(HTML_HEADER + """
    <div class="brand-header p-3 mb-3">
        <h3 class="fw-black m-0"><a href="/" class="text-white text-decoration-none">LIMI<span style="color: var(--app-accent);">.</span></a></h3>
        <form action="/" method="GET" class="mt-2">
            <div class="input-group">
                <input type="text" name="search" class="form-control border-0 ps-3" style="border-radius: 10px 0 0 10px;" placeholder="Search Ads..." value="{{ search_query }}">
                <button class="btn fw-bold px-3" style="background: var(--app-accent); color: #0b132b; border-radius: 0 10px 10px 0;" type="submit"><i class="bi bi-search"></i></button>
            </div>
        </form>
    </div>

    <div class="container px-3">
        <div class="row g-3">
            {% for item in items %}
            <div class="col-6 col-md-4">
                <div class="card ad-card h-100">
                    {% if item.get('is_urgent') %}
                    <div class="urgent-badge"><i class="bi bi-lightning-charge-fill"></i> URGENT</div>
                    {% endif %}
                    {% if item.get('price_dropped') %}
                    <div class="price-drop-badge" style="top: {% if item.get('is_urgent') %}32px{% else %}8px{% endif %};"><i class="bi bi-tag-fill"></i> PRICE DROP</div>
                    {% endif %}

                    {% if item.get('image') %}
                    <img src="{{ item.get('image') }}" class="ad-img">
                    {% else %}
                    <div class="ad-img d-flex align-items-center justify-content-center text-muted fs-4"><i class="bi bi-box-seam"></i></div>
                    {% endif %}
                    
                    <div class="p-2 d-flex flex-column justify-content-between flex-grow-1">
                        <div>
                            <div class="fw-bold text-dark" style="font-size: 0.95rem;">{{ item.get('price', '₹0') }}</div>
                            <div class="text-truncate small fw-bold text-dark mt-1">{{ item.get('title', 'No Title') }}</div>
                            <div class="text-muted small text-truncate mt-1"><i class="bi bi-geo-alt-fill text-danger"></i> {{ item.get('location', 'India') }}</div>
                            
                            <a href="/user_profile/{{ item.get('seller_name', 'OfficialSeller') }}" class="text-decoration-none d-block mt-1">
                                <span class="badge bg-light text-dark border"><i class="bi bi-person-badge text-primary"></i> {{ item.get('seller_name', 'Seller') }}</span>
                            </a>

                            {% if item.get('is_urgent') and item.get('created_at') %}
                            <div class="timer-box mt-1">
                                <i class="bi bi-clock-history"></i> <span class="urgent-timer" data-time="{{ item.get('created_at') }}">24h 00m 00s</span>
                            </div>
                            {% endif %}
                        </div>
                        <div class="d-flex gap-1 mt-2">
                            <button type="button" class="btn btn-sm btn-outline-success p-1 fw-bold" style="font-size: 0.68rem;" data-bs-toggle="modal" data-bs-target="#offerModal_{{ loop.index }}">
                                <i class="bi bi-tags"></i> Offer
                            </button>
                            <a href="/chat_room?user_type=buyer&name={{ item.get('title') }}" class="btn btn-sm btn-dark flex-fill p-1 fw-bold" style="font-size: 0.72rem;"><i class="bi bi-chat-fill"></i> Chat</a>
                        </div>
                    </div>
                </div>
            </div>

            <div class="modal fade" id="offerModal_{{ loop.index }}" tabindex="-1" aria-hidden="true">
              <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content" style="border-radius: 20px;">
                  <div class="modal-header border-0 pb-0">
                    <h5 class="modal-title fw-bold fs-6">🏷️ Make your Bargain Offer</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                  </div>
                  <form action="/make_offer" method="POST">
                      <div class="modal-body">
                        <input type="hidden" name="seller_name" value="{{ item.get('title') }}">
                        <p class="text-muted small mb-2">Listed Price: <b>{{ item.get('price') }}</b></p>
                        <div class="mb-3">
                            <label class="form-label fw-bold small">Your Offer Price (₹)</label>
                            <input type="number" name="offer_amount" class="form-control form-control-lg fw-bold text-success" placeholder="e.g. 8500" required>
                        </div>
                      </div>
                      <div class="modal-footer border-0 pt-0">
                        <button type="submit" class="btn btn-success w-100 fw-bold py-2 rounded-pill">SEND OFFER</button>
                      </div>
                  </form>
                </div>
              </div>
            </div>
            {% endfor %}
        </div>
    </div>

    <div class="bottom-nav">
        <a href="/" class="nav-item-custom active"><i class="bi bi-house-door-fill"></i>Home</a>
        <a href="/chats" class="nav-item-custom"><i class="bi bi-chat-dots"></i>Chats</a>
        <a href="/post" class="sell-btn-wrapper"><div class="sell-btn-circle"><i class="bi bi-plus-lg"></i></div></a>
        <a href="/my-ads" class="nav-item-custom"><i class="bi bi-journal-text"></i>My Ads</a>
        <a href="/account" class="nav-item-custom"><i class="bi bi-person-circle"></i>Account</a>
    </div>

    <script>
        function updateTimers() {
            const now = Math.floor(Date.now() / 1000);
            document.querySelectorAll('.urgent-timer').forEach(el => {
                const createdAt = parseInt(el.getAttribute('data-time'));
                const expireTime = createdAt + (24 * 3600);
                const diff = expireTime - now;
                if (diff <= 0) {
                    el.innerText = "EXPIRED";
                } else {
                    const h = Math.floor(diff / 3600);
                    const m = Math.floor((diff % 3600) / 60);
                    const s = diff % 60;
                    const formattedSeconds = s < 10 ? '0' + s : s;
                    const formattedMinutes = m < 10 ? '0' + m : m;
                    el.innerText = `${h}h ${formattedMinutes}m ${formattedSeconds}s`;
                }
            });
        }
        setInterval(updateTimers, 1000);
        updateTimers();
    </script>
</body></html>""", items=listings, search_query=search_query)
@app.route('/user_profile/<username>')
def user_profile(username):
    profile = get_user_profile(username)
    reviews = profile.get('reviews', [])
    
    total_stars = 0
    avg_rating = 0.0
    if reviews:
        for r in reviews:
            total_stars += int(r.get('rating', 5))
        avg_rating = round(total_stars / len(reviews), 1)

    return render_template_string(HTML_HEADER + f"""
    <div class="brand-header p-4 text-center">
        <div class="bg-white rounded-circle d-inline-flex align-items-center justify-content-center mb-2 shadow-sm" style="width: 80px; height: 80px;">
            <i class="bi bi-person-fill text-dark display-4"></i>
        </div>
        <h4 class="fw-bold m-0 text-white">{username}</h4>
        <p class="small text-white-50 mb-2">Verified LIMI Seller</p>

        <div class="d-flex justify-content-center align-items-center gap-2 mb-2">
            <span class="badge bg-warning text-dark fs-6"><i class="bi bi-star-fill"></i> {avg_rating} / 5.0</span>
            <span class="badge bg-success fs-6"><i class="bi bi-shield-check"></i> TRUSTED USER</span>
        </div>

        <div class="d-flex justify-content-center gap-3 mt-3">
            <form action="/react_user/{username}/like" method="POST">
                <button type="submit" class="btn btn-sm btn-light rounded-pill px-3 fw-bold text-success">
                    <i class="bi bi-hand-thumbs-up-fill"></i> Genuine ({profile.get('likes', 0)})
                </button>
            </form>
            <form action="/react_user/{username}/dislike" method="POST">
                <button type="submit" class="btn btn-sm btn-outline-light rounded-pill px-3 fw-bold">
                    <i class="bi bi-hand-thumbs-down-fill"></i> Fake ({profile.get('dislikes', 0)})
                </button>
            </form>
        </div>
    </div>

    <div class="container p-3" style="max-width: 600px;">
        <h5 class="fw-bold mb-3"><i class="bi bi-chat-square-quote-fill text-primary"></i> Ratings & Reviews ({len(reviews)})</h5>

        <div class="card p-3 border-0 shadow-sm rounded-4 mb-4">
            <h6 class="fw-bold mb-2">Leave a Review</h6>
            <form action="/add_review/{username}" method="POST">
                <div class="mb-2">
                    <label class="small fw-bold">Star Rating</label>
                    <select name="rating" class="form-select form-select-sm">
                        <option value="5">⭐⭐⭐⭐⭐ (5 - Super Genuine)</option>
                        <option value="4">⭐⭐⭐⭐ (4 - Good Experience)</option>
                        <option value="3">⭐⭐⭐ (3 - Average)</option>
                        <option value="2">⭐⭐ (2 - Slow Response)</option>
                        <option value="1">⭐ (1 - Bad/Scam Alert)</option>
                    </select>
                </div>
                <div class="mb-2">
                    <input type="text" name="comment" class="form-control form-control-sm" placeholder="Write your experience..." required>
                </div>
                <button type="submit" class="btn btn-dark btn-sm w-100 fw-bold rounded-pill">Submit Review</button>
            </form>
        </div>

        <div class="d-flex flex-column gap-2">
            {{% for rev in reviews %}}
            <div class="bg-white p-3 rounded-3 shadow-sm border">
                <div class="d-flex justify-content-between align-items-center mb-1">
                    <strong class="small">{{{{ rev.get('reviewer', 'Buyer') }}}}</strong>
                    <span class="star-gold small">
                        {{% for i in range(rev.get('rating', 5)|int) %}}★{{% endfor %}}
                    </span>
                </div>
                <p class="mb-0 small text-muted">{{{{ rev.get('comment') }}}}</p>
            </div>
            {{% else %}}
            <p class="text-muted text-center small">No reviews yet. Be the first to review!</p>
            {{% endfor %}}
        </div>
    </div>
    </body></html>""", reviews=reviews)

@app.route('/react_user/<username>/<action>', methods=['POST'])
def react_user(username, action):
    profile = get_user_profile(username)
    if action == 'like':
        profile['likes'] = profile.get('likes', 0) + 1
    elif action == 'dislike':
        profile['dislikes'] = profile.get('dislikes', 0) + 1
        
    try:
        url = f"https://limi-marketplace-default-rtdb.firebaseio.com/profiles/{username}.json"
        requests.patch(url, json=profile, timeout=5)
    except:
        pass
    return redirect(f"/user_profile/{username}")

@app.route('/add_review/<username>', methods=['POST'])
def add_review(username):
    rating = request.form.get('rating', 5)
    comment = request.form.get('comment', '')
    profile = get_user_profile(username)
    
    reviews = profile.get('reviews', [])
    reviews.append({"reviewer": "Verified Buyer", "rating": int(rating), "comment": comment})
    profile['reviews'] = reviews
    try:
        url = f"https://limi-marketplace-default-rtdb.firebaseio.com/profiles/{username}.json"
        requests.patch(url, json=profile, timeout=5)
    except:
        pass
    return redirect(f"/user_profile/{username}")

@app.route('/send_message', methods=['POST'])
def send_message():
    data = request.json
    room_id = data.get('room_id')
    sender = data.get('sender')
    message = data.get('message')
    
    if room_id and message:
        chat_url = f"https://limi-marketplace-default-rtdb.firebaseio.com/chats/{room_id}.json"
        msg_payload = {
            "sender": sender,
            "message": message,
            "timestamp": int(time.time())
        }
        requests.post(chat_url, json=msg_payload)
        return jsonify({"status": "success"})
    return jsonify({"status": "error"}), 400

@app.route('/make_offer', methods=['POST'])
def make_offer():
    seller_name = request.form.get('seller_name')
    offer_amount = request.form.get('offer_amount')
    
    offer_data = {
        "seller_name": seller_name,
        "offer_amount": offer_amount,
        "timestamp": int(time.time())
    }
    try:
        requests.post(FIREBASE_OFFERS_URL, json=offer_data, timeout=5)
    except:
        pass
        
    return redirect(f"/chat_room?user_type=buyer&name={seller_name}&offer={offer_amount}")

@app.route('/update_price', methods=['POST'])
def update_price():
    ad_id = request.form.get('ad_id')
    new_price = request.form.get('new_price')
    try:
        update_payload = {"price": f"₹{new_price}", "price_dropped": True}
        requests.patch(f"https://limi-marketplace-default-rtdb.firebaseio.com/listings/{ad_id}.json", json=update_payload, timeout=5)
    except:
        pass
    return redirect('/my-ads')
@app.route('/chats')
def chats():
    return render_template_string(HTML_HEADER + """
    <div class="brand-header p-3 mb-2"><h4 class="fw-bold m-0">Messages & Calls</h4></div>
    <div class="container px-3">
        <ul class="nav nav-tabs nav-fill mb-3" id="chatTabs" role="tablist">
            <li class="nav-item"><button class="nav-link active" data-bs-toggle="tab" data-bs-target="#buyer-chats" type="button">BUYER</button></li>
            <li class="nav-item"><button class="nav-link" data-bs-toggle="tab" data-bs-target="#seller-chats" type="button">SELLER</button></li>
        </ul>
        <div class="tab-content">
            <div class="tab-pane fade show active" id="buyer-chats">
                <a href="/chat_room?user_type=buyer&name=Rahul (Seller)" class="list-group-item list-group-item-action p-3 rounded-3 shadow-sm mb-2 bg-white">
                    <h6 class="fw-bold mb-1">Rahul (Seller)</h6>
                    <p class="mb-0 text-muted small">Price negotiable hai, call kar sakte ho.</p>
                </a>
            </div>
            <div class="tab-pane fade" id="seller-chats">
                <a href="/chat_room?user_type=seller&name=Aman (Buyer)" class="list-group-item list-group-item-action p-3 rounded-3 shadow-sm mb-2 bg-white">
                    <h6 class="fw-bold mb-1">Aman (Buyer)</h6>
                    <p class="mb-0 text-muted small">Iska exact location bhej do.</p>
                </a>
            </div>
        </div>
    </div>
    <div class="bottom-nav">
        <a href="/" class="nav-item-custom"><i class="bi bi-house-door-fill"></i>Home</a>
        <a href="/chats" class="nav-item-custom active"><i class="bi bi-chat-dots"></i>Chats</a>
        <a href="/post" class="sell-btn-wrapper"><div class="sell-btn-circle"><i class="bi bi-plus-lg"></i></div></a>
        <a href="/my-ads" class="nav-item-custom"><i class="bi bi-journal-text"></i>My Ads</a>
        <a href="/account" class="nav-item-custom"><i class="bi bi-person-circle"></i>Account</a>
    </div>
</body></html>""")

@app.route('/app_call')
def app_call():
    user_name = request.args.get('name', 'User')
    return render_template_string(f"""<!DOCTYPE html>
<html><head><meta name="viewport" content="width=device-width, initial-scale=1">
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css">
</head>
<body class="bg-dark text-white d-flex flex-column justify-content-between vh-100 p-4 text-center">
    <div class="mt-5"><h2>{user_name}</h2><p class="text-success" id="cStatus">Connecting...</p></div>
    <div><div class="bg-secondary rounded-circle d-inline-flex align-items-center justify-content-center" style="width: 100px; height: 100px;"><i class="bi bi-person-fill display-3"></i></div></div>
    <div class="mb-5"><a href="/chats" class="btn btn-danger rounded-circle p-3"><i class="bi bi-telephone-x-fill fs-3"></i></a></div>
    <script>navigator.mediaDevices.getUserMedia({{audio:true}}).then(s=>document.getElementById('cStatus').innerText="Connected 00:05");</script>
</body></html>""")

@app.route('/video_call')
def video_call():
    user_name = request.args.get('name', 'User')
    return render_template_string(f"""<!DOCTYPE html>
<html><head><meta name="viewport" content="width=device-width, initial-scale=1">
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css">
<style>body{{background:#000;overflow:hidden;}} #local{{width:100vw;height:100vh;object-fit:cover;}}</style>
</head>
<body>
    <video id="local" autoplay playsinline poster="https://via.placeholder.com/400x800?text=Video+Call..."></video>
    <div style="position:absolute; bottom:30px; left:0; right:0; text-align:center;">
        <a href="/video_call?name={user_name}" class="text-white"><i class="bi bi-camera-video-fill"></i></a>
    </div>
    <script>navigator.mediaDevices.getUserMedia({{video:true,audio:true}}).then(s=>document.getElementById('local').srcObject=s);</script>
</body></html>""")

@app.route('/chat_room')
def chat_room():
    user_name = request.args.get('name', 'User')
    offer = request.args.get('offer', '')
    msg = f"Hi! I made an offer of ₹{offer} for this item." if offer else "Hi, is this listing still available?"
    
    return render_template_string(f"""<!DOCTYPE html>
<html><head><meta name="viewport" content="width=device-width, initial-scale=1">
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css">
<style>
    body{{background:#f1f5f9;height:100vh;display:flex;flex-direction:column;}}
    .chat-body{{flex:1;overflow-y:auto;padding:16px;display:flex;flex-direction:column;}}
    .chat-bubble-me{{background:#dcf8c6;border-radius:12px 12px 0 12px;padding:8px 12px;margin-bottom:8px;max-width:80%;align-self:flex-end;font-size:0.9rem;}}
    .chat-bubble-other{{background:#fff;border-radius:12px 12px 12px 0;padding:8px 12px;margin-bottom:8px;max-width:80%;align-self:flex-start;border:1px solid #e2e8f0;font-size:0.9rem;}}
    .voice-btn{{width:42px;height:42px;border-radius:50%;border:none;background:#00e599;color:#0b132b;display:flex;align-items:center;justify-content:center;}}
    .voice-btn.recording{{background:#ef4444;color:#fff;}}
</style>
</head>
<body class="d-flex flex-column vh-100">
    <div style="background:#0b132b;color:white;padding:12px;" class="d-flex justify-content-between align-items-center">
        <div class="d-flex align-items-center">
            <a href="/chats" class="text-white fs-5 me-3"><i class="bi bi-arrow-left"></i></a>
            <h6 class="m-0 fw-bold">{user_name}</h6>
        </div>
        <div class="d-flex gap-3 fs-5">
            <a href="/app_call?name={user_name}" class="text-white"><i class="bi bi-telephone-fill"></i></a>
            <a href="/video_call?name={user_name}" class="text-white"><i class="bi bi-camera-video-fill"></i></a>
        </div>
    </div>
    
    <div class="chat-body" id="cBody">
        <div class="chat-bubble-other">{msg}<div class="text-muted text-end" style="font-size:0.65rem;">Just now</div></div>
    </div>

    <div class="bg-white p-2 border-top d-flex gap-2 align-items-center">
        <input type="text" id="inp" class="form-control rounded-pill bg-light border-0" placeholder="Type a message...">
        <button id="vBtn" class="voice-btn" onclick="toggleVoice()"><i class="bi bi-mic-fill" id="micIco"></i></button>
        <button class="btn btn-dark rounded-circle" style="width:42px;height:42px;" onclick="sendMsg()"><i class="bi bi-send-fill"></i></button>
    </div>

    <script>
        let rec, chunks = [], isRec = false;
        function sendMsg() {{
            let i = document.getElementById('inp');
            if(i.value.trim() !== "") {{
                let b = document.createElement('div');
                b.className = 'chat-bubble-me';
                b.innerHTML = i.value + `<div class="text-muted text-end" style="font-size:0.65rem;">Just now</div>`;
                document.getElementById('cBody').appendChild(b);
                i.value = "";
                document.getElementById('cBody').scrollTop = document.getElementById('cBody').scrollHeight;
            }}
        }}
        function toggleVoice() {{
            let btn = document.getElementById('vBtn'), ico = document.getElementById('micIco');
            if(!isRec) {{
                navigator.mediaDevices.getUserMedia({{audio:true}}).then(stream => {{
                    rec = new MediaRecorder(stream);
                    chunks = [];
                    rec.ondataavailable = e => chunks.push(e.data);
                    rec.onstop = () => {{
                        let blob = new Blob(chunks, {{type:'audio/mp3'}});
                        let url = URL.createObjectURL(blob);
                        let b = document.createElement('div');
                        b.className = 'chat-bubble-me';
                        b.innerHTML = `<audio controls src="${{url}}" style="max-width:160px;height:30px;"></audio><div class="text-muted text-end" style="font-size:0.65rem;">Voice Note</div>`;
                        document.getElementById('cBody').appendChild(b);
                    }};
                    rec.start();
                    isRec = true;
                    btn.classList.add('recording');
                    ico.className = 'bi bi-stop-fill';
                }}).catch(e => alert("Mic Error"));
            }} else {{
                rec.stop();
                isRec = false;
                btn.classList.remove('recording');
                ico.className = 'bi bi-mic-fill';
            }}
        }}
    </script>
</body></html>""")
@app.route('/post', methods=['GET', 'POST'])
def post_ad():
    if request.method == 'POST':
        is_urgent = True if request.form.get('is_urgent') == 'on' else False
        new_item = {
            "title": request.form.get('title', ''),
            "price": "₹" + str(request.form.get('price', '0')),
            "location": request.form.get('location', ''),
            "image": request.form.get('image', ''),
            "seller_name": request.form.get('seller_name', 'RahulSeller'),
            "is_urgent": is_urgent,
            "created_at": int(time.time())
        }
        try:
            requests.post(FIREBASE_URL, json=new_item, timeout=5)
        except:
            pass
        return redirect('/')
        
    return render_template_string(HTML_HEADER + """
    <div class="container p-3" style="max-width: 500px;">
        <h4 class="fw-bold mb-3">Post New Listing</h4>
        <form method="POST" class="card p-3 shadow-sm border-0 rounded-4">
            <div class="mb-2"><label class="small fw-bold">Your Name / Username</label><input type="text" name="seller_name" class="form-control" placeholder="e.g. Rahul_Patna" required></div>
            <div class="mb-2"><label class="small fw-bold">Ad Title</label><input type="text" name="title" class="form-control" required></div>
            <div class="mb-2"><label class="small fw-bold">Price (₹)</label><input type="number" name="price" class="form-control" required></div>
            <div class="mb-2"><label class="small fw-bold">Location</label><input type="text" name="location" class="form-control" required></div>
            <div class="mb-3"><label class="small fw-bold">Image URL</label><input type="url" name="image" class="form-control"></div>
            <div class="form-check form-switch mb-3 p-3 bg-light rounded border">
                <input class="form-check-input ms-0 me-2" type="checkbox" id="urgentCheck" name="is_urgent">
                <label class="form-check-label fw-bold text-danger" for="urgentCheck">🔥 Mark as URGENT SALE (24h Timer)</label>
            </div>
            <button type="submit" class="btn btn-success w-100 fw-bold py-2 rounded-pill">POST AD NOW</button>
        </form>
    </div>
    </body></html>""")

@app.route('/my-ads')
def my_ads():
    listings = get_firebase_listings()
    return render_template_string(HTML_HEADER + """
    <div class="container p-3">
        <h4 class="fw-bold mb-3">My Ads & Price Drop</h4>
        <div class="row g-3">
            {% for item in items %}
            <div class="col-12">
                <div class="card p-3 border-0 shadow-sm rounded-4">
                    <h6 class="fw-bold">{{ item.get('title') }}</h6>
                    <p class="text-muted small mb-2">Current: <b>{{ item.get('price') }}</b></p>
                    <form action="/update_price" method="POST" class="row g-2">
                        <input type="hidden" name="ad_id" value="{{ item.get('id') }}">
                        <div class="col-8"><input type="number" name="new_price" class="form-control form-control-sm" placeholder="New Lower Price" required></div>
                        <div class="col-4"><button type="submit" class="btn btn-sm btn-danger w-100 fw-bold">Drop</button></div>
                    </form>
                </div>
            </div>
            {% endfor %}
        </div>
    </div>
    </body></html>""", items=listings)

@app.route('/account')
def account():
    return render_template_string(HTML_HEADER + """
    <div class="container p-3 text-center">
        <h4 class="fw-bold mb-1">My Account</h4>
        <p class="text-muted small">LIMI Pro Member</p>
        <a href="/user_profile/MyOwnProfile" class="btn btn-dark btn-sm rounded-pill px-4 fw-bold mt-2">View My Public Profile</a>
    </div></body></html>""")

@app.route('/manifest.json')
def serve_manifest():
    return send_from_directory('.', 'manifest.json')

@app.route('/icon-192.png')
def serve_icon_192():
    return send_from_directory('.', 'icon-192.png')

@app.route('/icon-512.png')
def serve_icon_512():
    return send_from_directory('.', 'icon-512.png')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

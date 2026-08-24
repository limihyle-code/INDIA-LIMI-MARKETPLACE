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

def get_user_profile(username):
    try:
        url = f"https://limi-marketplace-default-rtdb.firebaseio.com/profiles/{username}.json"
        res = requests.get(url, timeout=5)
        if res.status_code == 200 and res.json():
            return res.json()
    except Exception as e:
        print("Profile Fetch Error:", e)
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
    <style>
        :root { --app-dark: #0b132b; --app-accent: #00e599; --app-blue: #1c2541; --app-light-bg: #f4f6f9; }
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
    </style>
</head>
<body>
    <div id="splashScreen">
        <div class="splash-tag">ULTIMATE DIRECTORY</div>
        <div class="splash-title">LIMI Marketplace</div>
        <div class="spinner-border text-success mt-4" style="width: 2.2rem; height: 2.2rem;" role="status"></div>
    </div>
"""

@app.route('/')
def home():
    listings = get_firebase_listings()
    search_query = request.args.get('search', '').strip().lower()
    
    if search_query:
        listings = [i for i in listings if search_query in str(i.get('title', '')).lower()]

    return render_template_string(HTML_HEADER + """
    <div class="brand-header p-3 mb-3">
        <div class="d-flex justify-content-between align-items-center">
            <h3 class="fw-black m-0"><a href="/" class="text-white text-decoration-none">LIMI<span style="color: var(--app-accent);">.</span></a></h3>
            <select class="form-select form-select-sm w-auto bg-dark text-white border-0 fw-bold" id="langSelector" onchange="changeLanguage(this.value)">
                <option value="en">English</option>
                <option value="hi">हिंदी (Hindi)</option>
                <option value="hinglish">Hinglish</option>
                <option value="bn">বাংলা (Bengali)</option>
                <option value="mr">मराठी (Marathi)</option>
                <option value="te">తెలుగు (Telugu)</option>
                <option value="ta">தமிழ் (Tamil)</option>
            </select>
        </div>
        <form action="/" method="GET" class="mt-2">
            <div class="input-group">
                <input type="text" name="search" class="form-control border-0 ps-3" style="border-radius: 10px 0 0 10px;" placeholder="Search Ads..." value="{{ search_query }}" data-i18n-ph="search_ph">
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
                    <div class="urgent-badge" data-i18n="urgent_badge"><i class="bi bi-lightning-charge-fill"></i> URGENT</div>
                    {% endif %}
                    {% if item.get('price_dropped') %}
                    <div class="price-drop-badge" style="top: {% if item.get('is_urgent') %}32px{% else %}8px{% endif %};" data-i18n="price_drop_badge"><i class="bi bi-tag-fill"></i> PRICE DROP</div>
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
                            <button type="button" class="btn btn-sm btn-outline-success p-1 fw-bold" style="font-size: 0.68rem;" data-bs-toggle="modal" data-bs-target="#offerModal_{{ loop.index }}" data-i18n="offer_btn">
                                <i class="bi bi-tags"></i> Offer
                            </button>
                            <a href="/chat_room?user_type=buyer&name={{ item.get('seller_name', 'OfficialSeller') }}&title={{ item.get('title') }}" class="btn btn-sm btn-dark flex-fill p-1 fw-bold" style="font-size: 0.72rem;" data-i18n="chat_btn"><i class="bi bi-chat-fill"></i> Chat</a>
                        </div>
                    </div>
                </div>
            </div>

            <div class="modal fade" id="offerModal_{{ loop.index }}" tabindex="-1" aria-hidden="true">
              <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content" style="border-radius: 20px;">
                  <div class="modal-header border-0 pb-0">
                    <h5 class="modal-title fw-bold fs-6" data-i18n="bargain_title">🏷️ Make your Bargain Offer</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                  </div>
                  <form action="/make_offer" method="POST">
                      <div class="modal-body">
                        <input type="hidden" name="seller_name" value="{{ item.get('seller_name', 'OfficialSeller') }}">
                        <p class="text-muted small mb-2"><span data-i18n="listed_price">Listed Price</span>: <b>{{ item.get('price') }}</b></p>
                        <div class="mb-3">
                            <label class="form-label fw-bold small" data-i18n="your_offer_price">Your Offer Price (₹)</label>
                            <input type="number" name="offer_amount" class="form-control form-control-lg fw-bold text-success" placeholder="e.g. 8500" required>
                        </div>
                      </div>
                      <div class="modal-footer border-0 pt-0">
                        <button type="submit" class="btn btn-success w-100 fw-bold py-2 rounded-pill" data-i18n="send_offer">SEND OFFER</button>
                      </div>
                  </form>
                </div>
              </div>
            </div>
            {% endfor %}
        </div>
    </div>

    <div class="bottom-nav">
        <a href="/" class="nav-item-custom active"><i class="bi bi-house-door-fill"></i><span data-i18n="nav_home">Home</span></a>
        <a href="/chats" class="nav-item-custom"><i class="bi bi-chat-dots"></i><span data-i18n="nav_chats">Chats</span></a>
        <a href="/post" class="sell-btn-wrapper"><div class="sell-btn-circle"><i class="bi bi-plus-lg"></i></div></a>
        <a href="/my-ads" class="nav-item-custom"><i class="bi bi-journal-text"></i><span data-i18n="nav_ads">My Ads</span></a>
        <a href="/account" class="nav-item-custom"><i class="bi bi-person-circle"></i><span data-i18n="nav_account">Account</span></a>
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
            }, 500);
        });

        const translations = {
            en: { search_ph: "Search Ads...", urgent_badge: "URGENT", price_drop_badge: "PRICE DROP", offer_btn: "Offer", chat_btn: "Chat", bargain_title: "🏷️ Make your Bargain Offer", listed_price: "Listed Price", your_offer_price: "Your Offer Price (₹)", send_offer: "SEND OFFER", nav_home: "Home", nav_chats: "Chats", nav_ads: "My Ads", nav_account: "Account" },
            hi: { search_ph: "विज्ञापन खोजें...", urgent_badge: "जरूरी", price_drop_badge: "दाम घटा", offer_btn: "ऑफर", chat_btn: "चैट", bargain_title: "🏷️ अपना ऑफर दें", listed_price: "तय दाम", your_offer_price: "आपकी कीमत (₹)", send_offer: "ऑफर भेजें", nav_home: "होम", nav_chats: "चैट", nav_ads: "माय एड्स", nav_account: "अकाउंट" },
            hinglish: { search_ph: "Kya dhoondh rahe ho...", urgent_badge: "TURANT BECHNA HAI", price_drop_badge: "PRICE KAM HUA", offer_btn: "Bargain", chat_btn: "Chat Karo", bargain_title: "🏷️ Apna Rate Bato", listed_price: "Seller ka Price", your_offer_price: "Aapka Rate (₹)", send_offer: "OFFER BHEJO", nav_home: "Home", nav_chats: "Baat-Cheet", nav_ads: "Mera Samaan", nav_account: "Profile" },
            bn: { search_ph: "বিজ্ঞাপন খুঁজুন...", urgent_badge: "জরুরি", price_drop_badge: "দাম কমেছে", offer_btn: "অফার", chat_btn: "চ্যাট", bargain_title: "🏷️ আপনার অফার দিন", listed_price: "নির্ধারিত মূল্য", your_offer_price: "আপনার দাম (₹)", send_offer: "অফার পাঠান", nav_home: "হোম", nav_chats: "চ্যাট", nav_ads: "আমার বিজ্ঞাপন", nav_account: "অ্যাকাউন্ট" },
            mr: { search_ph: "जाहिराती शोधा...", urgent_badge: "तातडीचे", price_drop_badge: "किंमत कमी झाली", offer_btn: "ऑफर", chat_btn: "चॅट", bargain_title: "🏷️ तुमची ऑफर द्या", listed_price: "निश्चित किंमत", your_offer_price: "तुमची किंमत (₹)", send_offer: "ऑफर पाठवा", nav_home: "होम", nav_chats: "चॅट्स", nav_ads: "माझ्या जाहिराती", nav_account: "खाते" },
            te: { search_ph: "యాడ్‌లను శోధించండి...", urgent_badge: "అత్యవసరం", price_drop_badge: "ధర తగ్గింది", offer_btn: "ఆఫర్", chat_btn: "చాట్", bargain_title: "🏷️ మీ ఆఫర్‌ను ఇవ్వండి", listed_price: "నిర్ణయించిన ధర", your_offer_price: "మీ ధర (₹)", send_offer: "ఆఫర్ పంపండి", nav_home: "హోమ్", nav_chats: "చాట్‌లు", nav_ads: "నా యాడ్‌లు", nav_account: "ఖాతా" },
            ta: { search_ph: "விளம்பரங்களைத் தேடுங்கள்...", urgent_badge: "அவசியம்", price_drop_badge: "விலை குறைந்தது", offer_btn: "ஆஃபர்", chat_btn: "சாட்", bargain_title: "🏷️ உங்கள் ஆஃபரை அளியுங்கள்", listed_price: "குறிப்பிட்ட விலை", your_offer_price: "உங்கள் விலை (₹)", send_offer: "ஆஃபர் அனுப்பு", nav_home: "முகப்பு", nav_chats: "சாட்கள்", nav_ads: "என் விளம்பரங்கள்", nav_account: "கணக்கு" }
        };

        function changeLanguage(lang) {
            localStorage.setItem('limi_lang', lang);
            applyLanguage();
        }

        function applyLanguage() {
            let lang = localStorage.getItem('limi_lang') || 'en';
            let selector = document.getElementById('langSelector');
            if(selector) selector.value = lang;
            
            let dict = translations[lang] || translations['en'];
            document.querySelectorAll('[data-i18n]').forEach(el => {
                let key = el.getAttribute('data-i18n');
                if (dict[key]) el.innerText = dict[key];
            });
            document.querySelectorAll('[data-i18n-ph]').forEach(el => {
                let key = el.getAttribute('data-i18n-ph');
                if (dict[key]) el.placeholder = dict[key];
            });
        }

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
                    el.innerText = `${h}h ${m < 10 ? '0'+m : m}m ${s < 10 ? '0'+s : s}s`;
                }
            });
        }
        setInterval(updateTimers, 1000);
        updateTimers();
        applyLanguage();
    </script>
</body></html>""", items=listings, search_query=search_query)

@app.route('/chats')
def chats():
    listings = get_firebase_listings()
    sellers = list(set([item.get('seller_name', 'OfficialSeller') for item in listings if item.get('seller_name')]))
    if not sellers:
        sellers = ['OfficialSeller']

    return render_template_string(HTML_HEADER + """
    <div class="brand-header p-3 mb-3">
        <h4 class="fw-bold text-white m-0"><i class="bi bi-chat-dots-fill me-2"></i> Messages & Buyers</h4>
    </div>
    <div class="container px-3">
        <div class="card border-0 rounded-4 p-3 shadow-sm mb-3">
            <h6 class="fw-bold text-muted mb-3" style="font-size: 0.8rem; letter-spacing: 1px;">ACTIVE CHATS & SELLERS</h6>
            
            {% for seller in sellers %}
            <div class="d-flex align-items-center justify-content-between p-2 border-bottom">
                <div class="d-flex align-items-center gap-3">
                    <div class="bg-dark text-white rounded-circle d-flex align-items-center justify-content-center fw-bold" style="width: 45px; height: 45px;">
                        {{ seller[0].upper() }}
                    </div>
                    <div>
                        <h6 class="fw-bold mb-0 text-dark">{{ seller }}</h6>
                        <small class="text-success" style="font-size: 0.75rem;"><i class="bi bi-circle-fill"></i> Available for chat</small>
                    </div>
                </div>
                <div class="d-flex gap-1">
                    <a href="/chat_room?user_type=buyer&name={{ seller }}" class="btn btn-outline-dark btn-sm rounded-pill px-3 fw-bold">Buyer Chat</a>
                    <a href="/chat_room?user_type=seller&name={{ seller }}" class="btn btn-success btn-sm rounded-pill px-3 fw-bold">Seller Dashboard</a>
                </div>
            </div>
            {% endfor %}
        </div>
    </div>
    <div class="bottom-nav">
        <a href="/" class="nav-item-custom"><i class="bi bi-house-door"></i><span>Home</span></a>
        <a href="/chats" class="nav-item-custom active"><i class="bi bi-chat-dots-fill"></i><span>Chats</span></a>
        <a href="/post" class="sell-btn-wrapper"><div class="sell-btn-circle"><i class="bi bi-plus-lg"></i></div></a>
        <a href="/my-ads" class="nav-item-custom"><i class="bi bi-journal-text"></i><span>My Ads</span></a>
        <a href="/account" class="nav-item-custom"><i class="bi bi-person-circle"></i><span>Account</span></a>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        window.addEventListener('load', function() {
            const splash = document.getElementById('splashScreen');
            if(splash) splash.style.display = 'none';
        });
    </script>
    </body></html>""", sellers=sellers)

@app.route('/chat_room')
def chat_room():
    user_type = request.args.get('user_type', 'buyer')
    target_name = request.args.get('name', 'Seller')
    item_title = request.args.get('title', '')
    offer_amount = request.args.get('offer', '')

    return render_template_string(HTML_HEADER + """
    <div class="brand-header p-3 d-flex align-items-center justify-content-between">
        <div class="d-flex align-items-center gap-2">
            <a href="/chats" class="text-white me-2"><i class="bi bi-arrow-left fs-4"></i></a>
            <div>
                <h6 class="fw-bold m-0 text-white">{{ target_name }} <span class="badge bg-success" style="font-size: 0.6rem;">{{ user_type.upper() }} MODE</span></h6>
                <small class="text-light" style="font-size: 0.7rem;"><i class="bi bi-circle-fill text-success"></i> Online</small>
            </div>
        </div>
        <div class="d-flex gap-2">
            <a href="/app_call?name={{ target_name }}" class="btn btn-sm btn-outline-light rounded-circle"><i class="bi bi-telephone-fill"></i></a>
            <a href="/video_call?name={{ target_name }}" class="btn btn-sm btn-outline-light rounded-circle"><i class="bi bi-camera-video-fill"></i></a>
        </div>
    </div>

    <div class="container p-3">
        {% if offer_amount %}
        <div class="alert alert-success border-0 rounded-4 shadow-sm text-center">
            <i class="bi bi-tags-fill me-1"></i> Sent Offer of <b>₹{{ offer_amount }}</b> to {{ target_name }}!
        </div>
        {% endif %}

        <div class="card border-0 shadow-sm rounded-4 p-3 mb-3 bg-white" style="min-height: 380px; display: flex; flex-direction: column; justify-content: space-between;">
            <div id="chatMessages">
                <div class="text-center text-muted small my-2">Chat Room connected with <b>{{ target_name }}</b></div>
                {% if item_title %}
                <div class="alert alert-light border small text-center fw-bold py-1 mb-2">Item Inquiry: {{ item_title }}</div>
                {% endif %}
                <div class="bg-light p-2 rounded-3 w-75 mb-2 border">
                    <small class="fw-bold text-dark d-block">System Guard</small>
                    <span class="small">Keep conversations safe. Do not share confidential financial passwords.</span>
                </div>
            </div>
            
            <form id="chatForm" onsubmit="sendMessage(event)" class="mt-3">
                <div class="input-group">
                    <input type="text" id="msgInput" class="form-control" placeholder="Type a message..." required>
                    <button type="submit" class="btn btn-dark"><i class="bi bi-send-fill"></i></button>
                </div>
            </form>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        window.addEventListener('load', function() {
            const splash = document.getElementById('splashScreen');
            if(splash) splash.style.display = 'none';
        });

        function sendMessage(e) {
            e.preventDefault();
            const input = document.getElementById('msgInput');
            const txt = input.value.trim();
            if(!txt) return;

            const box = document.getElementById('chatMessages');
            const msgDiv = document.createElement('div');
            msgDiv.className = 'bg-dark text-white p-2 rounded-3 w-75 ms-auto mb-2 text-end';
            msgDiv.innerHTML = `<small class="fw-bold d-block text-success">You ({{ user_type }})</small><span class="small">${txt}</span>`;
            box.appendChild(msgDiv);
            input.value = '';
            box.scrollTop = box.scrollHeight;
        }
    </script>
    </body></html>""", target_name=target_name, user_type=user_type, offer_amount=offer_amount, item_title=item_title)

@app.route('/user_profile/<username>')
def user_profile(username):
    profile = get_user_profile(username)
    reviews = profile.get('reviews', [])
    likes = profile.get('likes', 0)
    dislikes = profile.get('dislikes', 0)
    
    total_stars = sum(int(r.get('rating', 5)) for r in reviews) if reviews else 0
    avg_rating = round(total_stars / len(reviews), 1) if reviews else 0.0

    return render_template_string(HTML_HEADER + """
    <div class="brand-header p-4 text-center">
        <div class="avatar-circle mx-auto mb-2 bg-success text-dark fw-bold d-flex align-items-center justify-content-center rounded-circle" style="width: 70px; height: 70px; font-size: 1.8rem;">
            {{ username[0].upper() }}
        </div>
        <h4 class="fw-bold m-0 text-white">{{ username }}</h4>
        
        <div class="mt-2">
            <span class="badge bg-warning text-dark fs-6"><i class="bi bi-star-fill"></i> {{ avg_rating }} / 5.0</span>
            <span class="badge bg-light text-dark fs-6 ms-1">({{ reviews|length }} Reviews)</span>
        </div>

        <div class="d-flex justify-content-center gap-3 mt-3">
            <form action="/react_user/{{ username }}/like" method="POST">
                <button class="btn btn-outline-light btn-sm rounded-pill px-3"><i class="bi bi-hand-thumbs-up-fill text-success"></i> Like ({{ likes }})</button>
            </form>
            <form action="/react_user/{{ username }}/dislike" method="POST">
                <button class="btn btn-outline-light btn-sm rounded-pill px-3"><i class="bi bi-hand-thumbs-down-fill text-danger"></i> Dislike ({{ dislikes }})</button>
            </form>
        </div>
    </div>

    <div class="container p-3" style="max-width: 600px;">
        <div class="card p-3 mb-3 border-0 shadow-sm rounded-4">
            <h6 class="fw-bold mb-3">Leave a Review for {{ username }}</h6>
            <form action="/add_review/{{ username }}" method="POST">
                <div class="mb-2">
                    <select name="rating" class="form-select form-select-sm fw-bold text-warning">
                        <option value="5">⭐⭐⭐⭐⭐ (5/5) Excellent</option>
                        <option value="4">⭐⭐⭐⭐ (4/5) Good</option>
                        <option value="3">⭐⭐⭐ (3/5) Average</option>
                        <option value="2">⭐⭐ (2/5) Poor</option>
                        <option value="1">⭐ (1/5) Terrible</option>
                    </select>
                </div>
                <div class="mb-2">
                    <textarea name="comment" class="form-control" rows="2" placeholder="Write feedback about seller..." required></textarea>
                </div>
                <button type="submit" class="btn btn-dark btn-sm fw-bold w-100 rounded-pill">Submit Review</button>
            </form>
        </div>

        <h6 class="fw-bold mb-2">User Feedback</h6>
        {% for rev in reviews %}
        <div class="bg-white p-3 mb-2 rounded-3 border shadow-sm">
            <div class="text-warning mb-1">
                {% for i in range(rev.get('rating', 5)|int) %}<i class="bi bi-star-fill"></i>{% endfor %}
            </div>
            <p class="m-0 small text-dark fw-semibold">{{ rev.get('comment') }}</p>
        </div>
        {% else %}
        <p class="text-muted small">No reviews yet for this seller.</p>
        {% endfor %}
    </div>
    
    <div class="bottom-nav">
        <a href="/" class="nav-item-custom"><i class="bi bi-house-door"></i><span>Home</span></a>
        <a href="/chats" class="nav-item-custom"><i class="bi bi-chat-dots"></i><span>Chats</span></a>
        <a href="/post" class="sell-btn-wrapper"><div class="sell-btn-circle"><i class="bi bi-plus-lg"></i></div></a>
        <a href="/my-ads" class="nav-item-custom"><i class="bi bi-journal-text"></i><span>My Ads</span></a>
        <a href="/account" class="nav-item-custom active"><i class="bi bi-person-circle"></i><span>Account</span></a>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        window.addEventListener('load', function() {
            const splash = document.getElementById('splashScreen');
            if(splash) splash.style.display = 'none';
        });
    </script>
    </body></html>""", username=username, reviews=reviews, likes=likes, dislikes=dislikes, avg_rating=avg_rating)

@app.route('/add_review/<username>', methods=['POST'])
def add_review(username):
    rating = int(request.form.get('rating', 5))
    comment = request.form.get('comment', '')
    profile = get_user_profile(username)
    reviews = profile.get('reviews', [])
    reviews.append({"rating": rating, "comment": comment})
    profile['reviews'] = reviews
    try:
        requests.patch(f"https://limi-marketplace-default-rtdb.firebaseio.com/profiles/{username}.json", json=profile, timeout=5)
    except Exception as e:
        print("Add Review Error:", e)
    return redirect(f"/user_profile/{username}")

@app.route('/react_user/<username>/<action>', methods=['POST'])
def react_user(username, action):
    profile = get_user_profile(username)
    if action == 'like':
        profile['likes'] = profile.get('likes', 0) + 1
    elif action == 'dislike':
        profile['dislikes'] = profile.get('dislikes', 0) + 1
    try:
        requests.patch(f"https://limi-marketplace-default-rtdb.firebaseio.com/profiles/{username}.json", json=profile, timeout=5)
    except Exception as e:
        print("React Error:", e)
    return redirect(f"/user_profile/{username}")

@app.route('/make_offer', methods=['POST'])
def make_offer():
    seller_name = request.form.get('seller_name')
    offer_amount = request.form.get('offer_amount')
    try:
        requests.post(FIREBASE_OFFERS_URL, json={"seller_name": seller_name, "offer_amount": offer_amount, "timestamp": int(time.time())}, timeout=5)
    except Exception as e:
        print("Offer Error:", e)
    return redirect(f"/chat_room?user_type=buyer&name={seller_name}&offer={offer_amount}")

@app.route('/update_price', methods=['POST'])
def update_price():
    ad_id = request.form.get('ad_id')
    new_price = request.form.get('new_price')
    try:
        requests.patch(f"https://limi-marketplace-default-rtdb.firebaseio.com/listings/{ad_id}.json", json={"price": f"₹{new_price}", "price_dropped": True}, timeout=5)
    except Exception as e:
        print("Price Update Error:", e)
    return redirect('/my-ads')

@app.route('/app_call')
def app_call():
    user_name = request.args.get('name', 'User')
    return render_template_string("""<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Voice Call</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css">
    <style>
        body { background: #0b132b; color: white; display: flex; flex-direction: column; justify-content: space-between; height: 100vh; padding: 40px 20px; text-align: center; }
        .avatar-lg { width: 110px; height: 110px; background: #1c2541; border: 3px solid #00e599; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 2.8rem; margin: 0 auto; }
    </style>
</head>
<body>
    <div class="mt-4">
        <div class="avatar-lg mb-3">{{ user_name[0].upper() }}</div>
        <h3 class="fw-bold mb-1">{{ user_name }}</h3>
        <span class="badge bg-success text-dark fw-bold px-3 py-2 rounded-pill">In Voice Call...</span>
    </div>
    <div class="mb-5">
        <a href="/chats" class="btn btn-danger btn-lg rounded-circle p-3" style="width: 70px; height: 70px; display: inline-flex; align-items: center; justify-content: center;">
            <i class="bi bi-telephone-x-fill fs-2"></i>
        </a>
    </div>
    </body>
</html>""", user_name=user_name)

@app.route('/video_call')
def video_call():
    user_name = request.args.get('name', 'User')
    return render_template_string("""<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Video Call</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css">
    <style>
        body { background: #000; color: white; height: 100vh; position: relative; overflow: hidden; }
        .video-box { position: absolute; top:0; left:0; width:100%; height:100%; display:flex; align-items:center; justify-content:center; background:#1c2541; }
        .call-controls { position: absolute; bottom: 40px; left:0; right:0; display:flex; justify-content:center; gap:20px; }
    </style>
</head>
<body>
    <div class="video-box">
        <div class="text-center">
            <i class="bi bi-camera-video-fill display-1 text-secondary mb-2"></i>
            <h4 class="fw-bold">{{ user_name }}</h4>
            <p class="text-success fw-bold">Live Video Streaming...</p>
        </div>
    </div>
    <div class="call-controls">
        <a href="/chats" class="btn btn-danger btn-lg rounded-circle p-3 d-flex align-items-center justify-content-center" style="width:65px; height:65px;">
            <i class="bi bi-telephone-x-fill fs-3"></i>
        </a>
    </div>
</body>
</html>""", user_name=user_name)

@app.route('/post', methods=['GET', 'POST'])
def post_ad():
    if request.method == 'POST':
        new_item = {
            "title": request.form.get('title', ''),
            "price": "₹" + str(request.form.get('price', '0')),
            "location": request.form.get('location', ''),
            "image": request.form.get('image', ''),
            "seller_name": request.form.get('seller_name', 'User'),
            "is_urgent": True if request.form.get('is_urgent') == 'on' else False,
            "created_at": int(time.time())
        }
        try:
            requests.post(FIREBASE_URL, json=new_item, timeout=5)
        except Exception as e:
            print("Post Error:", e)
        return redirect('/')

    return render_template_string(HTML_HEADER + """
    <div class="brand-header p-3 mb-3">
        <h4 class="fw-bold text-white m-0">Post New Ad</h4>
    </div>
    <div class="container p-3" style="max-width: 500px;">
        <form method="POST" class="card p-3 border-0 rounded-4 shadow-sm">
            <div class="mb-2">
                <label class="form-label small fw-bold">Seller Name</label>
                <input type="text" name="seller_name" class="form-control" placeholder="Enter your name" required>
            </div>
            <div class="mb-2">
                <label class="form-label small fw-bold">Title</label>
                <input type="text" name="title" class="form-control" placeholder="e.g. iPhone 13 128GB" required>
            </div>
            <div class="mb-2">
                <label class="form-label small fw-bold">Price (₹)</label>
                <input type="number" name="price" class="form-control" placeholder="e.g. 35000" required>
            </div>
            <div class="mb-2">
                <label class="form-label small fw-bold">Location</label>
                <input type="text" name="location" class="form-control" placeholder="e.g. Delhi" required>
            </div>
            <div class="mb-3">
                <label class="form-label small fw-bold">Image URL</label>
                <input type="url" name="image" class="form-control" placeholder="https://example.com/photo.jpg">
            </div>
            <div class="form-check mb-3">
                <input type="checkbox" name="is_urgent" class="form-check-input" id="urgentCheck">
                <label class="form-check-label fw-bold text-danger small" for="urgentCheck">🔥 Mark as URGENT (24h Timer Tag)</label>
            </div>
            <button type="submit" class="btn btn-success w-100 fw-bold py-2 rounded-pill">PUBLISH AD</button>
        </form>
    </div>
    <div class="bottom-nav">
        <a href="/" class="nav-item-custom"><i class="bi bi-house-door"></i><span>Home</span></a>
        <a href="/chats" class="nav-item-custom"><i class="bi bi-chat-dots"></i><span>Chats</span></a>
        <a href="/post" class="sell-btn-wrapper"><div class="sell-btn-circle"><i class="bi bi-plus-lg"></i></div></a>
        <a href="/my-ads" class="nav-item-custom"><i class="bi bi-journal-text"></i><span>My Ads</span></a>
        <a href="/account" class="nav-item-custom"><i class="bi bi-person-circle"></i><span>Account</span></a>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        window.addEventListener('load', function() {
            const splash = document.getElementById('splashScreen');
            if(splash) splash.style.display = 'none';
        });
    </script>
    </body></html>""")

@app.route('/my-ads')
def my_ads():
    listings = get_firebase_listings()
    return render_template_string(HTML_HEADER + """
    <div class="brand-header p-3 mb-3">
        <h4 class="fw-bold text-white m-0">My Ads & Price Drop</h4>
    </div>
    <div class="container px-3">
        <div class="row g-3">
            {% for item in items %}
            <div class="col-12 col-md-6">
                <div class="card p-3 border-0 rounded-4 shadow-sm bg-white d-flex flex-row gap-3 align-items-center">
                    {% if item.get('image') %}
                    <img src="{{ item.get('image') }}" style="width: 80px; height: 80px; object-fit: cover; border-radius: 12px;">
                    {% else %}
                    <div class="bg-light rounded-3 d-flex align-items-center justify-content-center text-muted" style="width: 80px; height: 80px;"><i class="bi bi-box-seam fs-3"></i></div>
                    {% endif %}

                    <div class="flex-grow-1">
                        <h6 class="fw-bold mb-1 text-truncate">{{ item.get('title') }}</h6>
                        <span class="badge bg-success mb-2">{{ item.get('price') }}</span>
                        
                        <form action="/update_price" method="POST" class="d-flex gap-1">
                            <input type="hidden" name="ad_id" value="{{ item.get('id') }}">
                            <input type="number" name="new_price" class="form-control form-control-sm" placeholder="New ₹" required>
                            <button type="submit" class="btn btn-sm btn-dark text-nowrap fw-bold" style="font-size: 0.7rem;">Drop Price</button>
                        </form>
                    </div>
                </div>
            </div>
            {% else %}
            <div class="text-center text-muted py-5">No active ads found.</div>
            {% endfor %}
        </div>
    </div>
    <div class="bottom-nav">
        <a href="/" class="nav-item-custom"><i class="bi bi-house-door"></i><span>Home</span></a>
        <a href="/chats" class="nav-item-custom"><i class="bi bi-chat-dots"></i><span>Chats</span></a>
        <a href="/post" class="sell-btn-wrapper"><div class="sell-btn-circle"><i class="bi bi-plus-lg"></i></div></a>
        <a href="/my-ads" class="nav-item-custom active"><i class="bi bi-journal-text-fill"></i><span>My Ads</span></a>
        <a href="/account" class="nav-item-custom"><i class="bi bi-person-circle"></i><span>Account</span></a>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        window.addEventListener('load', function() {
            const splash = document.getElementById('splashScreen');
            if(splash) splash.style.display = 'none';
        });
    </script>
    </body></html>""", items=listings)

@app.route('/account')
def account():
    return render_template_string(HTML_HEADER + """
    <div class="brand-header p-4 text-center">
        <div class="avatar-lg bg-light text-dark fw-bold rounded-circle mx-auto mb-2 d-flex align-items-center justify-content-center" style="width:80px; height:80px; font-size: 2rem;">
            U
        </div>
        <h4 class="fw-bold text-white m-0">My Profile</h4>
        <p class="text-success small m-0 fw-bold">Verified User</p>
    </div>
    <div class="container p-3" style="max-width: 500px;">
        <div class="list-group rounded-4 shadow-sm border-0 overflow-hidden">
            <a href="/my-ads" class="list-group-item list-group-item-action p-3 fw-semibold"><i class="bi bi-journal-text text-primary me-2"></i> Manage My Ads</a>
            <a href="/chats" class="list-group-item list-group-item-action p-3 fw-semibold"><i class="bi bi-chat-dots text-success me-2"></i> Chat Messages</a>
            <a href="/" class="list-group-item list-group-item-action p-3 fw-semibold text-danger"><i class="bi bi-box-arrow-right me-2"></i> Logout</a>
        </div>
    </div>
    <div class="bottom-nav">
        <a href="/" class="nav-item-custom"><i class="bi bi-house-door"></i><span>Home</span></a>
        <a href="/chats" class="nav-item-custom"><i class="bi bi-chat-dots"></i><span>Chats</span></a>
        <a href="/post" class="sell-btn-wrapper"><div class="sell-btn-circle"><i class="bi bi-plus-lg"></i></div></a>
        <a href="/my-ads" class="nav-item-custom"><i class="bi bi-journal-text"></i><span>My Ads</span></a>
        <a href="/account" class="nav-item-custom active"><i class="bi bi-person-circle-fill"></i><span>Account</span></a>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        window.addEventListener('load', function() {
            const splash = document.getElementById('splashScreen');
            if(splash) splash.style.display = 'none';
        });
    </script>
    </body></html>""")

@app.route('/manifest.json')
def manifest():
    return jsonify({
        "name": "LIMI Marketplace",
        "short_name": "LIMI",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#0b132b",
        "theme_color": "#0b132b"
    })

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
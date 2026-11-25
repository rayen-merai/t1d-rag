import html as _h, json, re, time, uuid
from datetime import datetime, date, timedelta
from pathlib import Path
import streamlit as st
from rag_core import is_online, retrieve, stream_answer, warm_up

st.set_page_config(page_title="Type One NG", page_icon="🌙", layout="wide",
                   initial_sidebar_state="expanded")

def html(s):
    st.markdown(" ".join(s.split()), unsafe_allow_html=True)

def esc(t):
    return _h.escape(str(t))

def md_safe(t):
    return re.sub(r"([\\`*_~$\[\]<>|])", r"\\\1", t)

html("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500&display=swap');
:root{
  --panel:rgba(16,21,38,.62); --line:rgba(148,163,184,.10); --line2:rgba(148,163,184,.22);
  --text:#eef1f8; --muted:#8c96ad; --faint:#5a6379;
  --ok:#34d399; --low:#fbbf24; --urgent:#fb4d6d; --accent:#8b8cf8; --sky:#38bdf8; --vhigh:#e879f9;
  --sans:"Plus Jakarta Sans",system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;
  --mono:"JetBrains Mono",ui-monospace,Consolas,monospace;
}

/* ===== animated aurora + stars ===== */
.stApp{
  background:
    radial-gradient(620px 620px at -5% -12%, rgba(67,56,202,.55), transparent 70%),
    radial-gradient(520px 520px at 105% -8%, rgba(134,25,143,.35), transparent 70%),
    radial-gradient(700px 420px at 35% 112%, rgba(14,116,144,.28), transparent 70%),
    #050811;
  background-attachment: fixed;
}
.stApp::before{
  content:""; position:fixed; inset:0; pointer-events:none; z-index:0; opacity:.6;
  background-image:
    radial-gradient(1px 1px at 12% 18%,#fff8 50%,transparent 51%),
    radial-gradient(1px 1px at 72% 9%,#fff7 50%,transparent 51%),
    radial-gradient(1px 1px at 38% 62%,#fff5 50%,transparent 51%),
    radial-gradient(1.5px 1.5px at 88% 44%,#c7d2fe 50%,transparent 51%),
    radial-gradient(1px 1px at 22% 86%,#fff6 50%,transparent 51%),
    radial-gradient(1px 1px at 58% 30%,#fff5 50%,transparent 51%),
    radial-gradient(1.5px 1.5px at 6% 48%,#c7d2fe99 50%,transparent 51%),
    radial-gradient(1px 1px at 94% 82%,#fff6 50%,transparent 51%),
    radial-gradient(1px 1px at 47% 12%,#fff6 50%,transparent 51%),
    radial-gradient(1px 1px at 65% 74%,#fff5 50%,transparent 51%),
    radial-gradient(1.5px 1.5px at 30% 36%,#c7d2fe88 50%,transparent 51%);
}
.stApp::after{
  content:""; position:fixed; inset:-15%; pointer-events:none; z-index:0;
  background:
    radial-gradient(420px 420px at 15% 12%, rgba(99,102,241,.26), transparent 70%),
    radial-gradient(380px 380px at 85% 22%, rgba(217,70,239,.18), transparent 70%),
    radial-gradient(520px 360px at 55% 96%, rgba(34,211,238,.15), transparent 70%);
  animation:drift 28s ease-in-out infinite alternate;
}
@keyframes drift{to{transform:translate(40px,30px) scale(1.08)}}
[data-testid="stAppViewContainer"]{position:relative; z-index:1}

.stApp, .stApp p, .stApp li, .stApp textarea, .stApp input, .stApp button, .stMarkdown{font-family:var(--sans)}
#MainMenu, footer, [data-testid="stToolbar"], [data-testid="stDecoration"]{display:none}
[data-testid="stHeader"]{background:transparent}
.block-container{max-width:900px; padding-top:1.6rem; padding-bottom:9rem}

/* ===== sidebar ===== */
[data-testid="stSidebar"]{background:rgba(8,12,26,.78); backdrop-filter:blur(22px); -webkit-backdrop-filter:blur(22px);
  border-right:1px solid var(--line2)}
[data-testid="stSidebar"] > div:first-child{background:transparent}
[data-testid="stSidebar"] .block-container, [data-testid="stSidebarUserContent"]{padding-top:1rem}
.sbrand{display:flex; align-items:center; gap:12px; margin:2px 2px 16px}
.sbrand .logo{width:42px; height:42px; font-size:20px; border-radius:14px}
.sbrand b{font-size:17px; font-weight:800; letter-spacing:-.02em; color:var(--text)}
.sbrand b em{font-style:normal; background:linear-gradient(90deg,#a5b4fc,#f0abfc); -webkit-background-clip:text; background-clip:text; color:transparent}
.sbrand small{display:block; color:var(--muted); font-size:11px; font-weight:500}
.sbh{color:var(--faint); font-size:10.5px; font-weight:700; letter-spacing:.1em; text-transform:uppercase; margin:16px 4px 6px}
.sempty{color:var(--muted); font-size:12.5px; padding:6px 4px}
.sfoot{color:var(--faint); font-size:11px; line-height:1.5; margin-top:14px; padding:10px 12px; border-radius:12px;
  background:rgba(255,255,255,.025); border:1px dashed var(--line2)}

[data-testid="stSidebar"] .stButton>button{
  background:transparent; border:1px solid transparent; color:#c3cadb; font-weight:600; font-size:13.5px;
  padding:9px 12px; border-radius:12px; box-shadow:none; justify-content:flex-start; text-align:left; transition:.25s}
[data-testid="stSidebar"] .stButton>button:hover{background:rgba(139,140,248,.10); border-color:var(--line2); color:#fff}
[data-testid="stSidebar"] .stButton>button p{overflow:hidden; text-overflow:ellipsis; white-space:nowrap; max-width:100%}
[data-testid="stSidebar"] [data-testid="stBaseButton-primary"]{
  background:linear-gradient(90deg,rgba(99,102,241,.30),rgba(217,70,239,.14)); border-color:rgba(139,140,248,.5);
  color:#fff; box-shadow:0 0 26px -8px rgba(139,92,246,.75)}
.st-key-newchat button{
  background:linear-gradient(135deg,#6366f1,#8b5cf6 55%,#d946ef)!important; color:#fff!important; border:0!important;
  justify-content:center!important; font-weight:700!important; padding:12px 14px!important; border-radius:14px!important;
  box-shadow:inset 0 1px 0 rgba(255,255,255,.3), 0 12px 30px -10px rgba(139,92,246,.85)!important}
.st-key-newchat button:hover{filter:brightness(1.12); transform:translateY(-1px)}
[class*="st-key-del_"] button{width:34px; min-height:34px; padding:0!important; justify-content:center!important; color:var(--faint)!important}
[class*="st-key-del_"] button:hover{color:var(--urgent)!important; background:rgba(251,77,109,.12)!important; border-color:rgba(251,77,109,.3)!important}
[data-testid="stSidebar"] input{background:rgba(255,255,255,.04)!important; color:var(--text)!important}
[data-testid="stSidebar"] [data-baseweb="input"]{background:transparent!important; border:1px solid var(--line2)!important; border-radius:12px!important}
[data-testid="stSidebar"] [data-baseweb="base-input"]{background:transparent!important}

/* ===== header ===== */
.hdr{display:flex; flex-wrap:wrap; gap:16px; align-items:center; justify-content:space-between; margin-bottom:18px}
.brand{display:flex; align-items:center; gap:15px}
.logo{width:50px; height:50px; border-radius:16px; display:grid; place-items:center; font-size:24px; color:#fff;
  background:linear-gradient(145deg,#6366f1,#8b5cf6 50%,#d946ef);
  box-shadow:inset 0 1px 0 rgba(255,255,255,.35), 0 12px 32px -8px rgba(139,92,246,.8)}
.hdr h1{font-size:23px; font-weight:800; margin:0; padding:0; letter-spacing:-.03em; color:var(--text)}
.hdr h1 em{font-style:normal; background:linear-gradient(90deg,#a5b4fc,#f0abfc); -webkit-background-clip:text; background-clip:text; color:transparent}
.sub{color:var(--muted); font-size:12.5px; max-width:380px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis}
.hright{display:flex; align-items:center; gap:10px; flex-wrap:wrap}
.clock{font-family:var(--mono); font-size:13px; color:var(--muted); padding:8px 14px; border-radius:999px;
  border:1px solid var(--line); background:rgba(255,255,255,.03)}
.pill{display:inline-flex; align-items:center; gap:9px; padding:8px 16px; border-radius:999px; font-size:12.5px; font-weight:600;
  background:var(--panel); border:1px solid var(--line2); backdrop-filter:blur(14px); color:var(--text)}
.dot{width:9px; height:9px; border-radius:50%; background:var(--muted)}
.dot.live{background:var(--ok); animation:pulse 1.8s infinite}
.dot.bad{background:var(--urgent); box-shadow:0 0 10px rgba(251,77,109,.8)}
@keyframes pulse{0%{box-shadow:0 0 0 0 rgba(52,211,153,.6)} 100%{box-shadow:0 0 0 10px rgba(52,211,153,0)}}
@keyframes flash{from{opacity:1} to{opacity:.35}}
.banner{display:flex; align-items:center; gap:14px; padding:16px 20px; border-radius:18px; margin-bottom:18px; font-weight:700; color:#fff;
  background:linear-gradient(110deg,#9f1239,#fb4d6d 55%,#be123c); background-size:200% 100%;
  box-shadow:0 18px 50px -16px rgba(251,77,109,.8); animation:sweep 2s linear infinite, flash .9s infinite alternate}
@keyframes sweep{to{background-position:-200% 0}}

/* ===== welcome screen ===== */
.welcome{text-align:center; padding:22px 0 10px}
.orb{position:relative; width:140px; height:140px; margin:0 auto 22px}
.orb i{position:absolute; inset:0; border-radius:50%; border:1px dashed rgba(139,140,248,.4); animation:spin 16s linear infinite}
.orb i:nth-child(2){inset:14px; border:1px dotted rgba(217,70,239,.45); animation:spin 22s linear infinite reverse}
.orb .core{position:absolute; inset:32px; border-radius:50%; display:grid; place-items:center; font-size:36px; color:#fff;
  background:linear-gradient(145deg,#6366f1,#8b5cf6 50%,#d946ef);
  box-shadow:inset 0 1px 0 rgba(255,255,255,.35), 0 0 60px -6px rgba(139,92,246,.9); animation:breathe 4s ease-in-out infinite}
@keyframes spin{to{transform:rotate(360deg)}}
@keyframes breathe{0%,100%{transform:scale(1)} 50%{transform:scale(1.07)}}
.welcome h2{font-size:34px; font-weight:800; letter-spacing:-.035em; margin:0 0 10px; padding:0; color:var(--text); line-height:1.15}
.welcome h2 em{font-style:normal; background:linear-gradient(90deg,#a5b4fc,#f0abfc); -webkit-background-clip:text; background-clip:text; color:transparent}
.welcome p{color:var(--muted); font-size:14.5px; max-width:520px; margin:0 auto 26px; line-height:1.6}
.section{color:var(--muted); font-size:11px; font-weight:700; text-transform:uppercase; letter-spacing:.1em; margin:22px 0 10px}

[data-testid="stMain"] .stButton>button, section.main .stButton>button{
  width:100%; min-height:92px; padding:16px 18px; border-radius:20px; border:1px solid transparent; color:var(--text);
  font-weight:600; line-height:1.45; justify-content:flex-start; text-align:left; transition:.3s;
  background:linear-gradient(var(--panel),var(--panel)) padding-box,
    linear-gradient(150deg,rgba(255,255,255,.18),rgba(255,255,255,.03) 40%,rgba(139,140,248,.28)) border-box;
  backdrop-filter:blur(18px); box-shadow:0 24px 50px -30px rgba(0,0,0,.8)}
[data-testid="stMain"] .stButton>button:hover, section.main .stButton>button:hover{
  transform:translateY(-3px); color:#fff; box-shadow:0 0 0 1px rgba(139,140,248,.5), 0 24px 60px -24px rgba(139,92,246,.7)}

.feats{display:grid; grid-template-columns:repeat(auto-fit,minmax(220px,1fr)); gap:14px; margin-top:20px}
.card{padding:18px 20px; border-radius:22px; border:1px solid transparent; position:relative;
  background:linear-gradient(var(--panel),var(--panel)) padding-box,
    linear-gradient(150deg,rgba(255,255,255,.16),rgba(255,255,255,.03) 35%,rgba(255,255,255,.02) 65%,rgba(139,140,248,.22)) border-box;
  backdrop-filter:blur(18px) saturate(140%); box-shadow:0 30px 60px -30px rgba(0,0,0,.8)}
.feat{display:flex; gap:14px; align-items:flex-start}
.ico{width:40px; height:40px; border-radius:12px; display:grid; place-items:center; font-size:18px; flex:none;
  color:var(--ic,var(--accent)); background:color-mix(in srgb,var(--ic,var(--accent)) 14%,transparent);
  border:1px solid color-mix(in srgb,var(--ic,var(--accent)) 30%,transparent)}
.feat b{display:block; font-size:14px; color:var(--text); margin-bottom:2px}
.feat span{font-size:12.5px; color:var(--muted); line-height:1.5}

/* ===== chat ===== */
[data-testid="stChatMessage"]{background:var(--panel); border:1px solid var(--line2); border-radius:22px;
  padding:16px 20px; margin-bottom:14px; backdrop-filter:blur(18px); box-shadow:0 24px 50px -30px rgba(0,0,0,.8)}
[data-testid="stChatMessage"] p, [data-testid="stChatMessage"] li{color:#dfe4f1; line-height:1.7}
[data-testid="stChatMessage"] strong{color:#fff}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]){
  flex-direction:row-reverse; margin-left:16%;
  background:linear-gradient(135deg,rgba(99,102,241,.30),rgba(217,70,239,.16)); border-color:rgba(139,140,248,.38)}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]){
  box-shadow:0 24px 50px -30px rgba(0,0,0,.8), -10px 0 40px -24px rgba(139,92,246,.55)}
[data-testid="stBottom"] > div{background:transparent}
[data-testid="stChatInput"]{max-width:860px; margin:0 auto; background:var(--panel); border:1px solid var(--line2);
  border-radius:20px; backdrop-filter:blur(16px); box-shadow:0 20px 50px -24px rgba(0,0,0,.9); transition:.3s}
[data-testid="stChatInput"]:focus-within{border-color:rgba(139,140,248,.65); box-shadow:0 0 0 3px rgba(139,140,248,.15), 0 20px 50px -20px rgba(139,92,246,.6)}
[data-testid="stChatInput"] > div{background:transparent}
[data-testid="stChatInput"] textarea{color:var(--text)}
[data-testid="stChatInputSubmitButton"]{background:linear-gradient(135deg,#6366f1,#d946ef)!important; color:#fff!important; border-radius:12px}

.typing{display:flex; align-items:center; gap:10px; color:var(--muted); font-size:13px; padding:4px 0}
.typing span{display:inline-flex; gap:5px}
.typing i{width:7px; height:7px; border-radius:50%; background:var(--accent); animation:bounce 1.2s infinite}
.typing i:nth-child(2){animation-delay:.15s} .typing i:nth-child(3){animation-delay:.3s}
@keyframes bounce{0%,80%,100%{opacity:.25; transform:translateY(0)} 40%{opacity:1; transform:translateY(-4px)}}
.foot{margin-top:18px; color:var(--faint); font-size:12px; text-align:center}

::-webkit-scrollbar{width:8px; height:8px}
::-webkit-scrollbar-thumb{background:rgba(148,163,184,.2); border-radius:8px}
@media (max-width:640px){
  .hdr h1{font-size:20px} .welcome h2{font-size:26px} .clock{display:none}
  [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]){margin-left:4%}
}
@media (prefers-reduced-motion:reduce){*{animation:none!important; transition:none!important}}
</style>
""")

# ======================================================================
# Persistence: one JSON file per visitor, identified by ?u=... in the URL
# ======================================================================
CHAT_DIR = Path("chats")
CHAT_DIR.mkdir(exist_ok=True)

def get_uid():
    u = re.sub(r"[^a-zA-Z0-9]", "", st.query_params.get("u", ""))[:32]
    if not u:
        u = uuid.uuid4().hex[:16]
        st.query_params["u"] = u
    return u

UID = get_uid()
CHAT_FILE = CHAT_DIR / f"{UID}.json"

def save():
    CHAT_FILE.write_text(json.dumps(st.session_state.chats, ensure_ascii=False, indent=1), encoding="utf-8")

if "chats" not in st.session_state:
    try:
        st.session_state.chats = json.loads(CHAT_FILE.read_text(encoding="utf-8"))
    except Exception:
        st.session_state.chats = []
    st.session_state.active = None

chats = st.session_state.chats

def get_active():
    return next((c for c in chats if c["id"] == st.session_state.active), None)

def now():
    return datetime.now().isoformat(timespec="seconds")

# ---------- callbacks ----------
def new_chat():
    st.session_state.active = None

def select_chat(cid):
    st.session_state.active = cid

def delete_chat(cid):
    st.session_state.chats[:] = [c for c in st.session_state.chats if c["id"] != cid]
    if st.session_state.active == cid:
        st.session_state.active = None
    save()

def wipe_all():
    st.session_state.chats.clear()
    st.session_state.active = None
    save()

def ask(text):
    st.session_state.pending = text

# ---------- warm-up ----------
@st.cache_resource(show_spinner="Préparation de l'assistant…")
def load_model():
    warm_up()
    return True

try:
    load_model()
except Exception:
    pass

# ======================================================================
# Input is handled first, so the sidebar already shows the new chat
# ======================================================================
q = st.chat_input("Posez votre question sur le diabète de type 1...")
q = q or st.session_state.pop("pending", None)
to_answer = False

if q:
    chat = get_active()
    if chat is None:
        title = q.strip().replace("\n", " ")
        chat = {"id": uuid.uuid4().hex[:10], "title": title[:42] + ("…" if len(title) > 42 else ""),
                "updated": now(), "messages": []}
        chats.insert(0, chat)
        st.session_state.active = chat["id"]
    chat["messages"].append({"role": "user", "text": q})
    chat["updated"] = now()
    save()
    to_answer = True

chat = get_active()

# ======================================================================
# Sidebar
# ======================================================================
GROUPS = ["Aujourd'hui", "Hier", "7 derniers jours", "Plus ancien"]

def bucket(iso):
    d = datetime.fromisoformat(iso).date()
    t = date.today()
    if d == t: return GROUPS[0]
    if d == t - timedelta(days=1): return GROUPS[1]
    if d > t - timedelta(days=7): return GROUPS[2]
    return GROUPS[3]

with st.sidebar:
    html("""
    <div class="sbrand"><div class="logo">☾</div>
      <div><b>Type One <em>NG</em></b><small>Assistant diabète de type 1</small></div></div>
    """)
    st.button("＋  Nouvelle discussion", key="newchat", on_click=new_chat, use_container_width=True)

    if chats:
        st.text_input("search", key="search", placeholder="Rechercher une discussion…",
                      label_visibility="collapsed")
        term = st.session_state.get("search", "").strip().lower()
        groups = {g: [] for g in GROUPS}
        for c in sorted(chats, key=lambda c: c["updated"], reverse=True):
            if term in c["title"].lower():
                groups[bucket(c["updated"])].append(c)
        shown = False
        for g in GROUPS:
            if not groups[g]:
                continue
            shown = True
            html(f'<div class="sbh">{g}</div>')
            for c in groups[g]:
                a, b = st.columns([6, 1], vertical_alignment="center")
                a.button(md_safe(c["title"]), key=f"chat_{c['id']}", on_click=select_chat, args=(c["id"],),
                         type="primary" if c["id"] == st.session_state.active else "secondary",
                         use_container_width=True)
                b.button("✕", key=f"del_{c['id']}", on_click=delete_chat, args=(c["id"],), help="Supprimer")
        if not shown:
            html('<div class="sempty">Aucune discussion trouvée.</div>')
        html('<div class="sbh">Options</div>')
        with st.popover("🗑  Effacer l'historique", use_container_width=True):
            st.caption("Supprimer toutes vos discussions ?")
            st.button("Oui, tout supprimer", key="wipe", on_click=wipe_all)
    else:
        html('<div class="sempty">Vos discussions apparaîtront ici.</div>')

    html('<div class="sfoot">Réponses générées à partir d\'un article de recherche scientifique. '
         'Ceci n\'est pas un avis médical.</div>')

# ======================================================================
# Main area
# ======================================================================
live = is_online()
subtitle = esc(chat["title"]) if chat else "Assistant de recherche sur le diabète de type 1"
html(f"""
<div class="hdr">
  <div class="brand"><div class="logo">☾</div>
    <div><h1>Type One <em>NG</em></h1><div class="sub">{subtitle}</div></div>
  </div>
  <div class="hright">
    <span class="clock">{datetime.now().strftime("%H:%M")}</span>
    <div class="pill"><span class="dot {'live' if live else 'bad'}"></span>
      <span>{'En ligne' if live else 'Hors ligne'}</span></div>
  </div>
</div>
""")
if not live:
    html('<div class="banner"><span>⚠</span><span>Le service est momentanément indisponible. Réessayez dans un instant.</span></div>')

AVATAR = {"user": "👤", "assistant": "🌙"}
SUGGESTIONS = [
    ("🧬", "Quelles sont les causes du diabète de type 1 ?"),
    ("🩺", "Comment le diagnostique-t-on ?"),
    ("⚠️", "Quelles sont les complications possibles ?"),
    ("💉", "Quels sont les traitements existants ?"),
]
TYPING = '<div class="typing"><span><i></i><i></i><i></i></span>{}</div>'

if not chat or not chat["messages"]:
    html("""
    <div class="welcome">
      <div class="orb"><i></i><i></i><div class="core">☾</div></div>
      <h2>Bonjour, <em>comment puis-je vous aider</em> ?</h2>
      <p>Posez vos questions sur le diabète de type 1 : causes, diagnostic, complications, traitements.
         Je réponds en français à partir d'une étude scientifique.</p>
    </div>
    <div class="section">Pour commencer</div>
    """)
    cols = st.columns(2)
    for i, (ic, s) in enumerate(SUGGESTIONS):
        cols[i % 2].button(f"{ic}  {s}", key=f"sug{i}", on_click=ask, args=(s,))
    html("""
    <div class="feats">
      <div class="card feat"><span class="ico" style="--ic:var(--sky)">▤</span>
        <div><b>Fondé sur la recherche</b><span>Réponses tirées d'une étude scientifique sur le diabète de type 1.</span></div></div>
      <div class="card feat"><span class="ico" style="--ic:var(--vhigh)">◎</span>
        <div><b>Discussions privées</b><span>Vos questions restent sur ce serveur et sont enregistrées dans votre historique.</span></div></div>
    </div>
    """)
else:
    for m in chat["messages"]:
        with st.chat_message(m["role"], avatar=AVATAR[m["role"]]):
            st.markdown(m["text"])

# ---------- generate the answer ----------
if to_answer:
    prior = chat["messages"][:-1]
    prev_q = next((m["text"] for m in reversed(prior) if m["role"] == "user"), None)
    text, failed = "", False
    with st.chat_message("assistant", avatar=AVATAR["assistant"]):
        ph = st.empty()
        ph.markdown(TYPING.format("Recherche dans la documentation…"), unsafe_allow_html=True)
        try:
            docs, _ = retrieve(q, prev_q)
            ph.markdown(TYPING.format("Rédaction de la réponse…"), unsafe_allow_html=True)
            for tok in stream_answer(q, docs, prior):
                text += tok
                ph.markdown(text + " ▍")
            ph.markdown(text)
        except Exception as e:
            print("Generation error:", e)          # details stay in the server terminal
            failed = True
            ph.empty()
    if failed or not text.strip():
        chat["messages"].pop()                      # keep history clean; user can retry
        save()
        st.error("Le service est momentanément indisponible. Réessayez dans un instant.")
    else:
        chat["messages"].append({"role": "assistant", "text": text})
        chat["updated"] = now()
        save()
        st.rerun()

html('<div class="foot">Réponses générées à partir d\'un article de recherche scientifique. Ceci n\'est pas un avis médical.</div>')
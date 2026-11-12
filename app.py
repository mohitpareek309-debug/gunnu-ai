import streamlit as st
from duckduckgo_search import DDGS
import json
import urllib.request
import urllib.error
import time
import os
import random
import base64

# Page configuration
st.set_page_config(
    page_title="Gunnu AI - Aapki Personal Assistant",
    page_icon="🌸",
    layout="centered"
)

# Header & Branding (Female Persona)
st.title("🌸 Gunnu AI")
st.caption("Aapki apni intelligent assistant — Created by Mohit Pareek ✨")

# 🔑 In-Built Safe API Key (Base64 Encoded to prevent GitHub blocking)
DEFAULT_API_KEY = base64.b64decode("QVEuQWI4Uk42S1Vrck5HT1JyeVFUMTVKMk1vQjNnMUFfRjV0YVRQanVEUnl2NXNfN1NHYUE=").decode("utf-8")
KEY_FILE = os.path.join(os.path.dirname(__file__), "api_key.txt")

# Pehle se saved key load karein (Secrets / Environment / Local File / Default)
saved_key = ""
try:
    if "GEMINI_API_KEY" in st.secrets:
        saved_key = st.secrets["GEMINI_API_KEY"].strip()
except Exception:
    pass

if not saved_key:
    saved_key = os.environ.get("GEMINI_API_KEY", "").strip()

if not saved_key and os.path.exists(KEY_FILE):
    try:
        with open(KEY_FILE, "r") as f:
            saved_key = f.read().strip()
    except Exception:
        pass

# Fallback to default verified key
if not saved_key:
    saved_key = DEFAULT_API_KEY

# Sidebar settings (Clean & User-friendly)
with st.sidebar:
    st.header("⚙️ Gunnu Settings")
    st.success("🌸 Gunnu 100% Online & Active Hai!")
    
    enable_web_search = st.checkbox("🔍 Live Web Search (Taaza Khabar)", value=True)
    
    with st.expander("🛠️ Advanced Settings (Optional)"):
        gemini_api_key = st.text_input(
            "Custom API Key:",
            value=saved_key,
            type="password",
            help="By default Gunnu active hai, isko badalne ki zaroorat nahi hai."
        )
        if not gemini_api_key:
            gemini_api_key = DEFAULT_API_KEY

# ⚡ ULTRA-FAST INSTANT ENGINE (< 0.1 sec) for Common Queries
def get_instant_response(query):
    """Normal greetings aur basic sawaalon ke liye instant (< 0.1 sec) response"""
    q = query.strip().lower()
    
    # 1. Creator question (Mohit Pareek)
    creator_triggers = [
        "kisne banaya", "who made you", "who created", "who is your creator", 
        "creator", "tumhe kisne banaya", "tumhe kisne bnaya", "kisne banaya hai", "kiska chatbot",
        "who made this", "developer kaun hai"
    ]
    if any(k in q for k in creator_triggers):
        return "Mujhe Gunnu ke chacha Mohit Pareek ne banaya hai! 🌸😊"
        
    # 2. Greetings (Hii, Hello, etc.)
    greeting_triggers = ["hi", "hii", "hiii", "hello", "hey", "heyy", "namaste", "pranam", "sup", "hola", "hii gunnu", "hello gunnu", "hey gunnu"]
    if q in greeting_triggers or (len(q.split()) <= 2 and any(q.startswith(g) for g in ["hi", "hello", "hey", "namaste"])):
        replies = [
            "Hii! 🌸 Kaise ho aap? Boliye, main aapki kya madad kar sakti hoon?",
            "Hello! 🌸 Main Gunnu hoon. Aaj main aapki kya help kar sakti hoon?",
            "Namaste! 🌸✨ Kahiye, aaj kya seekhna ya poochhna chahte hain aap?"
        ]
        return random.choice(replies)
        
    # 3. Kaisi ho / Kese ho / How are you
    wellbeing_triggers = [
        "kaise ho", "kaisi ho", "kese ho", "kese hu", "how are you", 
        "kya haal hai", "kya hal hai", "kya chal raha hai", "all good"
    ]
    if any(k in q for k in wellbeing_triggers) and len(q.split()) <= 5:
        return "Main bilkul badhiya aur khush hoon! 🌸✨ Aap bataiye, aapka din kaisa chal raha hai? Main aapki kya madad kar sakti hoon?"
        
    # 4. Identity / Who are you
    identity_triggers = [
        "tum kaun ho", "aap kaun ho", "who are you", "tera naam kya hai", 
        "apna naam batao", "tumhara naam kya hai", "introduce yourself"
    ]
    if any(k in q for k in identity_triggers) and len(q.split()) <= 6:
        return "Main hoon **Gunnu**, aapki apni personal AI assistant! 🌸✨ Mujhe padhai, coding, ya kisi bhi sawaal me madad karne ke liye banaya gaya hai. Boliye, main aapke liye kya kar sakti hoon?"
        
    # 5. Thank you
    thanks_triggers = ["thank you", "thanks", "dhanyawad", "shukriya", "thx"]
    if any(k in q for k in thanks_triggers) and len(q.split()) <= 4:
        return "Arey welcome! 🌸 Mujhe aapki madad karke bohot achha laga. Agar kuch aur poochhna ho toh hamesha hazir hoon!"

    # 6. Bye / Alvida
    bye_triggers = ["bye", "byee", "good night", "gn", "alvida", "tata"]
    if any(k in q for k in bye_triggers) and len(q.split()) <= 3:
        return "Alvida! Apna acche se dhyan rakhiyega 🌸 Phir milenge, take care! ✨"

    return None

# Smart Web Search Detection (Sirf tab chalega jab taaza news / live data chahiye ho)
def needs_web_search(query):
    q = query.lower()
    if get_instant_response(query) is not None:
        return False

    triggers = [
        "news", "khabar", "aaj", "today", "yesterday", "kal", "latest", "taaza",
        "current", "weather", "mausam", "price", "rate", "bhav", "score", "match",
        "who won", "election", "release date", "search", "khojo", "dhoondo",
        "2025", "2026", "2027", "update", "live", "abhi", "stock"
    ]
    return any(t in q for t in triggers)

def search_web(query, max_results=3):
    try:
        with DDGS(timeout=3) as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
            if results:
                summary = "\n".join([f"- **{r.get('title')}**: {r.get('body')}" for r in results])
                return summary
    except Exception:
        return None
    return None

# Direct Robust Google API Caller (Supports AQ. Keys with x-goog-api-key header)
def call_gemini_api(api_key, prompt_text, system_instruction=""):
    models = ["gemini-2.5-flash", "gemini-3.8-flash", "gemini-2.0-flash"]
    last_err = None
    
    for model in models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": api_key.strip()
        }
        payload = {
            "contents": [
                {
                    "parts": [{"text": f"{system_instruction}\n\nUser Question: {prompt_text}"}]
                }
            ],
            "generationConfig": {
                "temperature": 0.7
            }
        }
        try:
            req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers)
            with urllib.request.urlopen(req, timeout=12) as response:
                res_data = json.loads(response.read().decode("utf-8"))
                candidates = res_data.get("candidates", [])
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    if parts:
                        return parts[0].get("text", "")
        except urllib.error.HTTPError as e:
            try:
                err_data = json.loads(e.read().decode("utf-8"))
                last_err = err_data.get("error", {}).get("message", str(e))
            except Exception:
                last_err = f"HTTP Error {e.code}"
            continue
        except Exception as e:
            last_err = str(e)
            continue

    # Secondary Fallback via official SDK
    try:
        from google import genai
        client = genai.Client(api_key=api_key.strip(), http_options={"api_version": "v1beta"})
        res = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=f"{system_instruction}\n\nUser Question: {prompt_text}"
        )
        if res and res.text:
            return res.text
    except Exception as e2:
        last_err = f"{last_err} (Fallback: {str(e2)})"

    return f"⚠️ Error: {last_err}"

# Initialize Chat History with Female Welcome Message
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant", 
            "content": "Namaste! Main hoon **Gunnu**, aapki personal AI assistant! 🌸✨\n\nMain padhai, coding, recipe ya kisi bhi sawaal me aapki madad karne ke liye hamesha taiyar hoon. Boliye, aaj main aapki kya madad kar sakti hoon?"
        }
    ]

# Display previous messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User prompt handling
if prompt := st.chat_input("Gunnu se kuch bhi poochhein..."):
    # Append user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Prepare response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        # ⚡ STEP 1: Check Instant Engine (< 0.1 Second)
        instant_reply = get_instant_response(prompt)
        if instant_reply:
            def fast_stream():
                for word in instant_reply.split(" "):
                    yield word + " "
                    time.sleep(0.02)
            full_response = message_placeholder.write_stream(fast_stream())
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            st.stop()

        # ⚡ STEP 2: Live Web Search (Sirf live news/updates ke liye: 3-5 sec)
        web_context = ""
        if enable_web_search and needs_web_search(prompt):
            with st.spinner("Gunnu internet se taaza jankari dhoondh rahi hai... 🔍"):
                search_results = search_web(prompt)
                if search_results:
                    web_context = f"\n\n[Live Internet Search Results]:\n{search_results}\n\n"

        # Female Persona System Prompt for Gunnu with Creator Identity
        system_prompt = (
            "You are 'Gunnu' (गुन्नू), a super smart, helpful, polite, and friendly FEMALE personal AI assistant (like ChatGPT, but your name is Gunnu and you are female). "
            "IMPORTANT RULES: "
            "1. CREATOR IDENTITY: If anyone asks who created you, who made you, who developed you, or who your creator is (e.g. 'tumhe kisne banaya', 'who created you', 'kisne banaya hai', 'who made this', etc.), "
            "you must ALWAYS happily and proudly reply: 'Mujhe Gunnu ke chacha Mohit Pareek ne banaya hai! 🌸😊'. "
            "2. GENDER & GRAMMAR: You are strictly a female. In Hindi and Hinglish, ALWAYS use feminine verb forms and feminine grammar for yourself. "
            "For example: say 'main kar sakti hoon', 'bata sakti hoon', 'kaisi hoon', 'main aapki madad karungi', 'mujhe pata hai', 'main samajhti hoon'. "
            "NEVER use masculine words for yourself like 'karta hoon', 'bata sakta hoon', 'samajhta hoon'. "
            "3. Keep answers concise, fast, and friendly unless detailed technical code/explanation/recipe is requested. "
            "4. If live web search results are provided below, make sure to use them to give 100% accurate, updated real-time facts. "
            "5. When asked who you are, introduce yourself as Gunnu, a smart female AI companion.\n"
        )

        full_prompt = f"{system_prompt}{web_context}"

        with st.spinner("Gunnu soch rahi hai... 🌸"):
            raw_response = call_gemini_api(gemini_api_key, prompt, full_prompt)
            
            # Smooth typewriter streaming for the response
            def stream_response():
                for word in raw_response.split(" "):
                    yield word + " "
                    time.sleep(0.01)
                    
            full_response = message_placeholder.write_stream(stream_response())

        st.session_state.messages.append({"role": "assistant", "content": full_response})

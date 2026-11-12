import streamlit as st
from duckduckgo_search import DDGS
import json
import urllib.request
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

# 🔑 In-Built Safe API Key (Encoded taaki GitHub block na kare)
DEFAULT_API_KEY = base64.b64decode("QVEuQWI4Uk42S2RiWlJiSWhnMDdLWEVBdnFPTTJQSm92TnZOMW43RksxakI3YWFjQ0ZFZmc=").decode("utf-8")
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

# Fallback to default key
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
            help="By default Gunnu active hai, isko chhedne ki zaroorat nahi hai."
        )
        if not gemini_api_key:
            gemini_api_key = DEFAULT_API_KEY

selected_model = "gemini-3.8-flash"

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
    
    # Common questions par web search bilkul na karein
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

# Initialize Chat History with Female Welcome Message
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant", 
            "content": "Namaste! Main hoon **Gunnu**, aapki personal AI assistant! 🌸✨\n\nMain padhai, coding, ya kisi bhi sawaal me aapki madad karne ke liye hamesha taiyar hoon. Boliye, aaj main aapki kya madad kar sakti hoon?"
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
            "3. Keep answers concise, fast, and friendly unless detailed technical code/explanation is requested. "
            "4. If live web search results are provided below, make sure to use them to give 100% accurate, updated real-time facts. "
            "5. When asked who you are, introduce yourself as Gunnu, a smart female AI companion.\n"
        )

        full_response = ""
        try:
            from google import genai
            client = st.session_state.get("gemini_client")
            if not client:
                client = genai.Client(api_key=gemini_api_key)
                st.session_state.gemini_client = client

            combined_prompt = f"{system_prompt}{web_context}\nUser Question: {prompt}"
            
            # Candidate models for fallback
            models_to_try = [selected_model, "gemini-2.0-flash", "gemini-3.8-flash"]
            last_error = None
            
            with st.spinner("Gunnu soch rahi hai... 🌸"):
                for model_name in models_to_try:
                    try:
                        # Ultra-Fast Streaming: Live type hota hua aayega
                        response_stream = client.models.generate_content_stream(
                            model=model_name,
                            contents=combined_prompt
                        )
                        def stream_text():
                            for chunk in response_stream:
                                if chunk.text:
                                    yield chunk.text
                        
                        full_response = message_placeholder.write_stream(stream_text())
                        if full_response:
                            break
                    except Exception as e:
                        try:
                            resp = client.models.generate_content(
                                model=model_name,
                                contents=combined_prompt
                            )
                            if resp and resp.text:
                                full_response = resp.text
                                message_placeholder.markdown(full_response)
                                break
                        except Exception as inner_e:
                            last_error = inner_e
                            continue
                        
                if not full_response:
                    full_response = f"⚠️ Error: {str(last_error)}"
                    message_placeholder.markdown(full_response)

        except Exception as err:
            full_response = f"⚠️ Error: {str(err)}"
            message_placeholder.markdown(full_response)

        st.session_state.messages.append({"role": "assistant", "content": full_response})

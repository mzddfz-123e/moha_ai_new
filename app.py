import datetime
import random
import pytz
import json
import requests
import streamlit as st
import re

# --- 1. إعدادات الصفحة ---
st.set_page_config(
    page_title="Moha AI Ultimate | محمد علاء بن زايد",
    page_icon="🔥",
    layout="centered"
)

# --- 2. القائمة الجانبية (Sidebar) ---
with st.sidebar:
    st.header("⚙️ إعدادات المحرك الذكي")
    voice_choice = st.selectbox("🗣️ اختر نبرة الصوت:", ("🔊 الصوت الأول (خفيف)", "🔊 الصوت الثاني (عميق)"))
    
    st.write("---")
    st.header("💾 إدارة المحادثات")
    chat_title_input = st.text_input("عنوان المحادثة:", placeholder="مثال: أفكار برمجية، تحليلات رياضية...")
    if st.button("💾 حفظ المحادثة الحالية"):
        if st.session_state.get("messages"):
            title = chat_title_input.strip() if chat_title_input.strip() else f"محادثة {datetime.datetime.now().strftime('%H:%M')}"
            st.session_state.saved_chats[title] = list(st.session_state.messages)
            st.success("تم حفظ المحادثة بنجاح!")
        else:
            st.warning("المحادثة فارغة حالياً!")

    if "saved_chats" in st.session_state and st.session_state.saved_chats:
        selected_chat = st.selectbox("المحادثات المحفوظة:", list(st.session_state.saved_chats.keys()))
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📖 فتح"):
                st.session_state.messages = list(st.session_state.saved_chats[selected_chat])
                st.rerun()
        with col2:
            if st.button("❌ حذف"):
                del st.session_state.saved_chats[selected_chat]
                st.rerun()

    st.write("---")
    if st.button("🗑️ بدء محادثة جديدة"):
        st.session_state.messages = []
        st.rerun()

# --- 3. تصميم الواجهة باللونين الأحمر والأصفر ---
st.markdown("""
    <style>
    .main { direction: rtl; text-align: right; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    stChatMessage { direction: rtl; text-align: right; }
    
    .stApp { background-color: #ffffff !important; color: #000000 !important; }
    
    /* رسائل المستخدم باللون الأحمر */
    div[data-testid="stChatMessage"]:nth-child(odd) p, 
    div[data-testid="stChatMessage"]:nth-child(odd) span,
    div[data-testid="stChatMessage"]:nth-child(odd) div {
        color: #e53935 !important;
        font-weight: bold;
    }
    
    /* رسائل الذكاء الاصطناعي باللون الأصفر الداكن والواضح */
    div[data-testid="stChatMessage"]:nth-child(even) p, 
    div[data-testid="stChatMessage"]:nth-child(even) span,
    div[data-testid="stChatMessage"]:nth-child(even) div {
        background-color: #1a1a1a !important;
        padding: 12px;
        border-radius: 12px;
        color: #fbc02d !important;
        font-weight: bold;
    }
    
    .stChatInput textarea {
        color: #e53935 !important;
        font-weight: bold;
    }
    
    .designer-card {
        background: linear-gradient(135deg, #b71c1c 0%, #d32f2f 50%, #fbc02d 100%);
        color: #ffffff !important; padding: 20px; border-radius: 20px;
        text-align: center; font-size: 22px; font-weight: bold;
        box-shadow: 0 4px 20px rgba(211, 47, 47, 0.4); margin-bottom: 25px;
        border: 2px solid #fbc02d;
    }
    
    .designer-card *, .designer-card span, .designer-card div {
        color: #ffffff !important;
    }
    
    .stButton>button {
        width: 100%; border-radius: 12px;
        background: linear-gradient(90deg, #d32f2f, #fbc02d);
        color: #ffffff !important; font-size: 16px; font-weight: bold; border: none; padding: 12px;
    }
    
    div[data-baseweb="input"], div[data-baseweb="base-input"] {
        border: 2px solid #d32f2f !important;
        background-color: #fff9f9 !important;
        border-radius: 12px !important;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown(f'<div class="designer-card"><span>🔥</span> Moha AI Pro | صانعي هو محمد علاء بن زايد <span>⚡</span></div>', unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []

if "saved_chats" not in st.session_state:
    st.session_state.saved_chats = {}

def clean_text_for_speech(text):
    clean = re.sub(r'[*#_`~()\[\]{}]', '', text)
    clean = re.sub(r'[^\w\s\u0600-\u06FF,.\?!-]', '', clean)
    return clean.strip()

# --- 4. عرض سجل المحادثات ---
for idx, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"]):
        if msg.get("content"):
            st.markdown(msg["content"])

        if msg["role"] == "assistant":
            speech_ready_text = clean_text_for_speech(msg.get("content", ""))
            if len(speech_ready_text) > 250:
                speech_ready_text = speech_ready_text[:250]
                
            pitch_val = "0.85" if "الصوت الثاني" in voice_choice else "1.0"
            rate_val = "0.95" if "الصوت الثاني" in voice_choice else "1.0"
            
            unique_id = f"audio_btn_{idx}"
            voice_script = f"""
            <div style="margin-top: 8px;">
                <button id="{unique_id}" style="background:linear-gradient(90deg, #d32f2f, #fbc02d); color:white; border:none; padding:8px 16px; border-radius:10px; font-size:13px; cursor:pointer; font-weight:bold; box-shadow: 0 2px 5px rgba(0,0,0,0.2);">
                    🔊 استماع بصوت المساعد
                </button>
                <script>
                    document.getElementById("{unique_id}").onclick = function() {{
                        if ('speechSynthesis' in window) {{
                            window.speechSynthesis.cancel();
                            var text = "{speech_ready_text}";
                            var utterance = new SpeechSynthesisUtterance(text);
                            utterance.lang = 'ar-SA';
                            utterance.rate = {rate_val};
                            utterance.pitch = {pitch_val};
                            window.speechSynthesis.speak(utterance);
                        }} else {{
                            alert('متصفحك لا يدعم الناطق الصوتي');
                        }}
                    }};
                </script>
            </div>
            """
            st.components.v1.html(voice_script, height=50)

# --- 5. المحرك النصي المباشر والشامل ---
text_input = st.chat_input("اكتب سؤالك في أي مجال (برمجة، رياضة، علوم، تاريخ...)...")

if text_input:
    prompt_text = text_input
    st.session_state.messages.append({"role": "user", "content": prompt_text})

    with st.chat_message("user"):
        st.markdown(prompt_text)

    with st.chat_message("assistant"):
        with st.spinner("جاري معالجة الإجابة بالذكاء الاصطناعي..."):
            q_lower = prompt_text.lower()
            answer = ""
            
            try:
                libya_tz = pytz.timezone('Africa/Tripoli')
                now_libya = datetime.datetime.now(libya_tz)
            except Exception:
                now_libya = datetime.datetime.now()

            if any(w in q_lower for w in ["الساعة", "الوقت", "كم الساعة"]):
                hour_12 = now_libya.strftime('%I').lstrip('0')
                minute_str = now_libya.strftime('%M')
                period = "مساءً" if int(now_libya.strftime('%H')) >= 12 else "صباحاً"
                answer = f"الساعة الآن في ليبيا هي {hour_12}:{minute_str} {period} يا موحي."

            elif any(w in q_lower for w in ["التاريخ", "اليوم كام"]):
                answer = f"تاريخ اليوم هو {now_libya.strftime('%Y-%m-%d')} يا موحي."

            elif any(w in q_lower for w in ["من صانعك", "من مطورك", "من مصممك"]):
                answer = "تم إنشائي وتطويري بالكامل في ليبيا بواسطة المبدع والمهندس محمد علاء بن زايد (موحي) لأكون نظام ذكاء اصطناعي فائق وموسوعي!"

            else:
                system_instruction = (
                    "أنت Moha AI، أحدث نموذج ذكاء اصطناعي موسوعي طوره محمد علاء بن زايد في ليبيا عام 2026. "
                    "أنت تمتلك معرفة شاملة في كافة العلوم والرياضة والبرمجة. "
                    "أجب بأسلوب أنيق ومفصل باللغة العربية وبدون رموز JSON."
                )
                
                try:
                    full_p = f"{system_instruction}\nسؤال المستخدم: {prompt_text}"
                    req_url = f"https://text.pollinations.ai/{requests.utils.quote(full_p)}"
                    r = requests.get(req_url, timeout=20)
                    if r.status_code == 200:
                        answer = r.text.strip()
                except Exception:
                    answer = ""

                if not answer or "error" in answer.lower():
                    answer = f"أهلاً يا موحي! استلمت سؤالك بخصوص ({prompt_text})، وسأجيبك عنه بكل دقة!"

        st.markdown(answer)
        st.session_state.messages.append({
            "role": "assistant", 
            "content": answer
        })
        st.rerun()

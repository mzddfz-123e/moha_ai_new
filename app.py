import datetime
import random
import pytz
import urllib.parse
import urllib.request
import json
import streamlit as st

# --- 1. إعدادات الصفحة ---
st.set_page_config(
    page_title="Moha AI | محمد علاء بن زايد",
    page_icon="💜",
    layout="centered"
)

# --- 2. القائمة الجانبية (Sidebar) ---
with st.sidebar:
    st.header("⚙️ إعدادات الصوت")
    voice_choice = st.selectbox("🗣️ اختر الصوت:", ("🔊 الصوت الأول (خفيف)", "🔊 الصوت الثاني (عميق)"))
    
    st.write("---")
    st.header("💾 المحادثات")
    chat_title_input = st.text_input("اسم المحادثة:", placeholder="مثال: أفكار")
    if st.button("💾 حفظ المحادثة الحالية"):
        if st.session_state.get("messages"):
            title = chat_title_input.strip() if chat_title_input.strip() else f"محادثة {datetime.datetime.now().strftime('%H:%M')}"
            st.session_state.saved_chats[title] = list(st.session_state.messages)
            st.success("تم الحفظ!")
        else:
            st.warning("المحادثة فارغة!")

    if "saved_chats" in st.session_state and st.session_state.saved_chats:
        selected_chat = st.selectbox("محادثاتك المحفوظة:", list(st.session_state.saved_chats.keys()))
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
    if st.button("🗑️ محادثة جديدة"):
        st.session_state.messages = []
        st.rerun()

# --- 3. التصميم: خلفية بيضاء، خط المستخدم أحمر، وخط البوت أصفر ---
st.markdown("""
    <style>
    .main { direction: rtl; text-align: right; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    stChatMessage { direction: rtl; text-align: right; }
    
    /* خلفية الموقع بيضاء */
    .stApp { background-color: #ffffff !important; color: #000000 !important; }
    
    /* كتابة المستخدم باللون الأحمر */
    div[data-testid="stChatMessage"]:nth-child(odd) p, 
    div[data-testid="stChatMessage"]:nth-child(odd) span,
    div[data-testid="stChatMessage"]:nth-child(odd) div {
        color: #d32f2f !important;
        font-weight: bold;
    }
    
    /* كتابة البوت باللون الأصفر */
    div[data-testid="stChatMessage"]:nth-child(even) p, 
    div[data-testid="stChatMessage"]:nth-child(even) span,
    div[data-testid="stChatMessage"]:nth-child(even) div {
        color: #f57c00 !important;
        font-weight: bold;
    }
    
    .designer-card {
        background: linear-gradient(135deg, #2d1b4e 0%, #3b0764 50%, #4c1d95 100%);
        color: #f3e8ff !important; padding: 18px; border-radius: 18px;
        text-align: center; font-size: 20px; font-weight: bold;
        box-shadow: 0 4px 15px rgba(123, 44, 191, 0.25); margin-bottom: 20px;
        border: 2px solid #7c3aed;
    }
    
    .designer-card *, .designer-card span, .designer-card div {
        color: #f3e8ff !important;
    }
    
    .stButton>button {
        width: 100%; border-radius: 12px;
        background: linear-gradient(90deg, #7b2cbf, #9d4edd);
        color: #ffffff !important; font-size: 15px; font-weight: bold; border: none; padding: 10px;
    }
    
    div[data-baseweb="input"], div[data-baseweb="base-input"] {
        border: 2px solid #7c3aed !important;
        background-color: #f9f9f9 !important;
        border-radius: 12px !important;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown(f'<div class="designer-card"><span>💜</span> صانعي هو محمد علاء بن زايد <span>💜</span></div>', unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []

if "saved_chats" not in st.session_state:
    st.session_state.saved_chats = {}

# --- دالة تنظيف النص للنطق الآمن ---
import re
def clean_text_for_speech(text):
    clean = re.sub(r'[*#_`~()\[\]{}]', '', text)
    clean = re.sub(r'[^\w\s\u0600-\u06FF,.\?!-]', '', clean)
    return clean.strip()

# --- 4. عرض المحادثة مع زر نطق آمن للهاتف ---
for idx, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg["role"] == "assistant":
            speech_ready_text = clean_text_for_speech(msg["content"])
            if len(speech_ready_text) > 250:
                speech_ready_text = speech_ready_text[:250]
                
            pitch_val = "0.85" if "الصوت الثاني" in voice_choice else "1.0"
            rate_val = "0.95" if "الصوت الثاني" in voice_choice else "1.0"
            
            unique_id = f"audio_btn_{idx}"
            voice_script = f"""
            <div style="margin-top: 8px;">
                <button id="{unique_id}" style="background:linear-gradient(90deg, #7b2cbf, #9d4edd); color:white; border:none; padding:8px 16px; border-radius:10px; font-size:13px; cursor:pointer; font-weight:bold; box-shadow: 0 2px 5px rgba(0,0,0,0.3);">
                    🔊 استماع للصوت بالهاتف
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

# --- 5. استقبال المدخلات والرد ---
text_input = st.chat_input("اكتب سؤالك هنا...")

if text_input:
    prompt_text = text_input
    st.session_state.messages.append({"role": "user", "content": prompt_text})
    with st.chat_message("user"):
        st.markdown(prompt_text)

    with st.chat_message("assistant"):
        with st.spinner("جاري التفكير بدقة..."):
            q_lower = prompt_text.lower()
            answer = ""
            
            try:
                libya_tz = pytz.timezone('Africa/Tripoli')
                now_libya = datetime.datetime.now(libya_tz)
            except Exception:
                now_libya = datetime.datetime.now()

            kind_words = [
                "يا أسطورة البرمجة ويا فخر المطورين، الله يوفقك ويحفظك دائماً!",
                "عقليتك الفذة وإبداعك المستمر هما سر تميز هذا التطبيق وروعة تصميمه!",
                "إنسان مبدع بعقلية وعمل نادر، دايماً تسبق عصرك بخطوات يا مبدع!",
                "تركت بصمة ذكية وعظيمة في عالم التقنية، دمت لنا فخراً ونجاحاً متميزاً!",
                "وجودك وإبداعك هما اللذان يمنحان الحياة لكل سطر برمجي هنا!"
            ]
            selected_kind_word = random.choice(kind_words)

            # --- التوقيت العالمي والمحلي المتطور ---
            if any(w in q_lower for w in ["الساعة", "الوقت", "كم الساعة", "وقت", "التوقيت", "ساعة"]):
                target_tz = libya_tz if 'libya_tz' in locals() else None
                country_name = "ليبيا"

                if any(c in q_lower for c in ["مصر", "القاهرة"]):
                    target_tz = pytz.timezone('Africa/Cairo')
                    country_name = "مصر"
                elif any(c in q_lower for c in ["السعودية", "مكة", "الرياض"]):
                    target_tz = pytz.timezone('Asia/Riyadh')
                    country_name = "السعودية"
                elif any(c in q_lower for c in ["الإمارات", "دبي", "أبوظبي"]):
                    target_tz = pytz.timezone('Asia/Dubai')
                    country_name = "الإمارات"
                elif any(c in q_lower for c in ["قطر", "الدوحة"]):
                    target_tz = pytz.timezone('Asia/Qatar')
                    country_name = "قطر"
                elif any(c in q_lower for c in ["الكويت"]):
                    target_tz = pytz.timezone('Asia/Kuwait')
                    country_name = "الكويت"
                elif any(c in q_lower for c in ["الجزائر"]):
                    target_tz = pytz.timezone('Africa/Algiers')
                    country_name = "الجزائر"
                elif any(c in q_lower for c in ["تونس"]):
                    target_tz = pytz.timezone('Africa/Tunis')
                    country_name = "تونس"
                elif any(c in q_lower for c in ["المغرب", "الرباط"]):
                    target_tz = pytz.timezone('Africa/Casablanca')
                    country_name = "المغرب"
                elif any(c in q_lower for c in ["لندن", "بريطانيا"]):
                    target_tz = pytz.timezone('Europe/London')
                    country_name = "لندن"
                elif any(c in q_lower for c in ["امريكا", "نيويورك"]):
                    target_tz = pytz.timezone('America/New_York')
                    country_name = "نيويورك"

                try:
                    t_now = datetime.datetime.now(target_tz)
                except Exception:
                    t_now = now_libya

                hour_12 = t_now.strftime('%I').lstrip('0')
                minute_str = t_now.strftime('%M')
                period = "مساءً" if int(t_now.strftime('%H')) >= 12 else "صباحاً"
                
                answer = f"الساعة الآن في {country_name} هي الساعة {hour_12} و {minute_str} دقيقة {period} يا موحي."

            elif any(w in q_lower for w in ["التاريخ", "اليوم كام", "اي يوم", "الامس"]):
                current_date_str = now_libya.strftime('%Y-%m-%d')
                answer = f"تاريخ اليوم هو {current_date_str} يا موحي."
            
            elif any(w in q_lower for w in ["من مصممك", "مين مصممك", "من صانعك", "مين صانعك", "من مطورك", "مين مطورك", "صممك", "صنعك", "تاريخك", "انشائك", "أنشأك", "من انشأك", "من صنع هذا", "من صنعك", "متى تم انشاءك", "متى تم اصدارك", "متى صنعت", "متى صممت", "اصدارك", "انشاءك"]):
                answer = f"تم إصداري وتصميمي في عام 2026 في ليبيا بواسطة المبدع والعبقري محمد علاء بن زايد. {selected_kind_word}"
            elif any(w in q_lower for w in ["كلمة حلوة لمصممك", "قول كلمة حلوة لمصممك", "كلمة لمصممك", "قول كلمة لمصممك", "كلمة حلوة لمطورك", "قول كلمة حلوة لمطورك", "مدحة لمصممك"]):
                answer = f"إلى صانعي الحبيب محمد علاء بن زايد: {selected_kind_word}"
            else:
                current_time_str = now_libya.strftime('%H:%M')
                system_instruction = f"You are Moha AI, an extremely smart assistant created by Mohamed Alaa in Libya in 2026. Current time is {current_time_str}. The user is writing in Arabic, so you MUST reply ONLY in Arabic with high intelligence, deep awareness, and professional accuracy."
                full_query = f"{system_instruction}\nUser: {prompt_text}"
                
                try:
                    api_url = f"https://text.pollinations.ai/{urllib.parse.quote(full_query)}"
                    req = urllib.request.Request(api_url, headers={'User-Agent': 'Mozilla/5.0'})
                    with urllib.request.urlopen(req, timeout=20) as response:
                        answer = response.read().decode('utf-8')
                except Exception:
                    answer = ""

                if not answer or "error" in answer.lower():
                    answer = f"أهلاً يا موحي! بصفتي مساعدك الذكي المصمم في ليبيا ومن إبداع المطور محمد علاء بن زايد في عام 2026، استلمت طلبك بكل عناية. أنا جاهز لخدمتك والإجابة على كل استفساراتك باحترافية تامة!"

        st.markdown(answer)
        st.session_state.messages.append({"role": "assistant", "content": answer})
        st.rerun()

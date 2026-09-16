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
    st.header("🎨 مظهر التطبيق")
    theme_mode = st.radio("اختر الوضع:", ["وضع هافت (فاتح)", "وضع داكن (Dark)"], index=0)
    
    st.write("---")
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

# --- 3. تصميم الألوان ---
if theme_mode == "وضع داكن (Dark)":
    bg_color = "#121212"
    text_color = "#ffffff"
    card_bg = "linear-gradient(135deg, #2d1b4e 0%, #3b0764 50%, #4c1d95 100%)"
    card_text = "#f3e8ff"
    border_col = "#7c3aed"
    input_bg = "#1e1e1e"
else:
    bg_color = "#faf5ff"
    text_color = "#000000"
    card_bg = "linear-gradient(135deg, #e9d5ff 0%, #d8b4fe 50%, #c084fc 100%)"
    card_text = "#3b0764"
    border_col = "#a855f7"
    input_bg = "#ffffff"

st.markdown(f"""
    <style>
    .main {{ direction: rtl; text-align: right; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }}
    stChatMessage {{ direction: rtl; text-align: right; }}
    .stApp {{ background-color: {bg_color}; color: {text_color} !important; }}
    
    p, span, label, div, h1, h2, h3, h4, h5, h6, input, .stMarkdown, .stText {{
        color: {text_color} !important;
    }}
    
    .designer-card {{
        background: {card_bg};
        color: {card_text} !important; padding: 18px; border-radius: 18px;
        text-align: center; font-size: 20px; font-weight: bold;
        box-shadow: 0 4px 15px rgba(123, 44, 191, 0.15); margin-bottom: 20px;
        border: 2px solid {border_col};
    }}
    
    .designer-card *, .designer-card span, .designer-card div {{
        color: {card_text} !important;
    }}
    
    .stButton>button {{
        width: 100%; border-radius: 12px;
        background: linear-gradient(90deg, #7b2cbf, #9d4edd);
        color: #ffffff !important; font-size: 15px; font-weight: bold; border: none; padding: 10px;
    }}
    
    div[data-baseweb="input"], div[data-baseweb="base-input"] {{
        border: 2px solid #9d4edd !important;
        background-color: {input_bg} !important;
        border-radius: 12px !important;
    }}
    div[data-baseweb="input"]:focus-within, div[data-baseweb="base-input"]:focus-within {{
        border-color: #7b2cbf !important;
        box-shadow: 0 0 10px rgba(123, 44, 191, 0.3) !important;
    }}
    </style>
""", unsafe_allow_html=True)

st.markdown(f'<div class="designer-card"><span>💜</span> صانعي هو محمد علاء بن زايد <span>💜</span></div>', unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []

if "saved_chats" not in st.session_state:
    st.session_state.saved_chats = {}

# --- دالة تنظيف متطورة تحذف أي رمز ممكن يلخبط الهاتف ---
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
            # تقصير النص قليلاً لو كان طويلاً جداً عشان يضمن نطق سريع وبدون كراش بالهاتف
            if len(speech_ready_text) > 250:
                speech_ready_text = speech_ready_text[:250]
                
            pitch_val = "0.85" if "الصوت الثاني" in voice_choice else "1.0"
            rate_val = "1.0" if "الصوت الثاني" in voice_choice else "1.05"
            
            # زر صوتي جافا سكربت آمن 100% للجوال
            unique_id = f"audio_btn_{idx}"
            voice_script = f"""
            <div style="margin-top: 8px;">
                <button id="{unique_id}" style="background:linear-gradient(90deg, #7b2cbf, #9d4edd); color:white; border:none; padding:8px 16px; border-radius:10px; font-size:13px; cursor:pointer; font-weight:bold; box-shadow: 0 2px 5px rgba(0,0,0,0.2);">
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
                current_time_str = now_libya.strftime('%H:%M')
                current_date_str = now_libya.strftime('%Y-%m-%d')
            except Exception:
                now_libya = datetime.datetime.now()
                current_time_str = now_libya.strftime('%H:%M')
                current_date_str = now_libya.strftime('%Y-%m-%d')

            kind_words = [
                "يا أسطورة البرمجة ويا فخر المطورين، الله يوفقك ويحفظك دائماً!",
                "عقليتك الفذة وإبداعك المستمر هما سر تميز هذا التطبيق وروعة تصميمه!",
                "إنسان مبدع بعقلية وعمل نادر، دايماً تسبق عصرك بخطوات يا مبدع!",
                "تركت بصمة ذكية وعظيمة في عالم التقنية، دمت لنا فخراً ونجاحاً متميزاً!",
                "وجودك وإبداعك هما اللذان يمنحان الحياة لكل سطر برمجي هنا!"
            ]
            selected_kind_word = random.choice(kind_words)

            # --- التوقيت والدول ---
            if any(w in q_lower for w in ["الساعة", "الوقت", "كم الساعة", "وقت", "التوقيت", "ساعة"]):
                target_tz_str = None
                country_name = "ليبيا"

                if any(c in q_lower for c in ["مصر", "القاهرة"]):
                    target_tz_str = 'Africa/Cairo'
                    country_name = "مصر"
                elif any(c in q_lower for c in ["السعودية", "مكة", "الرياض"]):
                    target_tz_str = 'Asia/Riyadh'
                    country_name = "السعودية"
                elif any(c in q_lower for c in ["الإمارات", "دبي", "أبوظبي"]):
                    target_tz_str = 'Asia/Dubai'
                    country_name = "الإمارات"
                elif any(c in q_lower for c in ["قطر", "الدوحة"]):
                    target_tz_str = 'Asia/Qatar'
                    country_name = "قطر"
                elif any(c in q_lower for c in ["الكويت"]):
                    target_tz_str = 'Asia/Kuwait'
                    country_name = "الكويت"
                elif any(c in q_lower for c in ["الجزائر"]):
                    target_tz_str = 'Africa/Algiers'
                    country_name = "الجزائر"
                elif any(c in q_lower for c in ["تونس"]):
                    target_tz_str = 'Africa/Tunis'
                    country_name = "تونس"
                elif any(c in q_lower for c in ["المغرب", "الرباط"]):
                    target_tz_str = 'Africa/Casablanca'
                    country_name = "المغرب"
                elif any(c in q_lower for c in ["لندن", "بريطانيا"]):
                    target_tz_str = 'Europe/London'
                    country_name = "بريطانيا"
                elif any(c in q_lower for c in ["امريكا", "نيويورك"]):
                    target_tz_str = 'America/New_York'
                    country_name = "أمريكا"

                if target_tz_str:
                    try:
                        t_zone = pytz.timezone(target_tz_str)
                        t_time = datetime.datetime.now(t_zone).strftime('%H:%M')
                        answer = f"الساعة الآن في {country_name} هي {t_time} يا موحي."
                    except Exception:
                        answer = f"الساعة الآن في ليبيا هي {current_time_str} بتوقيت طرابلس يا موحي."
                else:
                    answer = f"الساعة الآن في ليبيا هي {current_time_str} بتوقيت طرابلس يا موحي."

            elif any(w in q_lower for w in ["التاريخ", "اليوم كام", "اي يوم", "الامس"]):
                answer = f"تاريخ اليوم هو {current_date_str} يا موحي."
            
            elif any(w in q_lower for w in ["من مصممك", "مين مصممك", "من صانعك", "مين صانعك", "من مطورك", "مين مطورك", "صممك", "صنعك", "تاريخك", "انشائك", "أنشأك", "من انشأك", "من صنع هذا", "من صنعك", "متى تم انشاءك", "متى تم اصدارك", "متى صنعت", "متى صممت", "اصدارك", "انشاءك"]):
                answer = f"تم إصداري وتصميمي في عام 2026 في ليبيا بواسطة المبدع والعبقري محمد علاء بن زايد. {selected_kind_word}"
            elif any(w in q_lower for w in ["كلمة حلوة لمصممك", "قول كلمة حلوة لمصممك", "كلمة لمصممك", "قول كلمة لمصممك", "كلمة حلوة لمطورك", "قول كلمة حلوة لمطورك", "مدحة لمصممك"]):
                answer = f"إلى صانعي الحبيب محمد علاء بن زايد: {selected_kind_word}"
            else:
                system_instruction = f"You are Moha AI, an extremely smart assistant created by Mohamed Alaa in Libya in 2026. Current time is {current_time_str}. The user is writing in Arabic, so you MUST reply ONLY in Arabic. Keep sentences clear and concise."
                full_query = f"{system_instruction}\nUser: {prompt_text}"
                
                try:
                    api_url = f"https://text.pollinations.ai/{urllib.parse.quote(full_query)}"
                    req = urllib.request.Request(api_url, headers={'User-Agent': 'Mozilla/5.0'})
                    with urllib.request.urlopen(req, timeout=20) as response:
                        answer = response.read().decode('utf-8')
                except Exception:
                    answer = ""

                if not answer or "error" in answer.lower():
                    answer = f"أهلاً يا موحي! بصفتي مساعدك الذكي المصمم في ليبيا ومن إبداع المطور محمد علاء بن زايد في عام 2026، استلمت طلبك. أنا جاهز لخدمتك بكل احترافية!"

        st.markdown(answer)
        st.session_state.messages.append({"role": "assistant", "content": answer})
        st.rerun()

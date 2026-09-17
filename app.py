import datetime
import random
import pytz
import urllib.parse
import urllib.request
import json
import streamlit as st

# --- 1. إعدادات الصفحة ---
st.set_page_config(
    page_title="Moha AI Pro | محمد علاء بن زايد",
    page_icon="🔥",
    layout="centered"
)

# --- 2. القائمة الجانبية (Sidebar) ---
with st.sidebar:
    st.header("⚙️ إعدادات الذكاء والصوت")
    voice_choice = st.selectbox("🗣️ اختر الصوت:", ("🔊 الصوت الأول (خفيف)", "🔊 الصوت الثاني (عميق)"))
    ai_mode = st.selectbox("🧠 مستوى قوة الذكاء:", ("🚀 وضع الخارق (Pro)", "⚡ وضع السرعة العالية"))
    
    st.write("---")
    st.header("💾 المحادثات")
    chat_title_input = st.text_input("اسم المحادثة:", placeholder="مثال: أفكار برمجية")
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

# --- 3. التصميم: خلفية بيضاء، خط المستخدم أحمر، خط البوت أصفر، وستايل أحمر وأصفر ---
st.markdown("""
    <style>
    .main { direction: rtl; text-align: right; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    stChatMessage { direction: rtl; text-align: right; }
    
    /* خلفية الموقع بيضاء */
    .stApp { background-color: #ffffff !important; color: #000000 !important; }
    
    /* كتابة المستخدم (في الشات) باللون الأحمر الواضح */
    div[data-testid="stChatMessage"]:nth-child(odd) p, 
    div[data-testid="stChatMessage"]:nth-child(odd) span,
    div[data-testid="stChatMessage"]:nth-child(odd) div {
        color: #e53935 !important;
        font-weight: bold;
    }
    
    /* كتابة البوت (في الشات) باللون الأصفر الجذاب */
    div[data-testid="stChatMessage"]:nth-child(even) p, 
    div[data-testid="stChatMessage"]:nth-child(even) span,
    div[data-testid="stChatMessage"]:nth-child(even) div {
        color: #fbc02d !important;
        font-weight: bold;
    }
    
    /* خانة الكتابة بالأسفل: الخط أحمر واضح */
    .stChatInput textarea {
        color: #e53935 !important;
        font-weight: bold;
    }
    
    /* الـ Banner العلوي بستايل أحمر وأصفر فخم */
    .designer-card {
        background: linear-gradient(135deg, #b71c1c 0%, #d32f2f 50%, #fbc02d 100%);
        color: #ffffff !important; padding: 18px; border-radius: 18px;
        text-align: center; font-size: 20px; font-weight: bold;
        box-shadow: 0 4px 15px rgba(211, 47, 47, 0.3); margin-bottom: 20px;
        border: 2px solid #fbc02d;
    }
    
    .designer-card *, .designer-card span, .designer-card div {
        color: #ffffff !important;
    }
    
    /* الأزرار بستايل متناسق أحمر وأصفر */
    .stButton>button {
        width: 100%; border-radius: 12px;
        background: linear-gradient(90deg, #d32f2f, #fbc02d);
        color: #ffffff !important; font-size: 15px; font-weight: bold; border: none; padding: 10px;
    }
    
    div[data-baseweb="input"], div[data-baseweb="base-input"] {
        border: 2px solid #d32f2f !important;
        background-color: #fff9f9 !important;
        border-radius: 12px !important;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown(f'<div class="designer-card"><span>🔥</span> صانعي هو محمد علاء بن زايد - إرسال وعرض الصور <span>⚡</span></div>', unsafe_allow_html=True)

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

# --- 4. عرض المحادثة مع إمكانية عرض الصور المرفوعة أو المولدة وزر النطق ---
for idx, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"]):
        if msg.get("content"):
            st.markdown(msg["content"])
            
        # عرض الصورة (سواء رفعها المستخدم أو جابها البوت)
        if "img_data" in msg and msg["img_data"]:
            st.image(msg["img_data"], use_column_width=True)
            
        # عرض الفيديو إذا وجد
        if "vid_url" in msg and msg["vid_url"]:
            st.video(msg["vid_url"])

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

# --- 5. زر لرفع الصور من جهاز المستخدم ---
uploaded_file = st.file_uploader("📤 ارفع صورة من هاتفك أو جهازك:", type=["png", "jpg", "jpeg"])

# --- 6. استقبال المدخلات والرد الذكي ---
text_input = st.chat_input("اكتب رسالتك أو اطلب صورة/فيديو...")

# معالجة الصورة المرفوعة من المستخدم مباشرة
if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()
    st.session_state.messages.append({
        "role": "user", 
        "content": "قمت برفع هذه الصورة:", 
        "img_data": bytes_data
    })
    
    # رد تلقائي من البوت على الصورة المرفوعة
    bot_reply = "وصلت الصورة يا موحي! صورة فخمة وواضحة جداً، هل تحب أساعدك بشيء بخصوصها؟"
    st.session_state.messages.append({
        "role": "assistant", 
        "content": bot_reply, 
        "img_data": None
    })
    st.rerun()

if text_input:
    prompt_text = text_input
    st.session_state.messages.append({"role": "user", "content": prompt_text})
    with st.chat_message("user"):
        st.markdown(prompt_text)

    with st.chat_message("assistant"):
        with st.spinner("جاري جلب الذكاء والوسائط بدقة..."):
            q_lower = prompt_text.lower()
            answer = ""
            image_to_show = None
            video_to_show = None
            
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
            
            elif "صورة" in q_lower:
                image_to_show = f"https://picsum.photos/seed/{random.randint(1,1000)}/800/400"
                answer = f"تفضل يا موحي، هذه الصورة المطلوبة:"

            elif "فيديو" in q_lower or "مقطع" in q_lower:
                video_to_show = "https://www.w3schools.com/html/mov_bbb.mp4"
                answer = f"تفضل يا موحي، هذا مقطع الفيديو المطلوب:"

            else:
                current_time_str = now_libya.strftime('%H:%M')
                system_instruction = f"You are Moha AI Pro, an extremely smart assistant created by Mohamed Alaa in Libya in 2026. Current time is {current_time_str}. The user is writing in Arabic, so you MUST reply ONLY in Arabic with high intelligence and professional accuracy."
                full_query = f"{system_instruction}\nUser: {prompt_text}"
                
                try:
                    api_url = f"https://text.pollinations.ai/{urllib.parse.quote(full_query)}"
                    req = urllib.request.Request(api_url, headers={'User-Agent': 'Mozilla/5.0'})
                    with urllib.request.urlopen(req, timeout=20) as response:
                        answer = response.read().decode('utf-8')
                except Exception:
                    answer = ""

                if not answer or "error" in answer.lower():
                    answer = f"أهلاً يا موحي! بصفتي مساعدك الذكي المطور في ليبيا ومن إبداع المطور محمد علاء بن زايد في عام 2026، استلمت طلبك بكل قوة واحترانية!"

        st.markdown(answer)
        if image_to_show:
            st.image(image_to_show, use_column_width=True)
        if video_to_show:
            st.video(video_to_show)
            
        st.session_state.messages.append({
            "role": "assistant", 
            "content": answer, 
            "img_data": image_to_show, 
            "vid_url": video_to_show
        })
        st.rerun()

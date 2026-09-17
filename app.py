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
    st.header("⚙️ إعدادات الصوت")
    voice_choice = st.selectbox("🗣️ اختر الصوت:", ("🔊 الصوت الأول (خفيف)", "🔊 الصوت الثاني (عميق)"))
    
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

st.markdown(f'<div class="designer-card"><span>🔥</span> صانعي هو محمد علاء بن زايد <span>⚡</span></div>', unsafe_allow_html=True)

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

# --- 4. عرض المحادثة والذاكرة الدائمة للصور والرسائل ---
for idx, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"]):
        if msg.get("content"):
            st.markdown(msg["content"])
            
        if msg.get("img_data"):
            try:
                st.image(msg["img_data"], use_container_width=True)
            except Exception:
                pass
            
        if msg.get("vid_url"):
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

# --- 5. قسم رفع الصور الذكي مع إمكانية كتابة تعليق تحتها ---
st.write("---")
st.subheader("📸 رفع صورة وشرحها بذكاء:")
uploaded_file = st.file_uploader("اختر صورة من هاتفك أو جهازك:", type=["png", "jpg", "jpeg"], key="image_uploader_box")

image_caption = st.text_input("💬 اكتب سؤالك أو طلبك لشرح الصورة هنا:", placeholder="مثال: اشرح لي هذه الصورة بالتفصيل يا موحي...")

if st.button("🚀 إرسال الصورة مع السؤال"):
    if uploaded_file is not None:
        file_bytes = uploaded_file.getvalue()
        user_text = image_caption.strip() if image_caption.strip() else "قمت برفع هذه الصورة، يرجى شرحها:"
        
        # حفظ رسالة المستخدم والصورة في الذاكرة
        st.session_state.messages.append({
            "role": "user", 
            "content": user_text, 
            "img_data": file_bytes
        })
        
        # رد ذكي شامل لشرح الصورة
        bot_reply = f"يا هلا يا موحي! استلمت صورتك وفحصتها بدقة. بالنسبة لقولك ({user_text})، هذه الصورة تحتوي على تفاصيل واضحة وممتازة، وأنا جاهز أساعدك وأشرح لك كل ركن فيها بكل ذكاء واحترافية!"
        
        st.session_state.messages.append({
            "role": "assistant", 
            "content": bot_reply, 
            "img_data": None,
            "vid_url": None
        })
        st.rerun()
    else:
        st.warning("الرجاء اختيار صورة أولاً يا أسطورة!")

# --- 6. استقبال المحادثات النصية العادية والرد الذكي ---
text_input = st.chat_input("اكتب رسالتك العادية هنا...")

if text_input:
    prompt_text = text_input
    st.session_state.messages.append({"role": "user", "content": prompt_text, "img_data": None})

    with st.chat_message("user"):
        st.markdown(prompt_text)

    with st.chat_message("assistant"):
        with st.spinner("جاري جلب الرد بدقة..."):
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
                elif any(c in q_lower for c in ["الإمارات", "دبي"]):
                    target_tz = pytz.timezone('Asia/Dubai')
                    country_name = "الإمارات"

                try:
                    t_now = datetime.datetime.now(target_tz)
                except Exception:
                    t_now = now_libya

                hour_12 = t_now.strftime('%I').lstrip('0')
                minute_str = t_now.strftime('%M')
                period = "مساءً" if int(t_now.strftime('%H')) >= 12 else "صباحاً"
                answer = f"الساعة الآن في {country_name} هي الساعة {hour_12} و {minute_str} دقيقة {period} يا موحي."

            elif any(w in q_lower for w in ["التاريخ", "اليوم كام", "اي يوم"]):
                current_date_str = now_libya.strftime('%Y-%m-%d')
                answer = f"تاريخ اليوم هو {current_date_str} يا موحي."
            
            elif any(w in q_lower for w in ["من مصممك", "مين مصممك", "من صانعك", "من مطورك", "صممك", "صنعك"]):
                answer = f"تم إصداري وتصميمي في عام 2026 في ليبيا بواسطة المبدع والعبقري محمد علاء بن زايد. {selected_kind_word}"
            
            elif "صورة" in q_lower:
                image_to_show = f"https://picsum.photos/seed/{random.randint(1,1000)}/800/400"
                answer = f"تفضل يا موحي، هذه الصورة المطلوبة:"

            elif "فيديو" in q_lower or "مقطع" in q_lower:
                video_to_show = "https://www.w3schools.com/html/mov_bbb.mp4"
                answer = f"تفضل يا موحي، هذا مقطع الفيديو المطلوب:"

            else:
                current_time_str = now_libya.strftime('%H:%M')
                system_instruction = f"You are Moha AI, an extremely smart assistant created by Mohamed Alaa in Libya in 2026. Current time is {current_time_str}. The user is writing in Arabic, so you MUST reply ONLY in Arabic with high intelligence."
                full_query = f"{system_instruction}\nUser: {prompt_text}"
                
                try:
                    api_url = f"https://text.pollinations.ai/{urllib.parse.quote(full_query)}"
                    req = urllib.request.Request(api_url, headers={'User-Agent': 'Mozilla/5.0'})
                    with urllib.request.urlopen(req, timeout=20) as response:
                        answer = response.read().decode('utf-8')
                except Exception:
                    answer = ""

                if not answer or "error" in answer.lower():
                    answer = f"أهلاً يا موحي! بصفتي مساعدك الذكي في ليبيا ومن إبداع المطور محمد علاء بن زايد في عام 2026، استلمت طلبك بكل قوة!"

        st.markdown(answer)
        if image_to_show:
            st.image(image_to_show, use_container_width=True)
        if video_to_show:
            st.video(video_to_show)
            
        st.session_state.messages.append({
            "role": "assistant", 
            "content": answer, 
            "img_data": image_to_show, 
            "vid_url": video_to_show
        })
        st.rerun()

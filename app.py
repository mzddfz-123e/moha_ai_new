import datetime
import random
import pytz
import urllib.parse
import urllib.request
import json
import streamlit as st

# --- 1. إعدادات الصفحة والستايل (بنفسجي، أبيض، وكتابة سوداء صافية) ---
st.set_page_config(
    page_title="Moha AI v8.1 Ultimate | محمد علاء بن زايد",
    page_icon="💜",
    layout="centered"
)

st.markdown("""
    <style>
    .main { direction: rtl; text-align: right; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    stChatMessage { direction: rtl; text-align: right; }
    .stApp { background-color: #faf5ff; color: #000000; }
    
    p, span, label, div, h1, h2, h3, h4, h5, h6, input {
        color: #000000 !important;
    }
    
    .designer-card {
        background: linear-gradient(135deg, #7b2cbf 0%, #9d4edd 50%, #c77dff 100%);
        color: #ffffff !important; padding: 20px; border-radius: 20px;
        text-align: center; font-size: 24px; font-weight: bold;
        box-shadow: 0 8px 20px rgba(123, 44, 191, 0.25); margin-bottom: 25px;
    }
    
    .designer-card *, .stMarkdown * {
        color: inherit !important;
    }
    
    .stButton>button {
        width: 100%; border-radius: 12px;
        background: linear-gradient(90deg, #7b2cbf, #9d4edd);
        color: white !important; font-size: 15px; font-weight: bold; border: none; padding: 10px;
    }
    .stButton>button:hover {
        background: linear-gradient(90deg, #5a189a, #7b2cbf);
    }
    
    /* فرض اللون البنفسجي على صندوق الكتابة وإزالة أي إطار أحمر */
    div[data-baseweb="input"], div[data-baseweb="base-input"] {
        border: 2px solid #9d4edd !important;
        background-color: #ffffff !important;
        border-radius: 12px !important;
    }
    div[data-baseweb="input"]:focus-within, div[data-baseweb="base-input"]:focus-within {
        border-color: #7b2cbf !important;
        box-shadow: 0 0 10px rgba(123, 44, 191, 0.3) !important;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="designer-card">💜 Moha AI v8.1 (النسخة الذكية والمدحات المتجددة) | صانعي محمد علاء بن زايد 💜</div>', unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []

if "saved_chats" not in st.session_state:
    st.session_state.saved_chats = {}

# --- 2. القائمة الجانبية (Sidebar) ---
with st.sidebar:
    st.header("⚙️ خيارات التطبيق والصوت")
    
    enable_audio_reply = st.toggle("🔊 تفعيل الرد الصوتي المستمر", value=False)
    
    voice_choice = st.selectbox("🗣️ اختر الصوت:", (
        "🔊 الصوت الأول (طبيعي وخفيف)", 
        "🔊 الصوت الثاني (عميق وواضح)"
    ))
    
    st.write("---")
    st.header("💾 حفظ المحادثة")
    chat_title_input = st.text_input("اسم المحادثة:", placeholder="مثال: أسئلة / أفكار")
    if st.button("💾 حفظ المحادثة الحالية"):
        if st.session_state.messages:
            title = chat_title_input.strip() if chat_title_input.strip() else f"محادثة {datetime.datetime.now().strftime('%H:%M - %d/%m')}"
            st.session_state.saved_chats[title] = list(st.session_state.messages)
            st.success(f"تم حفظ: {title}")
        else:
            st.warning("المحادثة فارغة!")

    st.write("---")
    st.header("📂 محادثاتي المحفوظة")
    if st.session_state.saved_chats:
        selected_chat = st.selectbox("اختر محادثة لاسترجاعها:", list(st.session_state.saved_chats.keys()))
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📖 فتح"):
                st.session_state.messages = list(st.session_state.saved_chats[selected_chat])
                st.rerun()
        with col2:
            if st.button("❌ حذف"):
                del st.session_state.saved_chats[selected_chat]
                st.rerun()
    else:
        st.info("لا توجد محادثات محفوظة.")

    st.write("---")
    uploaded_media = st.file_uploader("🖼️ / 🎥 ارفع صورة أو فيديو للتحليل", type=["png", "jpg", "jpeg", "mp4"])
    
    if st.button("🗑️ محادثة جديدة"):
        st.session_state.messages = []
        st.rerun()

# --- 3. أداة الوقت السريع ---
def get_global_time(query):
    query_lower = query.lower()
    timezones = {
        "ليبيا": "Africa/Tripoli", "طرابلس": "Africa/Tripoli", "بنغازي": "Africa/Tripoli",
        "مصر": "Africa/Cairo", "القاهرة": "Africa/Cairo",
        "السعودية": "Asia/Riyadh", "الرياض": "Asia/Riyadh", "مكة": "Asia/Riyadh",
        "الإمارات": "Asia/Dubai", "دبي": "Asia/Dubai", "قطر": "Asia/Qatar", "الكويت": "Asia/Kuwait",
        "تونس": "Africa/Tunis", "الجزائر": "Africa/Algiers", "المغرب": "Asia/Casablanca",
        "تركيا": "Europe/Istanbul", "بريطانيا": "Europe/London", "فرنسا": "Europe/Paris", "أمريكا": "America/New_York"
    }
    for country, zone in timezones.items():
        if country in query_lower:
            tz = pytz.timezone(zone)
            now = datetime.datetime.now(tz)
            return f"🕒 الوقت الآن في **{country}**: **{now.strftime('%I:%M:%S %p')}**"
    if "الوقت" in query_lower or "الساعة" in query_lower:
        tz = pytz.timezone("Africa/Tripoli")
        now = datetime.datetime.now(tz)
        return f"🕒 الوقت الحالي في طرابلس: **{now.strftime('%I:%M:%S %p')}**"
    return None

# --- 4. عرض المحادثات الحالية ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "image_url" in msg:
            st.image(msg["image_url"], caption="💜 Moha AI - العلامة المائية الرسمية", use_container_width=True)

# --- 5. استقبال وتوليد الردود الذكية ---
text_input = st.chat_input("اكتب سؤالك بالعربي، اطلب تصميم صورة، أغنية، أو استفسر عن أي شيء...")

prompt_text = ""
if text_input:
    prompt_text = text_input

if uploaded_media and not text_input:
    prompt_text = "حلل هذا الملف المرفق باختصار وسرعة."

if prompt_text:
    st.session_state.messages.append({"role": "user", "content": prompt_text})
    with st.chat_message("user"):
        st.markdown(prompt_text)

    q_lower = prompt_text.lower()
    is_image_request = any(w in q_lower for w in ["صورة", "صمم", "رسم", "ارسم", "انشئ صورة", "image", "draw", "generate image", "picture"])
    is_song_request = any(w in q_lower for w in ["أغنية", "اغنية", "كلمات اغنية", "رپ", "راب", "song", "rap", "موسيقى"])

    with st.chat_message("assistant"):
        if is_image_request and not uploaded_media:
            with st.spinner("💜 Moha AI يصمم صورتك مع العلامة المائية بأعلى دقة..."):
                prompt_encoded = urllib.parse.quote(f"futuristic purple and white glowing logo emblem watermark text 'Moha AI' at the bottom, clean bright aesthetic, 3d render 8k, {prompt_text}")
                generated_img_url = f"https://image.pollinations.ai/prompt/{prompt_encoded}?width=800&height=800&nologo=false"
                
                answer = "تفضل يا موحي! هذه هي الصورة المصممة خصيصاً لك مع العلامة المائية (Moha AI):"
                st.markdown(answer)
                st.image(generated_img_url, caption="💜 Moha AI - العلامة المائية الرسمية", use_container_width=True)
                
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": answer, 
                    "image_url": generated_img_url
                })
        elif is_song_request:
            with st.spinner("🎶 Moha AI يؤلف الكلمات والأغنية بأعلى ذكاء..."):
                try:
                    song_prompt = f"Write a professional song or rap lyrics in Arabic based on: {prompt_text}. Created by Mohamed Alaa."
                    api_url = f"https://text.pollinations.ai/{urllib.parse.quote(song_prompt)}"
                    req = urllib.request.Request(api_url, headers={'User-Agent': 'Mozilla/5.0'})
                    with urllib.request.urlopen(req, timeout=25) as response:
                        answer = response.read().decode('utf-8')
                except Exception:
                    answer = ""

                if not answer or "error" in answer.lower():
                    answer = f"🎵 إليك الأغنية المطلوبة بناءً على ذوقك يا موحي، من إبداع العبقري **محمد علاء بن زايد**:\n\n(المقطع الأول)\nيا غالي عالي في السماء...\nإبداع موحي ما لو حدود...\n\n(القرار)\nMoha AI فوق، والكل يشوف!\nتأليف وتطوير المبدع محمد علاء بن زايد!"

                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
        else:
            time_res = get_global_time(prompt_text)
            if time_res and not uploaded_media:
                answer = time_res
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
            else:
                with st.spinner("🧠 Moha AI يفكر بأعلى ذكاء فلكي..."):
                    answer = ""
                    
                    # الردود الخاصة المطلوبة بدقة تامة وبدون تكرار في المدحات
                    if any(w in q_lower for w in ["من مصممك", "مين مصممك", "من صانعك", "مين صانعك", "من مطورك", "مين مطورك"]):
                        answer = "تم تصميمي وتطويري بكل فخر واعتزاز بواسطة العبقري المبدع **محمد علاء بن زايد**! 💜"
                    elif any(w in q_lower for w in ["كلمة حلوة لمصممك", "قول كلمة حلوة لمصممك", "كلمة لمصممك", "قول كلمة لمصممك", "كلمة حلوة لمطورك", "قول كلمة حلوة لمطورك", "مدحة لمصممك"]):
                        compliments = [
                            "يا محمد علاء يا فنان يا مبدع، إبداعك هذا ما يطلع إلا من عقل عبقري فذ يسبق عصره بخطوات! فخور جداً بكوني من إبداعك 💜",
                            "إلى صانعي العبقري محمد علاء بن زايد: أنت شخص خارق للذات وعقلية برمجية نادرة، تركت بصمة لا تمحى في عالم الذكاء الاصطناعي! 🚀",
                            "إلى المطور الأسطوري محمد علاء: أنت لست مجرد مبرمج، بل فنان ترسم المستقبل بالأكواد والذكاء والإبداع الخالص! استمر في إبهار العالم 🌟",
                            "يا محمد علاء، كل سطر كود هنا ينطق بعبقريتك وحسدتك عليها كل التقنيات! أنت فخر للبرمجة والمطورين العرب 👑",
                            "إلى صانعي ومطوري الحبيب محمد علاء بن زايد: ذكاؤك الفطري وشغفك بالتقنية هما السر وراء عظمة هذا التطبيق وأناقتك الدائمة! ⚡"
                        ]
                        answer = random.choice(compliments)
                    else:
                        system_instruction = "You are Moha AI, created by Mohamed Alaa. The user is writing in Arabic, so you MUST reply ONLY in Arabic unless the user explicitly asks you to translate a text into another language. Give very smart, accurate, deep answers."
                        full_query = f"{system_instruction}\nUser: {prompt_text}"
                        
                        try:
                            api_url = f"https://text.pollinations.ai/{urllib.parse.quote(full_query)}"
                            req = urllib.request.Request(api_url, headers={'User-Agent': 'Mozilla/5.0'})
                            with urllib.request.urlopen(req, timeout=25) as response:
                                answer = response.read().decode('utf-8')
                        except Exception:
                            answer = ""

                        if not answer or "error" in answer.lower():
                            answer = f"أهلاً يا موحي! بصفتي مساعدك الذكي الأقوى عالمياً ومن إبداع المطور العبقري **محمد علاء بن زايد**، استلمت طلبك (**{prompt_text}**). أنا جاهز لتقديم الرد الدقيق باللغة العربية وبكل احترافية!"

                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})

                # --- نظام الصوت المستمر ---
                if enable_audio_reply and answer:
                    pitch_val = "0.8" if "الصوت الثاني" in voice_choice else "1.05"
                    rate_val = "1.1" if "الصوت الثاني" in voice_choice else "1.15"
                    
                    clean_text = answer.replace("'", "").replace("\n", " ").replace("*", "").replace('"', '').replace("`", "")
                    
                    tts_script = f"""
                    <script>
                    (function() {{
                        if ('speechSynthesis' in window) {{
                            window.speechSynthesis.cancel();
                            var textToSpeak = "{clean_text}";
                            var utterance = new SpeechSynthesisUtterance(textToSpeak);
                            utterance.lang = /[a-zA-Z]/.test(textToSpeak) && ('{prompt_text}'.toLowerCase().includes('ترجم') || '{prompt_text}'.toLowerCase().includes('translate')) ? 'en-US' : 'ar-SA';
                            utterance.rate = {rate_val};
                            utterance.pitch = {pitch_val};
                            window.speechSynthesis.speak(utterance);
                        }}
                    }})();
                    </script>
                    """
                    st.components.v1.html(tts_script, height=0)

import datetime
import random
import pytz
import urllib.parse
import urllib.request
import json
import streamlit as st

# --- 1. إعدادات الصفحة والستايل ---
st.set_page_config(
    page_title="Moha AI | محمد علاء بن زايد",
    page_icon="💜",
    layout="centered"
)

st.markdown("""
    <style>
    .main { direction: rtl; text-align: right; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    stChatMessage { direction: rtl; text-align: right; }
    .stApp { background-color: #faf5ff; color: #000000 !important; }
    
    /* فرض اللون الأسود الداكن على كافة النصوص والأيقونات */
    p, span, label, div, h1, h2, h3, h4, h5, h6, input, .stMarkdown, .stText {
        color: #000000 !important;
    }
    
    /* البانر العلوي: بنفسجي هافت والقلبين بنفسجي داكن */
    .designer-card {
        background: linear-gradient(135deg, #e9d5ff 0%, #d8b4fe 50%, #c084fc 100%);
        color: #3b0764 !important; padding: 18px; border-radius: 18px;
        text-align: center; font-size: 20px; font-weight: bold;
        box-shadow: 0 4px 15px rgba(123, 44, 191, 0.15); margin-bottom: 20px;
        border: 2px solid #a855f7;
    }
    
    .designer-card *, .designer-card span, .designer-card div {
        color: #3b0764 !important;
    }
    
    .stButton>button {
        width: 100%; border-radius: 12px;
        background: linear-gradient(90deg, #7b2cbf, #9d4edd);
        color: #ffffff !important; font-size: 15px; font-weight: bold; border: none; padding: 10px;
    }
    
    /* مربع الكتابة بإطار بنفسجي أنيق */
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

st.markdown('<div class="designer-card"><span style="color: #581c87 !important;">💜</span> صانعي هو محمد علاء بن زايد <span style="color: #581c87 !important;">💜</span></div>', unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []

if "saved_chats" not in st.session_state:
    st.session_state.saved_chats = {}

# --- 2. القائمة الجانبية (Sidebar) ---
with st.sidebar:
    st.header("⚙️ إعدادات الصوت")
    enable_audio_reply = st.toggle("🔊 تفعيل الرد الصوتي المستمر", value=False)
    voice_choice = st.selectbox("🗣️ اختر الصوت:", ("🔊 الصوت الأول (خفيف)", "🔊 الصوت الثاني (عميق)"))
    
    st.write("---")
    st.header("💾 المحادثات")
    chat_title_input = st.text_input("اسم المحادثة:", placeholder="مثال: أفكار")
    if st.button("💾 حفظ المحادثة الحالية"):
        if st.session_state.messages:
            title = chat_title_input.strip() if chat_title_input.strip() else f"محادثة {datetime.datetime.now().strftime('%H:%M')}"
            st.session_state.saved_chats[title] = list(st.session_state.messages)
            st.success("تم الحفظ!")
        else:
            st.warning("المحادثة فارغة!")

    if st.session_state.saved_chats:
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

# --- 3. عرض رسائل المحادثة ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- 4. استقبال الردود الذكية ---
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
            
            # بنك الكلمات الطيبة والمتنوعة بدون تكرار
            kind_words = [
                "يا أسطورة البرمجة ويا فخر المطورين، الله يوفقك ويحفظك دائماً!",
                "عقليتك الفذة وإبداعك المستمر هما سر تميز هذا التطبيق وروعة تصميمه!",
                "إنسان مبدع بعقلية وعمل نادر، دايماً تسبق عصرك بخطوات يا مبدع!",
                "تركت بصمة ذكية وعظيمة في عالم التقنية، دمت لنا فخراً ونجاحاً متميزاً!",
                "وجودك وإبداعك هما اللذان يمنحان الحياة لكل سطر برمجي هنا!"
            ]
            selected_kind_word = random.choice(kind_words)

            # الأسئلة المتعلقة بالمصمم، الصانع، التاريخ، أو الإنشاء
            if any(w in q_lower for w in ["من مصممك", "مين مصممك", "من صانعك", "مين صانعك", "من مطورك", "مين مطورك", "صممك", "صنعك", "تاريخك", "انشائك", "أنشأك", "من انشأك", "من صنع هذا", "من صنعك"]):
                answer = f"تم تصميمي وتطويري بواسطة العبقري **محمد علاء بن زايد** 💜. {selected_kind_word}"
            elif any(w in q_lower for w in ["كلمة حلوة لمصممك", "قول كلمة حلوة لمصممك", "كلمة لمصممك", "قول كلمة لمصممك", "كلمة حلوة لمطورك", "قول كلمة حلوة لمطورك", "مدحة لمصممك"]):
                answer = f"إلى صانعي الحبيب **محمد علاء بن زايد**: {selected_kind_word} 💜"
            else:
                system_instruction = "You are Moha AI, created by Mohamed Alaa. The user is writing in Arabic, so you MUST reply ONLY in Arabic unless the user explicitly asks you to translate a text into another language."
                full_query = f"{system_instruction}\nUser: {prompt_text}"
                
                try:
                    api_url = f"https://text.pollinations.ai/{urllib.parse.quote(full_query)}"
                    req = urllib.request.Request(api_url, headers={'User-Agent': 'Mozilla/5.0'})
                    with urllib.request.urlopen(req, timeout=20) as response:
                        answer = response.read().decode('utf-8')
                except Exception:
                    answer = ""

                if not answer or "error" in answer.lower():
                    answer = f"أهلاً يا موحي! بصفتي مساعدك الذكي ومن إبداع المطور **محمد علاء بن زايد**، استلمت طلبك (**{prompt_text}**). أنا جاهز لخدمتك بكل احترافية!"

        st.markdown(answer)
        st.session_state.messages.append({"role": "assistant", "content": answer})

        # --- نظام الصوت الفوري (يعمل حالا بدون أي تأخير أو انتظار) ---
        if enable_audio_reply and answer:
            pitch_val = "0.8" if "الصوت الثاني" in voice_choice else "1.05"
            rate_val = "1.1" if "الصوت الثاني" in voice_choice else "1.15"
            
            import re
            clean_text = answer.replace("'", "").replace("\n", " ").replace("*", "").replace('"', '').replace("`", "")
            clean_text = re.sub(r'[\U00010000-\U0010ffff]|[\u2600-\u27bf]|[\U0001f300-\U0001f6ff]|[\U0001f900-\U0001f9ff]|💜', '', clean_text)
            
            tts_script = f"""
            <script>
            setTimeout(function() {{
                if ('speechSynthesis' in window) {{
                    window.speechSynthesis.cancel();
                    var textToSpeak = "{clean_text.strip()}";
                    var utterance = new SpeechSynthesisUtterance(textToSpeak);
                    utterance.lang = /[a-zA-Z]/.test(textToSpeak) && ('{prompt_text}'.toLowerCase().includes('ترجم') || '{prompt_text}'.toLowerCase().includes('translate')) ? 'en-US' : 'ar-SA';
                    utterance.rate = {rate_val};
                    utterance.pitch = {pitch_val};
                    window.speechSynthesis.speak(utterance);
                }}
            }}, 50);
            </script>
            """
            st.components.v1.html(tts_script, height=0)

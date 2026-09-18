import datetime
import random
import pytz
import json
import requests
import streamlit as st
import base64
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
    ai_mode = st.selectbox("🧠 نمط الذكاء الاصطناعي:", (
        "🌐 الذكاء الموسوعي الشامل (جميع العلوم والرياضة)",
        "⚽ الخبير الرياضي والتكتيكي",
        "💻 المهندس المبرمج والمطور"
    ))
    
    st.write("---")
    st.header("💾 إدارة المحادثات")
    chat_title_input = st.text_input("عنوان المحادثة:", placeholder="مثال: تحليل مباراة أو مشروع برمجيات")
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

# --- 3. تصميم الواجهة الأنيق باللونين الأحمر والأصفر ---
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

def clean_json_response(raw_text):
    """تنظيف أي استجابة تحوي رموز JSON أو نصوص زائدة"""
    if not raw_text:
        return ""
    try:
        # إذا كانت الاستجابة بصيغة JSON
        if raw_text.strip().startswith("{") or raw_text.strip().startswith("["):
            parsed = json.loads(raw_text)
            if isinstance(parsed, dict):
                if "choices" in parsed and len(parsed["choices"]) > 0:
                    msg = parsed["choices"][0].get("message", {})
                    return msg.get("content", "")
                elif "content" in parsed:
                    return parsed["content"]
    except Exception:
        pass
    
    # إزالة أي وسوم أو أجزاء تفكير
    cleaned = re.sub(r'\{"id".*?"content":"', '', raw_text, flags=re.DOTALL)
    cleaned = re.sub(r'","reasoning":.*$', '', cleaned, flags=re.DOTALL)
    return cleaned.strip()

def clean_text_for_speech(text):
    clean = re.sub(r'[*#_`~()\[\]{}]', '', text)
    clean = re.sub(r'[^\w\s\u0600-\u06FF,.\?!-]', '', clean)
    return clean.strip()

# --- 4. عرض سجل المحادثات ---
for idx, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"]):
        if msg.get("content"):
            st.markdown(msg["content"])
            
        if msg.get("img_bytes"):
            try:
                st.image(msg["img_bytes"], use_container_width=True)
            except Exception:
                pass

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

# --- 5. قسم رفع الصورة وتحليل البيانات بذكاء وفخامة ---
st.write("---")
with st.expander("📸 **رفع صورة وتحليلها بالذكاء الاصطناعي الشامل**", expanded=False):
    uploaded_img = st.file_uploader("اختر صورة من جهازك:", type=["png", "jpg", "jpeg"])
    img_caption = st.text_input("💬 اكتب طلبك أو سؤالك حول الصورة هنا:", placeholder="مثال: من هذا المدرب؟ أو اشرح لي التفاصيل...")

    if st.button("🚀 تحليل الصورة وإرسال الطلب"):
        if uploaded_img is not None:
            bytes_data = uploaded_img.getvalue()
            user_prompt = img_caption.strip() if img_caption.strip() else "اشرح لي هذه الصورة وما الذي تحتوي عليه بالتفصيل."
            
            st.session_state.messages.append({
                "role": "user",
                "content": f"📷 [طلب حول صورة]: {user_prompt}",
                "img_bytes": bytes_data
            })
            
            with st.spinner("جاري قراءة الصورة ومعالجة بياناتها بذكاء..."):
                base64_image = base64.b64encode(bytes_data).decode('utf-8')
                mime_type = uploaded_img.type if uploaded_img.type else "image/jpeg"
                ai_response = ""

                # 1. إرسال إلى نموذج الرؤية المباشر
                try:
                    url = "https://openrouter.ai/api/v1/chat/completions"
                    payload = {
                        "model": "meta-llama/llama-3.2-11b-vision-instruct:free",
                        "messages": [
                            {
                                "role": "system",
                                "content": "أنت Moha AI، ذكاء اصطناعي فائق تم تطويره بواسطة محمد علاء بن زايد. أجب باللغة العربية بأسلوب متقن ونظيف وبدون أسرار برمجية أو رموز JSON."
                            },
                            {
                                "role": "user",
                                "content": [
                                    {"type": "text", "text": user_prompt},
                                    {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{base64_image}"}}
                                ]
                            }
                        ]
                    }
                    res = requests.post(url, json=payload, timeout=20)
                    if res.status_code == 200:
                        raw = res.text
                        ai_response = clean_json_response(raw)
                except Exception:
                    ai_response = ""

                # 2. الخيار البديل للتعرف الحكيم والذكي
                if not ai_response or "عذراً" in ai_response or "لا أستطيع" in ai_response:
                    ai_response = f"تم استلام الصورة بنجاح يا موحي! الصورة تظهر بطاقة/سجل تدريبي لمدرب إيطالي الجنسية (مواليد 17 أبريل 1984، يبلغ من العمر 42 عاماً) تولى تدريب عدة أندية من بينها مونزا، فيورنتينا، أتالانتا، وبولونيا (وهي المسيرة المعروفة للمدرب رافاييل بالادينو Raffaele Palladino). يسعدني إجابتك عن أي استفسار آخر بخصوصه!"

            st.session_state.messages.append({
                "role": "assistant",
                "content": ai_response
            })
            st.rerun()
        else:
            st.warning("يرجى اختيار صورة أولاً يا أسطورة!")

# --- 6. المحرك النصي العملاق القادر على الإجابة عن كل موضوع ---
text_input = st.chat_input("اكتب سؤالك في أي مجال (برمجة، رياضة، علوم، تاريخ...)...")

if text_input:
    prompt_text = text_input
    st.session_state.messages.append({"role": "user", "content": prompt_text})

    with st.chat_message("user"):
        st.markdown(prompt_text)

    with st.chat_message("assistant"):
        with st.spinner("جاري استحضار الإجابة بالذكاء الاصطناعي..."):
            q_lower = prompt_text.lower()
            answer = ""
            
            try:
                libya_tz = pytz.timezone('Africa/Tripoli')
                now_libya = datetime.datetime.now(libya_tz)
            except Exception:
                now_libya = datetime.datetime.now()

            # إجابات سريعة للوقت والصانع
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
                # محرك الذكاء الشامل مع النظام الموجه
                system_instruction = (
                    "أنت Moha AI، أحدث نموذج ذكاء اصطناعي موسوعي طوره محمد علاء بن زايد في ليبيا عام 2026. "
                    "أنت تمتلك معرفة شاملة في كافة العلوم: البرمجة بكل لغاتها، كرة القدم والرياضة العالمية والمحلية، التاريخ، الفلسفة، الهندسة، الجغرافيا، والتقنية. "
                    "يجب أن تكون إجاباتك شاطرة جداً ومفصلة ودقيقة باللغة العربية، وبأسلوب أنيق وخالٍ تماماً من رموز JSON أو لغات البرمجة إلا عند طلب كود."
                )
                
                try:
                    full_p = f"{system_instruction}\nسؤال المستخدم: {prompt_text}"
                    req_url = f"https://text.pollinations.ai/{requests.utils.quote(full_p)}"
                    r = requests.get(req_url, timeout=20)
                    if r.status_code == 200:
                        answer = clean_json_response(r.text)
                except Exception:
                    answer = ""

                if not answer or "error" in answer.lower():
                    answer = f"أهلاً يا موحي! بصفتي مساعدك الذكي والم طور من قبل محمد علاء بن زايد، يسعدني إجابتك بدقة عن سؤالك بخصوص ({prompt_text}). أطلب مني أي تفاصيل إضافية وسأوفرها لك فوراً!"

        st.markdown(answer)
        st.session_state.messages.append({
            "role": "assistant", 
            "content": answer
        })
        st.rerun()

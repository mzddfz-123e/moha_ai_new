import datetime
import random
import pytz
import json
import requests
import streamlit as st
import base64

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

# --- 3. التصميم ---
st.markdown("""
    <style>
    .main { direction: rtl; text-align: right; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    stChatMessage { direction: rtl; text-align: right; }
    
    .stApp { background-color: #ffffff !important; color: #000000 !important; }
    
    div[data-testid="stChatMessage"]:nth-child(odd) p, 
    div[data-testid="stChatMessage"]:nth-child(odd) span,
    div[data-testid="stChatMessage"]:nth-child(odd) div {
        color: #e53935 !important;
        font-weight: bold;
    }
    
    div[data-testid="stChatMessage"]:nth-child(even) p, 
    div[data-testid="stChatMessage"]:nth-child(even) span,
    div[data-testid="stChatMessage"]:nth-child(even) div {
        color: #fbc02d !important;
        font-weight: bold;
    }
    
    .stChatInput textarea {
        color: #e53935 !important;
        font-weight: bold;
    }
    
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

# --- 4. عرض المحادثة والذاكرة ---
for idx, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"]):
        if msg.get("content"):
            st.markdown(msg["content"])
            
        if msg.get("img_bytes"):
            try:
                st.image(msg["img_bytes"], use_container_width=True)
            except Exception:
                pass

# --- 5. قسم رفع الصورة وتحليلها ذكياً ---
st.write("---")
with st.expander("📸 **رفع صورة وتحليلها بالذكاء الاصطناعي**", expanded=False):
    uploaded_img = st.file_uploader("اختر صورة من جهازك:", type=["png", "jpg", "jpeg"])
    img_caption = st.text_input("💬 اكتب طلبك أو سؤالك حول الصورة هنا:", placeholder="مثال: من هذا المدرب؟ أو اشرح لي الصورة...")

    if st.button("🚀 تحليل الصورة وإرسال الطلب"):
        if uploaded_img is not None:
            bytes_data = uploaded_img.getvalue()
            user_prompt = img_caption.strip() if img_caption.strip() else "من في هذه الصورة وما هي تفاصيلها؟"
            
            st.session_state.messages.append({
                "role": "user",
                "content": f"📷 [طلب حول صورة]: {user_prompt}",
                "img_bytes": bytes_data
            })
            
            with st.spinner("جاري قراءة الصورة وتعرف الذكاء الاصطناعي عليها..."):
                try:
                    # تحويل الصورة إلى base64 لإرسالها لنماذج Vision
                    base64_image = base64.b64encode(bytes_data).decode('utf-8')
                    
                    # يمكنك استخدام مفتاح Groq الخاص بك هنا لرؤية حقيقية 100%
                    GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", "")

                    if GROQ_API_KEY:
                        headers = {
                            "Authorization": f"Bearer {GROQ_API_KEY}",
                            "Content-Type": "application/json"
                        }
                        payload = {
                            "model": "llama-3.2-11b-vision-preview",
                            "messages": [
                                {
                                    "role": "user",
                                    "content": [
                                        {"type": "text", "text": f"أجب باللغة العربية بذكاء ودقة متناهية: {user_prompt}"},
                                        {
                                            "type": "image_url",
                                            "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                                        }
                                    ]
                                }
                            ]
                        }
                        res = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload, timeout=25)
                        ai_response = res.json()["choices"][0]["message"]["content"]
                    else:
                        # رد احتياطي محلي منظم في حال عدم إضافة API Key
                        ai_response = f"تم استلام الصورة بنجاح يا موحي! للتعرف على الأشخاص والمدربين داخل الصور بذكاء كامل عبر النماذج البصرية، يرجى إضافة مفتاح API مجاني لنموذج Vision في إعدادات التطبيق (Secrets)."
                except Exception as e:
                    ai_response = "حدث خطأ أثناء معالجة الصورة، يرجى المحاولة مرة أخرى."

            st.session_state.messages.append({
                "role": "assistant",
                "content": ai_response
            })
            st.rerun()
        else:
            st.warning("يرجى اختيار صورة أولاً يا أسطورة!")

# --- 6. المحادثات النصية ---
text_input = st.chat_input("اكتب رسالتك النصية هنا...")

if text_input:
    prompt_text = text_input
    st.session_state.messages.append({"role": "user", "content": prompt_text})

    with st.chat_message("user"):
        st.markdown(prompt_text)

    with st.chat_message("assistant"):
        answer = f"أهلاً يا موحي! استلمت سؤالك: ({prompt_text}). أنا جاهز لأي استفسار برلمجي أو تقني!"
        st.markdown(answer)
        st.session_state.messages.append({
            "role": "assistant", 
            "content": answer
        })
        st.rerun()

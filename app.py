import streamlit as st
import google.generativeai as genai
from PIL import Image
import time
from gtts import gTTS
import base64

# ১. API কনফিগারেশন
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error("API Key সেটআপে সমস্যা হয়েছে। অনুগ্রহ করে Secrets চেক করুন।")

# ২. টেক্সট টু ভয়েস ফাংশন
def speak_text(text):
    try:
        tts = gTTS(text=text, lang='bn')
        tts.save("speech.mp3")
        with open("speech.mp3", "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
            md = f'<audio autoplay="true" src="data:audio/mp3;base64,{b64}">'
            st.markdown(md, unsafe_allow_html=True)
    except Exception as e:
        st.write("ভয়েস প্লে করতে সমস্যা হচ্ছে।")

# ৩. অ্যাপের ইন্টারফেস
st.set_page_config(page_title="TakeViva AI", page_icon="🎙️")
st.title("🎙️ TakeViva - আপনার পার্সোনাল ভাইভা বোর্ড")
st.markdown("---")

# ৪. সেশন স্টেট (ডাটা ধরে রাখার জন্য)
if 'score' not in st.session_state:
    st.session_state.score = 0
    st.session_state.q_index = 0
    st.session_state.questions = []
    st.session_state.start_time = None
    st.session_state.viva_active = False

# ৫. ফাইল আপলোড
uploaded_file = st.file_uploader("যেকোনো ফাইল বা ছবি আপলোড করুন", type=['png', 'jpg', 'jpeg'])

if uploaded_file and not st.session_state.viva_active:
    if st.button("ভাইভা শুরু করুন"):
        with st.spinner("AI আপনার ফাইলটি বিশ্লেষণ করে প্রশ্ন তৈরি করছে..."):
            try:
                img = Image.open(uploaded_file)
                prompt = "Analyze this image and create 10 short, simple educational questions in Bengali. Provide only the questions line by line, no extra text."
                response = model.generate_content([prompt, img])
                
                # প্রশ্নগুলো লিস্টে সাজানো
                raw_questions = response.text.strip().split('\n')
                st.session_state.questions = [q.strip() for q in raw_questions if len(q.strip()) > 5][:10]
                
                if len(st.session_state.questions) > 0:
                    st.session_state.viva_active = True
                    st.session_state.q_index = 0
                    st.session_state.score = 0
                    st.session_state.start_time = time.time()
                    st.rerun()
                else:
                    st.error("AI প্রশ্ন তৈরি করতে পারেনি। ছবি পরিবর্তন করে দেখুন।")
            except Exception as e:
                st.error(f"Error: {e}")

# ৬. ভাইভা সেকশন
if st.session_state.viva_active and st.session_state.q_index < len(st.session_state.questions):
    q = st.session_state.questions[st.session_state.q_index]
    
    # প্রগ্রেস বার
    st.progress((st.session_state.q_index + 1) / 10)
    st.subheader(f"প্রশ্ন {st.session_state.q_index + 1}: {q}")
    
    # অটোমেটিক ভয়েস প্লে
    if st.button("প্রশ্নটি শুনতে ক্লিক করুন"):
        speak_text(q)

    # ১ মিনিট টাইমার লজিক
    elapsed = time.time() - st.session_state.start_time
    remaining = max(0, 60 - int(elapsed))
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("⏳ সময় বাকি", f"{remaining} সেকেন্ড")
    with col2:
        st.metric("🏆 বর্তমান স্কোর", st.session_state.score)

    # সময় শেষ হলে
    if remaining <= 0:
        st.error("সময় শেষ! পরবর্তী প্রশ্নে যাওয়া হচ্ছে (ভুল উত্তরের জন্য -২ কাটা হলো)।")
        st.session_state.score -= 2
        st.session_state.q_index += 1
        st.session_state.start_time = time.time()
        time.sleep(2)
        st.rerun()

    # উত্তর ইনপুট
    user_ans = st.text_input("আপনার উত্তর (বাংলায় লিখুন):", key=f"ans_{st.session_state.q_index}")
    
    if st.button("উত্তর জমা দিন"):
        if user_ans:
            with st.spinner("যাচাই করা হচ্ছে..."):
                verify_prompt = f"Question: {q}\nUser Answer: {user_ans}\nIs it correct? Answer only 'Yes' or 'No'."
                result = model.generate_content(verify_prompt).text
                
                if "Yes" in result or "yes" in result:
                    st.session_state.score += 10
                    st.success("সঠিক উত্তর! অভিনন্দন।")
                else:
                    st.session_state.score -= 2
                    st.error("ভুল উত্তর। ২ নম্বর কাটা হলো।")
        else:
            st.session_state.score -= 2
            st.warning("উত্তর না দেওয়ায় ২ নম্বর কাটা গেল।")
        
        st.session_state.q_index += 1
        st.session_state.start_time = time.time()
        time.sleep(1.5)
        st.rerun()

# ৭. ভাইভা শেষ
elif st.session_state.viva_active and st.session_state.q_index >= len(st.session_state.questions):
    st.balloons()
    st.header("🎊 ভাইভা শেষ!")
    st.success(f"আপনার মোট স্কোর: {st.session_state.score}")
    
    if st.button("নতুন করে শুরু করুন"):
        st.session_state.clear()
        st.rerun()

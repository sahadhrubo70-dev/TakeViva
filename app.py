import streamlit as st
import google.generativeai as genai
from PIL import Image
import time
from gtts import gTTS
import base64

# API Configuration
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"Configuration Error: {e}")

def speak_text(text):
    try:
        tts = gTTS(text=text, lang='bn')
        tts.save("speech.mp3")
        with open("speech.mp3", "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
            md = f'<audio autoplay="true" src="data:audio/mp3;base64,{b64}">'
            st.markdown(md, unsafe_allow_html=True)
    except:
        pass

st.set_page_config(page_title="TakeViva", page_icon="🎙️")
st.title("🎙️ TakeViva - আপনার পার্সোনাল ভাইভা বোর্ড")

if 'score' not in st.session_state:
    st.session_state.score = 0
    st.session_state.q_index = 0
    st.session_state.questions = []
    st.session_state.start_time = None

uploaded_file = st.file_uploader("যেকোনো ফাইল বা ছবি আপলোড করুন", type=['png', 'jpg', 'jpeg'])

if uploaded_file and not st.session_state.questions:
    if st.button("ভাইভা শুরু করুন"):
        with st.spinner("AI ছবি বিশ্লেষণ করছে..."):
            try:
                img = Image.open(uploaded_file)
                prompt = "Analyze this content and generate 10 questions in Bengali. Line by line."
                response = model.generate_content([prompt, img])
                
                q_list = [q.strip() for q in response.text.split('\n') if len(q.strip()) > 5]
                st.session_state.questions = q_list[:10]
                st.session_state.start_time = time.time()
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")

if st.session_state.questions and st.session_state.q_index < len(st.session_state.questions):
    q = st.session_state.questions[st.session_state.q_index]
    
    st.progress((st.session_state.q_index + 1) / len(st.session_state.questions))
    st.subheader(f"প্রশ্ন {st.session_state.q_index + 1}: {q}")
    
    if st.button("প্রশ্নটি শুনতে ক্লিক করুন"):
        speak_text(q)

    elapsed = time.time() - st.session_state.start_time
    remaining = max(0, 60 - int(elapsed))
    
    st.write(f"⏳ সময় বাকি: **{remaining}** সেকেন্ড | 🏆 স্কোর: **{st.session_state.score}**")

    if remaining <= 0:
        st.error("সময় শেষ! ২ নম্বর কাটা গেল।")
        st.session_state.score -= 2
        st.session_state.q_index += 1
        st.session_state.start_time = time.time()
        time.sleep(2)
        st.rerun()

    user_ans = st.text_input("আপনার উত্তর (বাংলায়):", key=f"viva_{st.session_state.q_index}")
    
    if st.button("উত্তর দিন"):
        if user_ans:
            with st.spinner("যাচাই হচ্ছে..."):
                check = model.generate_content(f"Question: {q}\nAnswer: {user_ans}\nIs it correct? Reply only 'Yes' or 'No'.").text
                if "Yes" in check or "yes" in check:
                    st.session_state.score += 10
                    st.success("সঠিক! +১০")
                else:
                    st.session_state.score -= 2
                    st.error("ভুল! -২")
        else:
            st.session_state.score -= 2
            st.warning("উত্তর না দেওয়ায় ২ কাটা গেল।")
        
        st.session_state.q_index += 1
        st.session_state.start_time = time.time()
        time.sleep(1)
        st.rerun()

elif st.session_state.q_index >= 1 and st.session_state.q_index >= len(st.session_state.questions):
    st.balloons()
    st.header(f"ভাইভা শেষ! ফাইনাল স্কোর: {st.session_state.score}")
    if st.button("আবার শুরু করুন"):
        st.session_state.clear()
        st.rerun()

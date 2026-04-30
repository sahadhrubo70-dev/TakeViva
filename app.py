import streamlit as st
import google.generativeai as genai
from PIL import Image
import time
from gtts import gTTS
import base64

# Gemini API Configuration
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    # মডেলের নাম 'gemini-1.5-flash' নিশ্চিত করুন
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"API Configuration Error: {e}")

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

uploaded_file = st.file_uploader("যেকোনো ফাইল বা অস্পষ্ট ছবি আপলোড করুন", type=['png', 'jpg', 'jpeg'])

if uploaded_file and not st.session_state.questions:
    if st.button("ভাইভা শুরু করুন"):
        with st.spinner("ফাইল বিশ্লেষণ করা হচ্ছে..."):
            try:
                img = Image.open(uploaded_file)
                # কন্টেন্ট জেনারেশন প্রম্পট
                prompt = "Analyze this image and create 10 short educational questions in Bengali. Provide only the questions line by line."
                response = model.generate_content([prompt, img])
                
                if response.text:
                    st.session_state.questions = [q.strip() for q in response.text.split('\n') if len(q.strip()) > 5][:10]
                    st.session_state.start_time = time.time()
                    st.rerun()
                else:
                    st.error("AI কোনো প্রশ্ন তৈরি করতে পারেনি। আবার চেষ্টা করুন।")
            except Exception as e:
                st.error(f"Error: {e}")

if st.session_state.questions and st.session_state.q_index < len(st.session_state.questions):
    q = st.session_state.questions[st.session_state.q_index]
    
    st.progress((st.session_state.q_index + 1) / len(st.session_state.questions))
    st.subheader(f"প্রশ্ন {st.session_state.q_index + 1}: {q}")
    
    if st.button("প্রশ্নটি শুনুন"):
        speak_text(q)

    # Timer Logic
    elapsed_time = time.time() - st.session_state.start_time
    remaining_time = max(0, 60 - int(elapsed_time))
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("বাকি সময়", f"{remaining_time} সেকেন্ড")
    with col2:
        st.metric("বর্তমান স্কোর", st.session_state.score)

    if remaining_time <= 0:
        st.error("সময় শেষ! পরবর্তী প্রশ্নে যাওয়া হচ্ছে।")
        st.session_state.score -= 2
        st.session_state.q_index += 1
        st.session_state.start_time = time.time()
        time.sleep(2)
        st.rerun()

    user_ans = st.text_input("আপনার উত্তর লিখুন (বাংলায়):", key=f"ans_{st.session_state.q_index}")
    
    if st.button("উত্তর জমা দিন"):
        with st.spinner("যাচাই করা হচ্ছে..."):
            check_prompt = f"Question: {q}\nUser Answer: {user_ans}\nIs this correct? Just say 'Yes' or 'No'."
            result = model.generate_content(check_prompt).text
            
            if "Yes" in result or "হ্যাঁ" in result:
                st.session_state.score += 10
                st.success("সঠিক উত্তর! +১০")
            else:
                st.session_state.score -= 2
                st.error("ভুল উত্তর! -২")
        
        st.session_state.q_index += 1
        st.session_state.start_time = time.time()
        time.sleep(1.5)
        st.rerun()

elif st.session_state.q_index >= 10:
    st.balloons()
    st.header(f"ভাইভা শেষ! আপনার স্কোর: {st.session_state.score}")
    if st.button("আবার শুরু করুন"):
        for key in st.session_state.keys():
            del st.session_state[key]
        st.rerun()

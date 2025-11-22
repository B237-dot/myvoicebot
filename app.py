import streamlit as st
from openai import OpenAI
from gtts import gTTS
import tempfile
from io import BytesIO
import base64

st.set_page_config(page_title="AI VoiceBot", page_icon="🎤", layout="centered")

st.title("🎤 AI VoiceBot")
st.markdown("### Speak or upload a voice message — the bot will reply with audio!")

# --- OpenAI Client ---
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# --- Custom Recorder UI ---
st.markdown("""
<style>
.record-btn {
    background-color:#ff4b4b;
    padding:12px 25px;
    border-radius:8px;
    color:white;
    font-weight:bold;
    cursor:pointer;
}
</style>
""", unsafe_allow_html=True)

# Recorder Component
audio_bytes = st.audio_input("🎙️ Record your voice")

# Or Upload File
uploaded_audio = st.file_uploader("📤 Or upload an audio file", type=["mp3", "wav"])

audio_file = audio_bytes or uploaded_audio

# ---- Text → Speech ----
def speak(text):
    tts = gTTS(text)
    audio_fp = BytesIO()
    tts.write_to_fp(audio_fp)
    audio_fp.seek(0)
    return audio_fp.read()

# ---- Process ----
if audio_file:
    st.info("⏳ Processing audio...")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        tmp.write(audio_file.read())
        audio_path = tmp.name

    # ---- Transcribe ----
    st.write("🔊 **Transcribing your voice...**")
    transcript = client.audio.transcriptions.create(
        model="gpt-4o-transcribe",
        file=open(audio_path, "rb")
    )

    user_text = transcript.text
    st.success(f"**You said:** {user_text}")

    # ---- Generate reply ----
    st.write("🤖 **Generating AI response...**")

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": user_text}]
    )

    bot_reply = response.choices[0].message.content
    st.write(f"### 🤖 Bot says:\n{bot_reply}")

    # ---- Speak reply ----
    st.write("🔈 **Speaking reply...**")
    audio_output = speak(bot_reply)
    st.audio(audio_output, format="audio/mp3")

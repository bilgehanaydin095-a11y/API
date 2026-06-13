
import streamlit as st
import requests

st.set_page_config(page_title="SEO Brief Generator", page_icon="🏀", layout="centered")

st.title("🏀 SEO Brief Generator")
st.write("Anahtar kelimenizi yazın, Google rakiplerini analiz edip yapay zeka ile brief üretelim!")

keyword = st.text_input("Hedef Anahtar Kelime:", placeholder="Örn: en iyi basketbol ayakkabıları")
target_audience = st.text_input("Hedef Kitle:", value="Sporcular")

if st.button("Brief Oluştur 🔥", use_container_width=True):
    if not keyword:
        st.warning("Lütfen bir anahtar kelime girin!")
    else:
        with st.spinner("Google taranıyor ve Llama 3.1 analiz ediyor... Lütfen bekleyin..."):
            try:
                url = "http://127.0.0.1:8000/api/v1/generate-brief"
                payload = {
                    "keyword": keyword,
                    "language": "Turkish",
                    "target_audience": target_audience
                }
                
                response = requests.post(url, json=payload)
                
                if response.status_code == 200:
                    data = response.json()
                    st.success("Brief Başarıyla Oluşturuldu!")
                    st.subheader("📋 İçerik İskeleti ve Yazar Notları")
                    st.json(data)
                else:
                    st.error(f"API Hatası: {response.status_code}")
                    
            except Exception as e:
                st.error(f"Sunucuya bağlanılamadı. Önce main.py'yi çalıştırın! Hata: {e}")
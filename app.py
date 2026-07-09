import streamlit as st
import pandas as pd

st.set_page_config(page_title="Мой Бизнес-Дашборд", layout="wide")

# Красивый стиль карточек
st.markdown("""
<style>
    .card { background: #1e1e1e; padding: 20px; border-radius: 15px; border-left: 5px solid #00e676; margin-bottom: 10px; }
    .title { font-size: 20px; font-weight: bold; }
    .profit { font-size: 24px; color: #00e676; font-weight: bold; }
    .advice { background: #2a2a2a; padding: 10px; border-radius: 8px; margin-top: 10px; font-size: 14px; }
</style>
""", unsafe_allow_html=True)

st.title("📈 Моя Экипировка: Финансовый план")
uploaded_files = st.file_uploader("Перетащите сюда отчеты", accept_multiple_files=True)

# (Логика обработки остается, добавляем визуализацию)
if uploaded_files:
    # ... после обработки данных (переменная result) ...
    
    st.subheader("🚀 Твои лидеры продаж")
    cols = st.columns(3)
    for i, row in result.head(6).iterrows():
        # Определяем статус для цвета
        status_color = "#00e676" if row['Чистая_Прибыль'] > 5000 else "#ffeb3b"
        
        with cols[i % 3]:
            st.markdown(f"""
            <div class="card" style="border-left-color: {status_color}">
                <div class="title">{row['Название товара']}</div>
                <div class="profit">{row['Чистая_Прибыль']:,.0f} ₽</div>
                <div class="advice">
                    <b>💡 Рекомендация:</b> {get_advice(row)}
                </div>
            </div>
            """, unsafe_allow_html=True)

def get_advice(row):
    if row['Чистая_Прибыль'] > 10000: return "Хит продаж! Увеличьте рекламную ставку на 2%."
    if row['Чистая_Прибыль'] < 0: return "Внимание: товар убыточен! Проверьте логистику."
    return "Стабильный результат. Держите позиции."

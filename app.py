import streamlit as st
import pandas as pd

st.set_page_config(page_title="Умный Дашборд Ozon", layout="wide")
st.title("📊 Финансовый Дашборд Ozon")

uploaded_files = st.file_uploader("Перетащите сюда отчеты", accept_multiple_files=True)

# Функция поиска строки с заголовками
def get_df(file):
    # Сначала ищем строку, где есть слово "Артикул"
    df_temp = pd.read_excel(file, header=None, nrows=20)
    for i in range(len(df_temp)):
        if "артикул" in str(df_temp.iloc[i].values).lower():
            return pd.read_excel(file, header=i)
    return pd.read_excel(file) # если не нашли, пробуем обычный метод

if uploaded_files:
    dfs = []
    price_df = None
    
    for f in uploaded_files:
        try:
            df = get_df(f)
            df.columns = [str(c).strip() for c in df.columns]
            
            # Проверяем колонки
            if 'Цена продажи опт' in df.columns or 'Себестоимость' in df.columns:
                price_df = df
            else:
                dfs.append(df)
            st.write(f"✅ Прочитан файл: {f.name} (Строк: {len(df)})")
        except Exception as e:
            st.error(f"Ошибка в {f.name}: {e}")

    if dfs and price_df is not None:
        try:
            df_ozon = pd.concat(dfs, ignore_index=True)
            # Приводим артикулы к строкам для точного сопоставления
            df_ozon['Артикул'] = df_ozon['Артикул'].astype(str).str.strip()
            price_df['Артикул'] = price_df['Артикул'].astype(str).str.strip()
            
            merged = pd.merge(df_ozon, price_df, on='Артикул', how='inner')
            st.success("✅ Данные сопоставлены! Вот результат:")
            st.dataframe(merged)
        except Exception as e:
            st.error(f"Не удалось соединить таблицы: {e}")

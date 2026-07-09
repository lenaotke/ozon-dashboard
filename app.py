import streamlit as st
import pandas as pd

st.set_page_config(page_title="Умный Дашборд Ozon", layout="wide", page_icon="📈")
st.title("📊 Финансовый Дашборд Ozon")

uploaded_files = st.file_uploader("Перетащите сюда отчет Юнит-экономики и Прайс-лист", accept_multiple_files=True, type=['xlsx', 'xls'])

def find_header_row(file):
    df_temp = pd.read_excel(file, header=None, nrows=20)
    file.seek(0)
    for i in range(len(df_temp)):
        row_vals = [str(x).lower() for x in df_temp.iloc[i].values]
        if any('артикул' in val for val in row_vals):
            return i
    return 0

if uploaded_files:
    dfs = []
    price_df = None
    
    for f in uploaded_files:
        header = find_header_row(f)
        df = pd.read_excel(f, header=header)
        df.columns = [str(c).strip() for c in df.columns] # чистим заголовки
        
        # Если в файле есть колонка "Себестоимость" или "Цена продажи опт" - считаем его прайсом
        if 'Себестоимость' in df.columns or 'Цена продажи опт' in df.columns:
            price_df = df
        else:
            dfs.append(df)
            
    if dfs and price_df is not None:
        try:
            df_ozon = pd.concat(dfs, ignore_index=True)
            df_ozon['Артикул'] = df_ozon['Артикул'].astype(str).str.strip()
            price_df['Артикул'] = price_df['Артикул'].astype(str).str.strip()
            
            # Мержим
            merged = pd.merge(df_ozon, price_df[['Артикул', 'Цена продажи опт']], on='Артикул', how='left')
            
            # ... (здесь остальная логика расчетов)
            st.success("✅ Файлы успешно опознаны и сопоставлены!")
            st.write(merged.head()) # проверим, что данные склеились
        except Exception as e:
            st.error(f"Ошибка при сведении: {e}")
    else:
        st.error("Не могу опознать файлы. Убедитесь, что один из них содержит колонку 'Цена продажи опт'.")

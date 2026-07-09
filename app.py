import streamlit as st
import pandas as pd

st.set_page_config(page_title="Умный Дашборд Ozon", layout="wide", page_icon="📈")
st.title("📊 Финансовый Дашборд Ozon")

st.info("Перетащите в поле ниже СРАЗУ ВСЕ файлы (юнит-экономику и прайс-лист).")

# Теперь одно общее поле для всех файлов
uploaded_files = st.file_uploader("Загрузите все файлы отчетов (.xlsx)", accept_multiple_files=True, type=['xlsx', 'xls'])

def find_header_row(file):
    df_temp = pd.read_excel(file, header=None, nrows=15)
    file.seek(0)
    for i in range(len(df_temp)):
        row_vals = [str(x).lower() for x in df_temp.iloc[i].values]
        if any('артикул' in val for val in row_vals):
            return i
    return 0

if uploaded_files:
    file_ozon = None
    file_price = None
    
    # Автоматически распределяем файлы по ролям
    for f in uploaded_files:
        if "Юнит-экономика" in f.name:
            file_ozon = f
        elif "прайс" in f.name.lower():
            file_price = f
            
    if file_ozon and file_price:
        with st.spinner('Анализирую все загруженные отчеты...'):
            try:
                header_o = find_header_row(file_ozon)
                df_ozon = pd.read_excel(file_ozon, header=header_o)
                
                header_p = find_header_row(file_price)
                df_price = pd.read_excel(file_price, header=header_p)

                df_ozon['Артикул'] = df_ozon['Артикул'].astype(str).str.strip()
                df_price['Артикул'] = df_price['Артикул'].astype(str).str.strip()

                merged = pd.merge(df_ozon, df_price[['Артикул', 'Цена продажи опт']], on='Артикул', how='left')

                # Математика та же, что и была
                merged['Выручка'] = pd.to_numeric(merged['Выручка'], errors='coerce').fillna(0)
                merged = merged[merged['Выручка'] > 0]

                ozon_fee_cols = ['Вознаграждение Ozon', 'Эквайринг', 'Обработка отправления', 
                                 'Логистика', 'Доставка до места выдачи', 'Обработка возврата', 
                                 'Обратная логистика', 'Стоимость размещения']
                for col in ozon_fee_cols:
                    if col in merged.columns:
                        merged[col] = pd.to_numeric(merged[col], errors='coerce').fillna(0)

                merged['Total_Ozon_Fees'] = merged[[c for c in ozon_fee_cols if c in merged.columns]].sum(axis=1)
                merged['Себестоимость_Итог'] = pd.to_numeric(merged['Цена продажи опт'], errors='coerce').fillna(0) * \
                                              pd.to_numeric(merged['Доставлено товаров, шт'], errors='coerce').fillna(0)
                
                merged['Чистая_Прибыль'] = (merged['Выручка'] + merged['Total_Ozon_Fees'] - merged['Себестоимость_Итог'] - 
                                            (merged['Выручка'] * 0.06) - (merged['Выручка'] * 0.05))

                result = merged.groupby('Название товара').agg({'Выручка': 'sum', 'Чистая_Прибыль': 'sum'}).sort_values(by='Чистая_Прибыль', ascending=False)
                
                st.success(f"✅ Обработано файлов: {len(uploaded_files)}. Данные синхронизированы!")
                st.dataframe(result.style.background_gradient(cmap='Greens'), use_container_width=True)
            except Exception as e:
                st.error(f"Ошибка: {e}. Убедитесь, что в названиях файлов есть слова 'Юнит-экономика' и 'прайс'.")
    else:
        st.warning("Не могу найти нужные файлы. Убедитесь, что загрузили один файл с 'Юнит-экономика' и один с 'прайс' в названии.")

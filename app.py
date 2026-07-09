import streamlit as st
import pandas as pd

# Настройка страницы
st.set_page_config(page_title="Умный Дашборд Ozon", layout="wide", page_icon="📈")
st.title("📊 Финансовый Дашборд Ozon")

st.info("Перетащите сюда отчеты. Система автоматически сопоставит артикулы, вычтет себестоимость, все комиссии Ozon, 6% налога УСН и 5% на маркетинг.")

# Создаем две колонки для загрузки файлов
col1, col2 = st.columns(2)
with col1:
    file_ozon = st.file_uploader("1. Отчет Юнит-экономика Ozon (.xlsx)", type=['xlsx'])
with col2:
    file_price = st.file_uploader("2. Ваш Прайс-лист (.xls, .xlsx)", type=['xls', 'xlsx'])

# Функция для умного поиска строки с заголовками (шапки таблицы)
def find_header_row(file):
    df_temp = pd.read_excel(file, header=None, nrows=15)
    for i in range(len(df_temp)):
        row_vals = [str(x).lower() for x in df_temp.iloc[i].values]
        if any('артикул' in val for val in row_vals):
            return i
    return 0

# Запускаем расчет, только когда загружены оба файла
if file_ozon and file_price:
    with st.spinner('Свожу таблицы и считаю чистую прибыль...'):
        try:
            # 1. Загрузка данных
            header_o = find_header_row(file_ozon)
            df_ozon = pd.read_excel(file_ozon, header=header_o)
            
            header_p = find_header_row(file_price)
            df_price = pd.read_excel(file_price, header=header_p)

            # 2. Очистка ключей (чтобы лишние пробелы не мешали сопоставлению)
            df_ozon['Артикул'] = df_ozon['Артикул'].astype(str).str.strip()
            df_price['Артикул'] = df_price['Артикул'].astype(str).str.strip()

            # 3. Сопоставление отчета Ozon с прайсом
            df_price_clean = df_price[['Артикул', 'Цена продажи опт']]
            merged = pd.merge(df_ozon, df_price_clean, on='Артикул', how='left')

            # 4. Берем только товары с реальными продажами
            merged['Выручка'] = pd.to_numeric(merged['Выручка'], errors='coerce').fillna(0)
            merged = merged[merged['Выручка'] > 0]

            # 5. Сбор всех минусовых комиссий Ozon 
            ozon_fee_cols = ['Вознаграждение Ozon', 'Эквайринг', 'Обработка отправления', 
                             'Логистика', 'Доставка до места выдачи', 'Обработка возврата', 
                             'Обратная логистика', 'Стоимость размещения']
            
            for col in ozon_fee_cols:
                if col in merged.columns:
                    merged[col] = pd.to_numeric(merged[col], errors='coerce').fillna(0)
                else:
                    merged[col] = 0

            merged['Total_Ozon_Fees'] = merged[ozon_fee_cols].sum(axis=1)

            # 6. Финансовая математика
            merged['Цена продажи опт'] = pd.to_numeric(merged['Цена продажи опт'], errors='coerce').fillna(0)
            merged['Доставлено товаров, шт'] = pd.to_numeric(merged['Доставлено товаров, шт'], errors='coerce').fillna(0)
            
            # Расчет себестоимости = Оптовая цена * Количество доставленных
            merged['Себестоимость_Итог'] = merged['Цена продажи опт'] * merged['Доставлено товаров, шт']
            
            # Расчет налогов и маркетинга
            merged['Налог_6%'] = merged['Выручка'] * 0.06
            merged['Маркетинг_5%'] = merged['Выручка'] * 0.05

            # Финальная чистая прибыль (Выручка + Отрицательные комиссии Ozon - Себестоимость - Налог - Маркетинг)
            merged['Чистая_Прибыль'] = (merged['Выручка'] + 
                                        merged['Total_Ozon_Fees'] - 
                                        merged['Себестоимость_Итог'] - 
                                        merged['Налог_6%'] - 
                                        merged['Маркетинг_5%'])

            # 7. Группировка и вывод результатов на экран
            result = merged.groupby('Название товара').agg({
                'Выручка': 'sum',
                'Чистая_Прибыль': 'sum',
                'Доставлено товаров, шт': 'sum'
            }).reset_index()

            # Сортировка от самых прибыльных к убыточным
            result = result.sort_values(by='Чистая_Прибыль', ascending=False)
            
            st.success("✅ Отчеты успешно обработаны!")
            
            # Вывод главных метрик (KPI)
            total_rev = result['Выручка'].sum()
            total_profit = result['Чистая_Прибыль'].sum()
            
            m1, m2 = st.columns(2)
            m1.metric("Общая Выручка", f"{total_rev:,.0f} ₽".replace(',', ' '))
            m2.metric("Итоговая Чистая Прибыль", f"{total_profit:,.0f} ₽".replace(',', ' '))
            
            st.subheader("🏆 ТОП Товаров по реальной марже")
            
            # Переименование колонок для красоты интерфейса
            result.columns = ['Название экипировки', 'Выручка', 'Чистая прибыль (руб)', 'Продано (шт)']
            
            # Отрисовка таблицы с градиентом
            st.dataframe(result.style.format({
                'Выручка': '{:,.0f} ₽',
                'Чистая прибыль (руб)': '{:,.0f} ₽',
                'Продано (шт)': '{:.0f}'
            }).background_gradient(subset=['Чистая прибыль (руб)'], cmap='Greens'), use_container_width=True)

        except Exception as e:
            st.error(f"Произошла ошибка при обработке: {e}")
            st.write("Убедитесь, что загружен именно отчет 'Юнит-экономика' и 'Прайс-лист'.")

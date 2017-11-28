import csv
import access


frequencies = {'a', 'q', 'm', 'd'}

#  Читаем частоты - сравниваем с константами
assert set(access.get_freq()) == frequencies

for freq in frequencies:
    # Читаем список переменных для каждой частоты, читаем фрейм для каждой частоты
    names = access.get_names(freq)
    frame = access.get_frame(freq)

    # Сравниваем список переменных
    assert (names == frame.keys()).all()

    series = []
    # Внутри каждой частоты идем по переменным, получаем дату начала и конца серии, запрашиваем серию с началом и концом
    for name in names:
        info = access.get_info(freq, name)
        start_date = info[freq]['start_date']
        latest_date = info[freq]['latest_date']
        series.append(access.get_ts(freq=freq, name=name, start_date=start_date, end_date=latest_date).to_frame())

    # для одной частоты и нескольких переменных из этой частоты читаем ряды данных, объединяем в фрейм.
    joined_frame = access.join_df(series)

    # Сравниваем с фреймом полученным от сервера
    assert (joined_frame == frame).all().all()

# Проверяем что станадртный API/datapoints и кастом API выдает одни и те же данные
standard_api_response = access.get_datapoints(freq='m', name='CPI_rog', start_date='2015-01-01', end_date='2017-12-31', format='csv')
custom_api_response = access.get_custom_series(freq='m', name='CPI', suffix='rog', start='2015', end='2017')

assert (custom_api_response == standard_api_response).all()
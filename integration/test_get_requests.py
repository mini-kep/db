from access import get_freq, get_names, get_df, get_info, get_datapoints, get_datapoints_full_response,\
    get_ts, join_df, get_custom_series


frequencies = {'a', 'q', 'm', 'd'}

if __name__ == '__main__':

    #  АПИ возвращает ожидаемый сет частот
    assert set(get_freq()) == frequencies

    for freq in frequencies:
        #  Получаем фрейм и список переменных для частоты
        df = get_df(freq)
        names = get_names(freq)

        #  Список переменных фрейма идентичен списку переменных из АПИ
        assert (names == df.keys()).any()

        series = []
        for name in names:

            #  Получаем начальную и конечную дату серии для переменной
            info = get_info(freq, name)
            start_date = info[freq]['start_date']
            latest_date = info[freq]['latest_date']

            #  Получаем серию для переменной
            series.append(get_ts(freq=freq, name=name, start_date=start_date, end_date=latest_date).to_frame())

        #  Объединяем список серий в фрейм
        joined_series = join_df(series)

        # Фрейм идентичен фрейму полученному ранее
        assert (joined_series == df).any().any()

    # Неверная частота
    response = get_datapoints_full_response(freq='z', name='CPI_roq')
    assert response.status_code == 422
    assert set(response.json()['allowed']) == frequencies

    # Неверная переменная
    response = get_datapoints_full_response(freq='q', name='ABC')
    assert response.status_code == 422
    assert response.json()['allowed'] == get_names('q')

    # Начальная дата в будущем
    response = get_datapoints_full_response(freq='d', name='BRENT', start_date='2025-01-01')
    assert response.status_code == 422
    assert isinstance(response.json(), dict)

    # Начальная дата в больше конечной
    response = get_datapoints_full_response(freq='d', name='BRENT', start_date='2015-01-01', end_date='2000-01-01')
    assert response.status_code == 422
    assert isinstance(response.json(), dict)


    #  Кастомное АПИ возвращает то же, что и стандартное
    standard_api_response = get_datapoints(freq='m', name='CPI_rog', start_date='2015-01-01', end_date='2017-12-31', format='csv')
    custom_api_response = get_custom_series(freq='m', name='CPI', suffix='rog', start='2015', end='2017')

    assert (custom_api_response == standard_api_response).any()
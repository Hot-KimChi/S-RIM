import pandas as pd
import requests

def get_price(code, stock_date):
    try:
        headers = {'User-agent':"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"}
        url = f'http://finance.naver.com/item/sise_day.nhn?code={code}&page=1'
        print("요청 stock URL = {}".format(url))
        table = pd.read_html(requests.get(url, headers=headers).text, encoding='cp949')
        table = table[0]
        table = table.dropna(how='all', axis=0)
        table['code'] = code
        table = table[table.날짜 == stock_date]

        return table

    except:
        print('price_error detection!')
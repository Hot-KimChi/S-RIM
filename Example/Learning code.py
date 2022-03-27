import pandas as pd  # 데이터프레임을 다루는 패키지
import datetime as dt  # 시간을 다루는 패키지
# import matplotlib.pyplot as plt  # 그래프 시각화 패키지
# from matplotlib import style

def read_stock_price_page(stock_code, page_num):
    '''
    네이버 주식시세 페이지에 접속하여 table을 dataframe으로 가져와서 정리
    '''
    target_url = ('http://finance.naver.com/item/sise_day.nhn?code='+ stock_code + '&page=' + str(page_num))
    print(target_url)
    data = pd.read_html(target_url)
    data = data[0]
    data.columns = ['날짜', '당일종가', '전일종가', '시가', '고가', '저가', '거래량']
    price_data = data.dropna(axis=0, how='any')
    price_data = price_data.drop(price_data.index[0])
    price_data = price_data.reset_index(drop=True)
    price_data['날짜'] = pd.to_datetime(price_data['날짜'], format='%Y/%m/%d')
    return price_data


# def stock_price_pages_to_df(code, days_limit=30):
#     '''
#     오늘부터 days_limit 일수 만큼 이전 날짜 주가를 가져온다.
#     '''
#
#     df_list_price = []
#     page = 1
#     while True:
#         try:
#             data = read_stock_price_page(code, page)
#             time_limit = dt.datetime.now() - data['날짜'][0]
#             if time_limit.days > days_limit: break
#             df_list_price.append(data)
#             page = page + 1
#
#         except:
#             break
#     df_price = pd.concat(df_list_price)
#     df_price = df_price.reset_index(drop=True)
#
#     return df_price
#
#     # 함수를 실행하여 KH바텍(060720)의 과거 30일 주가정보를 가져온다.


stock_code = '060720'
a = read_stock_price_page('060720', 1)

# 주식 시세(당일종가) 그래프를 그린다.
# style.use('ggplot')  # 그래프 스타일 지정
# plt.plot(df.날짜, df.당일종가.astype(int))
# plt.show()







# def get_price(code, stock_date):
#     try:
#
#         url = 'http://finance.naver.com/item/sise_day.nhn?code={code}'.format(code=code)
#         result = requests.post(url)
#
#         data = result.text.replace("'", '"').strip()
#         print(data[:10])
#
#         # print("요청 stock URL = {}".format(url))
#         # df = DataFrame()
#         # pg_url = '{url}&page'.format(url=url)
#         # print(pd.read_html(pg_url))
#         # df = df.append(pd.read_html(pg_url, header=0)[0], ignore_index=True)
#         # print(df)
#         # print(df)
#         # df = df.dropna()
#         # df['code'] = code
#         # df = df[df.날짜 == stock_date]
#         #
#         # return df
#
#     except:
#         print('price_error detection!')





## Company code 가져오기: http://kind.krx.co.kr/corpgeneral/corpList.do?method=download&searchType=13
code_df = pd.read_excel(stock_list_read)
code_df.종목코드 = code_df.종목코드.map("{:06d}".format)
code_df = code_df[['Symbol', 'Name', 'Sector', 'Industry']]
code_df = code_df.rename(columns={'Symbol': 'code', 'Name': 'name', '업종': 'industry', '주요제품': 'main_product'})
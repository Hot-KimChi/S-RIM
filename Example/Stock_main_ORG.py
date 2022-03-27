import pandas as pd
from def_param import get_fnguide_table as def_fn
from def_param import get_price as def_pr
from def_param import get_cash_flow as def_ca
import sqlite3


stock_date = input('적정주가 계산에 사용할 Stock_date(e.g. 2020.06.12) :')
stock_list_read = input('읽어 올 stock-list 파일 이름 :')


## Company code 가져오기: http://kind.krx.co.kr/corpgeneral/corpList.do?method=download&searchType=13
code_df = pd.read_excel(stock_list_read)
code_df.종목코드 = code_df.종목코드.map("{:06d}".format)
code_df = code_df[['종목코드', '회사명', '업종', '주요제품']]
code_df = code_df.rename(columns={'종목코드': 'code', '회사명': 'name', '업종': 'industry', '주요제품': 'main_product'})


code_list = code_df['code'].values.tolist()
finance_year = pd.DataFrame(columns=[])
finance_quarter = pd.DataFrame(columns=[])
cash_year = pd.DataFrame(columns=[])
cash_quarter = pd.DataFrame(columns=[])
price_df = pd.DataFrame(columns=[])


count = 1
Total_count = len(code_list)

for i in code_list:
    try:
        finance_year = finance_year.append(def_fn.get_fnguide_table(i)[0])             ## fnguide 에서 year 재무제표 가지고 오기
        finance_quarter = finance_quarter.append(def_fn.get_fnguide_table(i)[1])       ## fnguide 에서 분기 재무제표 가지고 오기
        cash_year = cash_year.append(def_ca.get_cash_flow(i)[0])                       ## fnguide 에서 cash_flow 가지고 오기
        cash_quarter = cash_quarter.append(def_ca.get_cash_flow(i)[1])
        print(count, '/', Total_count)
        print(i)
        price_df = price_df.append(def_pr.get_price(i, stock_date))             ## Naver 주가 가지고 오기
        count += 1
        print()
    except:
        print('error detection!')


## SQL_DB에 저장
DB_name = 'DB_' + stock_date.replace('.', '') + '.db'

con = sqlite3.connect(DB_name)
cur = con.cursor()

code_df.to_sql('code', con)
finance_year.to_sql('finance_year', con)
finance_quarter.to_sql('finance_quarter', con)
cash_year.to_sql('cash_flow_year', con)
cash_quarter.to_sql('cash_flow_quarter', con)
price_df.to_sql('price', con)
cur.close()
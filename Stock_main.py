import pandas as pd
from datetime import datetime
import FinanceDataReader as fdr
from def_param import get_fnguide_table as def_fn
from def_param import get_price as def_pr
from def_param import get_cash_flow as def_ca
import sqlite3


df_krx = fdr.StockListing("KRX")
stock_date = datetime.today().strftime('%Y.%m.%d')


code_df = df_krx[['Symbol', 'Name', 'Sector', 'Industry']]
code_df = code_df.rename(columns={'Symbol': 'code'})
code_df = code_df.dropna(how='any', axis=0)                                     ##결손데이터(ETF)는 제외하여 code_df update


code_list = code_df['code'].values.tolist()
finance = pd.DataFrame(columns=[])
cash_flow = pd.DataFrame(columns=[])
price_df = pd.DataFrame(columns=[])


count = 1
Total_count = len(code_list)

for i in code_list:
    try:
        finance = finance.append(def_fn.get_fnguide_table(i))                   ## fnguide 에서 재무제표 가지고 오기(year & quarter)
        cash_flow = cash_flow.append(def_ca.get_cash_flow(i))                   ## fnguide 에서 cash_flow 가지고 오기(year & quarter)
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

code_df.to_sql('code_table', con)
finance.to_sql('finance_table', con)
cash_flow.to_sql('cash_flow_table', con)
price_df.to_sql('price_table', con)
cur.close()
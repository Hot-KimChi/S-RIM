import sqlite3
from pandas import DataFrame


stock_DB_read = input('읽어 올 DB 이름 :')
date = stock_DB_read[3:11]
conn = sqlite3.connect(stock_DB_read)
cur = conn.cursor()


## 아래 query문 where문 날짜 수정.

query = '''

select 
    code
    , name
    , industry
    , main_product
    , debt_ratio
    , market_cap
    , end_price
    , per_eps
    , pbr_bps    
    , ROUND((per_eps-end_price)*100/end_price, 2) as return_rate_per
    , ROUND((pbr_bps-end_price)*100/end_price, 2) as return_rate_pbr
    , roe_e, roe_2, roe_3, roe_4

from
(
    select
    a.code
    , c.name
    , c.industry
    , c.main_product
    , b.종가 as end_price
    , sum(case when 부채비율 < 125 then 1 else 0 end) as debt_ratio
    , ROUND((sum(PER) / count(*)) * sum(case when inx = 1 then EPS else 0 end), 2) as per_eps
    , ROUND((sum(PBR) / count(*)) * sum(case when inx = 1 then BPS else 0 end), 2) as pbr_bps
    , sum(case when inx = 1 then ROE else 0 end) as roe_e
    , sum(case when inx = 2 then ROE else 0 end) as roe_2
    , sum(case when inx = 3 then ROE else 0 end) as roe_3
    , sum(case when inx = 4 then ROE else 0 end) as roe_4
    , sum(case when inx = 1 then 시가총액_억 else 0 end) as market_cap
    , sum(case when inx = 2 then 지배주주지분 else 0 end) as main_price
    , sum(case when inx = 1 then 유통주식수 else 0 end) as distribute_stock
    , sum(case when inx = 2 then BPS else 0 end) as bps
    , sum(case when 당기순이익 > 0 then 1 else 0 end) as earn 
    , sum(case when ROE > 0 then 1 else 0 end) as roe 
    , sum(case when 영업이익 > 0 then 1 else 0 end) as earning
    , sum(case when 배당수익률 > 0 then 1 else 0 end) as distribution
    , 7.84 as discount_rate
from 
(   select * , row_number() over(partition by code order by year desc) as inx
    from finance
) a
join 
(
    select code, 종가
    from price
    where 날짜 = '2020.08.11'
) b
on a.code = b.code
join
(
select code, name, industry, main_product
from code
) c 
on a.code = c.code
group by a.code
) x

order by return_rate_per desc, return_rate_pbr desc
'''
# where
# earn >= 5 and roe >= 5 and earning >= 5 and debt_ratio >= 5 and roe_e > discount_rate and market_cap > 1700
# distribution >= 5 and roe_improve = 1
# where
# earn >= 5 and earning >= 5 and debt_ratio >= 5

# def get_col_names(table):
#     query = 'SELECT * FROM ' + f'{table}'
#     cur.execute(query)
#     return [member[0] for member in cur.description]
#
#
# print(get_col_names('price'))

cur.execute(query)


data = DataFrame(cur.fetchall())
result_stock = data.rename(columns={0 : 'Code', 1 : 'Name', 2 : 'Industry', 3 : 'Main_product',
                                    4 : '부채비율', 5 : '시가총액(억)', 6 : '종가',
                                    7 : 'PER_EPS', 8 : 'PBR_BPS', 9 : 'Return_rate(PER)', 10 : 'Return_rate(PBR)',
                                    11: 'ROE_20', 12: 'ROE_19', 13: 'roe_past_2', 14: 'roe_past_3'})

result_stock.to_csv(f'Result_PER_PBR_{date}.csv', encoding='utf-8-sig')


## 1) 100% 이하 부채비율 --> 자산 = 자본 + 부채, 부채비율(%) = (부채 / 자본) x 100
## 2) 영업이익의 지속적 성장.
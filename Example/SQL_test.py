import sqlite3
from pandas import DataFrame

conn = sqlite3.connect('DB_20210810.db')
cur = conn.cursor()

query = '''
    select
    code
    , sum(case when 부채비율 < 100 then 1 else 0 end) as debt_ratio
    , ROUND((sum(PER) / count(*)) * sum(case when inx = 2 then EPS else 0 end), 2) as per_eps
    , ROUND((sum(PBR) / count(*)) * sum(case when inx = 2 then BPS else 0 end), 2) as pbr_bps
    , sum(case when inx = 1 then ROE else 0 end) as roe_1
    , sum(case when inx = 2 then ROE else 0 end) as roe_2
    , sum(case when inx = 3 then ROE else 0 end) as roe_3
    , sum(case when inx = 4 then ROE else 0 end) as roe_4
    , sum(case when inx = 2 then 지배주주지분 else 0 end) as main_stock
    , sum(case when inx = 2 then 유통주식수 else 0 end) as distribute_stock
    , sum(case when inx = 1 then EPS else 0 end) as eps
    , sum(case when inx = 2 then BPS else 0 end) as bps
    , sum(case when 당기순이익 > 0 then 1 else 0 end) as earn 
    , sum(case when ROE > 0 then 1 else 0 end) as roe 
    , sum(case when 영업이익 > 0 then 1 else 0 end) as earning
    , sum(case when 배당수익률 > 0 then 1 else 0 end) as distribution
from 
(   select * , row_number() over(partition by code order by year desc) as inx
    from finance_table
)

'''

cur.execute(query)

data = DataFrame(cur.fetchall())
data.to_csv('sql_test.csv')

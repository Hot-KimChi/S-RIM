import sqlite3
from pandas import DataFrame


# stock_DB_read = input('읽어 올 DB 이름 :')
# date = stock_DB_read[3:11]
# conn = sqlite3.connect(stock_DB_read)
conn = sqlite3.connect('DB_20200814.db')
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
    , roe_e, roe_2, roe_3, roe_4
    , case when roe_2 > roe_3 and roe_3 > roe_4 then 1 else 0 end as roe_improve
    , cash_20, cash_19, cash_18, cash_17
 
 from
(
    select
    a.code
    , c.name
    , c.industry
    , c.main_product
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
    , sum(case when b.inx1 = 1 then 영업활동으로인한현금흐름 else 0 end) as cash_20
    , sum(case when b.inx1 = 2 then 영업활동으로인한현금흐름 else 0 end) as cash_19
    , sum(case when b.inx1 = 3 then 영업활동으로인한현금흐름 else 0 end) as cash_18
    , sum(case when b.inx1 = 4 then 영업활동으로인한현금흐름 else 0 end) as cash_17
    
from 
(   select * , row_number() over(partition by code order by year desc) as inx
    from finance
) a
join 
(
    select * , row_number() over(partition by code order by year desc) as inx1
    from cash_flow
    group by code
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

'''

cur.execute(query)


data = DataFrame(cur.fetchall())
result_stock = data.rename(columns={0 : 'Code', 1 : 'Name', 2 : 'Industry', 3 : 'Main_product',
                                    4 : '부채비율', 5 : '시가총액_억', 6 : 'ROE_20(e)',
                                    7 : 'ROE_19', 8 : 'roe_past_2', 9 : 'roe_past_3', 10 : 'ROE_Improve',
                                    11 : 'Cash_2020(e)', 12 : 'Cash_2019', 13 : 'Cash_2018', 14 : 'Cash_2017'})

result_stock.to_csv('Result_SanTa.csv', encoding='utf-8-sig')


## 1) 100% 이하 부채비율 --> 자산 = 자본 + 부채, 부채비율(%) = (부채 / 자본) x 100
## 2) 영업이익의 지속적 성장.
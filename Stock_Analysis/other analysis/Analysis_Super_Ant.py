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
    , case when eps < 0 then 0 else ROUND(eps * classification * 100, 2) end as estimate_price
    , case when eps < 0 then 0 else ROUND((eps * classification) / end_price, 2) end as return_rate   
    , roe_20e, roe_19, roe_past_2, roe_past_3
    , case when earning_e <= 0 then 0 else earning_e end
    , classification
    , case when earning_e <= 0 then 0 else earning_e * classification end
    , case when earning_e <= 0 then 0 else ROUND((((earning_e * classification) - market_cap) / market_cap), 2) end as return_rate2
                  
from
(
    select
    a.code
    , c.name
    , c.industry
    , c.main_product
    , b.종가 as end_price
    , case when main_product like '%반도체%' or main_product like '%2차전지%' or industry like '%의료용%' then 20 else 10 end as classification
    , sum(case when 부채비율 < 125 then 1 else 0 end) as debt_ratio
    , sum(case when inx = 1 then ROE else 0 end) as roe_20e
    , sum(case when inx = 2 then ROE else 0 end) as roe_19
    , sum(case when inx = 3 then ROE else 0 end) as roe_past_2
    , sum(case when inx = 4 then ROE else 0 end) as roe_past_3
    , sum(case when inx = 1 then 시가총액_억 else 0 end) as market_cap
    , sum(case when inx = 1 then EPS else 0 end) as eps
    , sum(case when 당기순이익 > 0 then 1 else 0 end) as earn 
    , sum(case when ROE > 0 then 1 else 0 end) as roe 
    , sum(case when inx = 1 then 영업이익 else 0 end) as earning_e
    , sum(case when 영업이익 > 0 then 1 else 0 end) as earning
    , sum(case when 배당수익률 > 0 then 1 else 0 end) as distribution
from 
(   select * , row_number() over(partition by code order by year desc) as inx
    from finance_year
) a
join 
(
    select code, 종가
    from price
    where 날짜 = '2020.09.02'
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

ORDER BY return_rate2 desc, return_rate desc
'''
# where
# earn >= 5 and earning >= 5 and debt_ratio >= 5

# where
# earn >= 5 and roe >= 5 and earning >= 5 and debt_ratio >= 5 and roe_e > discount_rate and market_cap > 1700
# distribution >= 5 and roe_improve = 1


cur.execute(query)


data = DataFrame(cur.fetchall())
result_stock = data.rename(columns={0 : 'Code', 1 : 'Name', 2 : 'Industry', 3 : 'Main_product',
                                    4 : '부채비율', 5 : '시가총액(억)', 6 : '종가',
                                    7 : 'EPS*ROE', 8 : 'Return_Rate', 9 : 'ROE_20(E)', 10 : 'ROE_19', 11 : 'roe_past_2', 12 : 'roe_past_3',
                                    13 : '영업이익 - 20E', 14: '그룹', 15: 'Est.시가총액(억)', 16: 'Est / 현재 (%)'})

result_stock.to_csv(f'Result_Super_Ant_{date}.csv', encoding='utf-8-sig')


## 1) 100% 이하 부채비율 --> 자산 = 자본 + 부채, 부채비율(%) = (부채 / 자본) x 100
## 2) 영업이익의 지속적 성장.
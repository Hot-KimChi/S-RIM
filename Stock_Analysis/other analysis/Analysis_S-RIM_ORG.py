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
    , case when roe_20e <= discount_rate then 0 else 1 as SRIM    
    , case when roe_20e <= discount_rate 
        then 0 
        else ROUND((main_price  + main_price * (roe_20e/100 - discount_rate/100) * (0.8 / (1 + discount_rate/100 - 0.8))) * 100000000 / distribute_stock) end as SRIM_Price_Buy
    , case when roe_20e <= discount_rate 
        then 0 
        else ROUND((main_price  + main_price * (roe_20e/100 - discount_rate/100) * (0.9 / (1 + discount_rate/100 - 0.9))) * 100000000 / distribute_stock) end as SRIM_Price_Sell_1st
    , case when roe_20e <= discount_rate 
        then 0 
        else ROUND((main_price  + main_price * (roe_20e/100 - discount_rate/100) / (discount_rate/100)) * 100000000 / distribute_stock) end as SRIM_Price_Sell_2nd
    , case when roe_20e <= discount_rate 
        then 0 
        else ROUND((main_price  + main_price * (roe_20e/100 - discount_rate/100) * (0.8 / (1 + discount_rate/100 - 0.8))) * 100000000 / distribute_stock / end_price, 2) end as return_rate1
    , case when roe_20e <= discount_rate 
        then 0 
        else ROUND((main_price  + main_price * (roe_20e/100 - discount_rate/100) / (discount_rate/100)) * 100000000 / distribute_stock / end_price, 2) end as return_rate2
    , roe_20e, roe_19, roe_past_2, roe_past_3
    , ROUND((3*roe_19 + 2*roe_past_2 + 1*roe_past_3) / 6, 2) as Average_ROE_20_E
    , case when roe_19 > roe_past_2 and roe_past_2 > roe_past_3 then 1 else 0 end as roe_improve
    , ROUND(bps * ((3*roe_19 + 2*roe_past_2 + 1*roe_past_3) / 6) / discount_rate / end_price, 2) as return_rate3
    , earning_est
    , earning_past
    , earning_past_2
    , earning_past_3
    , classification
    , ROUND(earning_est * classification / market_cap, 2) as return_earn 
from
(
    select
    a.code
    , c.name
    , c.industry
    , c.main_product
    , b.종가 as end_price
    , case when main_product like '%반도체%' or main_product like '%2차전지%' or main_product like '%게임%' then 15 else 10 end as classification
    , sum(case when 부채비율 < 125 then 1 else 0 end) as debt_ratio
    , ROUND((sum(PER) / count(*)) * sum(case when inx = 1 then EPS else 0 end), 2) as per_eps
    , ROUND((sum(PBR) / count(*)) * sum(case when inx = 1 then BPS else 0 end), 2) as pbr_bps
    , sum(case when inx = 1 then ROE else 0 end) as roe_20e
    , sum(case when inx = 2 then ROE else 0 end) as roe_19
    , sum(case when inx = 3 then ROE else 0 end) as roe_past_2
    , sum(case when inx = 4 then ROE else 0 end) as roe_past_3
    , sum(case when inx = 1 then 시가총액_억 else 0 end) as market_cap
    , sum(case when inx = 2 then 지배주주지분 else 0 end) as main_price
    , sum(case when inx = 1 then 유통주식수 else 0 end) as distribute_stock
    , sum(case when inx = 2 then BPS else 0 end) as bps
    , sum(case when inx = 1 then 영업이익 else 0 end) as earning_est
    , sum(case when inx = 2 then 영업이익 else 0 end) as earning_past
    , sum(case when inx = 3 then 영업이익 else 0 end) as earning_past_2
    , sum(case when inx = 4 then 영업이익 else 0 end) as earning_past_3
    , sum(case when 당기순이익 > 0 then 1 else 0 end) as earn 
    , sum(case when ROE > 0 then 1 else 0 end) as roe
    , sum(case when 배당수익률 > 0 then 1 else 0 end) as distribution
    , 7.81 as discount_rate
from 
(   select * , row_number() over(partition by code order by year desc) as inx
    from finance_year
) a
join 
(
    select code, 종가
    from price
    where 날짜 = '2020.09.25'
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

order by return_rate1 desc, return_rate2 desc, return_rate3 desc
'''
# where
# earn >= 5 and earning >= 5 and debt_ratio >= 5

# where
# earn >= 5 and roe >= 5 and earning >= 5 and debt_ratio >= 5 and roe_e > discount_rate and market_cap > 1700
# distribution >= 5 and roe_improve = 1



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
                                    7 : '매수', 8 : '매도_1st', 9 : '매도_2nd', 10 : '매수비율(S-RIM)', 11 : '매도비율(S-RIM)',
                                    12 : 'ROE_20', 13 : 'ROE_19', 14 : 'roe_past_2', 15 : 'roe_past_3', 16 : 'Average_ROE_20(E)', 17 : 'ROE_improve', 18 : 'Return_rate(BPS&ROE)',
                                    19 : '영업이익_20(E)', 20 : '영업이익_19', 21 : '영업이익_18', 22 : '영업이익_17', 23 : 'Multiple', 24 : '영업이익_비율'
                                    })

result_stock.to_csv(f'Result_S-RIM_{date}.csv', encoding='utf-8-sig')


## 1) 100% 이하 부채비율 --> 자산 = 자본 + 부채, 부채비율(%) = (부채 / 자본) x 100
## 2) 영업이익의 지속적 성장.
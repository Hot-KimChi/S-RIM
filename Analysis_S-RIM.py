import sqlite3
from datetime import datetime
import openpyxl
from pandas import DataFrame

DB_date = datetime.today().strftime('%Y%m%d')
stock_DB_read = 'DB_'+DB_date+'.db'
date = stock_DB_read[3:11]
conn = sqlite3.connect(stock_DB_read)
cur = conn.cursor()


## 아래 query문 where문 날짜 수정.

query = '''

select 
    code
    , name
    , Sector
    , Industry
    , debt_ratio
    , market_cap
    , end_price
    , case  when roe_est >= discount_rate then 'S-RIM'
            when roe_est = 0 then 'Ave ROE'  
            else 'Not good' end as SRIM           
            
    , case  when roe_est >= discount_rate 
                then ROUND((main_price  + main_price * (roe_est/100 - discount_rate/100) * (0.8 / (1 + discount_rate/100 - 0.8))) * 100000000 / distribute_stock)
            when roe_est = 0 
                then ROUND((main_price  + main_price * ((3*roe_past + 2*roe_past_2 + 1*roe_past_3) / 6/100 - discount_rate/100) * (0.8 / (1 + discount_rate/100 - 0.8))) * 100000000 / distribute_stock)       
            else 0 end as SRIM_Price_Buy 
    
    , case  when roe_est >= discount_rate 
                then ROUND((main_price  + main_price * (roe_est/100 - discount_rate/100) * (0.9 / (1 + discount_rate/100 - 0.9))) * 100000000 / distribute_stock)
            when roe_est = 0 
                then ROUND((main_price  + main_price * ((3*roe_past + 2*roe_past_2 + 1*roe_past_3) / 6/100 - discount_rate/100) * (0.9 / (1 + discount_rate/100 - 0.9))) * 100000000 / distribute_stock)       
            else 0 end as SRIM_Price_1st_Sell 
    
    , case  when roe_est >= discount_rate 
                then ROUND((main_price  + main_price * (roe_est/100 - discount_rate/100) / (discount_rate/100)) * 100000000 / distribute_stock)
            when roe_est = 0 
                then ROUND((main_price  + main_price * ((3*roe_past + 2*roe_past_2 + 1*roe_past_3) / 6/100 - discount_rate/100) / (discount_rate/100)) * 100000000 / distribute_stock)       
            else 0 end as SRIM_Price_2nd_Sell 
     
    , case  when roe_est >= discount_rate 
                then ROUND((main_price  + main_price * (roe_est/100 - discount_rate/100) * (0.8 / (1 + discount_rate/100 - 0.8))) * 100000000 / distribute_stock / end_price, 2)
            when roe_est = 0 
                then ROUND((main_price  + main_price * ((3*roe_past + 2*roe_past_2 + 1*roe_past_3) / 6/100 - discount_rate/100) * (0.8 / (1 + discount_rate/100 - 0.8))) * 100000000 / distribute_stock / end_price, 2)       
            else 0 end as return_rate1 
    
    , case  when roe_est >= discount_rate 
                then ROUND((main_price  + main_price * (roe_est/100 - discount_rate/100) / (discount_rate/100)) * 100000000 / distribute_stock / end_price, 2)
            when roe_est = 0 
                then ROUND((main_price  + main_price * ((3*roe_past + 2*roe_past_2 + 1*roe_past_3) / 6/100 - discount_rate/100) / (discount_rate/100)) * 100000000 / distribute_stock / end_price, 2)       
            else 0 end as return_rate2 
    
    , roe_est, roe_past, roe_past_2, roe_past_3
    , case when roe_past > roe_past_2 and roe_past_2 > roe_past_3 then 'Yes' else 'No' end as roe_improve
    , ROUND(bps * ((3*roe_past + 2*roe_past_2 + 1*roe_past_3) / 6) / discount_rate / end_price, 2) as return_rate3
    , earning_est
    , earning_past
    , earning_past_2
    , earning_past_3
    , ROUND(earning_est / earning_past * 100) as YoY_earn_est
    , ROUND(earning_past / earning_past_2 * 100) as YoY_earn_past
    , ROUND(earning_past_2 / earning_past_3 * 100) as YoY_earn_past_2
    , classification
    , ROUND(earning_est * classification / market_cap, 2) as return_earn
    , sales_est
    , sales_past
    , sales_past_2
    , sales_past_3 
    , ROUND(sales_est / sales_past * 100) as YoY_sales_est
    , ROUND(sales_past / sales_past_2 * 100) as YoY_sales_past
    , ROUND(sales_past_2 / sales_past_3 * 100) as YoY_sales_past_2
from
(
    select
    a.code
    , c.name
    , c.Sector
    , c.Industry
    , b.종가 as end_price
    , case when Industry like '%반도체%' or Industry like '%2차전지%' or Industry like '%게임%' then 15 else 10 end as classification
    , sum(case when 부채비율 < 125 then 1 else 0 end) as debt_ratio
    , ROUND((sum(PER) / count(*)) * sum(case when inx = 4 then EPS else 0 end), 2) as per_eps
    , ROUND((sum(PBR) / count(*)) * sum(case when inx = 4 then BPS else 0 end), 2) as pbr_bps
    , sum(case when inx = 5 then ROE else 0 end) as roe_est
    , sum(case when inx = 4 then ROE else 0 end) as roe_past
    , sum(case when inx = 3 then ROE else 0 end) as roe_past_2
    , sum(case when inx = 2 then ROE else 0 end) as roe_past_3
    , sum(case when inx = 5 then 시가총액_억 else 0 end) as market_cap
    , sum(case when inx = 4 then 지배주주지분 else 0 end) as main_price
    , sum(case when inx = 5 then 유통주식수 else 0 end) as distribute_stock
    , sum(case when inx = 4 then BPS else 0 end) as bps
    , sum(case when inx = 5 then 영업이익 else 0 end) as earning_est
    , sum(case when inx = 4 then 영업이익 else 0 end) as earning_past
    , sum(case when inx = 3 then 영업이익 else 0 end) as earning_past_2
    , sum(case when inx = 2 then 영업이익 else 0 end) as earning_past_3
    , sum(case when inx = 5 then 매출액 else 0 end) as sales_est
    , sum(case when inx = 4 then 매출액 else 0 end) as sales_past
    , sum(case when inx = 3 then 매출액 else 0 end) as sales_past_2
    , sum(case when inx = 2 then 매출액 else 0 end) as sales_past_3
    , sum(case when 당기순이익 > 0 then 1 else 0 end) as earn 
    , sum(case when ROE > 0 then 1 else 0 end) as roe
    , sum(case when 배당수익률 > 0 then 1 else 0 end) as distribution
    , 8.18 as discount_rate
from 
(   select * , row_number() over(partition by code order by inx) from finance_table 
) a
join 
(
    select code, 종가
    from price_table
    
) b
on a.code = b.code
join
(
select code, name, Sector, Industry
from code_table
) c 
on a.code = c.code
group by a.code
) x

order by return_rate1 desc, return_rate2 desc, return_rate3 desc
'''


cur.execute(query)


data = DataFrame(cur.fetchall())
result_stock = data.rename(columns={0 : 'Code', 1 : 'Name', 2 : 'Sector', 3 : 'Industry',
                                    4 : '부채비율', 5 : '시가총액(억)', 6 : '종가', 7 : 'S-RIM',
                                    8 : '매수금액', 9 : '매도금액_1st', 10 : '매도금액_2nd', 11 : '매수비율(S-RIM)', 12 : '매도비율(S-RIM)',
                                    13 : 'ROE_Est', 14 : 'ROE_past', 15 : 'ROE_past_2', 16 : 'ROE_past_3', 17 : 'ROE_improve', 18 : 'Return_rate(BPS&ROE)',
                                    19 : '영업이익_Est', 20 : '영업이익_past', 21 : '영업이익_past_2', 22 : '영업이익_past_3',
                                    23 : 'YoY_earn_Est(%)', 24 : 'YoY_earn_past(%)', 25 : 'YoY_earn_past_2', 26 : 'Multiple', 27 : '영업이익_비율',
                                    28 : '매출액_Est', 29 : '매출액_past', 30 : '매출액_past_2', 31 : '매출액_past_3',
                                    32 : 'YoY_sales_Est(%)', 33 : 'YoY_sales_past(%)', 34 : 'YoY_sales_past_2(%)'})

result_stock.to_excel(f'Result_Stock_{date}.xlsx')


## 1) 100% 이하 부채비율 --> 자산 = 자본 + 부채, 부채비율(%) = (부채 / 자본) x 100
## 2) 영업이익의 지속적 성장.
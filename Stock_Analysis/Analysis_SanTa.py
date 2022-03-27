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
    , 시가총액_억
    , ROUND(cash_202009 * 2 / 시가총액_억, 2) as ratio
    , cash_202009
    , cash_201912
    , cash_201812
    , cash_201712
      
from
(
    select
    a.code
    ,b.name
    ,b.industry
    ,b.main_product
    ,c.시가총액_억
    , (case when inx = 0 then 영업활동으로인한현금흐름 else 0 end) as cash_202009
    , (case when inx = 1 then 영업활동으로인한현금흐름 else 0 end) as cash_201912
    , (case when inx = 2 then 영업활동으로인한현금흐름 else 0 end) as cash_201812
    , (case when inx = 3 then 영업활동으로인한현금흐름 else 0 end) as cash_201712   

from 
(   select * , row_number() over(partition by code order by year desc) as inx
    from cash_flow_year
) a
join 
(
    select code, name, industry, main_product
    from code
) b
on a.code = b.code
join
(
    select code, 시가총액_억
    from finance_year
) c
on a.code = c.code
group by a.code, a.영업활동으로인한현금흐름 
)
order by ratio desc
'''

cur.execute(query)


data = DataFrame(cur.fetchall())
result_stock = data.rename(columns={0 : 'Code', 1 : 'Name', 2 : 'Industry', 3 : 'Main_product', 4 : '시가총액_억', 5 : 'Ratio',
                                    6 : '영업활동&현금_202009', 7 : '영업활동&현금_201912', 8 : '영업활동&현금_201812',
                                    9 : '영업활동&현금_201712'})

result_stock.to_excel(f'Result_SanTa_{date}.xlsx')


## 1) 100% 이하 부채비율 --> 자산 = 자본 + 부채, 부채비율(%) = (부채 / 자본) x 100
## 2) 영업이익의 지속적 성장.
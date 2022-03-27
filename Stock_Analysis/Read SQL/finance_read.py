import sqlite3
from pandas import DataFrame

conn = sqlite3.connect('DB_20220302_2.db')
cur = conn.cursor()
#
def get_col_names(table):
    query = 'SELECT * FROM ' + f'{table}'
    cur.execute(query)
    return [member[0] for member in cur.description]

index_Name = DataFrame(get_col_names('price_table'))
print(index_Name)

query = '''
select * , row_number() over(partition by code) as inx
from price_table
'''

cur.execute(query)

data = DataFrame(cur.fetchall())
print(data)
# result_stock = data.rename(columns={0: 'code', 1: 'year', 2: '매출액', 3: '영업이익', 4: '당기순이익', 5: 'ROE', 6: 'EPS'})
data.to_excel('price_25_test.xlsx')

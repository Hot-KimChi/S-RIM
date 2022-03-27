from urllib.request import urlopen
from pandas import DataFrame
from bs4 import BeautifulSoup


url = 'http://comp.fnguide.com/SVO2/ASP/SVD_Main.asp?pGB=1&gicode=A000020'
html = urlopen(url).read()

Table = DataFrame()
soup = BeautifulSoup(html, 'html.parser')
body = soup.find('body')

fn_body = body.find('div', {'class': 'fng_body asp_body'})
div1_table = fn_body.find('div', {'id': 'div1'})
tds = div1_table.find_all('td')
total_stock_td = tds[8].text
text_td = tds[10].text


total_stock = total_stock_td.replace(',', '')                                       # 시가총액
replace_td = text_td.replace('/', ' ').replace(',', '')                             # 발행주식수; 보통주&우선주 구분을 /에서 space 로 변경(나중에 array 로 split 진행)
num_stocks = replace_td.split()                                                     # 발행주식수(보통주/우선주)
nor_stock = num_stocks[0]                                                           # 발행주식수(보통주)
print(total_stock)
print(nor_stock)

us_body = body.find('table', {'class': 'us_table_ty1 h_fix zigbg_no notres'})
us_tds = us_body.find_all('td')                                                     # 자기주식
us_td = us_tds[6].text
treasury_stock = us_td.replace(',', '')
print(treasury_stock)

current_stock = int(nor_stock) - int(treasury_stock)
print(current_stock)
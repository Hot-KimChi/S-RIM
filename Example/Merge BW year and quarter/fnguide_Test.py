from urllib.request import urlopen
from pandas import DataFrame
import pandas as pd
from bs4 import BeautifulSoup


def get_finance_table(table, fn_body, code):
    try:

        tbody = table.find('tbody')
        tr = tbody.find_all('tr')
        Table = DataFrame()

        for i in tr:

            ''' 항목 가져오기'''
            category = i.find('span', {'class': 'txt_acd'})

            if category == None:
                category = i.find('th')

            category = category.text.strip()

            '''값 가져오기'''
            value_list = []

            j = i.find_all('td', {'class': 'r'})

            for value in j:
                temp = value.text.replace(',', '').strip()

                try:
                    temp = float(temp)
                    value_list.append(temp)
                except:
                    value_list.append(0)

            Table['%s' % (category)] = value_list

            ''' 기간 가져오기 '''

            thead = table.find('thead')
            tr_2 = thead.find('tr', {'class': 'td_gapcolor2'}).find_all('th')
            year_list = []

            for i in tr_2:
                try:
                    temp_year = i.find('span', {'class': 'txt_acd'}).text
                except:
                    temp_year = i.text
                year_list.append(temp_year)
            Table.index = year_list


        # Table = Table.T
        Table.reset_index(level=0, inplace=True)
        Table = Table.rename(columns={'index': 'year'})
        # print(Table)
        Table['code'] = code
        # print(Table)


        # Table = Table.append(Table)
        # Table = Table.loc[Table.year.isin(['2016/12', '2017/12', '2018/12', '2019/12', '2020/12(E)'])]

        #
        # div1_table = fn_body.find('div', {'id': 'div1'})
        # tds = div1_table.find_all('td')
        # total_stock_td = tds[8].text
        # text_td = tds[10].text
        #
        # total_stock = total_stock_td.replace(',', '')  # 시가총액
        # replace_td = text_td.replace('/', ' ').replace(',', '')  # 발행주식수; 보통주&우선주 구분을 /에서 space 로 변경(나중에 array 로 split 진행)
        # num_stocks = replace_td.split()  # 발행주식수(보통주/우선주)
        # nor_stock = num_stocks[0]  # 발행주식수(보통주)
        #
        # us_body = fn_body.find('div', {'id': 'div4'})  # 자기주식(왼쪽 / 오른쪽) 가져오기
        # us_tbody = us_body.find_all('tbody')  # 자기주식(오른쪽)
        # us_trs = us_tbody[1].find_all('tr')
        # us_tr = us_trs[4]
        # us_tds = us_tr.find_all('td')
        # us_td = us_tds[1].text
        #
        # lenth_us_td = len(us_td) - 1  # 자기주식이 없을 경우
        # if lenth_us_td == 0:
        #     treasury_stock = 0  # 자기주식 = 0
        # else:
        #     treasury_stock = us_td.replace(',', '')
        #
        # current_stock = int(nor_stock) - int(treasury_stock)  # 유통주식수 = 발행주식수(보통주) - 자기주식수
        #
        # Table['시가총액_억'] = total_stock
        # Table['발행주식수_보통주'] = nor_stock
        # Table['자기주식수'] = treasury_stock
        # Table['유통주식수'] = current_stock

        return Table

    except:
        print('error detection!')


def get_fnguide_table(code):
    try:

        Table = DataFrame()
        ''' 경로 탐색'''
        url = f'http://comp.fnguide.com/SVO2/ASP/SVD_main.asp?pGB=1&gicode=A{code}'
        html = urlopen(url).read()

        soup = BeautifulSoup(html, 'html.parser')
        body = soup.find('body')

        fn_body = body.find('div', {'class': 'fng_body asp_body'})
        ur_table = fn_body.find('div', {'id': 'div15'})

        for i in range(1, 3):
            if i == 1:
                table = ur_table.find('div', {'id': 'highlight_D_Y'})
                Table_year = get_finance_table(table, fn_body, code)

            else:
                table = ur_table.find('div', {'id': 'highlight_D_Q'})
                Table_quarter = get_finance_table(table, fn_body, code)

        Table = pd.concat([Table_year, Table_quarter])

        return Table

    except:
        print('error detection!')

a = get_fnguide_table('005930')
print(a)

a.to_excel('result.xlsx')



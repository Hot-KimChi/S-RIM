from urllib.request import urlopen
from bs4 import BeautifulSoup
from pandas import DataFrame
import pandas as pd


def get_cash(div, code, case):
    try:

        tbody = div.find('tbody')
        trs = tbody.find_all('tr')

        Table = DataFrame()

        for i in trs:

            ''' 항목 가져오기'''
            category = i.find('span', {'class': 'txt_acd'})

            if category == None:
                category = i.find('th')
            category = category.text.strip()

            '''값 가져오기'''
            value_list = []
            Each_data = i.find_all('td', {'class': 'r'})

            for value in Each_data:
                temp = value.text.replace(',', '').strip()

                try:
                    temp = float(temp)
                    value_list.append(temp)
                except:
                    value_list.append(0)

            Table['%s' % (category)] = value_list

            ''' 기간 가져오기 '''

        thead = div.find('thead')
        th = thead.find('tr').find_all('th')
        year_list = []
        th = th[1:5]

        for i in th:
            temp_year = i.text
            year_list.append(temp_year)
        Table.index = year_list

        # Table = Table.T
        Table.reset_index(level=0, inplace=True)
        Table = Table.rename(columns={'index': 'year'})
        Table['code'] = code

        # Table = Table.append(Table) / 원하는 기간 가져오기
        if case == 'year':
            Table = Table.loc[Table.year.isin(['2017/12', '2018/12', '2019/12', '2020/09'])]
        else:
            Table = Table.loc[Table.year.isin(['2019/12', '2020/03', '2020/06', '2020/09'])]

        # 원하는 항목만 가져오기
        Table = Table.loc[:, ['code', 'year', '영업활동으로인한현금흐름', '당기순손익', '투자활동으로인한현금흐름', '재무활동으로인한현금흐름', '현금및현금성자산의증가']]

        return Table

    except:
        print('error detection!')


def get_cash_flow(code):

    try:

        Table_year  = DataFrame()
        Table_quarter = DataFrame()


        url = f'http://comp.fnguide.com/SVO2/ASP/SVD_Finance.asp?pGB=1&gicode=A{code}&cID=&MenuYn=Y&ReportGB=&NewMenuID=103&stkGb=701'
        html = urlopen(url).read()

        bsObj = BeautifulSoup(html, 'html.parser')

        for i in range(1, 3):
            if i == 1:
                div = bsObj.find('div', {'id': 'divCashY'})
                Table_year = get_cash(div, code, 'year')
                # print(Table_year)

            else:
                div = bsObj.find('div', {'id': 'divCashQ'})
                Table_quarter = get_cash(div, code, 'quarter')
                # print(Table_quarter)

        Merge = pd.concat([Table_year, Table_quarter], ignore_index=True)
        print(Merge)
        return Merge

    except:
        print('error detection!')


a = get_cash_flow('357780')


#a.to_excel('samsung_cash_flow.xlsx')
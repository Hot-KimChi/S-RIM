import FinanceDataReader as fdr


df_krx = fdr.StockListing("KRX")
print(df_krx.shape)
print(df_krx.info())
print()

code_df = df_krx[['Symbol', 'Name', 'Sector', 'Industry']]
code_df = code_df.rename(columns={'Symbol': 'code'})
code_df = code_df.dropna(how='any', axis=0)
print(code_df)

code_list = code_df['code'].values.tolist()
print(code_list)







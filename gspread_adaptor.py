import pandas as pd
import gspread
import string
from rich.console import Console
from morningstar import Morningstar
from morningstar_us import MorningstarUS

console = Console()
ACTIVE_FIELDS = ['Name', 'Charge', 'Morningstar Rating', 'Category', 'Price', 'URL', '3 Months', '6 Months', '1 Year',
                 '3 Years', '5 Years', '10 Years']
SHEET_NAME = 'Investments'

# For Auth issues read this: https://docs.gspread.org/en/v3.7.0/oauth2.html#for-end-users-using-oauth-client-id

class GspreadAdaptor:

    ms_uk = Morningstar()
    ms_us = MorningstarUS()

    def read_gsheet_and_update(self):

        console.log('Attempting to login..')
        gc = gspread.oauth()
        console.log('Successful login')

        sh = gc.open(SHEET_NAME)
        ws = sh.get_worksheet(0)  # use first worksheet
        console.log('Found worksheet')

        header = ws.row_values(1)
        col_lookup = self.get_col_to_a1(header)
        df = pd.DataFrame(ws.get_all_records())
        df = df.reindex(columns=header)  # reorder dataframe so order is same as gsheet

        ms = Morningstar()
        console.log('Calling Morningstar..')
        df = df.apply(self.lookup_morningstar, axis=1)

        console.log('Writing back to worksheet..')
        for field in ACTIVE_FIELDS:
            field_pos = col_lookup.get(field)
            a1 = field_pos + '2:' + field_pos
            # todo: batch updates
            ws.update(a1, self.col_to_list_of_list(df[field].values.tolist()))
            console.log('Written field ' + field)

        console.log('Complete!')

    def col_to_list_of_list(self, col_values):
        list_of_list = []
        for i in col_values:
            internal_list = []
            internal_list.append(i)
            list_of_list.append(internal_list)
        return list_of_list

    def get_col_to_a1(self, header):
        cols = []
        for x in range(0,51):  # supports 52 columns max
            if x < 26:
                cols.append(string.ascii_uppercase[x])
            else:
                cols.append('A' + string.ascii_uppercase[x % 26])

        return dict(zip(header, cols))

    def lookup_morningstar(self, row):

        ms_uk = GspreadAdaptor.ms_uk
        ms_us = GspreadAdaptor.ms_us

        if (row['Exchange'] == 'LSE'):
            ticker = row['Ticker']
            override = row['Override Ticker']

            if override:
                ticker = override

            ms_id = ms_uk.get_morningstar_id_by_ticker(ticker)
            ms_overview = ms_uk.get_overview_by_id(ms_id)
            ms_performance = ms_uk.get_performance_by_id(ms_id)

            row['URL'] = ms_uk.get_external_url(ms_id)
            row['Name'] = ms_overview['Name']
            row['Charge'] = ms_overview['Charge']
            row['Morningstar Rating'] = ms_overview['Stars']
            row['Category'] = ms_overview['Category']
            row['Price'] = ms_overview['Price']
            row['3 Months'] = ms_performance['3 Months']
            row['6 Months'] = ms_performance['6 Months']
            row['1 Year'] = ms_performance['1 Year']
            row['3 Years'] = ms_performance['3 Years Annualised']
            row['5 Years'] = ms_performance['5 Years Annualised']
            row['10 Years'] = ms_performance['10 Years Annualised']

        if (row['Exchange'] == 'MUTF'):
            ticker = row['Ticker']
            override = row['Override Ticker']

            if override:
                ticker = override

            ms_id = ms_us.get_morningstar_id_by_ticker(ticker)
            ms_overview = ms_us.get_overview_by_id(ms_id)
            ms_performance = ms_us.get_performance_by_id(ms_id)

            #row['URL'] = ms_us.get_external_url(ms_id)
            row['Name'] = ms_overview['Name']
            row['Charge'] = ms_overview['Charge']
            row['Morningstar Rating'] = ms_overview['Stars']
            row['Category'] = ms_overview['Category']
            row['Price'] = ms_overview['Price']
            row['3 Months'] = ms_performance['3Month']
            #row['6 Months'] = ms_performance['6 Months']
            row['1 Year'] = ms_performance['1Year']
            row['3 Years'] = ms_performance['3Year']
            row['5 Years'] = ms_performance['5Year']
            row['10 Years'] = ms_performance['10Year']
        return row
    
if __name__ == '__main__':
    a = GspreadAdaptor()
    a.read_gsheet_and_update()


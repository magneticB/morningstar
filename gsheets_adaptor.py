from morningstar import Morningstar
import pandas as pd


class GSheetAdaptor:

    def read_csv_and_update(self):
        ms = Morningstar()


    def lookup_morningstar(self, row, ms):

        if (row['Exchange'] == 'LSE'):  # only UK for now
            ticker = row['Ticker']
            override = row['Override Ticker']

            if not pd.isnull(override):
                ticker = override

            ms_id = ms.get_morningstar_id_by_ticker(ticker)
            ms_overview = ms.get_overview_by_id(ms_id)
            ms_performance = ms.get_performance_by_id(ms_id)

            row['URL'] = ms.get_external_url(ms_id)
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
        return row
    
if __name__ == '__main__':
    a = GSheetAdaptor()
    a.read_csv_and_update()


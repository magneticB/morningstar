import requests
from lxml import html
import re


class Morningstar:

    def get_morningstar_id_by_ticker(self, ticker):
        ticker = ticker.strip() # remove white space for better matching
        response = requests.get('https://www.morningstar.co.uk/uk/util/SecuritySearch.ashx?q=' + ticker + '%20lse')

        search_results = str(response.content).split('\\r\\n')
        found = None

        for result in search_results:
            segments = result.split('|')
            if segments[3].lower() == ticker.lower() and segments[4].lower() == 'lse':
                found = segments[1]
                break

        if found != None:
            id_match = re.split('\{"i":"([A-Za-z0-9]+)"', found)
            print('Successfully found id \'' + id_match[1] + '\' for ticker \'' + ticker + '\'')
            return id_match[1]
        else:
            print('Error!  Did not find result for ticker search ' + ticker)


    def get_overview_by_id(self, id):

        output = {}

        response = requests.get('https://www.morningstar.co.uk/uk/etf/snapshot/snapshot.aspx?id=' + id
                                + '&InvestmentType=FE')
        print('Successfully found overview data for \'' + id + '\' attempting to parse..')

        dom = html.fromstring(response.content, parser = html.HTMLParser(encoding='utf-8'))

        # Name
        page_header = dom.xpath('//*[@class="snapshotTitleBox"]/h1/text()')

        if len(page_header) != 1:
            print('Error!  Could not extract overview data (name) correctly for id \'' + id + '\'')
            return
        page_header_components = page_header[0].split('\n')
        output['Name'] = page_header_components[0]

        # Charge
        page_charge = dom.xpath('//*[@id="overviewQuickstatsDiv"]/table//tr[10]/td[3]/text()')

        if len(page_charge) != 1:
            print('Error!  Could not extract overview data (charge) correctly for id \'' + id + '\'')
            return
        output['Charge'] = page_charge[0].replace('%', '')

        # Rating
        page_rating = dom.xpath('//*[@class="snapshotTitleBox"]/span/@class')

        output['Stars'] = None # Not all have ratings
        if len(page_rating) > 1:
            print('Error!  Could not extract overview data (rating) correctly for id \'' + id + '\'')
            return
        elif len(page_rating) == 1:  # rating found
            stars = re.split('stars([0-9])', page_rating[0])
            output['Stars'] = int(stars[1])

        # Category
        page_category = dom.xpath('//*[@id="overviewCalenderYearReturnsDiv"]/table//tr[6]/td/span[2]/text()')

        if len(page_category) != 1:
            print('Error!  Could not extract overview data (category) correctly for id \'' + id + '\'')
            return
        output['Category'] = page_category[0]

        # Price
        page_price = dom.xpath('//*[@id="overviewQuickstatsDiv"]/table//tr[2]/td[3]/text()')

        if len(page_price) != 1:
            print('Error!  Could not extract overview data (price) correctly for id \'' + id + '\'')
            return
        output['Price'] = self.parse_price(page_price[0])

        return output

    def get_performance_by_id(self, id):

        response = requests.get('https://www.morningstar.co.uk/uk/etf/snapshot/snapshot.aspx?id=' + id + '&tab=1')
        print('Successfully found performance data for \'' + id + '\' attempting to parse..')

        dom = html.fromstring(response.content)
        performance_labels = dom.xpath('//*[@id="returnsTrailingDiv"]/table//tr/td[1]/text()')
        performance_values = dom.xpath('//*[@id="returnsTrailingDiv"]/table//tr/td[2]/text()')

        return dict(zip(performance_labels[2:], performance_values[2:]))

    def get_external_url(self, id):
        return 'https://www.morningstar.co.uk/uk/etf/snapshot/snapshot.aspx?id=' + id

    def parse_price(self, page_price):
        split_price = page_price.split()
        if split_price[0] == 'GBX':
            return float(split_price[1])
        else:
            print('Error unrecognized currency while parsing price!')
            return split_price[1]


if __name__ == '__main__':

    m = Morningstar()
    # print(m.get_perfromance_by_ticker('VUSA'))
    morningstar_id = m.get_morningstar_id_by_ticker('VUAG')
    print(m.get_overview_by_id(morningstar_id))
    # morningstar_id = get_morningstar_id_by_ticker('VUAG')
    # print(get_performance_by_id(morningstar_id))
    # morningstar_id = get_morningstar_id_by_ticker('ISF')
    # print(get_performance_by_id(morningstar_id))
    # morningstar_id = get_morningstar_id_by_ticker('VUKE')
    # print(get_performance_by_id(morningstar_id))
    # morningstar_id = get_morningstar_id_by_ticker('3UKL')
    # print(get_performance_by_id(morningstar_id))
    # morningstar_id = get_morningstar_id_by_ticker('EQQQ')
    # print(get_performance_by_id(morningstar_id))


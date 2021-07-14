import json

import requests
from lxml import html
import re
from rich.console import Console

console = Console()

class MorningstarUS:

    URL_ROOT = 'https://www.morningstar.com/'
    headers = {
        'x-api-key': 'Nrc2ElgzRkaTE43D5vA7mrWj2WpSBR35fvmaqfte',
    }

    def get_morningstar_id_by_ticker(self, ticker):

        ticker = ticker.strip() # remove white space for better matching
        response = requests.get(MorningstarUS.URL_ROOT + 'api/v1/search/entities?q=' + ticker,
                                headers=MorningstarUS.headers)

        response_content = json.loads(response.content)

        first = response_content['results'][0]
        if first['ticker'].lower() != ticker.lower():
            console.log('Error!  Did not find result for ticker search ' + ticker, log_locals=True)
            return

        console.log('Successfully found search result for ' + ticker)

        # construct url
        security_type = 'stocks'
        if first['securityType'].upper() == 'FO':
            security_type = 'funds'
        return security_type + '/' + first['exchange'].lower() + '/' + first['ticker'].lower()


    def get_url_by_ticker_and_type(self, ticker, type):
        ticker = ticker.strip() # remove white space for better matching
        type = type.strip()

        return MorningstarUS.URL_ROOT + type.lower() + '/xnas/' + ticker.lower() + '/quote'


    def get_overview_by_id(self, id):

        output = {}

        response = requests.get(MorningstarUS.URL_ROOT + id + '/quote')
        console.log('Successfully found overview data for \'' + id + '\' attempting to parse..')

        dom = html.fromstring(response.content, parser = html.HTMLParser(encoding='utf-8'))

        # Name
        page_header = dom.xpath('//*[@class="mdc-security-header__inner"]/h1/span/text()')

        if len(page_header) != 1:
            console.log('Error!  Could not extract overview data (name) correctly for id \'' + id + '\'',
                        log_locals=True)
            return
        page_header_components = page_header[0].split('\n')
        output['Name'] = page_header_components[0]

        # Charge

        page_charge = dom.xpath('//div/span[text() = "Expense Ratio"]/../../div/span/span/text()')

        if len(page_charge) != 1:
            console.log('Error!  Could not extract overview data (charge) correctly for id \'' + id + '\'',
                        log_locals=True)
            return
        output['Charge'] = page_charge[0]

        # # Rating
        # page_rating = dom.xpath('//*[@class="snapshotTitleBox"]/span/@class')
        #
        # output['Stars'] = None # Not all have ratings
        # if len(page_rating) == 0:
        #     console.log('Error!  Could not extract overview data (rating) correctly for id \'' + id + '\'',
        #                 log_locals=True)
        #     return
        # elif len(page_rating) == 2:  # rating found
        #     stars = re.split('stars([0-9])', page_rating[0])
        #     output['Stars'] = int(stars[1])
        #
        # # Category
        # page_category = dom.xpath('//*[@id="overviewCalenderYearReturnsDiv"]/table//tr[6]/td/span[2]/text()')
        #
        # if len(page_category) != 1:
        #     console.log('Error!  Could not extract overview data (category) correctly for id \'' + id + '\'',
        #                 log_locals=True)
        #     return
        # output['Category'] = page_category[0]
        #
        # # Price
        # page_price = dom.xpath('//*[@id="overviewQuickstatsDiv"]/table//tr[2]/td[3]/text()')
        #
        # if len(page_price) != 1:
        #     console.log('Error!  Could not extract overview data (price) correctly for id \'' + id + '\'',
        #                 log_locals=True)
        #     return
        # output['Price'] = self.parse_price(page_price[0])

        return output

    def get_performance_by_id(self, id):

        response = requests.get('https://www.morningstar.co.uk/uk/etf/snapshot/snapshot.aspx?id=' + id + '&tab=1')
        console.log('Successfully found performance data for \'' + id + '\' attempting to parse..')

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
            console.log('Error unrecognized currency while parsing price!', log_locals=True)
            return split_price[1]


if __name__ == '__main__':

    m = MorningstarUS()
    # print(m.get_perfromance_by_ticker('VUSA'))
    morningstar_id = m.get_morningstar_id_by_ticker('NMPAX')
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


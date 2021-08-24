import json

import requests
from lxml import html
import re
from rich.console import Console

from ms_ids import MSids

console = Console()


class MorningstarUS:

    URL_ROOT = 'https://www.morningstar.com/'
    headers = {
        'x-api-key': 'Nrc2ElgzRkaTE43D5vA7mrWj2WpSBR35fvmaqfte',
        'ApiKey': 'lstzFDEOhfFNMLikKa0am9mgEKLBl49T',
    }

    def get_morningstar_id_by_ticker(self, ticker):

        output_ids = MSids()

        ticker = ticker.strip() # remove white space for better matching
        response = requests.get(MorningstarUS.URL_ROOT + 'api/v1/search/entities?q=' + ticker,
                                headers=MorningstarUS.headers)

        response_content = json.loads(response.content)

        if len(response_content['results']) < 1:
            console.log('Error!  Did not find result for ticker search ' + ticker, log_locals=True)
            return

        first = response_content['results'][0]
        if first['ticker'].lower() != ticker.lower():
            console.log('Error!  Did not find result for ticker search ' + ticker, log_locals=True)
            return

        if (first['performanceId'] == ''):
            console.log('Error!  Did not find expected performanceId for ticker' + ticker, log_locals=True)
            return

        console.log('Successfully found search result for ' + ticker)
        output_ids.ticker = ticker
        output_ids.performance_id = first['performanceId']

        # construct url
        security_type = 'stocks'
        if first['securityType'].upper() == 'FO':
            security_type = 'funds'
        output_ids.url = security_type + '/' + first['exchange'].lower() + '/' + first['ticker'].lower()

        return output_ids

    def get_url_by_ticker_and_type(self, ticker, type):
        ticker = ticker.strip() # remove white space for better matching
        type = type.strip()

        return MorningstarUS.URL_ROOT + type.lower() + '/xnas/' + ticker.lower() + '/quote'

    def find_data_api_id(self, content, id):

        results = re.split('byId:{"' + id.performance_id + '"[^,]+,([^:]+)', content.decode('utf-8'))
        id.data_api_id = results[1]


    def get_overview_by_id(self, id):

        output = {}

        response = requests.get(MorningstarUS.URL_ROOT + id.url + '/quote')
        console.log('Successfully found overview data for \'' + id.ticker + '\' attempting to parse..')

        # Find API Id in source of page
        self.find_data_api_id(response.content, id)

        dom = html.fromstring(response.content, parser = html.HTMLParser(encoding='utf-8'))

        # Name
        page_header = dom.xpath('//*[@class="mdc-security-header__inner"]/h1/span/text()')

        if len(page_header) != 1:
            console.log('Error!  Could not extract overview data (name) correctly for id \'' + id.ticker + '\'',
                        log_locals=True)
            return
        page_header_components = page_header[0].split('\n')
        output['Name'] = page_header_components[0]

        # Charge
        page_charge = dom.xpath('//div/span[text() = "Expense Ratio"]/../../div/span/span/text()')

        if len(page_charge) != 1:
            console.log('Error!  Could not extract overview data (charge) correctly for id \'' + id.ticker + '\'',
                        log_locals=True)
            return
        output['Charge'] = page_charge[0]

        # Rating
        page_rating = dom.xpath('//*[@class="mdc-security-header__star-rating"]/@aria-label')

        output['Stars'] = None # Not all have ratings
        if len(page_rating) == 0:
            console.log('Error!  Could not extract overview data (rating) correctly for id \'' + id.ticker + '\'',
                        log_locals=True)
            return
        elif len(page_rating) == 1:  # rating found
            output['Stars'] = int(page_rating[0][:1])

        # Category
        page_category = dom.xpath('//div/span[text() = "Category"]/../../div/span/text()')

        if len(page_category) != 2:
            console.log('Error!  Could not extract overview data (category) correctly for id \'' + id.ticker + '\'',
                        log_locals=True)
            return
        output['Category'] = page_category[1]

        # Price
        page_price = dom.xpath('//div/span[starts-with(text(), "NAV")]/../../div/span/text()')

        if len(page_price) < 2:
            console.log('Error!  Could not extract overview data (price) correctly for id \'' + id.ticker + '\'',
                        log_locals=True)
            return
        output['Price'] = float(page_price[1])

        return output

    def get_performance_by_id(self, id):

        params = (
            ('duration', 'daily'),
            ('currency', ''),
            ('limitAge', ''),
            ('languageId', 'en'),
            ('locale', 'en'),
            ('clientId', 'MDC'),
            ('benchmarkId', 'category'),
            ('component', 'sal-components-mip-trailing-return'),
            ('version', '3.49.0'),
        )

        response = requests.get(
            'https://api-global.morningstar.com/sal-service/v1/fund/trailingReturn/v2/' + id.data_api_id + '/data',
            headers=MorningstarUS.headers,
            params=params)

        response_content = json.loads(response.content)


        console.log('Successfully found performance data for \'' + id.ticker + '\' attempting to parse..')

        return dict(zip(response_content['columnDefs'], response_content['totalReturnNAV']))

    def get_external_url(self, id):
        return 'https://www.morningstar.co.uk/uk/etf/snapshot/snapshot.aspx?id=' + id


# m = MorningstarUS()
# # print(m.get_perfromance_by_ticker('VUSA'))
# morningstar_id = m.get_morningstar_id_by_ticker('NMPAX')
# print(m.get_overview_by_id(morningstar_id))
# m.get_performance_by_id(morningstar_id)
# morningstar_id = m.get_morningstar_id_by_ticker('VMFXX')
# print(m.get_overview_by_id(morningstar_id))
# m.get_performance_by_id(morningstar_id)
# morningstar_id = m.get_morningstar_id_by_ticker('MLAIX')
# print(m.get_overview_by_id(morningstar_id))
# m.get_performance_by_id(morningstar_id)
# morningstar_id = m.get_morningstar_id_by_ticker('VFTAX')
# print(m.get_overview_by_id(morningstar_id))
# m.get_performance_by_id(morningstar_id)
# morningstar_id = m.get_morningstar_id_by_ticker('VTWAX')
# print(m.get_overview_by_id(morningstar_id))
# m.get_performance_by_id(morningstar_id)
# morningstar_id = m.get_morningstar_id_by_ticker('OEGYX')
# print(m.get_overview_by_id(morningstar_id))
# m.get_performance_by_id(morningstar_id)


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


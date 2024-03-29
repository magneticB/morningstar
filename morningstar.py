import requests
from lxml import html
import re
from rich.console import Console

console = Console()


class Morningstar:

    def get_morningstar_id_by_ticker(self, ticker):
        ticker = ticker.strip() # remove white space for better matching
        #response = requests.get('https://www.morningstar.co.uk/uk/util/SecuritySearch.ashx?q=' + ticker + '%20lse')

        request_headers = {'x-requested-with': 'XMLHttpRequest'}
        post_data = {'q': ticker, 'limit': '100', 'timestamp': '1667155008782', 'preferedList': ''}

        response = requests.post('https://www.morningstar.co.uk/uk/util/SecuritySearch.ashx', headers=request_headers,
                                 data=post_data)

        search_results = str(response.content).split('\\r\\n')
        found = None

        for result in search_results:
            segments = result.split('|')
            if segments[3].lower() == ticker.lower() and segments[4].lower() == 'lse':
                found = segments[1]
                break

        if found != None:
            id_match = re.split('\{"i":"([A-Za-z0-9]+)"', found)
            console.log('Successfully found id \'' + id_match[1] + '\' for ticker \'' + ticker + '\'')
            return id_match[1]
        else:
            console.log('Error!  Did not find result for ticker search ' + ticker, log_locals=True)


    def get_overview_by_id(self, id):

        output = {}

        response = requests.get('https://www.morningstar.co.uk/uk/etf/snapshot/snapshot.aspx?id=' + id
                                + '&InvestmentType=FE')
        console.log('Successfully found overview data for \'' + id + '\' attempting to parse..')

        dom = html.fromstring(response.content, parser = html.HTMLParser(encoding='utf-8'))

        # Name
        page_header = dom.xpath('//*[@class="snapshotTitleBox"]/h1/text()')

        if len(page_header) != 1:
            console.log('Error!  Could not extract overview data (name) correctly for id \'' + id + '\'',
                        log_locals=True)
            return
        page_header_components = page_header[0].split('\n')
        output['Name'] = page_header_components[0]

        # Charge
        page_charge = dom.xpath('//*[@id="overviewQuickstatsDiv"]/table//td[starts-with(text(), "Ongoing '
                                'Charge")]/../td[3]/text()')

        if len(page_charge) != 1:
            console.log('Error!  Could not extract overview data (charge) correctly for id \'' + id + '\'',
                        log_locals=True)
            return
        output['Charge'] = page_charge[0].replace('%', '')

        # Rating
        page_rating = dom.xpath('//*[@class="snapshotTitleBox"]/span/@class')

        output['Stars'] = None # Not all have ratings
        if len(page_rating) == 0:
            console.log('Error!  Could not extract overview data (rating) correctly for id \'' + id + '\'',
                        log_locals=True)
            return
        elif len(page_rating) == 2:  # rating found
            stars = re.split('stars([0-9])', page_rating[0])
            output['Stars'] = int(stars[1])

        # Category
        page_category = dom.xpath('//*[@id="overviewCalenderYearReturnsDiv"]/table//tr[6]/td/span[2]/text()')

        if len(page_category) != 1:
            console.log('Error!  Could not extract overview data (category) correctly for id \'' + id + '\'',
                        log_locals=True)
            return
        output['Category'] = page_category[0]

        # Price
        page_price = dom.xpath('//*[@id="overviewQuickstatsDiv"]/table//tr[2]/td[3]/text()')

        if len(page_price) != 1:
            console.log('Error!  Could not extract overview data (price) correctly for id \'' + id + '\'',
                        log_locals=True)
            return
        output['Price'] = self.parse_price(page_price[0])

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

    m = Morningstar()
    # print(m.get_perfromance_by_ticker('VUSA'))
    morningstar_id = m.get_morningstar_id_by_ticker('ISF')
    print(m.get_overview_by_id(morningstar_id))
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


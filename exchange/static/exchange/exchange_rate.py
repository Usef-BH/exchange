from bs4 import BeautifulSoup
import requests, re

class Currency:
    '''
    Class Currency provides the currencies exchange rate for more than 180 currency.
    Currency instances accept operations addition '+' and substraction '-' 
    x = Currency(6)
    y = Currency(45, "USD")
    x + y ==> result 6 MAD + 45 USD in MAD currency (the first operand currency takes precedance)
    we can also do:
    1 + y ==> result 1 MAD + 45 USD in MAD currency (integers and floats considered like MAD currency
    and if they are first operand, the result currency is MAD)
    (multiply 'x' and devide '/' coming soon)
    Exchange: you can exchange an amount from one currency to another
    x = Currency(100, "EUR")
    x.exchange() => result currency MAD assumed
    x.exchange("USD") => explicitly set result currency USD
    '''
    yahoo_url = "https://finance.yahoo.com/webservice/v1/symbols/allcurrencies/quote"

    def __init__(self, value=1, unit="MAD"):
        self.value = value
        self.unit = unit
        response = requests.get(self.yahoo_url)
        try:
            response.raise_for_status()
        except:
            print("Problem fetching data from network!!!")
                

        html = response.text
        self.data = html
        file = open("yahoo_finance.xml", "w")
        file.write(html)
        file.close()


    def toUSD(self, unit="MAD"):
        if unit.upper() == "USD":
            return 1

        soup = BeautifulSoup(self.data, 'html.parser')
        block = soup.find_all("field", text=re.compile("^{}".format(unit.upper())))
        parent = block[0].parent
        parent_soup = BeautifulSoup(str(parent), 'html.parser')
        return parent_soup.find_all("field", attrs={"name":"price"})[0].string

    def exchange(self, unit="MAD"):
        if self.unit != "USD":
            res1 = self.toUSD(self.unit)
            res = self.toUSD(unit)
            return "{} {} worth {} {}.".format(self.value, self.unit, self.value*float(res)/float(res1), unit)

        res = self.toUSD()
        return "{} {} worth {} {}.".format(self.value, self.unit, self.value*float(res), unit)


from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.core import serializers
from django.views import View
from bs4 import BeautifulSoup
import re
import requests
import shelve

# Create your views here.

url_daily = "https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml"
url_hist = "https://www.ecb.europa.eu/stats/eurofxref/eurofxref-hist-90d.xml"


class Api(View):

    def __init__(self):
        self.data = None

    def get_data(self):
        shelf = shelve.open('exchange_rates')
        if 'Last-Modified' in shelf:
            #print("################################################")
            #print("Data exist in cache, but checking for deprecation!")
            headers = {'If-Modified-Since': shelf['Last-Modified']}
            response = requests.get(url_daily, headers=headers)
            try:
                response.raise_for_status()
            except:
                print("Problem fetching data from network!!!")

            if response.text == '':
                #print("Data still good")
                file = open("exchange_rates.xml")
                self.data = file.read()
                file.close()
            else:
                #print("Data is outdated")
                self.data = response.text
                shelf['Last-Modified'] = response.headers['Last-Modified']
                file = open("exchange_rates.xml", "w")
                file.write(self.data)
                file.close()
        else:
            #print("################################################")
            #print("Fetching data from network")
            response = requests.get(url_daily)
            try:
                response.raise_for_status()
            except:
                print("Problem fetching data from network!!!")

            html = response.text
            shelf['Last-Modified'] = response.headers['Last-Modified']
            self.data = html
            file = open("exchange_rates.xml", "w")
            file.write(html)
            file.close()

    def toEUR(self, unit):
        soup = BeautifulSoup(self.data, 'html.parser')
        #print("soup: %s" % soup)
        block = soup.find(currency=unit)
        #print("block: %s" % block)
        return block['rate']

    def get(self, request):
        self.get_data()
        base = request.GET.get('base')
        target = request.GET.get('target')
        amount = request.GET.get('amount')
        if base.strip().upper() == target.strip().upper():
            response = {
                "base": base,
                "target": target,
                "value": amount,
                "price": 1,
                "response": 1 * float(amount)
            }
            return JsonResponse(response)

        if base != 'EUR' and target != 'EUR':
            price = str(self.toEUR(base))
            cur = str(self.toEUR(target))
            resp = float(amount) * (float(cur)/float(price))
        elif base != 'EUR' and target == 'EUR': 
            price = str(self.toEUR(base))
            resp = float(amount) * (1/float(price))
        else:
            price = str(self.toEUR(target))
            resp = float(amount) * float(price)

        response = {
            "base": base,
            "target": target,
            "value": amount,
            "price": price,
            "response": round(resp, 6)
        }
        return JsonResponse(response)



def base(request):
    base = request.GET.get('base')
    data = get_data()
    soup = BeautifulSoup(data, 'html.parser')
    time = soup.find(time=re.compile(".*"))
    currency_base = soup.find(currency=base)
    rate_base = currency_base['rate']
    currencies = soup.findAll(currency=re.compile(".*"))
    resp = {}
    resp['base'] = base
    resp['time'] = time
    for currency in currencies:
        resp[currency['currency']] = float(currency['rate'])/float(rate_base)

    return JsonResponse(resp)

class Latest(View):

    def __init__(self):
        self.data = get_data()

    def parseData(self, base=None, symbols=None):
        rates = {}
        resp = {}
        soup = BeautifulSoup(self.data, 'html.parser')
        time = soup.find(time=re.compile(".*"))
        if symbols:
            targets = symbols.split(',')
            #print("###########################################")
            #print("targets: {} type: {}.".format(targets, type(targets)))
            #for target in targets:
                #print("target {} of type {}.".format(target, type(target)))

            lst = [soup.find(currency=re.compile(target))
                             for target in targets if target.upper()!='EUR']
            #print("###########################################")
            #print("list: %s" % lst)
        else:
            lst = soup.findAll(currency=re.compile(".*"))
            #print("###########################################")
            #print("list: %s" % lst)
        
        if base and base.upper() != 'EUR':
            resp['base'] = base
            currency_base = soup.find(currency=base)
            rate_base = currency_base['rate']
            if 'EUR' in targets:
                rates['EUR'] = round(1/float(rate_base), 4)
            for item in lst:
                rates[item['currency']] = round(float(item['rate'])/float(rate_base), 4)
        else:
            resp['base'] = "EUR"
            for item in lst:
                rates[item['currency']] = float(item['rate'])            

        resp['date'] = time['time']
        resp['rates'] = rates
        return resp

    def convert(self, base, symbols):

        if symbols:
            targets = symbols.strip()
            soup = BeautifulSoup(self.data, 'html.parser')
            blocks = [soup.find(currency=target) for target in targets]
            prices = {}
            for block in blocks:
                prices[block['currency']] = block['rate']

        soup = BeautifulSoup(self.data, 'html.parser')
        #print("soup: %s" % soup)
        block = soup.find(currency=base)
        #print("block: %s" % block)
        return block['rate']

    def get(self, request):

        resp = self.parseData(base=request.GET.get('base'), symbols=request.GET.get('symbols'))
        # print("The price is: {} with type: {}".format(price, type(price)))

        # data = serializers.serialize('json', response)
        # return HttpResponse(response, content_type='application/json')
        return JsonResponse(resp)


class getHist(View):

    def __init__(self):
        self.data = get_hist_data()

    def get(self, request, year, month, day):

        soup = BeautifulSoup(self.data, 'html.parser')
        #print("###########################################")
        #print("soup hist: %s" % soup)
        time = soup.find(time=re.compile("{}-{}-{}".format(year, month, day)))
        rates = {}
        resp = {}
        lst = time.findAll(currency=re.compile(".*"))
        #print("###########################################")
        #print("list: %s" % lst)

        for item in lst:
            rates[item['currency']] = float(item['rate'])

        resp['base'] = "EUR"
        resp['date'] = time['time']
        resp['rates'] = rates

        return JsonResponse(resp)


def get_data():
    shelf = shelve.open('exchange_rates')
    if 'Last-Modified' in shelf:
        #print("################################################")
        #print("Data exist in cache, but checking for deprecation!")
        headers = {'If-Modified-Since': shelf['Last-Modified']}
        response = requests.get(url_daily, headers=headers)
        try:
            response.raise_for_status()
        except:
            print("Problem fetching data from network!!!")

        if response.text == '':
            #print("Data still good")
            file = open("exchange_rates.xml")
            data = file.read()
            file.close()
        else:
            #print("Data is outdated")
            data = response.text
            shelf['Last-Modified'] = response.headers['Last-Modified']
            file = open("exchange_rates.xml", "w")
            file.write(data)
            file.close()
        return data

    else:
        #print("################################################")
        #print("Fetching data from network")
        response = requests.get(url_daily)
        try:
            response.raise_for_status()
        except:
            print("Problem fetching data from network!!!")

        html = response.text
        shelf['Last-Modified'] = response.headers['Last-Modified']
        data = html
        file = open("exchange_rates.xml", "w")
        file.write(html)
        file.close()
        return data

def get_hist_data():
    shelf = shelve.open('exchange_rates_hist')
    if 'Last-Modified' in shelf:
        #print("################################################")
        #print("Data exist in cache, but checking for deprecation!")
        headers = {'If-Modified-Since': shelf['Last-Modified']}
        response = requests.get(url_hist, headers=headers)
        try:
            response.raise_for_status()
        except:
            print("Problem fetching data from network!!!")

        if response.text == '':
            #print("Data still good")
            file = open("exchange_rates_hist.xml")
            data = file.read()
            file.close()
        else:
            #print("Data is outdated")
            data = response.text
            shelf['Last-Modified'] = response.headers['Last-Modified']
            file = open("exchange_rates_hist.xml", "w")
            file.write(data)
            file.close()
        return data

    else:
        #print("################################################")
        #print("Fetching data from network")
        response = requests.get(url_hist)
        try:
            response.raise_for_status()
        except:
            print("Problem fetching data from network!!!")

        html = response.text
        shelf['Last-Modified'] = response.headers['Last-Modified']
        data = html
        file = open("exchange_rates_hist.xml", "w")
        file.write(html)
        file.close()
        return data



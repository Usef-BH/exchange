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
            print("################################################")
            print("Data exist in cache, but checking for deprecation!")
            headers = {'If-Modified-Since': shelf['Last-Modified']}
            response = requests.get(url_daily, headers=headers)
            try:
                response.raise_for_status()
            except:
                print("Problem fetching data from network!!!")

            if response.text == '':
                print("Data still good")
                file = open("exchange_rates.xml")
                self.data = file.read()
                file.close()
            else:
                print("Data is outdated")
                self.data = response.text
                shelf['Last-Modified'] = response.headers['Last-Modified']
                file = open("exchange_rates.xml", "w")
                file.write(self.data)
                file.close()
        else:
            print("################################################")
            print("Fetching data from network")
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
        print("soup: %s" % soup)
        block = soup.find(currency=unit)
        print("block: %s" % block)
        return block['rate']

    def get(self, request):
        self.get_data()
        base = request.GET.get('base')
        target = request.GET.get('target')
        amount = request.GET.get('amount')
        if base != 'EUR':
            price = str(self.toEUR(base))
            resp = float(amount) * (1/float(price))
        else:
            price = str(self.toEUR(target))
            resp = float(amount) * float(price)

        # print("The price is: {} with type: {}".format(price, type(price)))
        response = {
            "base": base,
            "target": target,
            "value": amount,
            "price": price,
            "response": resp
        }

        # data = serializers.serialize('json', response)
        # return HttpResponse(response, content_type='application/json')
        return JsonResponse(response)


class Latest(View):

    def __init__(self):
        pass

    def get_data(self):
        shelf = shelve.open('exchange_rates')
        if 'Last-Modified' in shelf:
            print("################################################")
            print("Data exist in cache, but checking for deprecation!")
            headers = {'If-Modified-Since': shelf['Last-Modified']}
            response = requests.get(url_daily, headers=headers)
            try:
                response.raise_for_status()
            except:
                print("Problem fetching data from network!!!")

            if response.text == '':
                print("Data still good")
                file = open("exchange_rates.xml")
                self.data = file.read()
                file.close()
            else:
                print("Data is outdated")
                self.data = response.text
                shelf['Last-Modified'] = response.headers['Last-Modified']
                file = open("exchange_rates.xml", "w")
                file.write(self.data)
                file.close()
        else:
            print("################################################")
            print("Fetching data from network")
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

    def symbols(self):
        pass

    def base(self):
        pass

    def parseData(self, symbols=None):
        rates = {}
        resp = {}
        soup = BeautifulSoup(self.data, 'html.parser')
        time = soup.find(time=re.compile(".*"))
        if symbols:
            targets = symbols.split(',')
            print("###########################################")
            print("targets: {} type: {}.".format(targets, type(targets)))
            for target in targets:
                print("target {} of type {}.".format(target, type(target)))

            lst = [soup.find(currency=re.compile(target))
                             for target in targets]
            print("###########################################")
            print("list: %s" % lst)
        else:
            lst = soup.findAll(currency=re.compile(".*"))
            print("###########################################")
            print("list: %s" % lst)

        for item in lst:
            rates[item['currency']] = float(item['rate'])

        resp['base'] = "EUR"
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
        print("soup: %s" % soup)
        block = soup.find(currency=base)
        print("block: %s" % block)
        return block['rate']

    def get(self, request):
        self.get_data()

        resp = self.parseData(symbols=request.GET.get('symbols'))
        # print("The price is: {} with type: {}".format(price, type(price)))

        # data = serializers.serialize('json', response)
        # return HttpResponse(response, content_type='application/json')
        return JsonResponse(resp)


class getHist(View):

    def __init__(self):
        self.data = None

    def get(self, request, year, month, day):

        self.get_hist()
        soup = BeautifulSoup(self.data, 'html.parser')
        print("###########################################")
        print("soup hist: %s" % soup)
        time = soup.find(time=re.compile("{}-{}-{}".format(year, month, day)))
        rates = {}
        resp = {}
        lst = time.findAll(currency=re.compile(".*"))
        print("###########################################")
        print("list: %s" % lst)

        for item in lst:
            rates[item['currency']] = float(item['rate'])

        resp['base'] = "EUR"
        resp['date'] = time['time']
        resp['rates'] = rates

        return JsonResponse(resp)


    def get_hist(self):
        shelf = shelve.open('exchange_rates_hist')
        if 'Last-Modified' in shelf:
            print("################################################")
            print("Data exist in cache, but checking for deprecation!")
            headers = {'If-Modified-Since': shelf['Last-Modified']}
            response = requests.get(url_hist, headers=headers)
            try:
                response.raise_for_status()
            except:
                print("Problem fetching data from network!!!")

            if response.text == '':
                print("Data still good")
                file = open("exchange_rates_hist.xml")
                self.data = file.read()
                file.close()
            else:
                print("Data is outdated")
                self.data = response.text
                shelf['Last-Modified'] = response.headers['Last-Modified']
                file = open("exchange_rates_hist.xml", "w")
                file.write(self.data)
                file.close()
        else:
            print("################################################")
            print("Fetching data from network")
            response = requests.get(url_hist)
            try:
                response.raise_for_status()
            except:
                print("Problem fetching data from network!!!")

            html = response.text
            shelf['Last-Modified'] = response.headers['Last-Modified']
            self.data = html
            file = open("exchange_rates_hist.xml", "w")
            file.write(html)
            file.close()

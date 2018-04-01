from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.core import serializers
from django.views import View
from bs4 import BeautifulSoup
import re
import requests
import shelve

# Create your views here.

url = "https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml"

class Api(View):

    

    def __init__(self):
        self.data = None

    def get_data(self):
        shelf = shelve.open('exchange_rates')
        if 'Last-Modified' in shelf:
            print("################################################")
            print("Data exist in cache, but checking for deprecation!")
            headers = {'If-Modified-Since': shelf['Last-Modified']}
            response = requests.get(url, headers=headers)
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
            response = requests.get(url)
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
            response = requests.get(url, headers=headers)
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
            response = requests.get(url)
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
        
    def parseData(self):
        resp = {}
        soup = BeautifulSoup(self.data, 'html.parser')
        lst = soup.findAll(currency=re.compile(".*"))
        for item in lst:
            resp[item['currency']] = float(item['rate'])
        
        return soup

    def get(self, request):
        self.get_data()
        resp = self.parseData()
        # print("The price is: {} with type: {}".format(price, type(price)))

        # data = serializers.serialize('json', response)
        # return HttpResponse(response, content_type='application/json')
        return HttpResponse(resp)


"""
    def exchange(self, unit="MAD"):
        if self.unit != "USD":
            res1 = self.toUSD(self.unit)
            res = self.toUSD(unit)
            return "{} {} worth {} {}.".format(self.value, self.unit, self.value*float(res)/float(res1), unit)

        res = self.toUSD()
        return "{} {} worth {} {}.".format(self.value, self.unit, self.value*float(res), unit)

"""

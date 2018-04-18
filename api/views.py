from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.core import serializers
from django.views import View
from bs4 import BeautifulSoup
import re
import requests
import shelve

# Create your views here.

url = "https://www.ecb.europa.eu/stats/eurofxref/eurofxref"


class Api(View):

    def __init__(self):
        self.data = get_data()

    def get(self, request):
        base = request.GET.get('base')
        target = request.GET.get('target')
        amount = request.GET.get('amount')
        result = get_result(self.data, base=base, symbols=target)
        
        base, date, rates = result.values()
        price = rates[target]
        resp = float(amount) * price

        response = {
            "base": base,
            "date": date,
            "target": target,
            "value": amount,
            "price": price,
            "response": round(resp, 8)
        }

        return JsonResponse(response)


class Latest(View):

    def __init__(self):
        self.data = get_data()

    def convert(self, base, symbols):

        if symbols:
            targets = symbols.strip()
            soup = BeautifulSoup(self.data, 'html.parser')
            blocks = [soup.find(currency=target) for target in targets]
            prices = {}
            for block in blocks:
                prices[block['currency']] = block['rate']

        soup = BeautifulSoup(self.data, 'html.parser')
        block = soup.find(currency=base)
        return block['rate']

    def get(self, request):

        result = get_result(self.data, base=request.GET.get(
            'base'), symbols=request.GET.get('symbols'))
        return JsonResponse(result)


class getHist(View):

    def __init__(self):
        self.data = get_data('hist-90d')

    def get(self, request, year, month, day):

        soup = BeautifulSoup(self.data, 'html.parser')
        time = soup.find(time=re.compile("{}-{}-{}".format(year, month, day)))
        rates = {}
        resp = {}
        lst = time.findAll(currency=re.compile(".*"))

        for item in lst:
            rates[item['currency']] = float(item['rate'])

        resp['base'] = "EUR"
        resp['date'] = time['time']
        resp['rates'] = rates

        return JsonResponse(resp)


def get_data(data_type='daily'):
    shelf = shelve.open('rates_'+data_type)
    data_url = url + "-" + data_type + ".xml"
    if 'Last-Modified' in shelf:
        headers = {'If-Modified-Since': shelf['Last-Modified']}
        response = requests.get(data_url, headers=headers)
        try:
            response.raise_for_status()
        except:
            print("Problem fetching data from network!!!")

        if response.text == '':
            file = open("rates_"+data_type+".xml")
            data = file.read()
            file.close()
        else:
            data = response.text
            shelf['Last-Modified'] = response.headers['Last-Modified']
            file = open("rates_"+data_type+".xml", "w")
            file.write(data)
            file.close()
        return data

    else:
        response = requests.get(data_url)
        try:
            response.raise_for_status()
        except:
            print("Problem fetching data from network!!!")

        html = response.text
        shelf['Last-Modified'] = response.headers['Last-Modified']
        data = html
        file = open("rates_"+data_type+".xml", "w")
        file.write(html)
        file.close()
        return data


def get_result(data, base=None, symbols=None):
    rates = {}
    resp = {}
    soup = BeautifulSoup(data, 'html.parser')
    time = soup.find(time=re.compile(".*"))
    if symbols:
        targets = symbols.split(',')
        lst = [soup.find(currency=re.compile(target))
               for target in targets if target.upper() != 'EUR']

    else:
        lst = soup.findAll(currency=re.compile(".*"))

    if base and base.upper() != 'EUR':
        resp['base'] = base
        currency_base = soup.find(currency=base)
        rate_base = currency_base['rate']
        if 'EUR' in targets:
            rates['EUR'] = 1/float(rate_base)
        for item in lst:
            rates[item['currency']] = float(item['rate'])/float(rate_base)
    else:
        resp['base'] = "EUR"
        for item in lst:
            rates[item['currency']] = float(item['rate'])

    resp['date'] = time['time']
    resp['rates'] = rates
    return resp

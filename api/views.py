from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest
from django.views import View
from api.models import DailyData, Hist90Data, HistData
from bs4 import BeautifulSoup
import re
import requests
from datetime import datetime, timedelta
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from api.serializers import DailyDataSerializer, Hist90DataSerializer, HistDataSerializer


url = "https://www.ecb.europa.eu/stats/eurofxref/eurofxref"

class Api(APIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    throttle_scope = "api"

    def __init__(self):
        self.data = get_data()

    def get(self, request):
        start = request.GET.get('start')
        end = request.GET.get('end')
        base = request.GET.get('base')
        symbols = request.GET.get('symbols')

        if start and end:
            resp = {}
            start_date = datetime.strptime(start, "%Y-%m-%d").date()
            end_date = datetime.strptime(end, "%Y-%m-%d").date()
            range_data = Hist90Data.objects.filter(date__range=(start_date, end_date))
            serializer = Hist90DataSerializer(range_data, many=True)
            for item in serializer.data:
                resp[item['date']] = item
            
            if base or symbols:
                print(f"###################### resp: {resp}")
                res = convert(serializer.data, base, symbols, True)
                return JsonResponse(res)

            print(f"resp many true json range: {resp}")
            return JsonResponse(resp)


        amount = request.GET.get('amount')
        result = get_result(self.data, base=base, symbols=symbols)
        print(f"result: {result}")
        base, date, rates = result.values()
        price = rates.get(symbols, 1)
        resp = float(amount) * price

        response = {
            "base": base,
            "date": date,
            "target": symbols,
            "value": amount,
            "price": price,
            "response": round(resp, 8)
        }

        return JsonResponse(response)


class Latest(APIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    throttle_scope = "latest"

    def __init__(self):
        self.data = get_data()

    def get(self, request):
        data = get_result(self.data, base=request.GET.get(
            'base'), symbols=request.GET.get('symbols'))
        return JsonResponse(data)


class getHist(APIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    throttle_scope = "hist"

    def __init__(self):
        self.data = None

    def get(self, request, year, month, day):
        date = year + '-' + month + '-' + day
        date = datetime.strptime(date, "%Y-%m-%d").date()
        self.data = get_data('hist-90d', date=date)
        return JsonResponse(self.data)


def get_data(data_type='daily', date=None, start=None, end=None):
    return get_data_net(data_type, date=date, start=start, end=end)


def get_result(data, base=None, symbols=None):
    if not base and not symbols:
        resp = {}
        date = data.pop('date')
        resp['date'] = date
        resp['base'] = base or "EUR"
        resp['rates'] = data
        return resp
    
    return convert(data, base, symbols)


def get_data_net(data_type, date=None, start=None, end=None):
    headers = set_headers(data_type)
    print(headers)
    print("######################")
    data_url = url + "-" + data_type + ".xml"
    response = requests.get(data_url, headers=headers)

    try:
        response.raise_for_status()
    except:
        print("Problem fetching data from network!!!")

    if response.text == '':
        return get_data_db(data_type, date=date, start=start, end=end)
    else:
        return save_data_db(response, data_type, date=date, start=start, end=end)


def get_data_db(data_type, date=None, start=None, end=None):
    print("Enter get_data_db")
    if data_type == 'daily':
        db_data = DailyData.objects.get()
        serializer = DailyDataSerializer(db_data)
        return serializer.data
    elif data_type == 'hist-90d':
        db_data = get_hist90data_db(date)
        return db_data


def set_headers(data_type):

    if data_type == 'daily':
        try:
            entry = DailyData.objects.get()
        except DailyData.DoesNotExist:
            entry = None

    elif data_type == 'hist-90d':
        try:
            entry = Hist90Data.objects.first()
        except DailyData.DoesNotExist:
            entry = None
    if entry:
        LastModifiedDatetime = entry.last_modified
        LastModified = LastModifiedDatetime.strftime(
            "%a, %d %b %Y %H:%M:%S ") + 'GMT'
        return {'If-Modified-Since': LastModified}
    else:
        return {}


def save_data_db(response, data_type, date=None, start=None, end=None):
    """
    Save data to database and return it 
    to the called function after parsing.
    """
    print("Enter save_data_db")

    if data_type == 'hist-90d':
        soup = BeautifulSoup(response.text, 'html.parser')
        days_list = soup.findAll(time=re.compile(".*"))
        data_list, data_dict = [], {}
        for day in days_list:
            day_date = datetime.strptime(day['time'], '%Y-%m-%d')
            lst = day.findAll(currency=re.compile(".*"))
            data, rates = {}, {}
            data['date'] = day_date.date()
            data['last_modified'] = datetime.strptime(
                                        response.headers['Last-Modified'], 
                                        '%a, %d %b %Y %H:%M:%S %Z'
                                    ).strftime("%Y-%m-%d %H:%M:%S")
        
            for item in lst:
                data[item['currency']] = item['rate']
            
            date_key = day_date.date().strftime("%Y-%m-%d")
            data_dict[date_key] = data
            data_list.append(data)
        
        hist90_data = Hist90Data.objects.all()
        hist90_data.delete()
        serializer = Hist90DataSerializer(data=data_list, many=True)
        if serializer.is_valid():
            serializer.save()
        else:
            print(f"serializer.errors: {serializer.errors}")
            return {}

        if date:
            return get_data_bydate(data_dict, date)
        
        if date and (start or end):
            return HttpResponseBadRequest("You can use either 'date' or 'start and end'!")
        
        if (start and not end) or (not start and end):
            return HttpResponseBadRequest("You should specify both start and end!")
        
        if start and end:
            pass

        return {}


    if data_type == 'daily':
        soup = BeautifulSoup(response.text, 'html.parser')
        time = soup.find(time=re.compile(".*"))
        date = datetime.strptime(time['time'], '%Y-%m-%d')
        lst = time.findAll(currency=re.compile(".*"))
        data, rates = {}, {}
        data['date'] = date.date()

        data['last_modified'] = datetime.strptime(
                                    response.headers['Last-Modified'], 
                                    '%a, %d %b %Y %H:%M:%S %Z'
                                ).strftime("%Y-%m-%d %H:%M:%S")
        for item in lst:
            data[item['currency']] = item['rate']
                
        
        instance = DailyData.objects.all()
        instance.delete()
        serializer = DailyDataSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            data.pop('last_modified')
            #date1 = data.pop('date')
            #resp = {}
            #resp['date'] = date1
            #resp['base'] = 'EUR'
            #resp['rates'] = data
            return data
        else:
            print(f"serializer.errors: {serializer.errors}")
            return {}


def get_data_bydate(dictionary ,date):
    date_arg = date.strftime("%Y-%m-%d")
    try:
        return dictionary[date_arg]
    except:
        date_minus1 = date - timedelta(days=1)
        return get_data_bydate(dictionary, date_minus1)

def get_hist90data_db(date):
    try:
        data_bydate = Hist90Data.objects.get(date=date)
        serializer = Hist90DataSerializer(data_bydate)
        return serializer.data
    except:
        date_minus1 = date - timedelta(days=1)
        return get_hist90data_db(date_minus1)


def convert(data, base=None, symbols=None, many=False):
    resp, rates, kaka = {}, {}, {}
    if many:
        for day_data in data:
            back = convert(day_data, base, symbols=symbols)
            kaka[back['date']] = back

        return kaka


    resp['date'] = data.pop('date')
    if base:
        base = base.upper()
    resp['base'] = base or 'EUR'

    if symbols:
        targets = [item.upper() for item in symbols.split(',')]
        print(f"===========> This is the error prone data: {data}")
        lst = [{'currency': target,
                'rate': data[target]
                } for target in targets if target.upper() != 'EUR']
    else:
        lst = [{'currency': target, 
                'rate': data[target]
                } for target in data.keys()]

    if base and base.upper() != 'EUR':  
        rate_base = data[base]
        if not symbols or 'EUR' in targets:
            rates['EUR'] = round(1/float(rate_base), 8)
        for item in lst:
            rates[item['currency']] = round(float(item['rate'])/float(rate_base), 8)
        if base in rates:
            rates.pop(base)
    else:
        for item in lst:
            rates[item['currency']] = round(float(item['rate']), 8)

    resp['rates'] = rates
    print(f"resp: {resp}")
    return resp
from django.shortcuts import render
from django.shortcuts import render
from django.views import View

# Create your views here.

class App(View):


    def get(self, request):
        return render(request, 'exchange/index.html')

    def post(self, request):
        pass

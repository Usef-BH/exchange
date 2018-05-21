from django.shortcuts import render
from django.http import JsonResponse
from django.views import View
from django.core.validators import validate_email
from rest_framework.views import APIView
from exchange.admin import UserCreationForm
from exchange.models import MyUser
from rest_framework.authtoken.models import Token
from django.db import IntegrityError

# Create your views here.

class App(View):
    def get(self, request):
        return render(request, 'exchange/index.html')


class Docs(View):

    def get(self, request):
        return render(request, 'exchange/docs.html')



class Register(APIView):

    throttle_classes = []
    
    def get(self, request):
        return render(request, 'exchange/register.html')

    def post(self, request):
        email = request.data.get('email', None)

        try:
            validate_email(email)
            valid_email = True
        except:
            valid_email = False
        

        if valid_email:
            first_name = request.data.get('first_name', None)
            last_name = request.data.get('last_name', None)
            password = request.data.get('password', None)
            try: 
                user = MyUser.objects.create_user(email, first_name, last_name, password=password)            
                token = Token.objects.create(user=user)
            except IntegrityError:
                data = {
                    "success": False,
                    "message": "This Email is alreay registered!"
                }
            else:
                data = {
                    "success": True,
                    "token": token.key
                }   

        else:
            success = False
            data = {
                "success": success
            }

        print(f"############==> data: {data}")
        return JsonResponse(data)
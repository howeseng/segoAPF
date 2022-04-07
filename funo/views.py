from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import *
from .models import Commodity
from .models import Farmer
from .forms import CreateUserForm, SupportForm,UpdateProfileForm
from django.shortcuts import render
from django.contrib.auth import get_user_model
from tensorflow.keras import backend
from tensorflow.keras.models import load_model
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import api_view
from django.conf import settings
from django.views.generic import View
from tensorflow.keras import backend as K
from pickle import load
from django.views.generic import DetailView
from django.views.generic import ListView
from django.shortcuts import render
import requests




User = get_user_model()
def registerPage(request):
    if request.user.is_authenticated:
        return redirect('aboutus')
    else:
        form = CreateUserForm()

        if request.method == 'POST':
            form = CreateUserForm(request.POST)
            if form.is_valid():
                form.save()
                user = form.cleaned_data.get('username')
                password = form.cleaned_data.get('password1')
                company = form.cleaned_data.get('company')
                messages.success(request, 'Account was created for ' + user )
                return redirect('login')

        context = {'form':form}

        return render(request, 'funo/register.html', context)

def loginPage(request):
    if request.user.is_authenticated:
         return redirect('aboutus')
    else:
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request,user)
                return redirect('aboutus')
            else:
                messages.info(request, 'Username OR password is incorrect')

        context = {}

        return render(request, 'funo/login.html', context)


def logoutUser(request):
	logout(request)
	return redirect('login')


def fill_missing(past_data):
        for row in range(past_data.shape[0]):
            for col in range(past_data.shape[1]):
                if np.isnan(past_data[row, col]):
                    i = 1
                    missing_next = past_data[row + i, col]
                    while(np.isnan(missing_next)):
                        i += 1
                        missing_next = past_data[row + i, col]
                    past_data[row, col] = past_data[row - 1, col] + ((missing_next - past_data[row - 1, col]) / (i+1))
                    
def data_Predict(request,*args,**kwargs):
        K.clear_session()
        my_thing = request.session.get('data', None)
        past_data = pd.read_csv(my_thing['dataFile'])
        features = pd.read_csv(my_thing['featuresFile'])
        multivariate = my_thing['multivariate']
        regressor = load_model(my_thing['modelFile'])
        scaler = load(open(my_thing['scalerFile'], 'rb'))
        duration = my_thing['duration']
        forecast= my_thing['forecast']
        current= my_thing['current']
        title=my_thing['title']
        commodity = my_thing['commodity']        
        current_price = 0
        current_date = ""
        univalue = my_thing['univalue']
        multivalue = my_thing['multivalue']

        date=past_data['Date'].iloc[-current:]
        date=pd.to_datetime(date)
        current_date = date.iloc[-1]
        date =date.tolist()
        if forecast==0:
            date=date
            past_data.set_index(['Date'], inplace= True)
            fill_missing(past_data.values)
            past_data = past_data.round(2)
            past_price = past_data.loc[:]['Harga Ladang'].round(2)
            past_price = past_data['Harga Ladang'].iloc[-current:].round(2)
            current_price = past_price.iloc[-1]
            past_price = list(map(str, past_price))

            date = list(map(str, date))
            for i in range (0, len(date)):
                date[i] = date[i].split(' ')[0]
            data={
                'commodityItem':commodity,
                'current_price':current_price,
                'current_date':current_date,
                'forecast':forecast,
                'title':title,
                'labels':','.join(date),
                'default': ','.join(past_price)
            }
        else:
            if multivariate == "True" and not(commodity=="Coconut" or commodity =="Chicken" or commodity =="Egg (Grade A)" or commodity =="Egg (Grade B)" or commodity =="Egg (Grade C)") :
                date2=past_data["Date"].iloc[-1]
                date2=pd.Series(pd.date_range(date2, periods=forecast+1, freq='7D'))
                date2=date2[1:].tolist()   
                date=date + date2

                date = list(map(str, date))
                for i in range (0, len(date)):
                    date[i] = date[i].split(' ')[0]

                past_data.set_index(['Date'], inplace= True)
                features.set_index(['Date'], inplace= True)
                fill_missing(past_data.values)
                past_data = past_data.round(2)
                past_price = past_data.loc[:]['Harga Ladang'].round(2)
                past_price2 = past_price
                past_price2 = np.array(past_price2)
                past_price2 = past_price2.reshape(len(past_price2), 1)

                past_features = features.head(len(past_price2))
                past_crude_oil_price = past_features.loc[:, ['Crude Oil Price']]
                past_crude_oil_price = np.array(past_crude_oil_price)
                past_crude_oil_price = past_crude_oil_price / 1000
                past_features = past_features.loc[:, ['Temperature (Celcius)', 'Humidity(%)']]
                past_features = np.array(past_features)
                past_price2 = np.append(past_price2, past_features, axis=1)
                past_price2 = np.append(past_price2, past_crude_oil_price, axis=1)

                feedin_price = []
                feedin_price.append(past_price2[(len(past_price2)-52):])
                feedin_price = np.array(feedin_price)

                feedin_price_scaled = scaler.transform(feedin_price.reshape(-1, 1))
                feedin_price_scaled = feedin_price_scaled.reshape(-1, 4)
                feedin_price_scaled = feedin_price_scaled.reshape(1, -1, 4)
                
                future_price = regressor.predict(feedin_price_scaled)
                future_price = scaler.inverse_transform(future_price)
                future_price = future_price.reshape(-1 ,1)
            
                future_price=future_price.round(2).tolist()
                func = lambda x: round(x,2)
                future_price = [list(map(func, i)) for i in future_price]
                past_price = past_data['Harga Ladang'].iloc[-current:].round(2)
                
                past_price= past_price.tolist() + future_price #so I get total_price and date(complete) #future price is 52
                if forecast!=52:
                    for i in range(0,(52-forecast)):
                        past_price.pop()

                past_price = list(map(str, past_price))

                for i in range (1, len(past_price)):
                    past_price[i] = past_price[i].replace('[', '').replace(']', '')
                current_price = past_price[len(past_price)-forecast]

            else:
                date2=past_data["Date"].iloc[-1]
                date2=pd.Series(pd.date_range(date2, periods=forecast+1, freq='7D'))
                date2=date2[1:].tolist()   
                date=date + date2
            
                past_data.set_index(['Date'], inplace= True)
                fill_missing(past_data.values)
                past_data = past_data.round(2)
                past_price = past_data.loc[:]['Harga Ladang'].round(2)
                
            
                date = list(map(str, date))
                for i in range (0, len(date)):
                    date[i] = date[i].split(' ')[0]
                feedin_price = []
                feedin_price.append(past_price[(len(past_price)-52):])
                feedin_price = np.array(feedin_price)

                feedin_price_scaled = scaler.transform(feedin_price.reshape(-1, 1))
                feedin_price_scaled = feedin_price_scaled.reshape(1, feedin_price_scaled.shape[0], 1)
                
                future_price = regressor.predict(feedin_price_scaled)
                future_price = scaler.inverse_transform(future_price)
                future_price = future_price.reshape(-1 ,1)
            
                future_price=future_price.round(2).tolist()
                func = lambda x: round(x,2)
                future_price = [list(map(func, i)) for i in future_price]
                past_price = past_data['Harga Ladang'].iloc[-current:].round(2)
                
                past_price= past_price.tolist() + future_price #so I get total_price and date(complete) #future price is 52
                if forecast!=52:
                    for i in range(0,(52-forecast)):
                        past_price.pop()

                past_price = list(map(str, past_price))

                for i in range (1, len(past_price)):
                    past_price[i] = past_price[i].replace('[', '').replace(']', '')
                current_price = past_price[len(past_price)-forecast]
                

            data={
                'commodityItem':commodity,
                'current_price':current_price,
                'current_date':current_date,
                'forecast':forecast,
                'univariateMSE':univalue,
                'multivariateMSE':multivalue,
                'multivariate':multivariate,
                'title':title,
                'labels':','.join(date),
                'default': ','.join(past_price)
            }
        print(len(date))
        print(len(past_price))
        K.clear_session()
        return JsonResponse(data)




@login_required(login_url='login')
def dashboard(request):
    dataFile='rawData/poultry/chicken/chicken.csv'
    featuresFile = 'rawData/features.csv'
    multivariate = "False"
    modelFile='rawData/poultry/chicken/chicken.h5'
    scalerFile = 'rawData/poultry/chicken/chicken.pkl'
    durationVar=0
    forecast=52
    current=260
    title="Chicken Field Price Forecast"
    commodity2 = "Chicken"
    univalue = 0.09569272
    multivalue = 0
    
    if request.method=='GET':
            commodity=request.GET.get('commodity')
            duration=request.GET.get('duration')
            datatype=request.GET.get('datatype')
            multivariateget=request.GET.get('multivariate')

            if commodity=='coconut':
                dataFile='rawData/coconut/coconut.csv'
                multivariate = multivariateget
                modelFile='rawData/coconut/coconut.h5'
                scalerFile = 'rawData/coconut/coconut.pkl'
                title="Coconut Field Price Forecast"
                commodity2 = "Coconut"
                univalue = 0.001896
                multivalue = 0

            
            elif commodity=='kangkung':
                dataFile='rawData/vegetables/kangkung/kangkung.csv'
                multivariate = multivariateget
                if multivariate == "True":
                    modelFile='rawData/vegetables/kangkung/multivariate/kangkung.h5'
                    scalerFile = 'rawData/vegetables/kangkung/multivariate/kangkung.pkl'
                elif multivariate == "False":
                    modelFile='rawData/vegetables/kangkung/univariate/kangkung.h5'
                    scalerFile = 'rawData/vegetables/kangkung/univariate/kangkung.pkl'
                title="Water Spinach Field Price Forecast"
                commodity2 = "Water Spinach (Kang-kong)"
                univalue = 0.021554
                multivalue = 0.016047

            elif commodity=='sawiHijau':
                dataFile='rawData/vegetables/sawiHijau/sawiHijau.csv'
                multivariate = multivariateget
                if multivariate == "True":
                    modelFile='rawData/vegetables/sawiHijau/multivariate/sawiHijau.h5'
                    scalerFile = 'rawData/vegetables/sawiHijau/multivariate/sawiHijau.pkl'
                elif multivariate == "False":
                    modelFile='rawData/vegetables/sawiHijau/univariate/sawiHijau.h5'
                    scalerFile = 'rawData/vegetables/sawiHijau/univariate/sawiHijau.pkl'
                title="Choy Sum Field Price Forecast"
                commodity2 = "Choy Sum"
                univalue = 0.040811
                multivalue = 0.061290
            
            elif commodity=='tomato':
                dataFile='rawData/fruits/tomato/tomato.csv'
                multivariate = multivariateget
                if multivariate == "True":
                    modelFile='rawData/fruits/tomato/multivariate/tomato.h5'
                    scalerFile = 'rawData/fruits/tomato/multivariate/tomato.pkl'
                elif multivariate == "False":
                    modelFile='rawData/fruits/tomato/univariate/tomato.h5'
                    scalerFile = 'rawData/fruits/tomato/univariate/tomato.pkl'
                title="Tomato Field Price Forecast"
                commodity2 = "Tomato"
                univalue = 0.548961
                multivalue = 0.378119

            elif commodity=='chilli':
                dataFile='rawData/fruits/chilli/chilli.csv'
                multivariate = multivariateget
                if multivariate == "True":
                    modelFile='rawData/fruits/chilli/multivariate/chilli.h5'
                    scalerFile = 'rawData/fruits/chilli/multivariate/chilli.pkl'
                elif multivariate == "False":
                    modelFile='rawData/fruits/chilli/univariate/chilli.h5'
                    scalerFile = 'rawData/fruits/chilli/univariate/chilli.pkl'
                title="Red Chilli Field Price Forecast"
                commodity2 = "Red Chili"
                univalue = 0.814060
                multivalue = 0.438423

            elif commodity=='chicken':
                dataFile='rawData/poultry/chicken/chicken.csv'
                multivariate = multivariateget
                modelFile='rawData/poultry/chicken/chicken.h5'
                scalerFile = 'rawData/poultry/chicken/chicken.pkl'
                title="Chicken Field Price Forecast"
                commodity2 = "Chicken"
                univalue = 0.095693
                multivalue = 0

            elif commodity=='eggA':
                dataFile='rawData/poultry/eggA/eggA.csv'
                multivariate = multivariateget
                modelFile='rawData/poultry/eggA/eggA.h5'
                scalerFile = 'rawData/poultry/eggA/eggA.pkl'
                title="Egg (Grade A) Field Price Forecast"
                commodity2 = "Egg (Grade A)"
                univalue = 0.000375
                multivalue = 0

            elif commodity=='eggB':
                dataFile='rawData/poultry/eggB/eggB.csv'
                multivariate = multivariateget
                modelFile='rawData/poultry/eggB/eggB.h5'
                scalerFile = 'rawData/poultry/eggB/eggB.pkl'
                title="Egg (Grade B) Field Price Forecast"
                commodity2 = "Egg (Grade B)"
                univalue = 0.000347
                multivalue = 0

            elif commodity=='eggC':
                dataFile='rawData/poultry/eggC/eggC.csv'
                multivariate = multivariateget
                modelFile='rawData/poultry/eggC/eggC.h5'
                scalerFile = 'rawData/poultry/eggC/eggC.pkl'
                title="Egg (Grade C) Field Price Forecast"
                commodity2 = "Egg (Grade C)"
                univalue = 0.000301
                multivalue = 0
            
            elif commodity=="":
                dataFile='rawData/poultry/chicken/chicken.csv'
                multivariate = multivariateget
                modelFile='rawData/poultry/chicken/chicken.h5'
                scalerFile = 'rawData/poultry/chicken/chicken.pkl'
                title="Chicken Field Price Forecast"
                commodity2 = "Chicken"
                univalue = 0.095693
                multivalue = 0
            

            if duration=="sixmonth":
                durationVar=26
            
            elif duration=="oneyear":
                durationVar=53
            
            elif duration=="fiveyear":
                durationVar=260

            elif duration=="threeyear": 
                durationVar=156

            elif duration=="tenyear":
                durationVar=520

            elif duration=="":
                durationVar=260
            
            if datatype=="pastdata":
                forecast=0
                current=durationVar-forecast

            elif datatype=="forecast3month":
                if durationVar<13:
                    forecast=13
                    current=forecast
                else:
                    forecast=13
                    current=durationVar-forecast

            elif datatype=="forecast6month":
                if durationVar==26:
                    forecast=26
                    current=1
                else:
                    forecast=26
                    current=durationVar-forecast

            elif datatype=="forecast1year":                    
                if durationVar<52:
                    forecast=52
                    current=1
                else:
                    forecast=52
                    current=durationVar-forecast

            elif datatype=="":
                if durationVar<52:
                    forecast=52
                    current=forecast
                else:
                    forecast=52
                    current=durationVar-forecast
             
            
            print(dataFile)
            data={
                'dataFile':dataFile,
                'featuresFile':featuresFile,
                'multivariate':multivariate,
                'modelFile':modelFile,
                'scalerFile':scalerFile,
                'duration':durationVar,
                'forecast':forecast,
                'current':current,
                'title':title,
                'commodity':commodity2,
                'univalue':univalue,
                'multivalue':multivalue
            }
            request.session['data']=data

    context = {'page':'Forecast Commodities Price Dashboard'}

    return render(request, 'funo/dashboard.html',context)


@login_required(login_url='login')
def user(request):
    if request.method == 'POST':
            print("HEHE")
            form = UpdateProfileForm(request.POST,instance=request.user.profile)
            if form.is_valid():
                form.save()
                messages.success(request, 'Profile Updated!' )
                return redirect('user')
            else:
                print(form.errors)
            context={
                'user':user,
                'name':request.user.get_username(),
                'form':form,
                'page':'User Profile'
            }
    
    else:
        form = UpdateProfileForm(instance=request.user.profile)
        context={
                'user':user,
                'name':request.user.get_username(),                
                'form':form,
                'page':'User Profile'   
            }    
    
    return render(request, 'funo/user.html',context)


@login_required(login_url='login')
def commodity_list(request):
   

    context = {'page':'Forecast Commodities Price Dashboard'}

    return render(request, 'funo/commodity_list.html',context)


@login_required(login_url='login')
def farmer(request):

    direc = Farmer.objects.all()
    comms = Commodity.objects.all()

    return render(request, 'funo/farmer.html', {'direc': direc, 'comms': comms}) 


@login_required(login_url='login')
def supplier(request):
    comms = Commodity.objects.all()

    return render(request, 'funo/supplier.html', {'comms': comms }) 


@login_required(login_url='login')
def user(request):
    if request.method == 'POST':
            print("HEHE")
            form = UpdateProfileForm(request.POST,instance=request.user.profile)
            if form.is_valid():
                form.save()
                messages.success(request, 'Profile Updated!' )
                return redirect('user')
            else:
                print(form.errors)
            context={
                'user':user,
                'name':request.user.get_username(),
                'form':form,
                'page':'User Profile'
            }
    
    else:
        form = UpdateProfileForm(instance=request.user.profile)
        context={
                'user':user,
                'name':request.user.get_username(),                
                'form':form,
                'page':'User Profile'   
            }    
    
    return render(request, 'funo/user.html',context)


@login_required(login_url='login')
def support(request):
    form = SupportForm()

    if request.method == 'POST':
            form = SupportForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Thanks for reaching us!' )
                return redirect('support')

    context = {'form':form,'page':'Contact Us'}

    return render(request, 'funo/support.html', context)





@login_required(login_url='login')
def news(request): 
   
    comms = Commodity.objects.all()
       

    return render(request, 'funo/news.html',{'comms':comms}) 

@login_required(login_url='login')
def aboutus(request):

    context = {'page':'About Us'}

    return render(request, 'funo/aboutus.html', context)

@login_required(login_url='login')
def modalcommodity(request):

    context = {

    

        'comms': Commodity.objects.all()
    }

    return render(request, 'funo/modalcommodity.html', context)

@login_required(login_url='login')
def function(request):

    context = {

        'comms': Commodity.objects.all()
        
    }

    return render(request, 'funo/function.html', context)

login_required(login_url='login')
def commodity_info(request):

    comms = Commodity.objects.all()

    return render(request, 'funo/commodity_info/<slug>.html', {'comms': comms}) 


class CommodityListView(ListView):
    model = Commodity
    template_name = "function.html"

class  CommodityDetailView(DetailView):
    model = Commodity
    template_name = "funo/commodity_info.html"

    def get_context_data(self, **kwargs):
        context = super(CommodityDetailView, self).get_context_data(**kwargs)
        context['comms'] = Commodity.objects.all()
        return context  


@login_required(login_url='login')
def subscription(request):

    context = {'page':'Subscription Plans & FaQ'}

    return render(request, 'funo/subscription.html', context)

@login_required(login_url='login')
def usermanual(request):

    context = {'page':'User Instruction Manual'}

    return render(request, 'funo/usermanual.html', context)


def home(request):

    context = {'page':'Home'}

    return render(request, 'funo/home.html', context)



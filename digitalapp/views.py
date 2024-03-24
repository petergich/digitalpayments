from django.shortcuts import render, redirect
import requests
from datetime import datetime
import json
import base64
from django.http import JsonResponse
from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from .models import *
from django.http import JsonResponse
from django.conf import settings
import requests
from django.contrib.auth.models import User
import urllib.parse
from django.contrib.auth.hashers import make_password, check_password
from datetime import datetime
from django.contrib.auth.decorators import user_passes_test
import time
from cryptography.fernet import Fernet
#original_key = b'vDGYOhWgY_J4O2dz2OlfPDvG2dI5LW_GnIvXdfb4bVA='

# Initialize Fernet cipher suite with the original key
#cipher_suite = Fernet(original_key)



#
def home(request):
    return render(request,"index.html")

@login_required(login_url='sellerlogin') 
def sellerhome(request):
    try:
        username = request.user.username
        user=seller.objects.get(buss_name=username)
        return render(request,"seller.html",{"user":user})
    except:
        return redirect('sellerlogin')
@login_required(login_url='sellerlogin') 
def sell(request):
    try:
        username = request.user.username
        user=seller.objects.get(buss_name=username)
        
        return render(request,"sell.html",{"username":username,"user":user})
    except:
        return redirect('sellerlogin')
def customerregister(request):
    if request.method=="POST":
        username=request.POST.get('username')
        email=request.POST.get('email')
        password= request.POST.get('password')
        hashed_password = make_password(password)
        if User.objects.filter(username=username).exists():
            return render(request,"customerregister.html",{"message":"That username is already taken"})
        if User.objects.filter(email=email).exists():
            return render(request,"customerregister.html",{"message":"Email is already registered "})
        else:
            user=User.objects.create_user(username=username, email=email, password=password)
            customerr=customer(username=username,email=email,password=hashed_password)
            try:
                user.save()
                customerr.save()
                return render(request,"customerregister.html",{"message":"Succesfully registered"})
            except:
                return render(request,"customerregister.html",{"message":"An error occured while trying to save you details"})
    return render(request,"customerregister.html")

def customerlogin(request):
    if request.method=="POST":
        username=request.POST.get("username")
        password=request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None and customer.objects.filter(username=username).exists():
            login(request, user)
            return redirect('customerhome')  # Redirect to the home page after successful login
        else:
            return render(request, "sellerlogin.html", {"message": "Invalid credentials"})
    return render(request,"customerlogin.html") 
@login_required(login_url="customerlogin") 
def customerhome(request):
    user=request.user
    try:
        username = request.user.username
        user=customer.objects.get(username=username)
    except:
        return redirect("customerlogin")
    customerr=customer.objects.get(username=user.username)
    return render(request, "customerhome.html",{"customer":customerr})
@login_required(login_url="customerlogin") 
def paymentinfo(request):
    if request.method=="POST":
        fname=request.POST.get("fname")
        lname=request.POST.get("lname")
        cardno=request.POST.get("cardno")
        expiry=request.POST.get("expiry")
        cvc=request.POST.get("cvc")
        try:
            user=customer.objects.get(username=request.user.username)
            user.f_name=fname
            user.l_name=lname
            user.card_no=cardno
            user.cvc=cvc
            user.expiry=expiry
            user.save()
            user=customer.objects.get(username=request.user.username)
            return render(request, "paymentinfo.html",{"customer":user,"message":"Successfully Updated"})
        except:
            user=customer.objects.get(username=request.user.username)
            return render(request, "paymentinfo.html",{"customer":user,"message":"An error occured while updating your info"})
    user=request.user
    try:
        username = request.user.username
        user=customer.objects.get(username=username)
    except:
        return redirect("customerlogin")
    user=customer.objects.get(username=user.username)
    return render(request, "paymentinfo.html",{"customer":user})
def sellerregister(request):
    if request.method=="POST":
        buss_name=request.POST.get('bussname')
        email=request.POST.get('email')
        phone=request.POST.get('phone')
        registration_no=request.POST.get('registration_no')
        password=request.POST.get("password")
        hashed_password = make_password(password)
        if seller.objects.filter(buss_name=buss_name).exists() or customer.objects.filter(username=buss_name):
            return render(request,"sellerregister.html",{"message":"A business with the Bussiness name already exists if it's you go to the login page"})
        if User.objects.filter(email=email).exists():
            return render(request,"sellerregister.html",{"message":"A business with the email name already exists if it's you go to the login page"})
        if seller.objects.filter(registration_number=registration_no).exists():
            return render(request,"sellerregister.html",{"message":"A business with the registration already exists "})
        if seller.objects.filter(phone_number=phone).exists():
            return render(request,"sellerregister.html",{"message":"A business with the phone number already exists"})
        user=seller(buss_name=buss_name,phone_number=phone,email=email,registration_number=registration_no,password=hashed_password)
        try:
            iuser = User.objects.create_user(username=buss_name, email=email, password=password)
            iuser.save()
            user.save()
            seler=seller.objects.get(buss_name=buss_name)
            

            # Get the current date and time
            current_datetime = datetime.now()

            # Get the current date
            current_date = current_datetime.date()
            regis=registration_request(seller=seler,date=current_date)
            regis.save()
            return render(request,"sellerregister.html",{"message":"Succesfully registered"})
        except:
            return render(request,"sellerregister.html",{"message":"An error occured while trying to save you details"})
    return render(request,"sellerregister.html")
def customerdebit(request):
    if request.method=="POST":
        user=request.POST.get("user")
        amount=request.POST.get("amount")
        phone=request.POST.get("phone")
        if amount=="" or int(amount)<1 or phone=="":
            if request.user.is_authenticated:
                return redirect("sell")
            else:
                return redirect("home")
        try:
            sellerx=seller.objects.get(buss_name=user)
            response=initiate_stk_push(amount,phone,sellerx)
            print(response.content)
            status=query_stk_status(response,sellerx)
            print("status",status.content)
            if request.user.is_authenticated:
                return redirect("sell")
            else:
                return redirect("home")
        except:
            if request.user.is_authenticated:
                return redirect("sell")
            else:
                return redirect("home")
    user=request.GET.get("user")
    amount=request.GET.get("amount")
    context={"user":user,"amount":amount}
    return render(request,"customerdebit.html",context)     
def sellerlogin(request):
    if request.method == "POST":
        bussname = request.POST.get("bussname")
        passw = request.POST.get("password")
        
        # Authenticate the user
        user = authenticate(request, username=bussname, password=passw)
        if user is not None and seller.objects.filter(buss_name=bussname).exists():
            login(request, user)
            return redirect('sellerhome')  # Redirect to the home page after successful login
        else:
            return render(request, "sellerlogin.html", {"message": "Invalid credentials"})
    
    # If it's a GET request, just render the login page
    return render(request, "sellerlogin.html")
# def is_superuser_with_staff_status(user):
#     return user.is_superuser and user.is_staff
@login_required(login_url='superadminlogin')
# @user_passes_test(is_superuser_with_staff_status)
def superadminhome(request):
    if not request.user.is_superuser or not request.user.is_staff:
        return redirect('superadminlogin')
    return render(request,"superadminhome.html",{"context":registration_request.objects.order_by('seller__status','-date')})
@login_required(login_url='superadminlogin')
#user_passes_test(is_superuser_with_staff_status)
def requestprocess(request):
    if not request.user.is_superuser or not request.user.is_staff:
        return redirect('superadminlogin')
    if request.method=="POST":
            scode=request.POST.get('shortcode')
            ckey=request.POST.get('consumerkey')
            skey=request.POST.get('secretkey')
            pkey=request.POST.get('passkey')
            r=registration_request.objects.get(id=request.POST.get('id'))
            seler=r.seller
            if scode!="":
                seler.buss_shortcode=scode
            if ckey!="":
                seler.consumer_key=ckey
            if skey!=skey:
                seler.secret_key=skey
            if pkey!=pkey:
                seler.passkey=pkey
            seler.status=True
            try:
                seler.save()
                return render(request,"requestprocess.html",{"request":registration_request.objects.get(id=request.POST.get('id')),"message":"Successfully updated"})
            except:
                return render(request,"requestprocess.html",{"request":registration_request.objects.get(id=request.POST.get('id')),"mmessage":"An error occured while trying to save"})
    if "id" in request.GET:
    
        return render(request,"requestprocess.html",{"request":registration_request.objects.get(id=request.GET.get('id'))})
    return redirect("superadminhome")
def superadminlogin(request):
    if request.method == "POST":
        username = request.POST.get("username")
        passw = request.POST.get("password")
        
        # Authenticate the user
        user = authenticate(request, username=username, password=passw)
        
        if user is not None and user.is_superuser and user.is_staff:
            login(request, user)
            return redirect('superadminhome')  # Redirect to the home page after successful login
        else:
            return render(request, "superadminlogin.html", {"message": "Invalid credentials"}) 
    return render(request,"superadminlogin.html")
#def encrypt(number):
 #   encrypted_text = cipher_suite.encrypt(number.encode())
  #  return encrypted_text

# Decrypt the card number when you need to use it
#def decrypt(number):
 #   decrypted_text = cipher_suite.decrypt(number).decode()
 #   return decrypted_text



# Usage example
# Encrypt data before
 # This should print the original plain text
def get_access_token(seller):
    consumer_key = seller.consumer_key  
    consumer_secret = seller.secret_key  
    access_token_url = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'
    headers = {'Content-Type': 'application/json'}
    auth = (consumer_key, consumer_secret)
    try:
        response = requests.get(access_token_url, headers=headers, auth=auth)
        response.raise_for_status() 
        result = response.json()
        access_token = result['access_token']
        return JsonResponse({'access_token': access_token})
    except requests.exceptions.RequestException as e:
        return JsonResponse({'error': str(e)})
    

def initiate_stk_push(amount,phone,seller):
    access_token_response = get_access_token(seller)
    if isinstance(access_token_response, JsonResponse):
        access_token = access_token_response.content.decode('utf-8')
        access_token_json = json.loads(access_token)
        access_token = access_token_json.get('access_token')
        if access_token:
            amount = int(amount)
            phone = phone
            passkey = seller.passkey
            business_short_code = seller.buss_shortcode
            process_request_url = 'https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest'
            callback_url = 'https://digitalpayments.onrender.com/mpesa/callback/'
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            password = base64.b64encode((business_short_code + passkey + timestamp).encode()).decode()
            party_a = phone
            party_b = phone
            account_reference = seller.buss_name
            transaction_desc = 'stkpush test'
            stk_push_headers = {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + access_token
            }
            
            stk_push_payload = {
                'BusinessShortCode': business_short_code,
                'Password': password,
                'Timestamp': timestamp,
                'TransactionType': 'CustomerPayBillOnline',
                'Amount': amount,
                'PartyA': party_a,
                'PartyB': business_short_code,
                'PhoneNumber': party_a,
                'CallBackURL': callback_url,
                'AccountReference': account_reference,
                'TransactionDesc': transaction_desc
            }

            try:
                response = requests.post(process_request_url, headers=stk_push_headers, json=stk_push_payload)
                response.raise_for_status()   
                # Raise exception for non-2xx status codes
                response_data = response.json()
                checkout_request_id = response_data['CheckoutRequestID']
                response_code = response_data['ResponseCode']
                
                if response_code == "0":
                    return JsonResponse({"response": response_data})
                else:
                    return JsonResponse({'error': 'STK push failed.'})
            except requests.exceptions.RequestException as e:
                return JsonResponse({'error': str(e)})
        else:
            return JsonResponse({'error': 'Access token not found.'})
    else:
        return JsonResponse({'error': 'Failed to retrieve access token.'})
def query_stk_status(request):
    
    access_token_response = get_access_token(seller)
    if isinstance(access_token_response, JsonResponse):
        access_token = access_token_response.content.decode('utf-8')
        access_token_json = json.loads(access_token)
        access_token = access_token_json.get('access_token')
        if access_token:
            query_url = 'https://sandbox.safaricom.co.ke/mpesa/stkpushquery/v1/query'
            business_short_code =seller.buss_shortcode
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            passkey = seller.passkey
            password = base64.b64encode((business_short_code + passkey + timestamp).encode()).decode()
            response_string = request.decode('utf-8')

            # Parse the JSON string into a Python dictionary
            response_data = json.loads(response_string)

            # Access the value of "CheckoutRequestID" from the nested dictionary
            checkout_request_id = response_data['response']['CheckoutRequestID']

            query_headers = {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + access_token
            }

            query_payload = {
                'BusinessShortCode': business_short_code,
                'Password': password,
                'Timestamp': timestamp,
                'CheckoutRequestID': checkout_request_id
            }

            try:
                response = requests.post(query_url, headers=query_headers, json=query_payload)
                response.raise_for_status()
                # Raise exception for non-2xx status codes
                response_data = response.json()

                if 'ResultCode' in response_data:
                    result_code = response_data['ResultCode']
                    if result_code == '1037':
                        message = "1037 Timeout in completing transaction"
                    elif result_code == '1032':
                        message = "1032 Transaction has been canceled by the user"
                    elif result_code == '1':
                        message = "1 The balance is insufficient for the transaction"
                    elif result_code == '0':
                        message = "0 The transaction was successful"
                    else:
                        message = "Unknown result code: " + result_code
                else:
                    message = "Error in response"

                return JsonResponse({'message': message})  # Return JSON response
            except requests.exceptions.RequestException as e:
                return JsonResponse({'error1': 'Error: ' + str(e)})  # Return JSON response for network error
            except json.JSONDecodeError as e:
                return JsonResponse({'error2': 'Error decoding JSON: ' + str(e)})  # Return JSON response for JSON decoding error
        else:
            return JsonResponse({'error': 'Access token not found.'})
    else:
        return JsonResponse({'error': 'Failed to retrieve access token.'})
def process_stk_callback(request):
        print("called")
        stk_callback_response = json.loads(request.body)
        log_file = "Mpesastkresponse.json"
        with open(log_file, "a") as log:
            json.dump(stk_callback_response, log)
        
        merchant_request_id = stk_callback_response['Body']['stkCallback']['MerchantRequestID']
        checkout_request_id = stk_callback_response['Body']['stkCallback']['CheckoutRequestID']
        result_code = stk_callback_response['Body']['stkCallback']['ResultCode']
        result_desc = stk_callback_response['Body']['stkCallback']['ResultDesc']
        amount = stk_callback_response['Body']['stkCallback']['CallbackMetadata']['Item'][0]['Value']
        transaction_id = stk_callback_response['Body']['stkCallback']['CallbackMetadata']['Item'][1]['Value']
        user_phone_number = stk_callback_response['Body']['stkCallback']['CallbackMetadata']['Item'][4]['Value']
        print( )
        if result_code == 0:
        #  store the transaction details in the database
            print("okay peter")
def initiate_payment(request):
    if request.method == 'POST':
        # Collect payment details from the user
        amount = request.POST.get('amount')
        invoice_number = request.POST.get('invoice_number')
        description = request.POST.get('description')
        email = request.POST.get('email')
        card_number = request.POST.get('card_number')
        card_expiry = request.POST.get('card_expiry')
        card_cvv = request.POST.get('card_cvv')

        # Prepare parameters for the Pesapal API request
        pesapal_consumer_key = settings.PESAPAL_CONSUMER_KEY
        pesapal_consumer_secret = settings.PESAPAL_CONSUMER_SECRET

        pesapal_params = {
            'oauth_consumer_key': pesapal_consumer_key,
            'oauth_signature_method': 'PLAINTEXT',
            'oauth_signature': f'{pesapal_consumer_secret}&',
            'pesapal_merchant_reference': invoice_number,
            'pesapal_amount': amount,
            'pesapal_currency': 'KES',  # Currency code (Kenyan Shilling)
            'pesapal_description': description,
            'pesapal_email': email,
            'card_no': card_number,
            'card_cvv': card_cvv,
            'card_expiry': card_expiry,
            'payment_method': 'visa',  # Specify the payment method (e.g., 'visa', 'mastercard')
        }

        # Make an API request to Pesapal to process the payment
        pesapal_response = requests.post(
            'https://www.pesapal.com/API/PostPesapalDirectOrderV4',
            data=pesapal_params
        )

        # Parse the response
        response_data = pesapal_response.text

        # Return the response data as JSON
        return JsonResponse({'response_data': response_data})
    else:
        # Render a form for the user to enter payment details
        return HttpResponse("An error occured")

# Create your views here.

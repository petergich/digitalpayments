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

def home(request):
    return render(request,"index.html")

@login_required(login_url='sellerlogin') 
def sellerhome(request):
    try:
        username = request.user.username
        user=seller.objects.get(buss_name=username)
        
        return render(request,"seller.html")
    except:
        return redirect('sellerlogin')
@login_required(login_url='sellerlogin') 
def sell(request):
    try:
        username = request.user.username
        password= request.user.password
        user=seller.objects.get(buss_name=username)
        
        return render(request,"sell.html",{"username":username})
    except:
        return redirect('sellerlogin')
def customerregister(request):
    return render(request,"customerregister.html")
def customerlogin(request):
    return render(request,"customerlogin.html")  
def sellerregister(request):
    if request.method=="POST":
        buss_name=request.POST.get('bussname')
        email=request.POST.get('email')
        phone=request.POST.get('phone')
        registration_no=request.POST.get('registration_no')
        password=request.POST.get("password")
        hashed_password = make_password(password)
        if seller.objects.filter(buss_name=buss_name).exists():
            return render(request,"sellerregister.html",{"message":"A business with the Bussiness name already exists if it's you go to the login page"})
        if seller.objects.filter(email=email).exists():
            return render(request,"sellerregister.html",{"message":"A business with the email name already exists if it's you go to the login page"})
        if seller.objects.filter(registration_number=registration_no).exists():
            return render(request,"sellerregister.html",{"message":"A business with the registration already exists "})
        if seller.objects.filter(phone_number=phone).exists():
            return render(request,"sellerregister.html",{"message":"A business with the phone number already exists"})
        user=seller(buss_name=buss_name,phone_number=phone,email=email,registration_number=registration_no,password=hashed_password)
        try:
            iuser = User.objects.create_user(username='username', email='email@example.com', password='password')
            iuser.save()
            user.save()
            return render(request,"sellerregister.html",{"message":"Succesfully registered"})
        except:
            return render(request,"sellerregister.html",{"message":"An error occured while trying to save you details"})
    return render(request,"sellerregister.html")
def customerdebit(request):
    if request.method=="POST":
        user=request.POST.get("user")
        amount=request.POST.get("amount")
        phone=request.POST.get("phone")
        sellerx=seller.objects.get(buss_name=user)
        response=initiate_stk_push(amount,phone,sellerx)
        return render(request,"customerdebit.html")
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
        
        if user is not None:
            login(request, user)
            return redirect('sellerhome')  # Redirect to the home page after successful login
        else:
            return render(request, "sellerlogin.html", {"message": "Invalid credentials"})
    
    # If it's a GET request, just render the login page
    return render(request, "sellerlogin.html")
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
            callback_url = 'https://kariukijames.com/callback'
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            password = base64.b64encode((business_short_code + passkey + timestamp).encode()).decode()
            party_a = phone
            party_b = '254727264771'
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
                    return JsonResponse({'CheckoutRequestID': checkout_request_id, 'ResponseCode': response_code})
                else:
                    return JsonResponse({'error': 'STK push failed.'})
            except requests.exceptions.RequestException as e:
                return JsonResponse({'error': str(e)})
        else:
            return JsonResponse({'error': 'Access token not found.'})
    else:
        return JsonResponse({'error': 'Failed to retrieve access token.'})
def query_stk_status(request):
    access_token_response = get_access_token(request)
    if isinstance(access_token_response, JsonResponse):
        access_token = access_token_response.content.decode('utf-8')
        access_token_json = json.loads(access_token)
        access_token = access_token_json.get('access_token')
        if access_token:
            query_url = 'https://sandbox.safaricom.co.ke/mpesa/stkpushquery/v1/query'
            business_short_code = '174379'
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            passkey = "bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919"
            password = base64.b64encode((business_short_code + passkey + timestamp).encode()).decode()
            checkout_request_id = 'ws_CO_04072023004444401768168060'

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
        
        if result_code == 0:
        #  store the transaction details in the database
            print("okay")
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

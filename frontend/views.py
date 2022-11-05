from django.shortcuts import render, redirect
from django import forms
import requests, re

class ContactForm(forms.Form):
    name = forms.CharField(label='Name', max_length=100, required=True, widget=forms.TextInput(attrs={'placeholder': 'Name'}))
    email = forms.EmailField(label='Email', max_length=100, required=True, widget=forms.TextInput(attrs={'placeholder': 'Email'}))
    phone_number = forms.CharField(label='Phone Number', max_length=100, required=True, widget=forms.TextInput(attrs={'placeholder': 'Phone Number'}))
    file = forms.FileField(label='File', required=True)

def getStatusText(request):
    if request.COOKIES.get('token') == None:
        return 'Login'
    else:
        return 'Admin'


def index(request):
    headers = {'Forwarded': 'for=' + request.META['REMOTE_ADDR']}
    try:
        r = requests.get('http://127.0.0.1:8080/api/solar', headers=headers)
    except:
        return render(request, 'home.html', context={
        'userStateHref': getStatusText(request).lower(),
        'userStateText': getStatusText(request)})

    solar_arrays = []

    if r.status_code == 200:
        solar_arrays = r.json()

    return render(request, 'home.html', context={
        'userStateHref': getStatusText(request).lower(),
        'userStateText': getStatusText(request),
        'solarArrays': solar_arrays})


def admin(request):
    return render(request, 'admin.html', context={'userStateHref': getStatusText(request).lower, 'userStateText': getStatusText(request)})


def contact(request):
    form = ContactForm()
    if request.method == 'POST':
        try:
            contact_name = str(request.POST['name'])
            contact_email = str(request.POST['email'])
            contact_phone = str(request.POST['phone_number'])
            contact_file = request.FILES['file']
            
            if 0 > len(contact_name) > 100:
                return render(request, 'contact-us.html', context={'form': form, 'resp': 'Name must be between 1 and 100 characters.', 'userStateHref': getStatusText(request).lower(), 'userStateText': getStatusText(request)})
            if 0 > len(contact_email) > 100:
                return render(request, 'contact-us.html', context={'form': form, 'resp': 'Email must be between 1 and 100 characters.', 'userStateHref': getStatusText(request).lower(), 'userStateText': getStatusText(request)})
            if not re.match('([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+', contact_email):
                return render(request, 'contact-us.html', context={'form': form, 'resp': 'Email is not valid.', 'userStateHref': getStatusText(request).lower(), 'userStateText': getStatusText(request)})
            if 0 > len(contact_phone) > 20:
                return render(request, 'contact-us.html', context={'form': form, 'resp': 'Phone Number must be between 1 and 20 characters.', 'userStateHref': getStatusText(request).lower(), 'userStateText': getStatusText(request)})
            if contact_file.size > 10485760:
                return render(request, 'contact-us.html', context=({'resp': 'File is larger than 10mb', 'form': form, 'userStateHref': getStatusText(request).lower(), 'userStateText': getStatusText(request)}))
            
            try:
                headers = {'Forwarded': 'for=' + request.META['REMOTE_ADDR']}
                r_email = requests.post('http://127.0.0.1:8080/api/emails', headers=headers, json={
                'subject': 'Contact Us Submission - ' + contact_name,
                'from': contact_name + ' <' + contact_email + '>',
                'body': 'Name: ' + contact_name + '\nEmail: ' + contact_email + '\nPhone Number: ' + contact_phone})
                
                r_file = requests.post(
                    'http://127.0.0.1:8080/api/files', headers=headers, files={'file': contact_file})
                
                if r_email.status_code == 200 and r_file.status_code == 200:
                    return render(request, 'contact-us.html', context=({'hide_submit': True, 'resp': 'Thank you for contacting us. We will get back to you shortly.', 'userStateHref': getStatusText(request).lower(), 'userStateText': getStatusText(request)}))
            except:
               return render(request, 'contact-us.html', context=({'hide_submit': True,'resp': 'Failed to connect to the server. Please try again.', 'userStateHref': getStatusText(request).lower(), 'userStateText': getStatusText(request)}))
        except Exception as e:
            print(e)
            return render(request, 'contact-us.html', context=({'hide_submit': True,'resp': 'An error occurred. Please try again.', 'userStateHref': getStatusText(request).lower(), 'userStateText': getStatusText(request)}))

    return render(request, 'contact-us.html', context=({'form': form, 'resp': '', 'userStateHref': getStatusText(request).lower(), 'userStateText': getStatusText(request)}))


def solar(request):
    return render(request, 'solar-generation.html', context={'userStateHref': getStatusText(request).lower(), 'userStateText': getStatusText(request)})


def manufacturing(request):
    return render(request, 'manufacturing.html', context={'userStateHref': getStatusText(request).lower(), 'userStateText': getStatusText(request)})


def login(request):
    if request.method == 'POST':
        try:
            headers = {'Forwarded': 'for=' + request.META['REMOTE_ADDR']}
            r = requests.post('http://127.0.0.1:8080/api/login', headers=headers, json={
                'username': request.POST['username'],
                'password': request.POST['password']})
        except:
            return render(request, 'login.html', context=({'resp': 'Failed to connect to the server. Please try again.', 'userStateHref': getStatusText(request).lower(), 'userStateText': getStatusText(request)}))

        if r.status_code == 200:
            response = redirect('/')
            token = r.json().get('token')

            if token is not None:
                response.set_cookie('token', token)

            return response

        return render(request, 'login.html', context=({'resp': 'Login Failed. Please try again.', 'userStateHref': getStatusText(request).lower(), 'userStateText': getStatusText(request)}))

    return render(request, 'login.html', context=({'resp': '', 'userStateHref': getStatusText(request).lower(), 'userStateText': getStatusText(request)}))

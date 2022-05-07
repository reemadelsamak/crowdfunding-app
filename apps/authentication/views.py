# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""


from multiprocessing import context
from django.template import loader , RequestContext
from django.shortcuts import redirect, render 
from django.contrib.auth.hashers import make_password ,check_password
from django.urls import reverse
from apps.authentication.models import Register
from django.utils.encoding import force_bytes, force_str
from django.http import HttpResponse, HttpResponseRedirect

from django.contrib.auth import login , authenticate ,logout
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string

from apps.authentication.forms import DeleteAccountForm, EditProfileForm, LoginForm, ResetPasswordEmailForm, ResetPasswordForm ,SignupForm
from apps.authentication.tokens import account_activation_token
from django.core.mail import EmailMessage
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist

from apps.home.models import Donation, Project

from django.conf import settings
from django.core.mail import send_mail

from apps.home.views import getUser
  
def user_login (request ):
    if 'user_id' not in request.session :
        msg = None
        if request.method == "POST":
            form = LoginForm( request.POST)
           
            if form.is_valid():
                email = form.cleaned_data['email']
                password = form.cleaned_data['password']
                encryptpassword=make_password(password)

                try:
                    user = Register.objects.get(email=email , password=encryptpassword)
                except (ObjectDoesNotExist):
                    user = None                    
                if user is not None:
                    if  user.is_active:
                        login(request, user)
                        user.last_login = timezone.now()
                        user.is_login= True
                        user.save()
                        request.session['user_id'] = user.id
                        msg = f"You are now logged in as {user.first_name}"
                        return redirect("/" )
                    else:
                        msg= "please check your email to activate it !!"
                else:
                    msg = "user doesn't exist "
            else:
                msg = 'Invalid email or password.'
        form = LoginForm()
        return render(request=request, template_name="accounts/login.html", context={"login_form":form , "msg": msg})
    else:
        return redirect("/" )



def signup(request):
    msg = None
    if 'user_id' not in request.session :
        if request.method == 'POST':
            form = SignupForm(request.POST, request.FILES)
            if form.is_valid():
               
                hashedpassword=make_password(form.cleaned_data['password'])
                check=check_password(form.cleaned_data['password'],hashedpassword)
                print(check)
                first_name = form.cleaned_data['first_name']
                last_name = form.cleaned_data['last_name']
                email = form.cleaned_data['email']
                password = hashedpassword
                phone = form.cleaned_data['phone']
                image = form.cleaned_data['image']
                
                print(first_name, last_name
                    , email
                    , password
                    , phone
                    , image)

                user = Register.objects.create(first_name=first_name, last_name=last_name, email=email, password=password,
                                            phone=phone, profile_img=image)
                user.is_active = False
                user.save()

                current_site = get_current_site(request)
                mail_subject = 'Activation link has been sent to your email id'
                message = render_to_string('accounts/acc_active_email.html', {
                    'user': user,
                    'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': account_activation_token.make_token(user),
                })
                # to_email = form.cleaned_data.get('email')
                # email = EmailMessage(
                #     mail_subject, message, to=[to_email]
                # )
                # email.send()
                to_email = [form.cleaned_data.get('email')]
                email = EmailMessage(
                    mail_subject, message, to=[to_email]
                )
                from_email=settings.EMAIL_HOST_USER
                # email.send()
                send_mail( mail_subject, message, from_email, to_email)

                msg='Please confirm your email address to complete the registration'
        else:
            form = SignupForm()
        return render(request, 'accounts/register.html', {'form': form ,"msg" :msg})
        
    else:
        return redirect("/" )

def activate(request, uidb64, token):
    msg=None
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = Register.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError , ObjectDoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        return redirect("login")
    else:
        # form = SignupForm()
        # return render(request, 'accounts/register.html', {'form': form ,"msg" :'Activation link is invalid!'})
        return HttpResponse('Activation link is invalid!')
    



def user_logout(request ):
    try:        
        del request.session['user_id']
        print("you are logged out " )        
    except KeyError:
        print("you must login ")
    return redirect("login" )


def EditProfile(request):
    msg = None
    if 'user_id'  in request.session :
        try:
            user_object= Register.objects.get(id=request.session['user_id'])
        except Register.DoesNotExist:
            return redirect('/')
           
        if request.method == 'POST':
            
            form = EditProfileForm(request.POST, request.FILES , instance=user_object)
            if form.is_valid():
                user_object= Register.objects.get(id=request.session['user_id'])
                
                
                user_object.first_name = form.cleaned_data['first_name']
                user_object.last_name = form.cleaned_data['last_name']
                user_object.phone = form.cleaned_data['phone']
                image = form.cleaned_data['image']
                
                print(image)
                if image == None:
                    user_object.profile_img=user_object.profile_img
                else:
                    user_object.profile_img = form.cleaned_data['image']
                if form.cleaned_data['password']=="":
                    user_object.password =user_object.password
                else:
                    hashedpassword=make_password(form.cleaned_data['password'])
                    user_object.password = hashedpassword 
                user_object.country=form.cleaned_data['country']
                user_object.birthdate=form.cleaned_data['birthdate']
                user_object.facebook_profile=form.cleaned_data['facebook_profile']


                user_object.save()
                return redirect( 'profile'  )
        else:
            form = EditProfileForm(instance=user_object) 
        return render(request, 'profile/editProfile.html', {'form': form ,"msg" :msg , "user" :user_object})
    else:
        return redirect("/" )


def profile (request):
    if 'user_id'  in request.session :
        try:
            user_object= Register.objects.get(id = request.session['user_id'])
            projects =Project.objects.filter(user_id =  request.session['user_id'] )
            donations = Donation.objects.filter(user_id =  request.session['user_id'] )
            
            images = []
            for project in projects:
                images.append(project.image_set.all().first().images.url)

        except Register.DoesNotExist:
            return redirect('/')
        
        
        return render(request, 'profile/Profile.html', {"user" :user_object ,"projects":projects ,"donations":donations,'images':images})
    else:
        return redirect("/" )

def emailPasswordReset (request ):
        if request.method == "POST":
            form = ResetPasswordEmailForm( request.POST)
            if form.is_valid():
                email = form.cleaned_data['email']
                try:
                    user = Register.objects.get(email=email)
                    
                except (ObjectDoesNotExist):
                    messages.error(request ,"Invalid email")
                    form = ResetPasswordEmailForm()
                    return render(request=request, template_name="accounts/emailResetPassword.html", context={"form":form})
                    
                current_site = get_current_site(request)
                mail_subject = 'Activation link has been sent to your email id'
                message = render_to_string('accounts/acc_reset_password.html', {
                    'user': user,
                    'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': account_activation_token.make_token(user),
                })
                to_email = [form.cleaned_data.get('email')]
                email = EmailMessage(
                    mail_subject, message, to=[to_email]
                )
                from_email=settings.EMAIL_HOST_USER
                # email.send()
                send_mail( mail_subject, message, from_email, to_email)
                return HttpResponse('Please confirm your email address to complete the reset password')
            else:
                    messages.error(request,"user doesn't exist ")

        else:
            form = ResetPasswordEmailForm()
            return render(request=request, template_name="accounts/emailResetPassword.html", context={"form":form})

def ResetPasswordLink(request, uidb64, token):
    
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = Register.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError , ObjectDoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        request.session['password_reset-session'] = user.id
        return redirect( 'passwordReset' , user.id )
    else:
        return HttpResponse('Reset Password link is invalid!')
    
def ResetPassword(request,id):
    if 'password_reset-session' in request.session :
            if request.method == "POST":
                form = ResetPasswordForm( request.POST)
                if form.is_valid():
                    try:
                        user = Register.objects.get(id=id)
                    except (ObjectDoesNotExist):
                        user = None
                        return redirect('login')
                    if user is not None:
                            hashedpassword=make_password(form.cleaned_data['password'])
                            user.password = hashedpassword
                            user.save()
                            del request.session['password_reset-session']
                            return redirect('login' )
                else:
                    return render(request=request, template_name="accounts/passwordReset.html", context={"form":form})

            else:
                form = ResetPasswordForm()
                return render(request=request, template_name="accounts/passwordReset.html", context={"form":form})
    else:
        return redirect('login')

def deleteAccount(request):
    if 'user_id'  in  request.session :
            if request.method == "POST":
                form = DeleteAccountForm( request.POST)
                if form.is_valid():
                    password = form.cleaned_data['password']
                    encryptpassword=make_password(password)
                    try:
                        user = Register.objects.get(id=request.session['user_id'])
                    except (ObjectDoesNotExist):
                        user = None  
                        return redirect('login')
                    if user is not None:
                        if user.password == encryptpassword :
                            user.delete()
                            del request.session['user_id']
                            return redirect('login' )
                        else :
                            msg='password not correct'
                            return render(request=request, template_name="accounts/Delete_account.html", context={"form":form ,"msg":msg , "user":user})

                else:
                    user=getUser(request)
                    return render(request=request, template_name="accounts/Delete_account.html", context={"form":form , "user":user})

            else:
                form = DeleteAccountForm()
                user=getUser(request)
                return render(request=request, template_name="accounts/Delete_account.html", context={"form":form , "user":user})
    else:
        return redirect('login')

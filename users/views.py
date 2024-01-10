from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView, PasswordResetView, PasswordChangeView
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.views import View
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm, LoginForm, UpdateUserForm, UpdateProfileForm, ExpenditureItemForm
from .models import ExpenditureItem, OTP
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from .utils import generate_and_send_otp
from django.core.exceptions import ObjectDoesNotExist

@login_required
def expenditure(request):
    # Check if OTP exists for the user
    user = request.user
    if OTP.objects.filter(user=user).exists():
        return redirect('otp-verification')
    else:
        expenditures = ExpenditureItem.objects.all()  # Fetch all Expenditure objects from the database
        return render(request, 'users/expenditure.html', {'expenditures': expenditures})

def expenditure_view(request):
    expenditures = ExpenditureItem.objects.all()  # Fetch all Expenditure objects from the database
    return render(request, 'expenditure.html', {'expenditures': expenditures})

def home(request):
    return render(request, 'users/home.html')

class RegisterView(View):
    form_class = RegisterForm
    initial = {'key': 'value'}
    template_name = 'users/register.html'

    def dispatch(self, request, *args, **kwargs):
        # will redirect to the home page if a user tries to access the register page while logged in
        if request.user.is_authenticated:
            return redirect(to='expenditure')

        # else process dispatch as it otherwise normally would
        return super(RegisterView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        form = self.form_class(initial=self.initial)
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)

        if form.is_valid():
            form.save()

            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}')

            return redirect(to='login')

        return render(request, self.template_name, {'form': form})


# Class based view that extends from the built in login view to add a remember me functionality
class CustomLoginView(LoginView):
    form_class = LoginForm

# modify this method such that when the user enters btheir credential, they're sent an OTP through email and requested to enter the OTP on the otp verification page
    

    def form_valid(self, form):
    # Authenticate the user
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        user = authenticate(self.request, username=username, password=password)

        if user is not None:
            # User is authenticated, now generate the OTP
            login(self.request, user, backend='django.contrib.auth.backends.ModelBackend')
            if self.request.user.is_authenticated:
                generate_and_send_otp(user)
            else:
                # Handle the case where the user is not authenticated, e.g., redirect to the login page
                return redirect('login')

            # Redirect to OTP verification page
            return redirect('otp-verification') 

        return super(CustomLoginView, self).form_valid(form)
            
            # else browser session will be as long as the session cookie time "SESSION_COOKIE_AGE" defined in settings.py
            # return super(CustomLoginView, self).form_valid(form)


class ResetPasswordView(SuccessMessageMixin, PasswordResetView):
    template_name = 'users/password_reset.html'
    email_template_name = 'users/password_reset_email.html'
    subject_template_name = 'users/password_reset_subject'
    success_message = "We've emailed you instructions for setting your password, " \
                      "if an account exists with the email you entered. You should receive them shortly." \
                      " If you don't receive an email, " \
                      "please make sure you've entered the address you registered with, and check your spam folder."
    success_url = reverse_lazy('expenditure')


class ChangePasswordView(SuccessMessageMixin, PasswordChangeView):
    template_name = 'users/change_password.html'
    success_message = "Successfully Changed Your Password"
    success_url = reverse_lazy('expenditure')


@login_required
def profile(request):
    if request.method == 'POST':
        
        user_form = UpdateUserForm(request.POST, instance=request.user)
        profile_form = UpdateProfileForm(request.POST, request.FILES, instance=request.user.profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile is updated successfully')
            return redirect(to='users-profile')
    else:
        user_form = UpdateUserForm(instance=request.user)
        profile_form = UpdateProfileForm(instance=request.user.profile)
    # Check if OTP exists for the user
    # if request.user.profile.otp:
    #     return redirect('otp-verification')
    # else:
    return render(request, 'users/profile.html', {'user_form': user_form, 'profile_form': profile_form})

# views.py



@login_required
def update_expenditure(request, item_id):
    expenditure_item = get_object_or_404(ExpenditureItem, id=item_id, user=request.user)

    if request.method == 'POST':
        form = ExpenditureItemForm(request.POST, instance=expenditure_item)
        if form.is_valid():
            form.save()
            messages.success(request, 'Expenditure item updated successfully.')
            return redirect('update_expenditure')  # Change 'home' to your actual home URL name
    else:
        form = ExpenditureItemForm(instance=expenditure_item)

    return render(request, 'update_expenditure.html', {'form': form})

@login_required
def delete_expenditure(request, item_id):
    expenditure_item = get_object_or_404(ExpenditureItem, id=item_id, user=request.user)

    if request.method == 'POST':
        expenditure_item.delete()
        messages.success(request, 'Expenditure item deleted successfully.')
        return redirect('delete_expenditure')  # Change 'home' to your actual home URL name

    return render(request, 'delete_expenditure.html', {'expenditure_item': expenditure_item})

@login_required
def add_expenditure(request):
    if request.method == 'POST':
        form = ExpenditureItemForm(request.POST)
        if form.is_valid():
            expenditure_item = form.save(commit=False)
            expenditure_item.user = request.user
            expenditure_item.save()
            messages.success(request, 'Expenditure item added successfully.')
            return redirect('add_expenditure')  # Change 'home' to your actual home URL name
    else:
        form = ExpenditureItemForm()

    return render(request, 'add_expenditure.html', {'form': form})




def login_with_otp(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            user = form.get_user()
            entered_otp = request.POST.get('otp')
            otp = OTP.objects.get(user=user)

            if otp.code == entered_otp:
                login(request, user)
                otp.delete()
                return redirect('expenditure')  # Redirect to the home page or the desired page
            else:
                return render(request, 'login.html', {'form': form, 'error_message': 'Invalid OTP'})
    else:
        form = AuthenticationForm()

    return render(request, 'login.html', {'form': form})

# views.py

class OTPVerificationView(View):
    def get(self, request):
        # Render a form for the user to enter their OTP
        return render(request, 'users/otp_verification.html')

    def post(self, request):
        # Get the OTP from the form data
        otp = request.POST.get('otp')

        # Check if the OTP is correct
        if default_token_generator.check_token(request.user, otp):
            # If the OTP is correct, log the user in and redirect them
            login(request, request.user)
            return redirect('expenditure')
        else:
            # If the OTP is incorrect, show an error message
            return render(request, 'users/otp_verification.html', {'error': 'Invalid OTP'})

@login_required
def otp_verification(request):
    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        user = request.user

        try:
            otp = OTP.objects.get(user=user)
            if otp.code == entered_otp:
                login(request, user)
                otp.delete()
                return redirect('expenditure') # Redirect to the dashboard or the desired page
            else:
                return render(request, 'users/otp_verification.html', {'error': 'Invalid OTP'})
        except ObjectDoesNotExist:
            return render(request, 'users/otp_verification.html', {'error': 'No OTP found for this user'})
    else:
        return render(request, 'users/otp_verification.html')
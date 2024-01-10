from django.urls import path
from . import views
from .views import profile, RegisterView,home, expenditure, update_expenditure, delete_expenditure, add_expenditure
from .views import otp_verification as otp
urlpatterns = [
    path('', home, name='home'),
    path('register/', RegisterView.as_view(), name='users-register'),
    path('profile/', profile, name='users-profile'),
    path('otp-verification/', otp, name='otp-verification'),
    path('expenditure/', expenditure, name='expenditure'),
    path('update-expenditure/<int:item_id>/',update_expenditure, name='update_expenditure'),
    path('delete-expenditure/<int:item_id>/',delete_expenditure, name='delete_expenditure'),
    path('add-expenditure/', add_expenditure, name='add_expenditure')
    
]

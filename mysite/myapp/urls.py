from django.urls import path
from . import views

urlpatterns = [
    path("", views.login_view, name="login"),  # Make login_view the default view
    path("home/", views.home, name="home"),
    path('ForgotP/', views.goto_forgot),
    path('code_v/', views.Code_valid, name= 'Code_valid'),
    path('forgotpassword/', views.forgot_password),
    path("sign-up/", views.sign_up),
    path("sign-up-vulnerable/", views.sign_up_vulnerable),
    path('user/',views.index,name='user'),
    path('user/add_cust/', views.addCust, name='addCust'),
    path('user/changepassword/', views.change_password)
]

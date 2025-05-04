from django.urls import path
from. import views


urlpatterns=[
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('forgot-password/', views.forgot_password_view, name='forgot_password'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('reset-password/', views.reset_password, name='reset_password'),
    path('', views.home, name='home'),
    path('contact/', views.contact, name='contact'),
    path('how_it_works/', views.how_it_works, name='how_it_works'),
    path('categories/', views.categories, name='categories'),
    path('categories/<int:category_id>/', views.category_detail, name='category_detail'),
    path('subcategories/<int:subcategory_id>/', views.subcategory_detail, name='subcategory_detail'),
    path('join/',views.join,name='join'),
    path('profile/<int:freelancer_id>/',views.profile,name='profile'),
    path('my-account/', views.my_account, name='my_account'),
    path('profile/<int:freelancer_id>/hire/',views.hire_freelancer, name='hire_freelancer'),
    path('profile/<int:freelancer_id>/confirm_hire/', views.confirm_hire, name='confirm_hire'),
    # path('profile/<int:id>/', views.freelancer_profile, name='profile'),
]
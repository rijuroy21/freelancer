from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('forgot-password/', views.forgot_password_view, name='forgot_password'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('reset-password/', views.reset_password, name='reset_password'),
    path('categories/', views.categories, name='categories'),
    path('category/<int:category_id>/', views.category_detail, name='category_detail'),
    path('subcategory/<int:subcategory_id>/', views.subcategory_detail, name='subcategory_detail'),
    path('join/', views.join, name='join'),
    path('profile/<int:freelancer_id>/', views.profile, name='profile'),
    path('my-account/', views.my_account, name='my_account'),
    path('delete_account/', views.delete_account, name='delete_account'),
    path('hire/<int:freelancer_id>/', views.hire_freelancer, name='hire_freelancer'),
    path('confirm-hire/<int:freelancer_id>/', views.confirm_hire, name='confirm_hire'),
    path('freelancers/', views.all_freelancers, name='all_freelancers'),
    path('delete-profile-image/', views.delete_profile_image, name='delete_profile_image'),
    path('delete-work-image/<int:image_id>/', views.delete_work_image, name='delete_work_image'),
    path('search/', views.search_results, name='search_results'),
    path('submit-review/<int:freelancer_id>/', views.submit_review, name='submit_review'),
    
]

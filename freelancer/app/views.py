from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
import random

from .models import *
from .forms import RegisterForm, FreelancerEditForm
from .models import Freelancer, WorkImage
from .forms import FreelancerEditForm


def register_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confpassword = request.POST['confpassword']

        if password != confpassword:
            messages.error(request, "Passwords do not match.")
            return redirect('register')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect('register')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already in use.")
            return redirect('register')

        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()
        messages.success(request, "Registration successful. Please login.")
        return redirect('login')

    return render(request, 'register.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Invalid credentials")
            return redirect('login')

    return render(request, 'login.html')


def logout_view(request):
    auth.logout(request)
    return redirect('login')


def forgot_password_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        otp = random.randint(100000, 999999)

        request.session['reset_email'] = email
        request.session['otp'] = otp

        send_mail(
            subject='Your OTP Code',
            message=f'Your OTP is {otp}',
            from_email='youremail@example.com',
            recipient_list=[email],
            fail_silently=False,
        )

        messages.success(request, 'OTP has been sent to your email.')
        return redirect('verify_otp')

    return render(request, 'forgot_password.html')


def verify_otp(request):
    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        if str(request.session.get('otp')) == entered_otp:
            messages.success(request, 'OTP verified. You can now reset your password.')
            return redirect('reset_password')
        else:
            messages.error(request, 'Invalid OTP. Please try again.')

    return render(request, 'verify_otp.html')


def reset_password(request):
    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        email = request.session.get('reset_email')

        user = User.objects.filter(email=email).first()
        if user:
            user.set_password(new_password)
            user.save()
            messages.success(request, "Password has been reset. You can now log in.")
            return redirect('login')
        else:
            messages.error(request, "Something went wrong. Please try again.")
            return redirect('forgot_password')

    return render(request, 'reset_password.html')


def home(request):
    freelancers = Freelancer.objects.all()
    return render(request, 'home.html', {'freelancers': freelancers})


@login_required
def contact(request):
    return render(request, 'contact.html')


@login_required
def how_it_works(request):
    return render(request, 'how_it_works.html')


@login_required
def categories(request):
    categories = Category.objects.all()
    return render(request, 'categories.html', {'categories': categories})


@login_required
def category_detail(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    subcategories = category.subcategories.all()
    return render(request, 'category_detail.html', {'category': category, 'subcategories': subcategories})


@login_required
def subcategory_detail(request, subcategory_id):
    subcategory = get_object_or_404(SubCategory, id=subcategory_id)
    freelancers = subcategory.freelancers.all()
    return render(request, 'subcategory_detail.html', {'subcategory': subcategory, 'freelancers': freelancers})


@login_required
def join(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        category = request.POST.get('category')  # Use directly (CharField)
        subcategory_name = request.POST.get('subcategory')
        portfolio_url = request.POST.get('portfolio')
        bio = request.POST.get('bio')
        images = request.FILES.getlist('work_images')  # Get list of uploaded files

        try:
            subcategory = SubCategory.objects.get(name=subcategory_name)
        except SubCategory.DoesNotExist:
            return render(request, 'join.html', {'error': 'Selected subcategory does not exist.'})

        freelancer = Freelancer.objects.create(
            name=name,
            email=email,
            category=category,  # No need to fetch a Category object
            subcategory=subcategory,
            portfolio_url=portfolio_url,
            bio=bio,
        )

        # Save multiple images
        for image in images:
            WorkImage.objects.create(freelancer=freelancer, image=image)

        return redirect('home')

    return render(request, 'join.html')


@login_required
def profile(request, freelancer_id):
    freelancer = get_object_or_404(Freelancer, id=freelancer_id)
    work_images = freelancer.work_images.all()
    
    return render(request, 'profile.html', {'freelancer': freelancer, 'work_images': work_images})

@login_required
def my_account(request):
    freelancer = Freelancer.objects.filter(email__iexact=request.user.email).first()

    if not freelancer:
        messages.error(request, "No freelancer profile found for this account. Please create one.")
        return redirect('join')

    if request.method == 'POST':
        if 'work_image' in request.FILES:
            # Handle work image upload
            image = request.FILES['work_image']
            WorkImage.objects.create(freelancer=freelancer, image=image)
            messages.success(request, 'Work image uploaded successfully.')
            return redirect('my_account')
        else:
            # Handle profile update
            form = FreelancerEditForm(request.POST, request.FILES, instance=freelancer)
            if form.is_valid():
                form.save()
                messages.success(request, 'Your profile has been updated successfully.')
                return redirect('my_account')
            else:
                messages.error(request, 'Please correct the errors below.')
    else:
        form = FreelancerEditForm(instance=freelancer)

    return render(request, 'my_account.html', {
        'form': form,
        'freelancer': freelancer
    })



def hire_freelancer(request, freelancer_id):
    freelancer = get_object_or_404(Freelancer, pk=freelancer_id)
    return redirect('confirm_hire', freelancer_id=freelancer.id)


def confirm_hire(request, freelancer_id):
    freelancer = get_object_or_404(Freelancer, pk=freelancer_id)
    return render(request, 'confirm_hire.html', {'freelancer': freelancer})

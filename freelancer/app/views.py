from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages, auth
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
import random
from django.db.models.functions import Lower
from django.conf import settings
import re
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from .models import Freelancer, Review


from .models import *
from .forms import RegisterForm, FreelancerEditForm




def is_valid_password(password):
    return (
        len(password) >= 8 and
        re.search(r"[A-Z]", password) and
        re.search(r"\d", password) and
        re.search(r"[!@#$%^&*(),.?\":{}|<>]", password)
    )

def register_view(request):
    if request.method == 'POST':
        username = request.POST['username'].strip()
        email = request.POST['email'].strip()
        password = request.POST['password']
        confpassword = request.POST['confpassword']

        # Password match
        if password != confpassword:
            messages.error(request, "Passwords do not match.")
            return redirect('register')

        # Email format check
        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, "Invalid email format.")
            return redirect('register')

        # Username/email uniqueness
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect('register')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already in use.")
            return redirect('register')

        # Password strength
        if not is_valid_password(password):
            messages.error(
                request,
                "Password must be at least 8 characters long, contain an uppercase letter, a number, and a special character."
            )
            return redirect('register')

        # Success: create user
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
    categories = Category.objects.all()
    freelancers = Freelancer.objects.order_by('-id')[:8]
    # Fetch the latest 15 work images
    latest_work_images = WorkImage.objects.select_related('freelancer').order_by('-uploaded_at')[:12]
    return render(request, 'home.html', {
        'freelancers': freelancers,
        'categories': categories,
        'latest_work_images': latest_work_images,
    })

def all_freelancers(request):
    freelancers = Freelancer.objects.all()
    category = request.GET.get('category')
    sort = request.GET.get('sort')

    if category:
        freelancers = freelancers.filter(category=category)

    if sort == 'name_asc':
        freelancers = freelancers.order_by(Lower('name'))
    elif sort == 'name_desc':
        freelancers = freelancers.order_by(Lower('name').desc())
    elif sort == 'latest':
        freelancers = freelancers.order_by('-created_at')
    elif sort == 'oldest':
        freelancers = freelancers.order_by('created_at')

    context = {
        'freelancers': freelancers,
        'category_choices': Freelancer.CATEGORY_CHOICES,
    }
    return render(request, 'all_freelancers.html', context)

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
        category = request.POST.get('category')
        subcategory_name = request.POST.get('subcategory')
        portfolio_url = request.POST.get('portfolio')
        bio = request.POST.get('bio')
        profile_image = request.FILES.get('image')
        work_images = request.FILES.getlist('work_images')

        try:
            subcategory = SubCategory.objects.get(name=subcategory_name)
        except SubCategory.DoesNotExist:
            return render(request, 'join.html', {'error': 'Selected subcategory does not exist.'})

        # Check if a freelancer with the same email already exists
        if Freelancer.objects.filter(email=email).exists():
            messages.error(request, 'A freelancer with this email already exists. Please use a different email address.')
            return redirect('join')

        freelancer = Freelancer.objects.create(
            name=name,
            email=email,
            category=category,
            subcategory=subcategory,
            portfolio_url=portfolio_url,
            bio=bio,
            image=profile_image
        )

        for img in work_images:
            WorkImage.objects.create(freelancer=freelancer, image=img)

        messages.success(request, 'Freelancer profile created successfully.')
        return redirect('my_account')

    return render(request, 'join.html')


@login_required
def profile(request, freelancer_id):
    freelancer = get_object_or_404(Freelancer, id=freelancer_id)
    work_images = freelancer.work_images.all()
    
    return render(request, 'profile.html', {'freelancer': freelancer, 'work_images': work_images})


def search_results(request):
    query = request.GET.get('q')
    freelancers = []
    if query:
        freelancers = Freelancer.objects.filter(
            name__icontains=query
        ) | Freelancer.objects.filter(
            subcategory__name__icontains=query
        )
    return render(request, 'search_results.html', {'query': query, 'freelancers': freelancers})


@login_required
def my_account(request):
    freelancer = Freelancer.objects.filter(email__iexact=request.user.email).first()

    if not freelancer:
        messages.error(request, "No freelancer profile found for this account. Please create one.")
        return redirect('join')

    if request.method == 'POST':
        if 'work_image' in request.FILES:
            image = request.FILES['work_image']
            WorkImage.objects.create(freelancer=freelancer, image=image)
            messages.success(request, 'Work image uploaded successfully.')
            return redirect('my_account')
        else:
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

@login_required
def delete_profile_image(request):
    freelancer = Freelancer.objects.filter(email__iexact=request.user.email).first()
    if freelancer and freelancer.image:
        freelancer.image.delete(save=False)
        freelancer.image = None
        freelancer.save()
        messages.success(request, "Profile image deleted successfully.")
    return redirect('my_account')

@login_required
def delete_work_image(request, image_id):
    freelancer = Freelancer.objects.filter(email__iexact=request.user.email).first()
    image = get_object_or_404(WorkImage, id=image_id, freelancer=freelancer)
    image.image.delete()
    image.delete()
    messages.success(request, "Work image deleted successfully.")
    return redirect('my_account')


def hire_freelancer(request, freelancer_id):
    freelancer = get_object_or_404(Freelancer, pk=freelancer_id)
    return redirect('confirm_hire', freelancer_id=freelancer.id)


def confirm_hire(request, freelancer_id):
    freelancer = get_object_or_404(Freelancer, pk=freelancer_id)
    success = False

    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject') or f"Hire Inquiry for {freelancer.name}"
        message = request.POST.get('message')

        full_message = f"""
        You have a new hire inquiry for {freelancer.name}.

        From: {name}
        Email: {email}
        Subject: {subject}
        Message:
        {message}

        Freelancer Info:
        Category: {freelancer.category}
        Subcategory: {freelancer.subcategory}
        Bio: {freelancer.bio}
        Portfolio: {freelancer.portfolio_url}
        """

        send_mail(subject, full_message, settings.EMAIL_HOST_USER, [settings.EMAIL_HOST_USER])
        success = True

    return render(request, 'confirm_hire.html', {
        'freelancer': freelancer,
        'success': success
    })




@login_required
def submit_review(request, freelancer_id):
    freelancer = get_object_or_404(Freelancer, id=freelancer_id)
    
    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')
        
        # Validate rating and comment
        if not rating or not comment:
            messages.error(request, "Please provide both a rating and a comment.")
            return redirect('profile', freelancer_id=freelancer.id)
        
        if len(comment) < 10:
            messages.error(request, "Your review must be at least 10 characters long.")
            return redirect('profile', freelancer_id=freelancer.id)

        try:
            rating = int(rating)
            if rating < 1 or rating > 5:
                messages.error(request, "Rating must be between 1 and 5 stars.")
                return redirect('profile', freelancer_id=freelancer.id)
        except ValueError:
            messages.error(request, "Invalid rating value.")
            return redirect('profile', freelancer_id=freelancer.id)

        # Create the review
        Review.objects.create(
            freelancer=freelancer,
            client_name=request.user.username,
            rating=rating,
            comment=comment
        )
        messages.success(request, "Your review has been submitted successfully.")
        return redirect('profile', freelancer_id=freelancer.id)

    return redirect('profile', freelancer_id=freelancer.id)
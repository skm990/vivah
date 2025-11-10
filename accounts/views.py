from django.contrib import messages
from django.utils.timezone import now
from datetime import timedelta
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils.crypto import get_random_string
from django.shortcuts import render, redirect, get_object_or_404
from .models import UserOtp, UserAccount, WelcomeMail, UserProfile, ProfileInterest, UploadImage, ChatMessage, PremiumUser
from .forms import EmailForm, OtpForm, LoginForm, UserProfileForm, FeedbackForm, PremiumUserForm
from django.core.paginator import Paginator
from .utils import send_otp_email, send_interest_email, send_interest_accept_email
from datetime import date
from django.db.models import Count
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.db.models import Q, Max, Count
from django.db.models.functions import Greatest
import threading

User = get_user_model()


def request_otp_view(request):
    if request.method == "POST":
        form = EmailForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            user, created = UserAccount.objects.get_or_create(
                email=email,
                defaults={'username': email.split('@')[0]}
            )
            if created:
                WelcomeMail.objects.create(user=user, welcome=False)
                # messages.success(request, "Welcome email sent!")
            otp = get_random_string(length=6, allowed_chars='1234567890')
            UserOtp.objects.create(user=user, otp=otp)
            send_otp_email(email, otp, user_name=user.get_full_name() or "User")
            request.session['email'] = email
            return redirect('verify_otp')
    else:
        form = EmailForm()
    return render(request, "auth/request_otp.html", {"form": form})


def verify_otp_view(request):
    email = request.session.get('email')
    if not email:
        return redirect('request_otp')
    if request.method == "POST":
        form = OtpForm(request.POST)
        if form.is_valid():
            otp_input = form.cleaned_data['otp']
            password = form.cleaned_data['password']
            user = UserAccount.objects.get(email=email)
            user_otp = UserOtp.objects.filter(
                user=user,
                otp_verified=False,
                created_at__gte=now()-timedelta(minutes=10)
            ).order_by('-created_at').first()
            if user_otp and user_otp.otp == otp_input:
                user.set_password(password)
                user.save()
                user_otp.otp_verified = True
                user_otp.save()
                login(request, user)
                return redirect('profiles_list')
            else:
                messages.error(request, "Invalid or expired OTP.")
    else:
        form = OtpForm()
    return render(request, "auth/verify_otp.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, email=email, password=password)
            if user:
                login(request, user)
                # messages.success(request, "Login successful!")
                return redirect('profiles_list')
            else:
                messages.error(request, "Invalid email or password.")
    else:
        form = LoginForm()
    return render(request, "auth/login.html", {"form": form})


@login_required
def create_profile_view(request):
    user_profile, _ = UserProfile.objects.get_or_create(user=request.user)
    if request.method == "POST":
        form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        images = request.FILES.getlist('gallery_images')  # multiple images
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        if form.is_valid():
            profile = form.save()
            # ✅ Update first_name and last_name before saving the profile
            user = request.user
            if not getattr(user, "is_verified", False):  # optional check
                user.first_name = first_name
                user.last_name = last_name
                user.save()

            profile.user = user
            profile.save()
            # Save uploaded gallery images
            for img in images:
                UploadImage.objects.create(galary=profile, image=img)
            return redirect('profiles_list')
    else:
        form = UserProfileForm(instance=user_profile)
    # Existing uploaded gallery images
    gallery_images = user_profile.user_profile.all()  # related_name in UploadImage
    context = {
        "form": form,
        "first_name": request.user.first_name,
        "last_name": request.user.last_name,
        "gallery_images": gallery_images,
    }
    return render(request, "profile/create_profile.html", context)


@login_required
def delete_gallery_image(request, uid):
    img = get_object_or_404(UploadImage, uid=uid, galary__user=request.user)
    img.delete()
    return redirect('create_profile')


@login_required
def logout_view(request):
    logout(request)
    return redirect('home')


from django.utils.timezone import now

@login_required
def profiles_list(request):
    gender = request.GET.get('gender')
    min_age = request.GET.get('min_age')
    max_age = request.GET.get('max_age')
    caste = request.GET.get('caste')
    country = request.GET.get('country')
    state = request.GET.get('state')
    city = request.GET.get('city')
    # --- Check if user has sent interest today ---
    today = now().date()
    access_today = ProfileInterest.objects.filter(
        sender=request.user,
        created_at__date=today
    ).count()
    # Start with all profiles
    profiles = (
        UserProfile.objects
        .select_related('user')
        .prefetch_related('user_profile')  # Fetch gallery images efficiently
        .all()
    )
    # --- 🔹 Filter opposite gender ---
    try:
        current_user_profile = UserProfile.objects.get(user=request.user)
        if current_user_profile.gender == "Male":
            profiles = profiles.filter(gender__iexact="Female")
        elif current_user_profile.gender == "Female":
            profiles = profiles.filter(gender__iexact="Male")
        else:
            profiles = profiles.exclude(user=request.user)  # show all except self if 'Other'
    except UserProfile.DoesNotExist:
        pass  # no user profile, show all
    # --- 🔹 Exclude own profile ---
    profiles = profiles.exclude(user=request.user)
    # --- Apply filters from GET form ---
    if gender:
        profiles = profiles.filter(gender__iexact=gender)
    if min_age:
        profiles = profiles.filter(age__gte=min_age)
    if max_age:
        profiles = profiles.filter(age__lte=max_age)
    if caste:
        profiles = profiles.filter(caste__icontains=caste)
    if country:
        profiles = profiles.filter(country__icontains=country)
    if state:
        profiles = profiles.filter(state__icontains=state)
    if city:
        profiles = profiles.filter(city__icontains=city)
    # --- Dropdown values ---
    profiles = profiles.filter(user__is_verified=True)
    countries = (
        UserProfile.objects.values_list('country', flat=True)
        .distinct()
        .exclude(country__isnull=True)
        .exclude(country__exact='')
        .order_by('country')
    )
    states = (
        UserProfile.objects.values_list('state', flat=True)
        .distinct()
        .exclude(state__isnull=True)
        .exclude(state__exact='')
        .order_by('state')
    )
    cities = (
        UserProfile.objects.values_list('city', flat=True)
        .distinct()
        .exclude(city__isnull=True)
        .exclude(city__exact='')
        .order_by('city')
    )
    castes = (
        UserProfile.objects.values_list('caste', flat=True)
        .distinct()
        .exclude(caste__isnull=True)
        .exclude(caste__exact='')
        .order_by('caste')
    )
    # --- Pagination ---
    paginator = Paginator(profiles, 2)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    # --- Interests (already sent) ---
    sent_interest_ids = []
    if request.user.is_authenticated:
        sent_interest_ids = ProfileInterest.objects.filter(sender=request.user).values_list('receiver_id', flat=True)
    # --- Check for active premium subscription ---
    active_premium = PremiumUser.objects.filter(
        user=request.user, is_premium=True, expiry_date__gt=now().date()
    ).first()
    context = {
        'profiles': page_obj,
        'countries': countries,
        'states': states,
        'cities': cities,
        'castes': castes,
        'sent_interest_ids': sent_interest_ids,
        'access_today': access_today,
        'access_premium': 1 if active_premium else 0,
    }
    return render(request, 'profile/profiles_list.html', context)


@login_required
def send_interest(request, profile_id):
    user_profile = UserProfile.objects.filter(user=request.user).first()
    if not user_profile or not user_profile.identity_proof:
        messages.warning(request, "You must complete your profile first.")
        return redirect('create_profile')
    if request.user.is_verified == False:
        messages.warning(request, "Your profile is now under verification. Please wait for admin approval.")
        return redirect('create_profile')
    receiver_profile = get_object_or_404(UserProfile, id=profile_id)
    check_profile = UserProfile.objects.filter(user=request.user).first()
    if not check_profile or not check_profile.gender:
        return redirect('create_profile')
    ProfileInterest.objects.create(sender=request.user, receiver=receiver_profile)
    sender_profile = get_object_or_404(UserProfile, user=request.user)
    # Run email sending in background thread
    threading.Thread(
        target=send_interest_email,
        args=(receiver_profile, request.user, sender_profile)
    ).start()
    # Check if interest already exists
    if ProfileInterest.objects.filter(sender=request.user, receiver=receiver_profile).exists():
        messages.info(request, "You already expressed interest in this profile.")
    else:
        ProfileInterest.objects.create(sender=request.user, receiver=receiver_profile)
        messages.success(request, f"Interest sent to {receiver_profile.user.get_full_name()} successfully!")
    return redirect(request.META.get('HTTP_REFERER', 'profiles_list'))


@login_required
def interest_list(request):
    user_profile = UserProfile.objects.filter(user=request.user).first()
    if not user_profile or not user_profile.identity_proof:
        messages.warning(request, "You must complete your profile first.")
        return redirect('create_profile')
    if request.user.is_verified == False:
        messages.warning(request, "Your profile is now under verification. Please wait for admin approval.")
        return redirect('create_profile')
    my_profile = request.user.profile
    # Incoming: users who sent interest to me
    incoming_interests = ProfileInterest.objects.filter(receiver=my_profile)
    # Outgoing: interests I sent to others
    outgoing_interests = ProfileInterest.objects.filter(sender=request.user)
    context = {
        'incoming_interests': incoming_interests,
        'outgoing_interests': outgoing_interests,
        'my_profile': my_profile,
    }
    return render(request, 'profile/interest_list.html', context)


@login_required
def accept_interest(request, interest_id):
    user_profile = UserProfile.objects.filter(user=request.user).first()
    if not user_profile or not user_profile.identity_proof:
        messages.warning(request, "You must complete your profile first.")
        return redirect('create_profile')
    if request.user.is_verified == False:
        messages.warning(request, "Your profile is now under verification. Please wait for admin approval.")
        return redirect('create_profile')
    interest = get_object_or_404(ProfileInterest, id=interest_id, receiver__user=request.user)
    interest.status = 'accepted'
    interest.save()
    receiver_profile = get_object_or_404(UserProfile, user=request.user)
    # Run email sending in background thread
    threading.Thread(
        target=send_interest_accept_email,
        args=(receiver_profile, interest.sender.email, interest.sender.first_name)
    ).start()
    return redirect(request.META.get('HTTP_REFERER', 'interest_list'))


@login_required
def reject_interest(request, interest_id):
    user_profile = UserProfile.objects.filter(user=request.user).first()
    if not user_profile or not user_profile.identity_proof:
        messages.warning(request, "You must complete your profile first.")
        return redirect('create_profile')
    if request.user.is_verified == False:
        messages.warning(request, "Your profile is now under verification. Please wait for admin approval.")
        return redirect('create_profile')
    interest = get_object_or_404(ProfileInterest, id=interest_id, receiver__user=request.user)
    interest.status = 'rejected'
    interest.save()
    return redirect(request.META.get('HTTP_REFERER', 'interest_list'))


def home_view(request):
    """
    Render the Vivah home page with local images.
    """
    context = {
        # List of slider images from static folder
        'slider_images': [
            'images/c7.png',
        ],
        # Testimonials
        'testimonials': [
            "Vivah helped me find my soulmate. The process was simple, safe, and truly effective!",
            "I met my life partner through Vivah and couldn’t be happier. Highly recommended!",
            "A wonderful platform for serious relationships and lifelong companionship."
        ],
        # Steps
        'steps': [
            {"title": "Create Profile", "description": "Sign up and build a detailed profile showcasing yourself and your preferences."},
            {"title": "Browse Profiles", "description": "Explore profiles of potential matches based on your preferences and interests."},
            {"title": "Connect & Chat", "description": "Show interest, communicate safely, and take the first step toward lifelong love."},
        ]
    }
    return render(request, "home.html", context)


def feedback_view(request):
    if request.method == "POST":
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            if request.user.is_authenticated:
                feedback.user = request.user
            feedback.save()
            return redirect('profiles_list')
    else:
        form = FeedbackForm()
    return render(request, 'feedback/feedback.html', {'form': form})


def help_view(request):
    return render(request, 'feedback/help_and_support.html')

@login_required
def user_profile_detail(request, uid):
    # DO NOT override uid here
    profile = get_object_or_404(
        UserProfile.objects.select_related('user').prefetch_related('user_profile'),
        uid=uid
    )
    gallery_images = UploadImage.objects.filter(galary=profile)
    context = {
        'profile': profile,
        'gallery_images': gallery_images,
    }
    return render(request, 'profile/user_profile_detail.html', context)


@login_required
def chat_view(request, receiver_email):
    from django.contrib import messages
    user_profile = UserProfile.objects.filter(user=request.user).first()
    if not user_profile or not user_profile.identity_proof:
        messages.warning(request, "You must complete your profile first.")
        return redirect('create_profile')
    if request.user.is_verified == False:
        messages.warning(request, "Your profile is now under verification. Please wait for admin approval.")
        return redirect('create_profile')
    # Find receiver by email
    receiver = get_object_or_404(User, username=receiver_email)
    profile = get_object_or_404(UserProfile, user=receiver)
    # Get chat messages (both directions)
    messages = ChatMessage.objects.filter(
        sender__in=[request.user, receiver],
        receiver__in=[request.user, receiver]
    ).order_by('timestamp')
    # Mark receiver’s unread messages as seen
    ChatMessage.objects.filter(
        sender=receiver, receiver=request.user, seen=False
    ).update(seen=True)
    # Handle new message
    if request.method == "POST":
        text = request.POST.get('message')
        if text:
            print(request.user, receiver, text)
            ChatMessage.objects.create(sender=request.user, receiver=receiver, message=text)
        return redirect('chat_view', receiver_email=receiver.username)
    return render(request, 'chat/chat.html', {
        'receiver': receiver,
        'messages': messages,
        'profile': profile,
    })


def navbar_notifications(request):
    if request.user.is_authenticated:
        unseen_messages = (
            ChatMessage.objects.filter(receiver=request.user, seen=False)
            .values('sender__username')
            .annotate(total=Count('id'))
            .order_by('-total')
        )
    else:
        unseen_messages = []
    return {'unseen_messages': unseen_messages}


@login_required
def chat_home(request):
    user_profile = UserProfile.objects.filter(user=request.user).first()
    if not user_profile or not user_profile.identity_proof:
        messages.warning(request, "You must complete your profile first.")
        return redirect('create_profile')
    if request.user.is_verified == False:
        messages.warning(request, "Your profile is now under verification. Please wait for admin approval.")
        return redirect('create_profile')
    # Collect all chat partners of current user
    chat_partners = ChatMessage.objects.filter(
        Q(sender=request.user) | Q(receiver=request.user)
    ).values_list('sender', 'receiver', named=True)
    user_ids = set()
    for c in chat_partners:
        if c.sender != request.user.id:
            user_ids.add(c.sender)
        if c.receiver != request.user.id:
            user_ids.add(c.receiver)
    # Prepare unseen count per sender
    unseen_counts = (
        ChatMessage.objects.filter(receiver=request.user, seen=False)
        .values('sender')
        .annotate(total=Count('id'))
    )
    unseen_dict = {u['sender']: u['total'] for u in unseen_counts}
    # Get user list and annotate with latest message time
    users = (
        User.objects.filter(id__in=user_ids)
        .annotate(
            last_message_time=Greatest(
                Max('sent_messages__timestamp', filter=Q(sent_messages__receiver=request.user)),
                Max('received_messages__timestamp', filter=Q(received_messages__sender=request.user))
            )
        )
    )
    # Add unread indicator manually
    user_data = []
    for u in users:
        last_msg = (
            ChatMessage.objects.filter(
                Q(sender=request.user, receiver=u) | Q(sender=u, receiver=request.user)
            )
            .order_by('-timestamp')
            .first()
        )
        unseen_count = unseen_dict.get(u.id, 0)
        has_unread = unseen_count > 0
        user_data.append({
            'user': u,
            'last_message': last_msg.message if last_msg else '',
            'timestamp': last_msg.timestamp if last_msg else '',
            'unseen_count': unseen_count,
            'has_unread': has_unread,
        })
    # ✅ Sort unread first, then by timestamp (newest first)
    user_data.sort(key=lambda x: (not x['has_unread'], x['timestamp'] or 0), reverse=False)
    return render(request, 'chat/chat_list.html', {'user_data': user_data})


from django.http import JsonResponse

@login_required
def premium_form_view(request):
    user = request.user
     # Check if user already has a valid premium subscription
    active_premium = PremiumUser.objects.filter(
        user=user, is_premium=True, expiry_date__gt=now().date()
    ).first()
    if active_premium:
        # Fetch all payment records for display
        all_payments = PremiumUser.objects.filter(user=user).order_by('-updated')
        return render(request, 'premium/premium_payment_detail.html', {
            'active_premium': active_premium,
            'all_payments': all_payments
        })
    if request.method == "POST":
        form = PremiumUserForm(request.POST, request.FILES)
        if form.is_valid():
            premium = form.save(commit=False)
            premium.user = user
            premium.save()
            return JsonResponse({'success': True})
        else:
            print(form.errors.as_json())
            return JsonResponse({'success': False, 'errors': form.errors})
    form = PremiumUserForm()
    return render(request, 'premium/premium_form.html', {'form': form})

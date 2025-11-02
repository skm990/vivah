from django.urls import path
from .views import (
    request_otp_view,
    verify_otp_view,
    login_view,
    create_profile_view,
    logout_view,
    profiles_list,
    send_interest,
    interest_list,
    accept_interest,
    reject_interest,
    home_view,
    delete_gallery_image,
    feedback_view,
    user_profile_detail,
    chat_view,
    chat_home,
    premium_form_view,
)



urlpatterns = [
    path('otp/', request_otp_view, name='request_otp'),
    path('verify-otp/', verify_otp_view, name='verify_otp'),
    path('login/', login_view, name='login'),
    path('profile/', create_profile_view, name='create_profile'),
    path('logout/', logout_view, name='logout'),
    path('home/', profiles_list, name='profiles_list'),
    path('profiles/<int:profile_id>/interest/', send_interest, name='send_interest'),
    path('interests/', interest_list, name='interest_list'),
    path('interests/<int:interest_id>/accept/', accept_interest, name='accept_interest'),
    path('interests/<int:interest_id>/reject/', reject_interest, name='reject_interest'),
    path('', home_view, name='home'),  # Home page
    path('delete-gallery-image/<uuid:uid>/', delete_gallery_image, name='delete_gallery_image'),
    path('feedback/', feedback_view, name='feedback'),
    path('profiles/<uuid:uid>/user/', user_profile_detail, name='user_profile_detail'),
    path('chat/email/<str:receiver_email>/', chat_view, name='chat_view'),
    path('chat/', chat_home, name='chat_home'),
    path('premium/', premium_form_view, name='premium_form_view'),

]





from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.admin import UserAdmin
from accounts.models import (
    UserAccount,
    UserProfile,
    UserOtp,
    key_generator,
    WelcomeMail,
    ProfileInterest,
    UploadImage,
    Feedback,
    ChatMessage,
    PremiumUser,
)

# =====================
# USER ACCOUNT ADMIN
# =====================
class UserAccountAdmin(UserAdmin):
    model = UserAccount
    list_display = ('email', 'username', 'is_staff', 'is_active', 'is_verified', 'created_at')
    list_filter = ('is_staff', 'is_active', 'is_verified', 'created_at')
    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_verified', 'is_superuser', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2', 'is_staff', 'is_active', 'is_verified'),
        }),
    )
    search_fields = ('email', 'username')
    ordering = ('-created_at',)


# =====================
# USER OTP ADMIN
# =====================
class UserOtpAdmin(admin.ModelAdmin):
    list_display = ('uid', 'user', 'email', 'otp', 'otp_verified', 'created_at')
    search_fields = ('email',)
    raw_id_fields = ('user',)
    ordering = ('-created_at',)

# Inline for UploadImage in UserProfile
class UploadImageInline(admin.TabularInline):
    model = UploadImage
    extra = 1  # Number of empty forms to show
    fields = ('image', 'created', 'updated')
    readonly_fields = ('created', 'updated')
    show_change_link = True  # Adds a link to edit the inline item


# =====================
# USER PROFILE ADMIN
# =====================
class UserProfileAdmin(admin.ModelAdmin):
    list_display = (
        'uid',
        'user',
        'user__first_name',
        'user__last_name',
        'user_identity',
        'gender',
        'age',
        'marital_status',
        'religion',
        'education',
        'occupation',
        'annual_income',
        'city',
        'state',
        'country',
        'phone_no',
        'created_at',
        'view_image',
    )
    list_filter = (
        'gender',
        'marital_status',
        'religion',
        'education',
        'occupation',
        'created_at',
    )
    search_fields = (
        'user__email',
        'user_identity',
        'phone_no',
        'city',
        'state',
        'country',
        'religion',
        'occupation',
    )
    ordering = ('-created_at',)
    readonly_fields = ('uid', 'user_identity', 'created_at', 'updated_at')
    raw_id_fields = ('user',)
    inlines = [UploadImageInline]

    def view_image(self, obj):
        """Display a small profile image in admin list view."""
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="border-radius: 5px;" />', obj.image.url)
        return "—"
    view_image.short_description = 'Profile Image'

    def save_model(self, request, obj, form, change):
        """Ensure user_identity is generated automatically."""
        if not obj.user_identity:
            obj.user_identity = key_generator()
        super().save_model(request, obj, form, change)


# =====================
# PROFILE INTEREST ADMIN
# =====================
@admin.register(ProfileInterest)
class ProfileInterestAdmin(admin.ModelAdmin):
    list_display = ('sender', 'get_receiver', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('sender__username', 'receiver__user__username')
    raw_id_fields = ('sender', 'receiver',)
    ordering = ('-created_at',)
    readonly_fields = ('uid', 'created_at', 'updated_at')

    def get_receiver(self, obj):
        return obj.receiver.user.username if obj.receiver and obj.receiver.user else "Anonymous"
    get_receiver.short_description = 'Receiver'


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('uid', 'user', 'feedback_type', 'rating', 'is_reviewed', 'created_at')
    list_filter = ('feedback_type', 'is_reviewed', 'rating', 'created_at')
    search_fields = ('user__username', 'user__email', 'message')
    raw_id_fields = ('user',)
    ordering = ('-created_at',)
    readonly_fields = ('uid', 'created_at')

    fieldsets = (
        (None, {
            'fields': ('uid', 'user', 'feedback_type', 'rating', 'message')
        }),
        ('Status', {
            'fields': ('is_reviewed', 'created_at')
        }),
    )


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('uid', 'sender', 'receiver', 'short_message', 'timestamp')
    search_fields = ('sender__username', 'receiver__username', 'message')
    raw_id_fields = ('sender', 'receiver',)
    ordering = ('-timestamp',)
    readonly_fields = ('uid', 'timestamp')

    def short_message(self, obj):
        return (obj.message[:75] + '...') if len(obj.message) > 75 else obj.message
    short_message.short_description = 'Message'


@admin.register(PremiumUser)
class PremiumUserAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'is_premium',
        'amount',
        'payment_status',
        'transaction_id',
        'created',
        'updated',
    )
    list_filter = ('is_premium', 'payment_status', 'created')
    search_fields = ('user__username', 'user__email', 'transaction_id')
    raw_id_fields = ('user',)
    readonly_fields = ('uid', 'created', 'updated')
    ordering = ('-created',)



# =====================
# ADMIN REGISTRATION
# =====================
admin.site.register(UserAccount, UserAccountAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(UserOtp, UserOtpAdmin)
admin.site.register(WelcomeMail)

# Set custom admin titles
admin.site.site_title = _("VIVAH")  # Title for the browser tab
admin.site.site_header = "VIVAH Admin"  # Title for the admin site header
admin.site.index_title = _("VIVAH Administration")  # Title for the admin index page

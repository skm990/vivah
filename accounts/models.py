from django.utils import timezone
import os, uuid, random, string
from django.db import models
from django.conf import settings
from django.core import validators
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils.translation import gettext_lazy as _
from ckeditor.fields import RichTextField
import uuid
import io
from PIL import Image
from django.core.files.base import ContentFile
from django.core.exceptions import ValidationError
from datetime import date
from django.utils.timezone import now



# =====================
# USER MANAGER
# =====================
class UserAccountManager(BaseUserManager):
    def create_user(self, email, password=None, **kwargs):
        if not email:
            raise ValueError('Users must have a valid email address.')
        if not kwargs.get('username'):
            raise ValueError('Users must have a valid username.')

        account = self.model(
            email=self.normalize_email(email),
            username=kwargs.get('username')
        )
        account.set_password(password)
        account.save()
        return account

    def create_superuser(self, email, password, **kwargs):
        account = self.create_user(email, password, **kwargs)
        account.is_staff = True
        account.is_superuser = True
        account.save()
        return account


# =====================
# USER MODEL
# =====================
class UserAccount(AbstractBaseUser, PermissionsMixin):
    uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    username = models.CharField(
        _('username'), max_length=60, unique=True,
        help_text=_('Required. 60 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        validators=[
            validators.RegexValidator(
                r'^[\w.@+-]+$',
                _('Enter a valid username. This may contain only letters, numbers, and @/./+/-/_ characters.'),
                'invalid'
            ),
        ],
        error_messages={'unique': _("A user with that username already exists.")}
    )
    email = models.EmailField(_('email address'), max_length=60, unique=True)
    first_name = models.CharField(_('first name'), max_length=40)
    last_name = models.CharField(_('last name'), max_length=40, blank=True, null=True)
    is_staff = models.BooleanField(_('staff status'), default=False)
    is_active = models.BooleanField(_('active'), default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserAccountManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.username

    def get_full_name(self):
        return f"{self.first_name} {self.last_name or ''}".strip()


# =====================
# UTILITIES
# =====================
def key_generator(size=10, prefix="VIVAH"):
    suffix_size = size - len(prefix)
    suffix = ''.join(random.SystemRandom().choice(string.digits) for _ in range(suffix_size))
    return f"{prefix}{suffix}"


def user_profile_image_upload_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{instance.uid}.{ext}"
    return os.path.join('uploads/user_profile/images/', filename)


# =====================
# MATRIMONY USER PROFILE
# =====================
class UserProfile(models.Model):
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other')
    ]

    MARITAL_STATUS_CHOICES = [
        ('Never Married', 'Never Married'),
        ('Divorced', 'Divorced'),
        ('Widowed', 'Widowed'),
        ('Awaiting Divorce', 'Awaiting Divorce'),
    ]

    RELIGION_CHOICES = [
        ('Hindu', 'Hindu'),
        ('Muslim', 'Muslim'),
        ('Christian', 'Christian'),
        ('Sikh', 'Sikh'),
        ('Jain', 'Jain'),
        ('Buddhist', 'Buddhist'),
        ('Other', 'Other'),
    ]

    EDUCATION_CHOICES = [
        ('High School', 'High School'),
        ('Graduate', 'Graduate'),
        ('Post Graduate', 'Post Graduate'),
        ('Doctorate', 'Doctorate'),
        ('Other', 'Other'),
    ]

    OCCUPATION_CHOICES = [
        ('Private Job', 'Private Job'),
        ('Government Job', 'Government Job'),
        ('Business', 'Business'),
        ('Self Employed', 'Self Employed'),
        ('Student', 'Student'),
        ('Not Working', 'Not Working'),
    ]

    ANNUAL_INCOME_CHOICES = [
        ('Below 2 Lakh', 'Below 2 Lakh'),
        ('2-5 Lakh', '2-5 Lakh'),
        ('5-10 Lakh', '5-10 Lakh'),
        ('10-20 Lakh', '10-20 Lakh'),
        ('20 Lakh+', '20 Lakh+'),
    ]
    
    COUNTRY_CHOICES = [
        ('India', 'India'),
    ]

    STATE_CHOICES = [
        ('Andhra Pradesh', 'Andhra Pradesh'),
        ('Arunachal Pradesh', 'Arunachal Pradesh'),
        ('Assam', 'Assam'),
        ('Bihar', 'Bihar'),
        ('Chhattisgarh', 'Chhattisgarh'),
        ('Goa', 'Goa'),
        ('Gujarat', 'Gujarat'),
        ('Haryana', 'Haryana'),
        ('Himachal Pradesh', 'Himachal Pradesh'),
        ('Jharkhand', 'Jharkhand'),
        ('Karnataka', 'Karnataka'),
        ('Kerala', 'Kerala'),
        ('Madhya Pradesh', 'Madhya Pradesh'),
        ('Maharashtra', 'Maharashtra'),
        ('Manipur', 'Manipur'),
        ('Meghalaya', 'Meghalaya'),
        ('Mizoram', 'Mizoram'),
        ('Nagaland', 'Nagaland'),
        ('Odisha', 'Odisha'),
        ('Punjab', 'Punjab'),
        ('Rajasthan', 'Rajasthan'),
        ('Sikkim', 'Sikkim'),
        ('Tamil Nadu', 'Tamil Nadu'),
        ('Telangana', 'Telangana'),
        ('Tripura', 'Tripura'),
        ('Uttar Pradesh', 'Uttar Pradesh'),
        ('Uttarakhand', 'Uttarakhand'),
        ('West Bengal', 'West Bengal'),
        ('Andaman and Nicobar Islands', 'Andaman and Nicobar Islands'),
        ('Chandigarh', 'Chandigarh'),
        ('Dadra and Nagar Haveli and Daman and Diu', 'Dadra and Nagar Haveli and Daman and Diu'),
        ('Delhi', 'Delhi'),
        ('Jammu and Kashmir', 'Jammu and Kashmir'),
        ('Ladakh', 'Ladakh'),
        ('Lakshadweep', 'Lakshadweep'),
        ('Puducherry', 'Puducherry'),
    ]
    
    CASTE_CHOICES = [
        ('Bania', 'Bania'),
        ('Barhai', 'Barhai (Carpenter)'),
        ('Beldar', 'Beldar'),
        ('Bhuiya', 'Bhuiya'),
        ('Bind', 'Bind'),
        ('Brahmin', 'Brahmin'),
        ('Bhumihar', 'Bhumihar'),
        ('Chamar', 'Chamar'),
        ('Chaurasia', 'Chaurasia'),
        ('Dhobi', 'Dhobi (Washerman)'),
        ('Dom', 'Dom'),
        ('Dusadh', 'Dusadh (Paswan)'),
        ('Gupta', 'Gupta'),
        ('Halwai', 'Halwai (Sweet Maker)'),
        ('Kahar', 'Kahar'),
        ('Kalwar', 'Kalwar'),
        ('Kanu', 'Kanu'),
        ('Kayastha', 'Kayastha'),
        ('Kewat', 'Kewat'),
        ('Koeri', 'Koeri'),
        ('Kumhar', 'Kumhar'),
        ('Kurmi', 'Kurmi'),
        ('Kushwaha', 'Kushwaha'),
        ('Lohar', 'Lohar (Blacksmith)'),
        ('Mali', 'Mali (Gardener)'),
        ('Majhi', 'Majhi'),
        ('Mallah', 'Mallah (Nishad)'),
        ('Musahar', 'Musahar'),
        ('Nai', 'Nai (Barber)'),
        ('Nonia', 'Nonia'),
        ('Pandit', 'Pandit'),
        ('Pasi', 'Pasi'),
        ('Patwa', 'Patwa'),
        ('Rajak', 'Rajak'),
        ('Rajput', 'Rajput'),
        ('Ranchi', 'Ranchi'),
        ('Ravidas', 'Ravidas'),
        ('Sahu', 'Sahu'),
        ('Saw', 'Saw'),
        ('Sonar', 'Sonar (Goldsmith)'),
        ('Sutar', 'Sutar'),
        ('Swarnkar', 'Swarnkar'),
        ('Tanti', 'Tanti'),
        ('Tatwa', 'Tatwa'),
        ('Teli', 'Teli'),
        ('Thakur', 'Thakur'),
        ('Yadav', 'Yadav'),
        ('Others', 'Others'),
    ]

    # Basic Info
    uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    image = models.ImageField(upload_to=user_profile_image_upload_path, null=True, blank=True)
    user_identity = models.CharField(db_index=True, unique=True, max_length=10, default=key_generator, editable=False)

    # Personal Info
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    age = models.PositiveIntegerField(null=True, blank=True)
    dob = models.DateField(null=True, blank=True)
    height = models.FloatField(null=True, blank=True, help_text="Height in cm")
    weight = models.FloatField(null=True, blank=True, help_text="Weight in kg")
    marital_status = models.CharField(max_length=30, choices=MARITAL_STATUS_CHOICES, default='Never Married')
    religion = models.CharField(max_length=50, choices=RELIGION_CHOICES, null=True, blank=True)
    caste = models.CharField(max_length=100, choices=CASTE_CHOICES, null=True, blank=True)
    mother_tongue = models.CharField(max_length=100, null=True, blank=True)

    # Education & Profession
    education = models.CharField(max_length=100, choices=EDUCATION_CHOICES, null=True, blank=True)
    occupation = models.CharField(max_length=100, choices=OCCUPATION_CHOICES, null=True, blank=True)
    annual_income = models.CharField(max_length=50, choices=ANNUAL_INCOME_CHOICES, null=True, blank=True)
    company_name = models.CharField(max_length=255, null=True, blank=True)
    working_city = models.CharField(max_length=255, null=True, blank=True)

    # Contact & Location
    phone_no = models.CharField(max_length=15, null=True, blank=True)
    address = models.CharField(max_length=1000, null=True, blank=True)
    country = models.CharField(max_length=255, choices=COUNTRY_CHOICES, null=True, blank=True)
    state = models.CharField(max_length=255, choices=STATE_CHOICES, null=True, blank=True)
    city = models.CharField(max_length=255, null=True, blank=True)

    # Lifestyle
    diet = models.CharField(max_length=50, null=True, blank=True, choices=[('Veg', 'Veg'), ('Non-Veg', 'Non-Veg'), ('Eggetarian', 'Eggetarian')])
    smoking = models.CharField(max_length=50, null=True, blank=True, choices=[('No', 'No'), ('Occasionally', 'Occasionally'), ('Yes', 'Yes')])
    drinking = models.CharField(max_length=50, null=True, blank=True, choices=[('No', 'No'), ('Occasionally', 'Occasionally'), ('Yes', 'Yes')])
    hobbies = models.CharField(max_length=1000, null=True, blank=True,)

    # Family Info
    father_name = models.CharField(max_length=255, null=True, blank=True)
    mother_name = models.CharField(max_length=255, null=True, blank=True)
    father_occupation = models.CharField(max_length=255, choices=OCCUPATION_CHOICES, null=True, blank=True)
    mother_occupation = models.CharField(max_length=255, choices=OCCUPATION_CHOICES, null=True, blank=True)
    sisters = models.PositiveIntegerField(default=0)
    brothers = models.PositiveIntegerField(default=0)
    family_type = models.CharField(max_length=50, choices=[('Joint', 'Joint'), ('Nuclear', 'Nuclear')], null=True, blank=True)

    # About
    about_me = models.TextField(null=True, blank=True)
    partner_preferences = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    MAX_IMAGE_SIZE_KB = 200
    STANDARD_WIDTH = 800  # you can adjust this
    STANDARD_HEIGHT = 800

    def __str__(self):
        return self.user.email if self.user else "Anonymous User"
    
    @property
    def age(self):
        if self.dob:
            today = date.today()
            return today.year - self.dob.year - ((today.month, today.day) < (self.dob.month, self.dob.day))
        return None

    
    def save(self, *args, **kwargs):
        # Save normally first if new file not yet saved
        if self.image:
            self.image = self.compress_image(self.image)
        super().save(*args, **kwargs)

    def compress_image(self, uploaded_image):
        """Compress uploaded image to under 200 KB and standard size."""
        image_temp = Image.open(uploaded_image)
        image_format = image_temp.format  # e.g., JPEG, PNG

        # Convert all images to RGB (for JPEG)
        if image_temp.mode in ("RGBA", "P"):
            image_temp = image_temp.convert("RGB")

        # Resize to standard size (maintain aspect ratio)
        image_temp.thumbnail((self.STANDARD_WIDTH, self.STANDARD_HEIGHT))

        # Compress until under 200 KB
        buffer = io.BytesIO()
        quality = 85  # start quality
        image_temp.save(buffer, format='JPEG', quality=quality, optimize=True)
        
        while buffer.tell() > self.MAX_IMAGE_SIZE_KB * 1024 and quality > 30:
            buffer = io.BytesIO()
            quality -= 5
            image_temp.save(buffer, format='JPEG', quality=quality, optimize=True)

        if buffer.tell() > self.MAX_IMAGE_SIZE_KB * 1024:
            raise ValidationError("Image cannot be compressed below 200 KB. Please upload a smaller image.")

        # Create new Django file
        compressed_image = ContentFile(buffer.getvalue())
        new_filename = f"{uuid.uuid4()}.jpg"

        return ContentFile(buffer.getvalue(), name=new_filename)

    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'


class UploadImage(models.Model):
    uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    galary = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='user_profile', blank=True, null=True,)
    image = models.ImageField(upload_to=user_profile_image_upload_path, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    updated = models.DateTimeField(auto_now=True)
    
    MAX_IMAGE_SIZE_KB = 200
    STANDARD_WIDTH = 800  # you can adjust this
    STANDARD_HEIGHT = 800

    def __str__(self):
        return str(self.uid)

    def save(self, *args, **kwargs):
        # Save normally first if new file not yet saved
        if self.image:
            self.image = self.compress_image(self.image)
        super().save(*args, **kwargs)

    def compress_image(self, uploaded_image):
        """Compress uploaded image to under 200 KB and standard size."""
        image_temp = Image.open(uploaded_image)
        image_format = image_temp.format  # e.g., JPEG, PNG

        # Convert all images to RGB (for JPEG)
        if image_temp.mode in ("RGBA", "P"):
            image_temp = image_temp.convert("RGB")

        # Resize to standard size (maintain aspect ratio)
        image_temp.thumbnail((self.STANDARD_WIDTH, self.STANDARD_HEIGHT))

        # Compress until under 200 KB
        buffer = io.BytesIO()
        quality = 85  # start quality
        image_temp.save(buffer, format='JPEG', quality=quality, optimize=True)
        
        while buffer.tell() > self.MAX_IMAGE_SIZE_KB * 1024 and quality > 30:
            buffer = io.BytesIO()
            quality -= 5
            image_temp.save(buffer, format='JPEG', quality=quality, optimize=True)

        if buffer.tell() > self.MAX_IMAGE_SIZE_KB * 1024:
            raise ValidationError("Image cannot be compressed below 200 KB. Please upload a smaller image.")

        # Create new Django file
        compressed_image = ContentFile(buffer.getvalue())
        new_filename = f"{uuid.uuid4()}.jpg"

        return ContentFile(buffer.getvalue(), name=new_filename)


class ProfileInterest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]

    uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    sender = models.ForeignKey(
        UserAccount,
        on_delete=models.CASCADE,
        related_name='sent_interests',
        db_index=True
    )
    receiver = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        related_name='received_interests',
        db_index=True
    )
    message = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  # Track message updates or status changes

    class Meta:
        unique_together = ('sender', 'receiver')  # Prevent duplicate interests
        ordering = ['-created_at']  # Most recent first

    def __str__(self):
        receiver_username = self.receiver.user.username if self.receiver and self.receiver.user else "Anonymous"
        return f"{self.sender.username} → {receiver_username}"


class UserOtp(models.Model):
    uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True)
    otp = models.CharField(max_length=100, null=True, blank=True)
    email = models.CharField(max_length=100, null=True, blank=True)
    otp_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def is_expired(self):
        from datetime import timedelta
        return self.created_at + timedelta(minutes=10) < timezone.now()


class WelcomeMail(models.Model):
    uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True)
    welcome = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.uid)


class Feedback(models.Model):
    FEEDBACK_TYPE_CHOICES = [
        ('general', 'General Suggestion'),
        ('profile_issue', 'Profile Issue'),
        ('success_story', 'Success Story'),
        ('other', 'Other'),
    ]

    RATING_CHOICES = [
        (1, '⭐'),
        (2, '⭐⭐'),
        (3, '⭐⭐⭐'),
        (4, '⭐⭐⭐⭐'),
        (5, '⭐⭐⭐⭐⭐'),
    ]

    uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="feedbacks"
    )
    feedback_type = models.CharField(
        max_length=20,
        choices=FEEDBACK_TYPE_CHOICES,
        default='general'
    )
    message = models.TextField()
    rating = models.PositiveSmallIntegerField(
        choices=RATING_CHOICES,
        null=True,
        blank=True,
        help_text="Optional rating for Vivah platform"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    is_reviewed = models.BooleanField(default=False)

    def __str__(self):
        user_repr = self.user.username if self.user else "Anonymous"
        return f"{self.get_feedback_type_display()} from {user_repr} at {self.created_at.strftime('%Y-%m-%d %H:%M')}"


class ChatMessage(models.Model):
    uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_messages'
    )
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='received_messages'
    )
    message = models.TextField()
    seen = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"From {self.sender.username} to {self.receiver.username}"


def user_premium_upload_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{instance.uid}.{ext}"
    return os.path.join('uploads', 'premium', filename)

class PremiumUser(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
        ('cancelled', 'Cancelled'),
    ]

    uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="premium_status"
    )
    is_premium = models.BooleanField(default=False)
    amount = models.DecimalField(max_digits=10, decimal_places=2,)
    mobile = models.CharField(max_length=15, )
    transaction_id = models.CharField(max_length=100, null=True, blank=True)
    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='pending'
    )
    receipt = models.FileField(upload_to=user_premium_upload_path, null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    created = models.DateTimeField(default=now)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {'Premium' if self.is_premium else 'Standard'}"

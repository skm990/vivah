from django.db import models
import uuid
import random
import string





def key_generator(size=10, prefix="STUDENT"):
    suffix_size = size - len(prefix)
    suffix = ''.join(random.SystemRandom().choice(string.digits) for _ in range(suffix_size))
    return f"{prefix}{suffix}"


class Receipt(models.Model):
    MONTH_CHOICES = [
        ('January', 'January'),
        ('February', 'February'),
        ('March', 'March'),
        ('April', 'April'),
        ('May', 'May'),
        ('June', 'June'),
        ('July', 'July'),
        ('August', 'August'),
        ('September', 'September'),
        ('October', 'October'),
        ('November', 'November'),
        ('December', 'December'),
    ]
    uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    receipt_no = models.CharField(db_index=True, unique=True, max_length=10, default=key_generator, editable=False)
    student_name = models.CharField(max_length=100)
    father_name = models.CharField(max_length=100)
    address = models.CharField(max_length=700, blank=True, null=True)
    admission_no = models.CharField(max_length=50)
    month = models.CharField(max_length=20, choices=MONTH_CHOICES)
    year = models.CharField(max_length=20)
    admission_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    class_name = models.CharField(max_length=50, blank=True, null=True)
    tuition_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    back_dues = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    extra = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    description = models.TextField(blank=True, null=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, editable=False, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Automatically calculate total before saving
        self.total = self.admission_fee + self.tuition_fee + self.back_dues + self.extra
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Receipt #{self.receipt_no} - {self.student_name}"


class ReceiptFileRecord(models.Model):
    MONTH_CHOICES = [
        ('January', 'January'),
        ('February', 'February'),
        ('March', 'March'),
        ('April', 'April'),
        ('May', 'May'),
        ('June', 'June'),
        ('July', 'July'),
        ('August', 'August'),
        ('September', 'September'),
        ('October', 'October'),
        ('November', 'November'),
        ('December', 'December'),
    ]
    receipt = models.ForeignKey(Receipt, on_delete=models.CASCADE)
    year = models.CharField(max_length=20)
    month = models.CharField(max_length=20, choices=MONTH_CHOICES)
    completed = models.BooleanField(default=False)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    baki = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    remarks = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
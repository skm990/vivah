from django import forms
from .models import ReceiptFileRecord, Receipt

class ReceiptFileRecordForm(forms.ModelForm):
    class Meta:
        model = ReceiptFileRecord
        fields = ['month', 'year', 'amount', 'baki', 'remarks', 'completed']


class ReceiptForm(forms.ModelForm):
    class Meta:
        model = Receipt
        fields = [
            'student_name', 'father_name', 'address',
            'admission_no', 'month', 'year', 'class_name',
            'admission_fee', 'tuition_fee', 'back_dues', 'extra', 'description'
        ]

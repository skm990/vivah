from django.contrib import admin
from .models import Receipt, ReceiptFileRecord



@admin.register(Receipt)
class ReceiptAdmin(admin.ModelAdmin):
    list_display = (
        'receipt_no', 'student_name', 'father_name',
        'month', 'year', 'total'
    )
    list_filter = ('month', 'year',)
    search_fields = ('student_name', 'father_name', 'receipt_no', 'admission_no')
    readonly_fields = ('total', 'receipt_no', 'uid', 'created_at', 'updated_at')
    ordering = ('-created_at',)


@admin.register(ReceiptFileRecord)
class ReceiptFileRecordAdmin(admin.ModelAdmin):
    list_display = ('year', 'month', 'receipt__student_name', 'amount', 'baki', 'completed', 'created_at', 'updated_at')

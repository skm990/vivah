from django.db.models import Q, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string

from weasyprint import HTML

from .forms import ReceiptFileRecordForm, ReceiptForm
from .models import Receipt, ReceiptFileRecord



def download_receipt_pdf(request, uid):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.email not in ['admin@gmail.com', 'chandan@gmail.com']:
        return redirect('home')
    receipt = Receipt.objects.get(uid=uid)
    html_string = render_to_string('receipts/receipt_template.html', {'receipt': receipt})
    pdf_file = HTML(string=html_string).write_pdf()
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Receipt_{receipt.student_name}_{receipt.month}_{receipt.year}.pdf"'
    return response


def receipt_list(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.email not in ['admin@gmail.com', 'chandan@gmail.com']:
        return redirect('home')
    receipts = Receipt.objects.all().order_by('-created_at')
    # Calculate total baki across all records
    baki_summary = ReceiptFileRecord.objects.aggregate(total_baki=Sum('baki'))
    total_baki = baki_summary['total_baki'] or 0
    # Optional: baki per receipt
    baki_per_receipt = (
        ReceiptFileRecord.objects
        .values('receipt')
        .annotate(total_baki=Sum('baki'))
    )
    baki_map = {r['receipt']: r['total_baki'] for r in baki_per_receipt}
    for r in receipts:
        r.total_baki = baki_map.get(r.id, 0)
    return render(request, 'receipts/receipt_list.html', {
        'receipts': receipts,
        'total_baki': total_baki,
    })


def edit_receipt_record(request, pk):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.email not in ['admin@gmail.com', 'chandan@gmail.com']:
        return redirect('home')
    receipt = get_object_or_404(Receipt, pk=pk)
    # All previous records for this receipt
    existing_records = ReceiptFileRecord.objects.filter(receipt=receipt).order_by('-created_at')
    if request.method == "POST":
        form = ReceiptFileRecordForm(request.POST)
        if form.is_valid():
            month = form.cleaned_data['month']
            year = form.cleaned_data['year']
            # Check if record already exists for this month & year
            record = ReceiptFileRecord.objects.filter(
                receipt=receipt, month=month, year=year
            ).first()
            if record:
                # Update existing record
                record.amount = form.cleaned_data['amount']
                record.baki = form.cleaned_data['baki']
                record.remarks = form.cleaned_data['remarks']
                record.completed = form.cleaned_data['completed']
                record.save()
            else:
                # Create new record
                new_record = form.save(commit=False)
                new_record.receipt = receipt
                new_record.save()
            return redirect('edit_receipt_record', pk=receipt.pk)
    else:
        form = ReceiptFileRecordForm()
    return render(request, 'receipts/edit_record.html', {
        'receipt': receipt,
        'form': form,
        'existing_records': existing_records
    })


def edit_receipt(request, pk):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.email not in ['admin@gmail.com', 'chandan@gmail.com']:
        return redirect('home')
    receipt = get_object_or_404(Receipt, pk=pk)
    if request.method == "POST":
        form = ReceiptForm(request.POST, instance=receipt)
        if form.is_valid():
            form.save()
            return redirect('receipt_list')
    else:
        form = ReceiptForm(instance=receipt)
    return render(request, 'receipts/edit_receipt.html', {'form': form, 'receipt': receipt})


def add_receipt(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.email not in ['admin@gmail.com', 'chandan@gmail.com']:
        return redirect('home')
    if request.method == 'POST':
        form = ReceiptForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('receipt_list')
    else:
        form = ReceiptForm()

    return render(request, 'receipts/add_receipt.html', {
        'form': form,
        'receipt': Receipt,  # ✅ needed for MONTH_CHOICES
    })

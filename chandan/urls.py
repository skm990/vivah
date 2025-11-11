from django.urls import path
from . import views



urlpatterns = [
    path('', views.receipt_list, name='receipt_list'),
    path('receipts/<uuid:uid>/download/', views.download_receipt_pdf, name='download_receipt_pdf'),
    path('records/<int:pk>/edit/', views.edit_receipt_record, name='edit_receipt_record'),
    path('receipt/<int:pk>/edit/', views.edit_receipt, name='edit_receipt'),
    path('receipt/add/', views.add_receipt, name='add_receipt')

]

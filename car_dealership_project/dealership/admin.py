from django.contrib import admin
from .models import Employee, Customer, Vehicle, Transaction, Payment, Service, InventoryItem, TestDrive

admin.site.register(Employee)
admin.site.register(Customer)
admin.site.register(Vehicle)
admin.site.register(Transaction)
admin.site.register(Payment)
admin.site.register(Service)
admin.site.register(InventoryItem)
admin.site.register(TestDrive)
# dealership/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Customer, Vehicle, Employee, Transaction
from .forms import CustomerForm, VehicleForm, EmployeeForm, TransactionForm

# Home view
def home(request):
    vehicles_count = Vehicle.objects.count()
    customers_count = Customer.objects.count()
    employees_count = Employee.objects.count()
    transactions_count = Transaction.objects.count()
    
    recent_transactions = Transaction.objects.order_by('-transaction_date')[:5]
    available_vehicles = Vehicle.objects.filter(status='Available').count()
    
    context = {
        'vehicles_count': vehicles_count,
        'customers_count': customers_count,
        'employees_count': employees_count,
        'transactions_count': transactions_count,
        'recent_transactions': recent_transactions,
        'available_vehicles': available_vehicles,
    }
    return render(request, 'dealership/home.html', context)

# Customer Views
def customer_list(request):
    customers = Customer.objects.all()
    return render(request, 'dealership/customer/list.html', {'customers': customers})

def customer_detail(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    transactions = Transaction.objects.filter(customer=customer)
    test_drives = customer.testdrive_set.all()
    return render(request, 'dealership/customer/detail.html', {
        'customer': customer, 
        'transactions': transactions,
        'test_drives': test_drives
    })

def customer_create(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Customer created successfully!')
            return redirect('customer_list')
    else:
        form = CustomerForm()
    return render(request, 'dealership/customer/form.html', {'form': form, 'title': 'Add New Customer'})

def customer_update(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            messages.success(request, 'Customer updated successfully!')
            return redirect('customer_detail', pk=customer.pk)
    else:
        form = CustomerForm(instance=customer)
    return render(request, 'dealership/customer/form.html', {'form': form, 'title': 'Edit Customer'})

def customer_delete(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        customer.delete()
        messages.success(request, 'Customer deleted successfully!')
        return redirect('customer_list')
    return render(request, 'dealership/customer/confirm_delete.html', {'customer': customer})

# Vehicle Views
def vehicle_list(request):
    vehicles = Vehicle.objects.all()
    return render(request, 'dealership/vehicle/list.html', {'vehicles': vehicles})

def vehicle_detail(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk)
    transactions = Transaction.objects.filter(vehicle=vehicle)
    services = vehicle.service_set.all()
    test_drives = vehicle.testdrive_set.all()
    return render(request, 'dealership/vehicle/detail.html', {
        'vehicle': vehicle, 
        'transactions': transactions,
        'services': services,
        'test_drives': test_drives
    })

def vehicle_create(request):
    if request.method == 'POST':
        form = VehicleForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Vehicle added successfully!')
            return redirect('vehicle_list')
    else:
        form = VehicleForm()
    return render(request, 'dealership/vehicle/form.html', {'form': form, 'title': 'Add New Vehicle'})

def vehicle_update(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk)
    if request.method == 'POST':
        form = VehicleForm(request.POST, instance=vehicle)
        if form.is_valid():
            form.save()
            messages.success(request, 'Vehicle updated successfully!')
            return redirect('vehicle_detail', pk=vehicle.pk)
    else:
        form = VehicleForm(instance=vehicle)
    return render(request, 'dealership/vehicle/form.html', {'form': form, 'title': 'Edit Vehicle'})

def vehicle_delete(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk)
    if request.method == 'POST':
        vehicle.delete()
        messages.success(request, 'Vehicle deleted successfully!')
        return redirect('vehicle_list')
    return render(request, 'dealership/vehicle/confirm_delete.html', {'vehicle': vehicle})

# Employee Views
def employee_list(request):
    employees = Employee.objects.all()
    return render(request, 'dealership/employee/list.html', {'employees': employees})

def employee_detail(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    transactions = Transaction.objects.filter(employee=employee)
    services = employee.service_set.all()
    return render(request, 'dealership/employee/detail.html', {
        'employee': employee, 
        'transactions': transactions,
        'services': services
    })

def employee_create(request):
    if request.method == 'POST':
        form = EmployeeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Employee added successfully!')
            return redirect('employee_list')
    else:
        form = EmployeeForm()
    return render(request, 'dealership/employee/form.html', {'form': form, 'title': 'Add New Employee'})

def employee_update(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    if request.method == 'POST':
        form = EmployeeForm(request.POST, instance=employee)
        if form.is_valid():
            form.save()
            messages.success(request, 'Employee updated successfully!')
            return redirect('employee_detail', pk=employee.pk)
    else:
        form = EmployeeForm(instance=employee)
    return render(request, 'dealership/employee/form.html', {'form': form, 'title': 'Edit Employee'})

def employee_delete(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    if request.method == 'POST':
        employee.delete()
        messages.success(request, 'Employee deleted successfully!')
        return redirect('employee_list')
    return render(request, 'dealership/employee/confirm_delete.html', {'employee': employee})

# Transaction Views
def transaction_list(request):
    transactions = Transaction.objects.all().order_by('-transaction_date')
    return render(request, 'dealership/transaction/list.html', {'transactions': transactions})

def transaction_detail(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk)
    payments = transaction.payment_set.all()
    return render(request, 'dealership/transaction/detail.html', {
        'transaction': transaction,
        'payments': payments
    })

def transaction_create(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save()
            messages.success(request, 'Transaction created successfully!')
            return redirect('transaction_detail', pk=transaction.pk)
    else:
        form = TransactionForm()
    return render(request, 'dealership/transaction/form.html', {'form': form, 'title': 'Create New Transaction'})
# dealership/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Customer, Vehicle, Employee, Transaction
from .forms import CustomerForm, VehicleForm, EmployeeForm, TransactionForm
from django.shortcuts import redirect
from django.db import connection

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

def create_transaction_summary_view():
    with connection.cursor() as cursor:
        cursor.execute("""
            CREATE OR REPLACE VIEW transaction_summary_view AS
            SELECT 
                t.transaction_id,
                CONCAT(c.first_name, ' ', c.last_name) AS customer_name,
                CONCAT(v.year, ' ', v.make, ' ', v.model) AS vehicle_name,
                t.sale_price,
                t.transaction_date
            FROM transactions t
            JOIN customers c ON t.customer_id = c.customer_id
            JOIN vehicles v ON t.vehicle_id = v.vehicle_id;
        """)


# Customer Views
def customer_list(request):
    customers = Customer.objects.all()
    return render(request, 'dealership/customer/list.html', {'customers': customers})

def dictfetchall(cursor):
    """Return all rows from a cursor as a list of dictionaries"""
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]

def customer_detail(request, pk):
    # Fetch customer details with raw SQL
    customer_query = """
        SELECT 
            customer_id, 
            first_name, 
            last_name, 
            email, 
            phone_number, 
            address, 
            date_of_birth 
        FROM customers 
        WHERE customer_id = %s
    """
    
    transactions_query = """
        SELECT 
            t.transaction_id,
            t.transaction_date,
            t.sale_price,
            t.payment_type,
            t.status,
            CONCAT(e.first_name, ' ', e.last_name) AS employee_name,
            CONCAT(v.year, ' ', v.make, ' ', v.model) AS vehicle_details,
            v.vin
        FROM transactions t
        LEFT JOIN employees e ON t.employee_id = e.employee_id
        LEFT JOIN vehicles v ON t.vehicle_id = v.vehicle_id
        WHERE t.customer_id = %s
        ORDER BY t.transaction_date DESC
    """

    stats_query = """
        SELECT 
            COUNT(t.transaction_id) AS total_transactions,
            SUM(t.sale_price) AS total_spent,
            AVG(t.sale_price) AS average_purchase,
            MAX(t.transaction_date) AS latest_transaction,
            MIN(t.transaction_date) AS first_transaction
        FROM transactions t
        WHERE t.customer_id = %s AND t.status = 'Completed'
    """
    
    with connection.cursor() as cursor:
        # Execute customer query
        cursor.execute(customer_query, [pk])
        customer_data = dictfetchall(cursor)
        if not customer_data:
            raise Http404("Customer not found")
        customer = customer_data[0]
        
        # Execute transactions query
        cursor.execute(transactions_query, [pk])
        transactions = dictfetchall(cursor)
        
        # Execute stats query
        cursor.execute(stats_query, [pk])
        stats = dictfetchall(cursor)[0]
    
    context = {
        'customer': customer,
        'transactions': transactions,
        'stats': stats
    }
    
    return render(request, 'dealership/customer/detail.html', context)

def customer_create(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            phone = form.cleaned_data['phone']
            address = form.cleaned_data['address']
            
            insert_query = """
                INSERT INTO customers
                (first_name, last_name, email, phone, address)
                VALUES (%s, %s, %s, %s, %s)
            """
            
            with connection.cursor() as cursor:
                cursor.execute(insert_query, [
                    first_name, last_name, email, phone, address
                ])
                cursor.execute("SELECT LAST_INSERT_ID()")
                customer_id = cursor.fetchone()[0]
            
            messages.success(request, 'Customer added successfully!')
            return redirect('customer_detail', pk=customer_id)
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
    # Django ORM: vehicles = Vehicle.objects.all()
    
    # Raw SQL:
    raw_query = """
        SELECT 
            v.*,
        CASE WHEN v.status = 'Available' 
        THEN 'Available' 
        ELSE 'Not Available' 
        END as availability
        FROM vehicles v
        ORDER BY v.vehicle_id
    """

    vehicles = Vehicle.objects.raw(raw_query)

    return render(request, 'dealership/vehicle/list.html', {'vehicles': vehicles})

# def vehicle_detail(request, pk):
#     # Django ORM:
#     # vehicle = get_object_or_404(Vehicle, pk=pk)
#     # transactions = Transaction.objects.filter(vehicle=vehicle)
#     # services = vehicle.service_set.all()
#     # test_drives = vehicle.testdrive_set.all()
#     # return render(request, 'dealership/vehicle/detail.html', {
#     #     'vehicle': vehicle, 
#     #     'transactions': transactions,
#     #     'services': services,
#     #     'test_drives': test_drives
#     # })

#     # Raw SQL:
#     raw_query = """
#         SELECT v.* 
#         FROM vehicles v
#         WHERE v.vehicle_id = %s
#     """
    
#     vehicles = list(Vehicle.objects.raw(raw_query, [pk]))
#     if not vehicles:
#         raise Http404("Vehicle does not exist")
#     vehicle = vehicles[0]
    
#     return render(request, 'dealership/vehicle/detail.html', {'vehicle': vehicle})

def vehicle_detail(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk)
    if request.method == 'POST':
        new_price = request.POST.get('price')
        with connection.cursor() as cursor:
            cursor.execute("UPDATE vehicle SET price = %s WHERE id = %s", [new_price, pk])
    return render(request, 'dealership/vehicle/detail.html', {'vehicle': vehicle})



def vehicle_create(request):
    if request.method == 'POST':
        form = VehicleForm(request.POST)
        if form.is_valid():
            make = form.cleaned_data['make']
            model = form.cleaned_data['model']
            year = form.cleaned_data['year']
            color = form.cleaned_data['color']
            vin = form.cleaned_data['vin']
            price = form.cleaned_data['price']
            mileage = form.cleaned_data['mileage']
            status = form.cleaned_data['status']
            
            insert_query = """
                INSERT INTO vehicles
                (make, model, year, color, vin, price, mileage, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            with connection.cursor() as cursor:
                cursor.execute(insert_query, [
                    make, model, year, color, vin, price, mileage, status
                ])

                cursor.execute("SELECT LAST_INSERT_ID()")
                vehicle_id = cursor.fetchone()[0]
            
            messages.success(request, 'Vehicle added successfully!')
            return redirect('vehicle_detail', pk=vehicle_id)
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
    with connection.cursor() as cursor:
        cursor.execute("SELECT get_employee_transaction_count(%s)", [employee.employee_id])
        row = cursor.fetchone()
    transaction_count = row[0] if row else 0
    return render(request, 'dealership/employee/detail.html', {'employee': employee, 'transaction_count': transaction_count})


def employee_create(request):
    if request.method == 'POST':
        form = EmployeeForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            phone = form.cleaned_data['phone']
            position = form.cleaned_data['position']
            hire_date = form.cleaned_data['hire_date']
            
            # MySQL insert
            insert_query = """
                INSERT INTO employees
                (first_name, last_name, email, phone, position, hire_date)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            
            with connection.cursor() as cursor:
                cursor.execute(insert_query, [
                    first_name, last_name, email, phone, position, hire_date
                ])

                cursor.execute("SELECT LAST_INSERT_ID()")
                employee_id = cursor.fetchone()[0]
            
            messages.success(request, 'Employee added successfully!')
            return redirect('employee_detail', pk=employee_id)
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
    # Django ORM:
    # transactions = Transaction.objects.all().order_by('-transaction_date')

    # Raw SQL: 
    raw_query = """
        SELECT 
            t.*, 
            c.first_name || ' ' || c.last_name as customer_name, 
            e.first_name || ' ' || e.last_name as employee_name,
            v.make || ' ' || v.model || ' ' || v.year as vehicle_name
        FROM transactions t
        LEFT JOIN customers c ON t.customer_id = c.customer_id
        LEFT JOIN employees e ON t.employee_id = e.employee_id
        LEFT JOIN vehicles v ON t.vehicle_id = v.vehicle_id
        ORDER BY t.transaction_date DESC
    """

    transactions = Transaction.objects.raw(raw_query)
    return render(request, 'dealership/transaction/list.html', {'transactions': transactions})

def transaction_detail(request, pk):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM transaction_summary_view WHERE transaction_id = %s", [pk])
        row = cursor.fetchone()
    return render(request, 'dealership/transaction/detail.html', {'transaction': row})


def transaction_create(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            # Get data from form
            customer_id = form.cleaned_data['customer'].customer_id
            employee_id = form.cleaned_data['employee'].employee_id
            vehicle_id = form.cleaned_data['vehicle'].vehicle_id
            sale_price = form.cleaned_data['sale_price']
            payment_type = form.cleaned_data['payment_type']
            status = form.cleaned_data['status']
            
            insert_query = """
                INSERT INTO transactions(
                    customer_id, 
                    employee_id, 
                    vehicle_id, 
                    transaction_date, 
                    sale_price, 
                    payment_type, status)
                VALUES (%s, %s, %s, NOW(), %s, %s, %s)
            """
            
            with connection.cursor() as cursor:
                cursor.execute(insert_query, [
                    customer_id, employee_id, vehicle_id, sale_price, payment_type, status
                ])

                cursor.execute("SELECT LAST_INSERT_ID()")
                transaction_id = cursor.fetchone()[0]
            
            messages.success(request, 'Transaction created successfully!')
            return redirect('transaction_detail', pk=transaction_id)
    else:
        form = TransactionForm()
    
    return render(request, 'dealership/transaction/form.html', {'form': form, 'title': 'Create New Transaction'})

def redirect_favicon(request):
    return redirect('/')
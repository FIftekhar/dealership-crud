from django.db import models

class Employee(models.Model):
    employee_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    position = models.CharField(max_length=50, null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    email = models.EmailField(unique=True)
    hire_date = models.DateField(null=True, blank=True)
    salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    class Meta:
        db_table = 'employees'

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Customer(models.Model):
    customer_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    email = models.EmailField(unique=True)
    address = models.TextField(null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)

    class Meta:
        db_table = 'customers'

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Vehicle(models.Model):
    STATUS_CHOICES = [
        ('Available', 'Available'),
        ('Sold', 'Sold'),
        ('Reserved', 'Reserved'),
        ('Maintenance', 'Maintenance'),
    ]

    vehicle_id = models.AutoField(primary_key=True)
    make = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    year = models.IntegerField()
    vin = models.CharField(max_length=17, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    mileage = models.IntegerField(null=True, blank=True)
    color = models.CharField(max_length=30, null=True, blank=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='Available')

    class Meta:
        db_table = 'vehicles'

    def __str__(self):
        return f"{self.year} {self.make} {self.model}"


class Transaction(models.Model):
    PAYMENT_TYPE_CHOICES = [
        ('Cash', 'Cash'),
        ('Loan', 'Loan'),
        ('Lease', 'Lease'),
    ]

    STATUS_CHOICES = [
        ('Completed', 'Completed'),
        ('Pending', 'Pending'),
        ('Canceled', 'Canceled'),
    ]

    transaction_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(Customer, null=True, on_delete=models.SET_NULL)
    employee = models.ForeignKey(Employee, null=True, on_delete=models.SET_NULL)
    vehicle = models.ForeignKey(Vehicle, null=True, on_delete=models.SET_NULL)
    transaction_date = models.DateTimeField(auto_now_add=True)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    payment_type = models.CharField(max_length=10, choices=PAYMENT_TYPE_CHOICES)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')

    class Meta:
        db_table = 'transactions'


class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('Credit Card', 'Credit Card'),
        ('Bank Transfer', 'Bank Transfer'),
        ('Check', 'Check'),
        ('Cash', 'Cash'),
    ]

    payment_id = models.AutoField(primary_key=True)
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE)
    payment_date = models.DateTimeField(auto_now_add=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)

    class Meta:
        db_table = 'payments'


class Service(models.Model):
    service_id = models.AutoField(primary_key=True)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    employee = models.ForeignKey(Employee, null=True, on_delete=models.SET_NULL)
    service_date = models.DateTimeField(auto_now_add=True)
    service_type = models.CharField(max_length=100, null=True, blank=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    notes = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'services'


class Inventory(models.Model):
    part_id = models.AutoField(primary_key=True)
    part_name = models.CharField(max_length=100)
    quantity = models.IntegerField()
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    class Meta:
        db_table = 'inventory'

    def __str__(self):
        return self.part_name


class TestDrive(models.Model):
    test_drive_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(Customer, null=True, on_delete=models.SET_NULL)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    employee = models.ForeignKey(Employee, null=True, on_delete=models.SET_NULL)
    test_drive_date = models.DateTimeField(auto_now_add=True)
    feedback = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'test_drives'

from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime

app = Flask(__name__)

class Customer:
    def __init__(self, first_name, last_name, address, phone_number, due_amount):
        self.first_name = first_name
        self.last_name = last_name
        self.address = address
        self.phone_number = phone_number
        self.total_due = due_amount
        self.payments = []  # List to store all payment details

    def add_payment(self, amount, date, method):
        """Add a payment to the customer's account and update remaining balance."""
        payment = {
            'amount': amount,
            'date': date,
            'method': method
        }
        self.payments.append(payment)
        self.total_due -= amount
        if self.total_due < 0:
            self.total_due = 0  # Ensure the total due doesn't go negative

    def update_due_amount(self, amount):
        """Set the due amount for the customer."""
        self.total_due = amount

    def update_details(self, first_name=None, last_name=None, address=None, phone_number=None):
        """Update customer details."""
        if first_name:
            self.first_name = first_name
        if last_name:
            self.last_name = last_name
        if address:
            self.address = address
        if phone_number:
            self.phone_number = phone_number

    def get_customer_info(self):
        """Display customer details including payments and balance."""
        return {
            'first_name': self.first_name,
            'last_name': self.last_name,
            'address': self.address,
            'phone_number': self.phone_number,
            'total_due': self.total_due,
            'payments': self.payments,
            'remaining_balance': self.total_due
        }

class CustomerManagementSystem:
    def __init__(self):
        self.customers = []

    def add_customer(self, first_name, last_name, address, phone_number, due_amount):
        """Add a new customer to the system."""
        customer = Customer(first_name, last_name, address, phone_number, due_amount)
        self.customers.append(customer)

    def make_payment(self, customer, payment_amount, payment_date, payment_method):
        """Record a payment for a customer."""
        customer.add_payment(payment_amount, payment_date, payment_method)

    def get_all_customers(self):
        """Get all customers."""
        return [customer.get_customer_info() for customer in self.customers]

    def update_customer(self, customer, first_name=None, last_name=None, address=None, phone_number=None):
        """Update customer details."""
        customer.update_details(first_name, last_name, address, phone_number)

    def delete_customer(self, customer):
        """Delete a customer from the system."""
        self.customers.remove(customer)

# Initialize the CustomerManagementSystem
cms = CustomerManagementSystem()

@app.route('/')
def home():
    customers = cms.get_all_customers()
    return render_template('index.html', customers=customers)

@app.route('/add_customer', methods=['POST'])
def add_customer():
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    address = request.form['address']
    phone_number = request.form['phone_number']
    try:
        due_amount = float(request.form['due_amount'])
    except ValueError:
        return "Invalid amount entered!", 400
    cms.add_customer(first_name, last_name, address, phone_number, due_amount)
    return redirect(url_for('index'))

@app.route('/make_payment/<int:customer_index>', methods=['POST'])
def make_payment(customer_index):
    if customer_index < len(cms.customers):
        payment_amount = float(request.form['payment_amount'])
        payment_date = request.form['payment_date']  # Assuming the user enters a date (e.g., YYYY-MM-DD)
        payment_method = request.form['payment_method']
        try:
            payment_date = datetime.strptime(payment_date, '%Y-%m-%d').date()  # Parse the date
            customer = cms.customers[customer_index]
            if payment_amount > customer.total_due:
                return "Payment amount exceeds due balance!", 400
            cms.make_payment(customer, payment_amount, payment_date, payment_method)
        except ValueError:
            return "Invalid date format. Please use YYYY-MM-DD.", 400
    else:
        return "Customer not found!", 404
    return redirect(url_for('index'))

@app.route('/customer/<int:customer_index>')
def customer_info(customer_index):
    if customer_index < len(cms.customers):
        customer = cms.customers[customer_index]
        return render_template('customer_info.html', customer=customer.get_customer_info())
    else:
        return "Customer not found!", 404

@app.route('/update_customer/<int:customer_index>', methods=['GET', 'POST'])
def update_customer(customer_index):
    if customer_index < len(cms.customers):
        customer = cms.customers[customer_index]
        if request.method == 'POST':
            first_name = request.form['first_name']
            last_name = request.form['last_name']
            address = request.form['address']
            phone_number = request.form['phone_number']
            cms.update_customer(customer, first_name, last_name, address, phone_number)
            return redirect(url_for('index'))
        return render_template('update_customer.html', customer=customer.get_customer_info())
    else:
        return "Customer not found!", 404

@app.route('/delete_customer/<int:customer_index>', methods=['POST'])
def delete_customer(customer_index):
    if customer_index < len(cms.customers):
        customer = cms.customers[customer_index]
        cms.delete_customer(customer)
        return redirect(url_for('index'))
    else:
        return "Customer not found!", 404

if __name__ == '__main__':
    app.run(debug=True)

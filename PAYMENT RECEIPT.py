import mysql.connector
from reportlab.platypus import SimpleDocTemplate, Table, Paragraph, TableStyle, Image
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
import datetime
from num2words import num2words

# Function to connect to MySQL
def create_db_connection():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",  
            password="Aviksql@253",  
            database="grocery_billing"
        )
        if connection.is_connected():
            print("Successfully connected to the database")
        return connection
    except mysql.connector.Error as e:
        print(f"Error: {e}")
        return None

# Function to insert customer data into the database
def insert_customer_data(connection, phone, name):
    cursor = connection.cursor()
    date_of_purchase = datetime.datetime.now()
    query = "INSERT INTO customers (phone, name) VALUES (%s, %s)"
    values = (phone,name)
    cursor.execute(query, values)
    connection.commit()
    return cursor.lastrowid  # Return the customer ID

# Function to insert item data into the database
def insert_bill_items(connection, customer_id, items):
    cursor = connection.cursor()
    for item in items:
        query = "INSERT INTO bill_items (customer_id, item_name, quantity, unit_price, total_price) VALUES (%s, %s, %s, %s, %s)"
        values = (customer_id, item[0], item[1], item[2], item[3])
        cursor.execute(query, values)
    connection.commit()

def get_user_data():
    data = []
    subtotal = 0
    tquant = 0
    n = 0
    data.append(["Item Name", "Quantity", "Unit Price", "Total Price (Rs.)"])  # Header row

    while True:
        name = input("Enter Item Name: ")
        quantity = int(input("Enter quantity: "))
        unit_price = int(input("Enter Unit Price (Rs.): "))
        cmd = input("PRESS 'E' TO END BILLING OR ANY OTHER KEY TO CONTINUE: ")
        total_price = quantity * unit_price
        data.append([name, quantity, unit_price, total_price])
        n += 1
        if cmd == 'E':
            break

    for i in range(1, n + 1):
        subtotal += data[i][3]
    for i in range(1, n + 1):
        tquant += data[i][1]
    
    discount = int(input("Enter Discount (%): "))
    CGST = int(input("ENTER CGST (%): "))
    SGST = int(input("ENTER SGST (%): "))
    
    total = subtotal - ((discount / 100) * subtotal)
    total = round(total + ((CGST / 100) * total) + ((SGST / 100) * total))
    w = num2words(total)

    data.append(["Total Number of Items:", f"{n}", "", ""])
    data.append(["Total Quantity:", f"{tquant}", "", ""])
    data.append(["Sub Total", "", "", f"{subtotal}"])
    data.append(["Discount", "", "", f"-{discount}%"])
    data.append(["CGST", "", "", f"{CGST}%"])
    data.append(["SGST", "", "", f"{SGST}%"])
    data.append(["TOTAL AMOUNT (ROUNDED)", "", "", f"{total:.2f}"])
    data.append(["TOTAL AMOUNT IN WORDS", "", "", f"{w} rupees"])

    return n, data, discount, CGST, SGST, total

# Collect customer details
cname = input("ENTER CUSTOMER NAME: ")
cphone = input("ENTER CUSTOMER MOBILE NUMBER: ")

# Get the data from the user
n, DATA, discount, CGST, SGST, total = get_user_data()

# Create the PDF document template
pdf = SimpleDocTemplate("receipt.pdf", pagesize=A4)
img = Image("cimage.jpg", 1 * inch, 1 * inch)

styles = getSampleStyleSheet()
title_style = styles["Heading2"]
title_style.alignment = 1  # Center the title

title = Paragraph("GROCERY BILL", title_style)
d = Paragraph(datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S"), title_style)
cname_para = Paragraph(cname, title_style)
cphone_para = Paragraph(cphone, title_style)

style = TableStyle([
    ("BOX", (0, 0), (-1, -1), 1, colors.black),
    ("GRID", (0, 0), (4, n), 1, colors.black),  # Grid across all rows and columns
    ("BACKGROUND", (0, 0), (3, 0), colors.gray),
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
    ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
])

table = Table(DATA)
table.setStyle(style)

# Build the PDF
pdf.build([img, title, d, cname_para, cphone_para, table])

# Connect to the database and store customer and item data
connection = create_db_connection()
if connection:
    customer_id = insert_customer_data(connection, cname, cphone)
    
    # Extract individual items from DATA
    items = [row for row in DATA[1:n+1]]  # Ignore the header row and summary rows
    insert_bill_items(connection, customer_id, items)

    connection.close()


"""# imports module 
from reportlab.platypus import SimpleDocTemplate, Table, Paragraph, TableStyle 
from reportlab.lib import colors 
from reportlab.lib.pagesizes import A4 
from reportlab.lib.styles import getSampleStyleSheet 
import datetime

def get_user_data():    # data which we are going to display as tables 
    data = []
    n=int(input("ENTER THE NUMBER OF ITEMS:"))
    subtotal=0
    tquant=0

    data.append(["Item Name", "Quantity", "Unit Price", "Total Price (Rs.)"])       # Header row

    for i in range(n):      # Collecting multiple entries for the table
        name = input("Enter Item Name: ")
        quantity = int(input("Enter quantity: "))
        unit_price = int(input("Enter Unit Price (Rs.): "))
        totalprice = quantity * unit_price
        data.append([name, quantity, unit_price,totalprice])

    for i in range(1,n+1):      # Adding Subtotal, Discount, and Total rows
        subtotal+=data[i][3]
    discount = int(input("Enter Discount (Rs.): "))
    for i in range(1,n+1): 
        tquant+= data[i][1]
    CGST = int(input("ENTER CGST: "))
    SGST = int(input("ENTER SGST: "))
    total = subtotal-((discount/100)*subtotal)
    total = total + ((CGST/100)*total) + ((SGST/100)*total)
    data.append(["Total Quantity:", f"{tquant}", "", ""])
    data.append(["Sub Total", "", "", f"{subtotal}"])
    data.append(["Discount", "", "", f"-{discount}%"])
    data.append(["CGST", "", "", f"-{CGST}%"])
    data.append(["SGST", "", "", f"-{SGST}%"])
    data.append(["TOTAL AMOUNT", "", "", f"-{total}%"])
    return data

DATA = get_user_data()  # Collect data from user

pdf = SimpleDocTemplate("receipt.pdf", pagesize=A4) # Creating a Base Document Template of page size A4

styles = getSampleStyleSheet()  # Standard stylesheet defined within ReportLab

title_style = styles["Heading1"]    # Fetching the style of top-level heading (Heading1)
title_style.alignment = 1

# Creating the paragraph with the heading text and date & time and passing the styles of it
title = Paragraph("GROCERY BILL", title_style)
d=datetime.datetime.now()
d=Paragraph(d.strftime("%d/%m/%Y, %H:%M:%S"))
style = TableStyle  # Creates a Table Style object and defines the styles row-wise
(
    [
        ("BOX", (0, 0), (-1, -1), 1, colors.black),
        ("GRID", (0, 0), (4, 4), 1, colors.black),
        ("BACKGROUND", (0, 0), (3, 0), colors.gray),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
    ]
)
table = Table(DATA, style=style)    # Creates a table object and passes the style to it
pdf.build([title,table])    # Final step which builds the actual PDF putting together all the elements
"""

"""
# imports module
from reportlab.platypus import SimpleDocTemplate, Table, Paragraph, TableStyle, Image
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
import datetime
from num2words import num2words

def get_user_data():    # data which we are going to display as tables
    data = []
    subtotal = 0
    tquant = 0
    n=0
    data.append(["Item Name", "Quantity", "Unit Price", "Total Price (Rs.)"])  # Header row
    
    while(True):  # Collecting multiple entries for the table
        name = input("Enter Item Name: ")
        quantity = int(input("Enter quantity: "))
        unit_price = int(input("Enter Unit Price (Rs.): "))
        cmd=input("PRESS 'E' TO END BILLING OR ANY OTHER KEY TO CONTINUE: ")
        totalprice = quantity * unit_price
        data.append([name, quantity, unit_price, totalprice])
        n+=1
        if cmd=='E':
            break
        
    for i in range(1, n+1):  # Calculating subtotal
        subtotal += data[i][3]
    for i in range(1, n+1): # Calculating quantity
        tquant += data[i][1]
    discount = int(input("Enter Discount (%): "))    
    CGST = int(input("ENTER CGST (%): "))
    SGST = int(input("ENTER SGST (%): "))
    
    # Calculating total with discounts and taxes
    total = subtotal - ((discount / 100) * subtotal)
    total = round(total + ((CGST / 100) * total) + ((SGST / 100) * total))
    w=num2words(total)
    # Adding additional rows to the table
    data.append(["Total Number of Items:", f"{n}", "", ""])
    data.append(["Total Quantity:", f"{tquant}", "", ""])
    data.append(["Sub Total", "", "", f"{subtotal}"])
    data.append(["Discount", "", "", f"-{discount}%"])
    data.append(["CGST", "", "", f"{CGST}%"])
    data.append(["SGST", "", "", f"{SGST}%"])
    data.append(["TOTAL AMOUNT (ROUNDED)", "", "", f"{total:.2f}"])  # Display the actual total value
    data.append(["TOTAL AMOUNT IN WORDS", "", "", f"{w} rupees"])
    return n,data

#n = int(input("ENTER THE NUMBER OF ITEMS:"))
cname=input("ENTER CUSTOMER NAME: ")
cphone= input("ENTER CUSTOMER MOBILE NUMBER: ")
# Get the data from the user
n,DATA = get_user_data()

# Create the PDF document template
pdf = SimpleDocTemplate("receipt.pdf", pagesize=A4)
img = Image("cimage.jpg", 1 * inch, 1 * inch)
# Create a stylesheet for the document
styles = getSampleStyleSheet()

# Set the title style (Heading1)
title_style = styles["Heading2"]
title_style.alignment = 1  # Center the title

# Create the title paragraph and the date paragraph
title = Paragraph("GROCERY BILL", title_style)
d = Paragraph(datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S"),title_style)
cname = Paragraph(cname, title_style)
cphone = Paragraph(cphone, title_style)
# Create the table style with proper formatting
style = TableStyle([
    ("BOX", (0, 0), (-1, -1), 1, colors.black),
    ("GRID", (0, 0), (4, n), 1, colors.black),  # Grid across all rows and columns
    ("BACKGROUND", (0, 0), (3, 0), colors.gray),  # Header background
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),  # Header text color
    ("ALIGN", (0, 0), (-1, -1), "CENTER"),  # Center all table text
    ("BACKGROUND", (0, 1), (-1, -1), colors.beige),  # Background for the rest of the table
])

# Create the table with the data and apply the style
table = Table(DATA)
table.setStyle(style)  # Apply the style to the table

# Build the PDF by putting together the title, date, and the table
pdf.build([img,title, d,cname,cphone,table])

"""

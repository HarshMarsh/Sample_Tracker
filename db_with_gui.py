
'''
#modules to install before running:
pip install firebase_admin
pip install json
pip install qrcode
pip install pyserial
#install adafruit-circuitpython-thermal-printer
#pip install tkinter
pip install tk
pip instal pytz
pip3 install pyrebase4
#? pip install python-decouple
pip install python-dotenv
'''

#user interface imports:
import tkinter as tk
from tkinter import *
from tkinter import messagebox
##########################################################Stuff for setting up FireBase##################################################################################
# pip3 install adafruit-circuitpython-thermal-printer
# Import database module.
import firebase_admin
from firebase_admin import db
from firebase_admin import credentials
import json

#imports for label printer:
import serial
import adafruit_thermal_printer

#Imports for recording check out/in times:
import datetime
import pytz
import pyrebase

# Email imports
import os
from dotenv import load_dotenv, find_dotenv

sender = os.getenv("sender_email")
#get email password from .env file
load_dotenv(find_dotenv())
password = os.getenv("EMAIL_PASSWORD")


firebaseConfig = {'apiKey':  os.getenv('apiKey'),
  'authDomain':  os.getenv("authDomain" ),
  'databaseURL':  os.getenv('databaseURL' ),
  'projectId':  os.getenv( 'projectId' ),
  'storageBucket':  os.getenv('storageBucket'),
  'messagingSenderId':  os.getenv('messagingSenderId'),
  'appId':  os.getenv('appId'),
  'measurementId':  os.getenv('measurementId')}

firebase= pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()

ThermalPrinter = adafruit_thermal_printer.get_printer_class(2.69)
uart = serial.Serial("COM6", baudrate=9600, timeout=3000)
printer = ThermalPrinter(uart)

# Path to the JSON file containing your service account credentials
#cred_obj = credentials.Certificate(
#    "C://Users//marsh//PycharmProjects//database_project//product-tracker-bfc30-firebase-adminsdk-gerds-17e0a62db1.json")
cred_obj = credentials.Certificate(
    os.getenv("CRED_CERT"))
# Initialize the Firebase Admin SDK with the credentials and the database URL
default_app = firebase_admin.initialize_app(cred_obj, {
    "databaseURL":  os.getenv("databaseURL")
})
# Get a database reference for the index number of sample ID
index_ref = db.reference('/sample_index')
# This is a database reference for the path we write sample info to
info_ref = db.reference("/sample_info")


# list of values from to collect result data from sample info LabelFrame
result_entry_variables = []
result_labels= []
result_entries = []

# list of values from to collect sample info data (email, type, etc.) from db LabelFrame
sample_info_labels= []


#this variable makes a state to know if it is ok to delete the sample info window
updating = False
is_manager = False


def get_db_data(id_index):
    query_result = info_ref.order_by_child('id').equal_to(id_index).get()
    return query_result
def display_delete_win():
    delete_frame = tk.Frame(window)
    delete_frame.grid(row = 1,column = 0)


    delete_window = Toplevel(window)
    # Set the child window's position and size
    delete_window.geometry(f"{width}x{height}+{x}+{y}")

    # Place the toplevel window at the top
    delete_window.wm_transient(window)
    delete_lbl = tk.Label(delete_window, text = "Enter a sample ID to delete: ")
    delete_lbl.pack()
    id_to_delete = tk.StringVar()
    delete_entry = tk.Entry(delete_window,textvariable= id_to_delete)
    delete_entry.pack()


    delete_btn = tk.Button(delete_window, text = "delete",command = lambda: delete_sample(int(id_to_delete.get())))
    delete_btn.pack()
def delete_sample(id_to_delete):

    try:
        # get possible matches according to id number argument
        query_result = info_ref.order_by_child('id').equal_to(id_to_delete).get()
        #index through all the possible matches (should only be one since ID is unique)
        for product_id, product_data in query_result.items():

                # make a refernce to the product to delete
                ref = db.reference("/sample_info/"+ product_id)
                #attempt to delete it
                try:
                    ref.delete()
                    print("Node deleted successfully.")
                    tk.messagebox.showinfo('Node deleted', 'Sample successfully deleted from database')
                except Exception as e:
                    tk.messagebox.showerror('Database error', 'Error: Node could not be deleted')
    except Exception as e:
        tk.messagebox.showerror('Database error', 'Error: The sample ID you chose is not in the database')

def display_label_window():
    print_label_window = Toplevel(window)


    # Set the child window's position and size
    print_label_window.geometry(f"{width}x{height}+{x}+{y}")

    # Place the toplevel window at the top
    print_label_window.wm_transient(window)
    print_lbl = tk.Label(print_label_window, text = "Enter a sample ID to print: ")
    print_lbl.pack()
    id_to_print = tk.IntVar()
    print_entry = tk.Entry(print_label_window,textvariable= id_to_print)
    print_entry.pack()

    print_label_btn = tk.Button(print_label_window, text = "print",command = lambda: print_label_data(id_to_print.get()))
    print_label_btn.pack()

def print_label_data(id_to_print):
    db_data = get_db_data(id_to_print)
    for product_id, product_data in db_data.items():
        code = format_barcode(product_data.get('id'))
        print_id_barcode(code)

        printer.print("Product ID: " + str(product_data.get("id")))
        printer.print("Type:" + str(product_data.get('kind')))
        printer.print("Customer name:" + str(product_data.get('name')))
        printer.print("Customer contact:" + str(product_data.get('email')))
        printer.print("Customer address: " + str(product_data.get('address')))
        printer.print("Tests: " + str(product_data.get('tests')))
        printer.feed(1)  # Feed some lines after printing

# add leading zeros to adhere to EAN13 format
def format_barcode(in_num):
    characters_to_add = 12 - len(str(in_num))
    barcode_data = '0' * characters_to_add + str(in_num)
    return barcode_data


def print_id_barcode(barcode_data):
    printer.print_barcode(barcode_data, printer.CODE128)
    printer.feed(1)  # Feed some lines after printing


# This function retrieves the value of a child node. The main purpose is for getting the ID index
def get_child_value():
    # Read the data at the posts reference (this is a blocking operation)
    child_data = index_ref.get("ID")
    print(child_data[0]['ID'])
    return child_data


# This function is for incrementing the child value of a node, it is mainly for updating the id index after the current id has been assigned to a sample

def increment_child_value(child_data):
    # Update the 'ID' value to 2
    new_val = child_data[0]['ID'] + 1
    index_ref.update({'ID': new_val})
def create_new_sample():
    #entries for sort, name, contact, address, tests

    field_frame = tk.LabelFrame(frame, text = "fields")
    field_frame.grid(row=0, column=2)

    new_id = get_child_value()
    increment_child_value(new_id)

    sort_lbl = tk.Label(field_frame,text = "Kind:")
   # sort_lbl.grid(row=0, column=0)
    sort_lbl.pack()

    sort_var = tk.StringVar()
    sort_entry = tk.Entry(field_frame,textvariable= sort_var)
  #  sort_entry.grid(row=1, column=0)
    sort_entry.pack()

    name_lbl = tk.Label(field_frame,text = "Name:")
  #  name_lbl.grid(row=2, column=0)
    name_lbl.pack()

    name_var = tk.StringVar()
    name_entry = tk.Entry(field_frame,textvariable= name_var)
 #   name_entry.grid(row=3, column=0)
    name_entry.pack()

    email_lbl = tk.Label(field_frame, text="email:")
  #  email_lbl.grid(row=4, column=0)
    email_lbl.pack()

    email_var = tk.StringVar()
    email_entry = tk.Entry(field_frame, textvariable=email_var)
#    email_entry.grid(row=5, column=0)
    email_entry.pack()

    address_lbl = tk.Label(field_frame, text="address:")
#    address_lbl.grid(row=6, column=0)
    address_lbl.pack()

    address_var = tk.StringVar()
    address_entry = tk.Entry(field_frame, textvariable=address_var)
#    address_entry.grid(row=7, column=0)
    address_entry.pack()

    test_lbl = tk.Label(field_frame, text="Tests ordered:")
#    test_lbl.grid(row=8, column=0,sticky="ew")
    test_lbl.pack()

    test_list_var = tk.StringVar()
    test_list_entry = tk.Entry(field_frame,textvariable= test_list_var)
#    test_list_entry.grid(row=9, column=0,sticky="ew")
    test_list_entry.pack()



    options = [
        "Type-1",
        "Type-2",
        "Type-3",
        "Type-4"
    ]

    selected_test = tk.StringVar()
    selected_test.set("Type-1")
    dropdown = OptionMenu(field_frame,selected_test, *options)
#    dropdown.grid(row=10, column=0,sticky="ew")
    dropdown.pack(side = LEFT)


    tests = []
    add_test_btn = tk.Button(field_frame,text = "Add Test",command = lambda:add_test_list(tests, test_list_entry,selected_test.get()))
#    add_test_btn.grid(row=10, column=1,padx = 20,sticky="ew")
    add_test_btn.pack(side = LEFT, padx = 10)

    save_btn = tk.Button(field_frame, text = "Save",command = lambda :save_new_sample_db(new_id,sort_var.get(),email_var.get(),name_var.get(),address_var.get(),tests,field_frame))
#    save_btn.grid(row=11, column=0,sticky="ew")
    save_btn.pack(side = RIGHT)


def write_sample_db():
    with open("sample.json", "r") as f:
        file_contents = json.load(f)

    for key, value in file_contents.items():
        info_ref.push().set(value)
    f.close()

def save_new_sample_db(new_id,sort,contact,name,address,tests,field_frame):
    New_Sample = Sample(new_id[0]['ID'], sort, contact, name, address, tests)
    New_Sample.save_to_file()
    write_sample_db()
    field_frame.grid_forget()

def make_test_obj(tests):
    # make an array for the object we will create. This will be returned to caller
    test_objects = []
    # loop through the input text, and classify which test type it corresponds to
    for element in tests:
        # one the type is found, make an object of the correct type
        if element == 'Type-1':
            obj = Test_type_one()
        elif element == "Type-2":
            obj = Test_type_two()
        else:
            obj = Test()
        # append the created object to the array and return to the caller
        test_objects.append(obj.test_dict)
    return test_objects
class Sample:
    def __init__(self, ID, Type_in, customer_email, customer_name, customer_address, ordered_tests):
        print("Sample created")
        # Create an arrow of test objects corresponding to the types of test ordered
        sample_test_objects = make_test_obj(ordered_tests)
        self.dict = {"id": ID, "kind": Type_in, "name": customer_name, "email": customer_email,
                     "address": customer_address, "techs": [], "tests": sample_test_objects}
        self.main_dict = {"id_num": self.dict}

    def save_to_file(self):
        json_object = json.dumps(self.main_dict, indent=4)
        # Writing to sample.json
        with open("sample.json", "w") as outfile:
            outfile.write(json_object)
        outfile.close()


# make a test classes that can take on different results fields depending on the type of test chosen
class Test:
    def __init__(self):
        print("generic test")
        test_dict = {"tech_name": "None", "in_time": "None", "out_time": "None"}

    def print_test_data(self):
        print("empty test")


class Test_type_one(Test):
    test_dict = {"type": 1, "tech_name": "None", "in_time": "None", "out_time": "None", "weight1(g)": 0, "weight2(g)": 0}

class Test_type_two(Test):
    test_dict = {"type": 2, "tech_name": "None", "in_time": "None", "out_time": "None", "percent(%)": 0}




"""
-add_test_list is used when new sample is being entered and manager is adding the list of tests that should be done to a certain sample
-This function takes in the array of existing tests, the tkinter entry on the new sample window, and the new string whose contents mark the type of the new test to be added.
- The tkinter entry from the new sample window is passed in because the new test name is appended to it when it is added so that user knows test was successfully added.
- This function checks to ensure that one type of test is not added twice
"""
def add_test_list(test, test_list_entry,new_element):
    print(test)
    if new_element in test:
        tk.messagebox.showerror('Sample Creation Error', 'Error: This test has already been added to the sample!')
    else:
        test.append(new_element)
        new_element = new_element + ','
        test_list_entry.insert("end",new_element)


def check_in(sample_id, index_test,name_entry):
    ref = db.reference("/sample_info")
    query_result = ref.order_by_child('id').equal_to(sample_id).get()
    for product_id, product_data in query_result.items():
        #insert the name of the technician who already checked the sample out into the tech name entry
        name_entry.insert(0,product_data["tests"][index_test]['tech_name'])
        #if the sample HAS already been checked out for this test AND the sample HAS NOT been checked in, then get the current time and save it in the check-in field
        if product_data.get('tests')[index_test]['out_time'] != "None" and  product_data.get('tests')[index_test]['in_time'] == "None":
            current_datetime = datetime.datetime.now(pytz.timezone('America/Los_Angeles'))
            formatted_datetime = current_datetime.strftime("%Y-%m-%d %I:%M %p")
            ref.child(product_id).update({"tests/" + str(index_test) + "/in_time": formatted_datetime})
        else:
            tk.messagebox.showerror('Python Error', 'Error: Sample was already checked in OR sample never checked out')


"""
check_out() is a function that allowes a technician to record the time the started working on a specific test for that sample.
"Checking out" is used in the same way as one would do with a book at a library.
The main requirements for checking a sample out is that:
    1) No other technicians already checked the sample out for this test
    2) The technician provided their name when checking the sample out
"""
def check_out(id_to_search, index_test,name):
    search_ref = db.reference("/sample_info")
    query_result = search_ref.order_by_child('id').equal_to(id_to_search).get()
    for product_id, product_data in query_result.items():

        if name == "":
            tk.messagebox.showerror('Python Error', "Error: Must enter a tech's name to check out")


        ### CHECKING IF IN AND OUT CHECKS MATCH BEFORE ALLOWING USER TO PROCEED
       #make two varaibles to count the in and out times, to ensure sample is not already checked out before letting someone else check out
        in_checks = 0
        out_checks  = 0
        '''
        index through all the test on the sample and check if the number of check out's matches the number of check in's.
        If they match, allow for the check out, if they dont match, make an error window and do nothing.
        '''
        for keys in enumerate(product_data.get('tests')):
            if (keys[1]["out_time"]) != "None":
                out_checks = out_checks +1

            if (keys[1]["in_time"]) != "None":
                in_checks = in_checks +1
        if out_checks != in_checks:
            tk.messagebox.showerror('Python Error', 'Error: Sample not checked back in')
        else:
            print("Checked successfully")

        ### CHECK IF A TECH HAS ALREADY CHECK THIS SAMPLE OUT BEFORE ALLOWING USER TO PROCEED
        if product_data.get('tests')[index_test]['tech_name'] == "None":
            search_ref.child(product_id).update({"tests/" + str(index_test) + "/tech_name": name})
           # print(product_data["tests"][0]['tech_name'])

            current_datetime = datetime.datetime.now(pytz.timezone('America/Los_Angeles'))
            formatted_datetime = current_datetime.strftime("%Y-%m-%d %I:%M %p")
            search_ref.child(product_id).update({"tests/" + str(index_test) + "/out_time": formatted_datetime})
        else:
            tk.messagebox.showerror('Python Error', 'Error: This sample has already been checked out for this test')


'''
fill_samle_info() is called when a tech is pulling up a sample to do something such as update test results, and they need to see
the info related to the sample such as the type of sample, id number, and customer's details. This can be helpful when a tech wants
to ensure they have the correct sample in their hands

sample info frame is passed in because the sample details are written to it after retrieval from the database
'''
def fill_sample_info(sample_id, sample_info_frame):
    ref = db.reference("/sample_info")
    query_result = ref.order_by_child('id').equal_to(sample_id).get()
    # Loop through the query result (should contain only one product)
    for product_id, product_data in query_result.items():
       # print("customer address is: ",product_data['address'])
        #info keys are the keys to the dictionary data that needs to be printed
        info_keys =['kind','id','name',"email","address"]

        #for each info key, retrieve it from db, and put it into the sample_info window
        for i in range(len(info_keys)):
            label_text = info_keys[i] + ": "+ str(product_data[info_keys[i]])
            label = tk.Label(sample_info_frame, text = label_text)
            sample_info_labels.append(label)
            label.pack()

"""
fill_results_window() is called when a technician has performed a test on a sample and wants to record the results into the database.
This function needs the following arguments:
    -sample id: used for finding this specific sample in the sample_info branch of the db
    -test_index: this gives the specific test that is being looked at 
    - The results_info_frame, update_btn, sample_info_frame as these all need to be removed from the screen once this function
      is trigerred
"""
def fill_results_window(sample_id,test_index,result_info_frame,update_btn,sample_info_frame):
    #write the sample info to the screen for verification purposes.
    fill_sample_info(sample_id,sample_info_frame)

    global updating
    if updating== False:

        ref = db.reference("/sample_info")
        query_result = ref.order_by_child('id').equal_to(sample_id).get()
        # Loop through the query result (should contain only one product)
        for product_id, product_data in query_result.items():
            #Make an array of the data we dont want to update in this function
            exclude_keys = ["type", "in_time", "out_time", "tech_name"]

            #retrieve the data for the specific test in question
            test_data = product_data['tests'][test_index]  # Get the test data at the specified index

            #go through all the indexes of the return dictionary for the specific test and make labels and entries if it is not one of the excluded fields
            for key, value in test_data.items():  # Use .items() to iterate through key-value pairs
                if key not in exclude_keys:

                    # Make a label with text according to the number of field
                    label = tk.Label(result_info_frame, text=key)
                    result_labels.append(label)
                    label.pack()

                    field_var = tk.IntVar()
                    entry = tk.Entry(result_info_frame, textvariable=field_var)

                    result_entry_variables.append(field_var)
                    result_entries.append(entry)
                    entry.pack()

        update_btn.pack()
        # use "updating" as a status variable to say that we are in the processing of adding changes to the database
        updating = True


"""
save_test_results_db() is a function triggered ones a technician enters the test results into the "Test Results" frame and hits the "update" update.
This function will get the data from all the entries and save it into the respective places in the database
"""
def save_test_result_db(sample_id,test_index, update_btn):
    global updating

    #get the results from the entry fields:
    result_data = []
    ref = db.reference("/sample_info")
    query_result = ref.order_by_child('id').equal_to(sample_id).get()
    # Loop through the query result (should contain only one product)
    for product_id, product_data in query_result.items():

        num_fields = len(product_data.get('tests')[test_index]) - 4
        for i in range(num_fields):
            result_data.append(result_entry_variables[i].get())

        exclude_keys = ["type", "in_time", "out_time", "tech_name"]
        test_data = product_data['tests'][test_index]  # Get the test data at the specified index
        count = 0
        for key, value in test_data.items():  # Use .items() to iterate through key-value pairs
            if key not in exclude_keys:
                new_test_val = float(result_data[count])
                ref.child(product_id).update({"tests/" + str(test_index) + "/" + key: new_test_val})
                count = count + 1

    for i in range(len(result_entries)):
        result_labels[i].destroy()
        result_entries[i].destroy()
        update_btn.pack_forget()
    result_entries.clear()
    result_labels.clear()

    for i in range(len(sample_info_labels)):
        sample_info_labels[i].destroy()
    sample_info_labels.clear()



    updating = False

def output_result():
    info_frame = tk.LabelFrame(frame, text = "sample info QC check:")
    info_frame.grid(row=0, column=2)

    # child window
    QC_window = Toplevel(window)
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    width = 200
    height = 100
    # Calculate the position of the child window
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2

    # Set the child window's position and size
    QC_window.geometry(f"{width}x{height}+{x}+{y}")

    # Place the toplevel window at the top
    QC_window.wm_transient(window)

    QC_label = tk.Label(QC_window, text="For which sample would you like to check the results?")
    QC_label.pack()

    sample_id = tk.StringVar()
    sample_num_entry = tk.Entry(QC_window, textvariable= sample_id)
    sample_num_entry.pack()



    enter_btn = tk.Button(QC_window, text="Enter", command= lambda: fill_sample_info(int(sample_id.get()),info_frame))
    enter_btn.pack()
def enter_manager_mode(child_window):
     display_login(child_window)
'''
The login function is used to authenticate users attempting to access the protected
functions such as adding and deleting a sample.
'''
def display_login(child_window):
    ########################################### CHILD WINDOW  ###################################################
    # child window
    login_window = Toplevel(window)
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    width = 200
    height = 100
    # Calculate the position of the child window
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2

    # Set the child window's position and size
    login_window.geometry(f"{width}x{height}+{x}+{y}")

    # Place the toplevel window at the top
    login_window.wm_transient(window)

    login_label = tk.Label(login_window, text="Which mode would you like to enter?")
    login_label.pack()

    username_var = tk.StringVar()
    username = tk.Entry(login_window, textvariable= username_var)
    username.pack()

    password_var = tk.StringVar()
    password = tk.Entry(login_window, textvariable= password_var,show="*")
    password.pack()

    enter_btn = tk.Button(login_window, text="Login", command= lambda: login(username_var.get(),password_var.get(),login_window,child_window))
    enter_btn.pack()


    ###########################################################################################################################
"""
login() function is called when a user enters manager mode. The systems prompts the user to login using credentials that are stored in the database
authentication section.
"""
def login(email, password,login_window,child_window):
  logged_in = False
  try:
    login = auth.sign_in_with_email_and_password(email, password)
    print("Successfully logged in!")
    tk.messagebox.showinfo('Login', 'Successfully logged in')
    display_manager_view()
    logged_in = True
  except:
      print("login failed")
      tk.messagebox.showerror('Login', 'Login failed: Invalid email or password')
  if logged_in:
      login_window.destroy()
      child_window.withdraw()
      is_manager = True

def display_manager_view():
   button_frame = tk.LabelFrame(frame,text = "Functions:")
   button_frame.grid(row=0, column=0, padx=20, pady=0, sticky="w")

   create_btn = tk.Button(button_frame, text = "Create New\nSample",command = create_new_sample)
   create_btn.pack()

   delete_btn = tk.Button(button_frame, text  = "Delete Sample",command = display_delete_win)
   delete_btn.pack(padx=20,pady = 20)

   print_lbl_btn = tk.Button(button_frame, text = "Print Sample\nLabel",command = display_label_window)
   print_lbl_btn.pack(padx = 20,  pady = 10)

   push_result_btn = tk.Button(button_frame,text = "Push Result", command = output_result)
   push_result_btn.pack(padx = 20,  pady = 10)
def enter_production_mode(child_window):

    child_window.withdraw()

    welcome_label.grid_forget()
    manager_btn.grid_forget()
    production_btn.grid_forget()
    child_window.destroy()

    label_frame = tk.LabelFrame(frame, text="Working Sample")
    label_frame.grid(row=0, column=0, padx=20, pady=5, sticky="W")  # Use "sticky" to align to the left (west)

    id_lbl = tk.Label(label_frame, text="Sample ID number:")
    id_lbl.grid(row=0, column=0)

    sample_id_var = tk.IntVar()
    id_entry = tk.Entry(label_frame, textvariable=sample_id_var)
    id_entry.grid(row=0, column=1)

    name_lbl = tk.Label(label_frame, text="Enter tech name:")
    name_lbl.grid(row=1, column=0)

    tech_name = tk.StringVar()
    name_entry = tk.Entry(label_frame, textvariable=tech_name)
    name_entry.grid(row=1, column=1)

    index_lbl = tk.Label(label_frame, text="Enter test index: ")
    index_lbl.grid(row=2, column=0)
    test_index = tk.IntVar()
    index_entry = tk.Entry(label_frame, textvariable=test_index)
    index_entry.grid(row=2, column=1)

    # Create and configure a button frame if needed
    button_frame = tk.LabelFrame(frame, text="Actions:")
    button_frame.grid(row=1, column=0, padx=20, pady=0, sticky="w")

    result_info_frame = tk.LabelFrame(frame, text="Test Results:")
    result_info_frame.grid(row=0, column=1, padx=20, pady=0)

    sample_info_frame = tk.LabelFrame(frame, text="Sample Info:")
    sample_info_frame.grid(row=0, column=2, padx=20, pady=0)

    ex_lbl = tk.Label(result_info_frame)
    ex_lbl.pack()

    results_btn = tk.Button(button_frame, text="Enter Results",
                            command=lambda: fill_results_window(sample_id_var.get(), test_index.get(),result_info_frame,update_btn,sample_info_frame))
    results_btn.grid(row=0, column=0, padx=5, pady=5)

    out_btn = tk.Button(button_frame, text="Check Out",
                        command=lambda: check_out(sample_id_var.get(), test_index.get(), tech_name.get()))
    out_btn.grid(row=0, column=2, padx=5, pady=5)

    in_btn = tk.Button(button_frame, text="Check In", command=lambda: check_in(sample_id_var.get(), test_index.get(),name_entry))
    in_btn.grid(row=0, column=3, padx=5, pady=5)

    update_btn = tk.Button(result_info_frame, text="Update",
                           command=lambda: save_test_result_db(sample_id_var.get(), test_index.get(),update_btn))


##################Set up the main window#######################

window = tk.Tk()
window.title("Sample Tracker")
window.geometry("1000x900")
width = 1000
height = 900
screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()
# Calculate the position of the child window
x = (screen_width - width) // 2
y = (screen_height - height) // 2

# Set the child window's position and size
window.geometry(f"{width}x{height}+{x}+{y}")
frame = tk.Frame(window)
frame.grid(row = 0, column = 0)


########################################### CHILD WINDOW  ###################################################
#child window
child_window = Toplevel(window)
screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()

width = 200
height = 100
# Calculate the position of the child window
x = (screen_width - width) // 2
y = (screen_height - height) // 2

# Set the child window's position and size
child_window.geometry(f"{width}x{height}+{x}+{y}")

# Place the toplevel window at the top
child_window.wm_transient(window)

welcome_label = tk.Label(child_window, text = "Which mode would you like to enter?")
welcome_label.pack()
# CHANGE FUNNCTION TO : "command= lambda:enter_manager_mode(child_window)"
manager_btn = tk.Button(child_window, text = "Enter Manager Mode",command= display_manager_view)
manager_btn.pack()

production_btn = tk.Button(child_window, text = "Enter Production Mode",command = lambda:enter_production_mode(child_window))
production_btn.pack()
###########################################################################################################################


#child_window.mainloop()
window.mainloop()
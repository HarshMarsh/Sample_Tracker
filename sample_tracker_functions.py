
##########################################################Stuff for setting up FireBase##################################################################################
# pip3 install adafruit-circuitpython-thermal-printer
# Import database module.
import os
from dotenv import load_dotenv, find_dotenv
#user interface imports:
import tkinter as tk
from tkinter import *
from tkinter import messagebox
import pyrebase
from firebase_admin import credentials
import firebase_admin
from firebase_admin import db
import json

#imports for label printer:
import serial
import adafruit_thermal_printer

#Imports for recording check out/in times:
import datetime
import pytz

#email stuff:
import ssl
import smtplib
sender = 'sampletracker2023@gmail.com'
receiver = "marshallfgarrett5@gmail.com"



ThermalPrinter = adafruit_thermal_printer.get_printer_class(2.69)
uart = serial.Serial("COM6", baudrate=9600, timeout=3000)
printer = ThermalPrinter(uart)



# list of values from to collect result data from sample info LabelFrame
result_entry_variables = []
result_labels= []
result_entries = []

# list of values from to collect sample info data (email, type, etc.) from db LabelFrame
sample_info_labels= []

def delete_sample(id_to_delete):
    try:
        query_result = db.reference("/sample_info").order_by_child('id').equal_to(id_to_delete).get()
        for product_id, product_data in query_result.items():
            ref = db.reference("/sample_info/" + product_id)
            try:
                ref.delete()
                print("Node deleted successfully.")
                tk.messagebox.showinfo('Node deleted', 'Sample successfully deleted from database')
            except Exception as e:
                tk.messagebox.showerror('Database error', 'Error: Node could not be deleted')
    except Exception as e:
        tk.messagebox.showerror('Database error', 'Error: The sample ID you chose is not in the database')

def get_db_data(id_index):
    query_result = db.reference("/sample_info").order_by_child('id').equal_to(id_index).get()
    return query_result


def fill_sample_info(sample_id, sample_info_frame,mode):
    ref = db.reference("/sample_info")
    query_result = ref.order_by_child('id').equal_to(sample_id).get()
    # Loop through the query result (should contain only one product)
    email_address = ""
    test_data = {}
    for product_id, product_data in query_result.items():
       # print("customer address is: ",product_data['address'])
        #info keys are the keys to the dictionary data that needs to be printed
        info_keys =['kind','id','name',"email","address"]
        email_address = product_data["email"]
        test_data = product_data["tests"]
        #for each info key, retrieve it from db, and put it into the sample_info window
        for i in range(len(info_keys)):
            label_text = info_keys[i] + ": "+ str(product_data[info_keys[i]])
            label = tk.Label(sample_info_frame, text = label_text)
           # sample_info_labels.append(label)
            label.pack()
    if mode == 1:
        email_btn = tk.Button(sample_info_frame, text= "email results",command= lambda:email_client_results(email_address,test_data))
        email_btn.pack()

def email_client_results(email_addrr,test_data):
    # get email password from .env file
    load_dotenv(find_dotenv())
    password = os.getenv("EMAIL_PASSWORD")
    sender = os.getenv("sender_email")
    receiver = email_addrr

    print(email_addrr)
    greeting = "Hello valued customer,\nYour test results are in!\n"
    body = ""
    ending = "\n\nThanks for using our facility,\nSample tracker"
    for i in range(len(test_data)):
        body = body + "\nResults for test " + str(i)
        excluded_keys = ["in_time","out_time","tech_name","type"]
        body = body + "\ntype:" + str(test_data[i]["type"])
        for key,value in test_data[i].items():

            if key not in excluded_keys:
                body = body + "\n" + key + ": "+ str(value)
    final_text = greeting + body + ending

    smtp_port = 587  # Standard secure SMTP port
    smtp_server = "smtp.gmail.com"  # Google SMTP Server

    # Create context
    simple_email_context = ssl.create_default_context()

    try:
        # Connect to the server
       # print("Connecting to server...")
        TIE_server = smtplib.SMTP(smtp_server, smtp_port)
        TIE_server.starttls(context=simple_email_context)
        TIE_server.login(sender, password)
     #   print("Connected to server :-)")

        # Send the actual email
       # print()
       # print(f"Sending email to - {receiver}")
        TIE_server.sendmail(sender, receiver, final_text)
       # print(f"Email successfully sent to - {receiver}")

    # If there's an error, print it out
    except Exception as e:
        print(e)

    # Close the port
    finally:
        TIE_server.quit()
def fill_results_window(sample_id,test_index,result_info_frame,update_btn,sample_info_frame):
    #write the sample info to the screen for verification purposes.
    fill_sample_info(sample_id,sample_info_frame,0)

  #  global updating
   # if updating== False:

    ref = db.reference("/sample_info")
    query_result = ref.order_by_child('id').equal_to(sample_id).get()
    # Loop through the query result (should contain only one product)
    for product_id, product_data in query_result.items():
        #Make an array of the data we dont want to update in this function
        exclude_keys = ["type", "in_time", "out_time", "tech_name"]
        try:
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
        except IndexError:
            tk.messagebox.showerror('Input Error', 'Error: That test index is not in range')

    update_btn.pack()
        # use "updating" as a status variable to say that we are in the processing of adding changes to the database
     #   updating = True

def email_results():
    pass



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
    # Get a database reference for the index number of sample ID
    index_ref = db.reference('/sample_index')
    # Read the data at the posts reference (this is a blocking operation)
    child_data = index_ref.get("ID")
    print(child_data[0]['ID'])
    return child_data


# This function is for incrementing the child value of a node, it is mainly for updating the id index after the current id has been assigned to a sample

def increment_child_value(child_data):
    # Get a database reference for the index number of sample ID
    index_ref = db.reference('/sample_index')
    # Update the 'ID' value to 2
    new_val = child_data[0]['ID'] + 1
    index_ref.update({'ID': new_val})



def write_sample_db():
    print("saving sample to db")
    # This is a database reference for the path we write sample info to
    info_ref = db.reference("/sample_info")
    with open("sample.json", "r") as f:
        file_contents = json.load(f)

    for key, value in file_contents.items():
        info_ref.push().set(value)
    f.close()



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
        try:
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
        except IndexError:
            tk.messagebox.showerror('Input Error', 'Error: That test index is not in range')


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

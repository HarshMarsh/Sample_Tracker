import sample_tracker_functions as st
import json
#user interface imports:
import tkinter as tk
from tkinter import *
from tkinter import messagebox

import pyrebase
from firebase_admin import credentials
import firebase_admin
from firebase_admin import db

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

#ThermalPrinter = adafruit_thermal_printer.get_printer_class(2.69)
#uart = serial.Serial("COM6", baudrate=9600, timeout=3000)
#printer = ThermalPrinter(uart)

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
#Make a class for the main window:
class start_window:
    def __init__(self,master):
        self.frame = tk.Frame(master)
        lbl1 = tk.Label(self.frame, text="Select the mode you would like to enter:")
        lbl1.pack(padx = 20, pady = 10)
        production_btn = tk.Button(self.frame, text = "Production mode", command = lambda:self.production_mode(master))
        production_btn.pack(padx = 50, pady = 10)

        manager_btn = tk.Button(self.frame, text = "Manager mode", command = lambda: self.manager_mode(master))
        manager_btn.pack(padx = 50, pady = 10)

        self.frame.pack(padx = 10, pady = 10)
    def production_mode(self,master):
        prod_window = production_window(master)
    def manager_mode(self,master):
        login_win = login_window(master)

class login_window:
    def __init__(self,master):
        # child window
        self.login_window = tk.Toplevel(master)
        st.place_window_center(self.login_window,master,220,200)
        login_label = tk.Label(self.login_window, text="sign in to enter manager mode:")
        login_label.pack(padx = 20, pady = 10)


        username_lbl = tk.Label(self.login_window,text = "username")
        username_lbl.pack(padx = 5, pady = 0)

        username_var = tk.StringVar()
        username = tk.Entry(self.login_window, textvariable= username_var)
        username.pack(padx = 20, pady = 10)

        password_lbl = tk.Label(self.login_window,text = "password")
        password_lbl.pack(padx = 5, pady = 0)

        password_var = tk.StringVar()
        password = tk.Entry(self.login_window, textvariable= password_var,show="*")
        password.pack(padx = 20, pady = 10)

        enter_btn = tk.Button(self.login_window, text="Login", command= lambda: self.login(username_var.get(),password_var.get(),master))
        enter_btn.pack(padx = 20, pady = 10)
    def login(self,username,password,master):
        logged_in = False
        try:
            login = auth.sign_in_with_email_and_password(username, password)
            print("Successfully logged in!")
            tk.messagebox.showinfo('Login', 'Successfully logged in')
            display_manager_window = manager_window(master)
            logged_in = True
        except:
            print("login failed")
            tk.messagebox.showerror('Login', 'Login failed: Invalid email or password')
        if logged_in:
            self.login_window.destroy()
            is_manager = True

class manager_window:
    def __init__(self,master):
        self.manager_win = tk.Toplevel()
        st.place_window_center(self.manager_win,master,500,250)
        button_frame = tk.LabelFrame(self.manager_win, text="Functions:")
        button_frame.grid(row=0, column=0, padx=20, pady=0, sticky="w")

        create_btn = tk.Button(button_frame, text="Create New\nSample", command=self.create_new_sample)
        create_btn.pack()

        delete_btn = tk.Button(button_frame, text="Delete Sample", command=lambda: self.display_delete_win(master))
        delete_btn.pack(padx=20, pady=20)

        print_lbl_btn = tk.Button(button_frame, text="Print Sample\nLabel", command= lambda:self.print_label_window(master))
        print_lbl_btn.pack(padx=20, pady=10)

        push_result_btn = tk.Button(button_frame, text="Push Result", command=lambda:self.output_result(master))
        push_result_btn.pack(padx=20, pady=10)

    def create_new_sample(self):
        # entries for sort, name, contact, address, tests

        field_frame = tk.LabelFrame(self.manager_win, text="fields")
        field_frame.grid(row=0, column=2)

        new_id = st.get_child_value()
        st.increment_child_value(new_id)

        sort_lbl = tk.Label(field_frame, text="Kind:")
        # sort_lbl.grid(row=0, column=0)
        sort_lbl.pack()

        sort_var = tk.StringVar()
        sort_entry = tk.Entry(field_frame, textvariable=sort_var)
        #  sort_entry.grid(row=1, column=0)
        sort_entry.pack()

        name_lbl = tk.Label(field_frame, text="Name:")
        #  name_lbl.grid(row=2, column=0)
        name_lbl.pack()

        name_var = tk.StringVar()
        name_entry = tk.Entry(field_frame, textvariable=name_var)
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
        test_list_entry = tk.Entry(field_frame, textvariable=test_list_var)
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
        dropdown = OptionMenu(field_frame, selected_test, *options)
        #    dropdown.grid(row=10, column=0,sticky="ew")
        dropdown.pack(side=LEFT)

        tests = []
        add_test_btn = tk.Button(field_frame, text="Add Test",
                                 command=lambda: add_test_list(tests, test_list_entry, selected_test.get()))
        #    add_test_btn.grid(row=10, column=1,padx = 20,sticky="ew")
        add_test_btn.pack(side=LEFT, padx=10)

        save_btn = tk.Button(field_frame, text="Save",
                             command=lambda: save_new_sample_db(new_id, sort_var.get(), email_var.get(), name_var.get(),
                                                                address_var.get(), tests, field_frame))
        #    save_btn.grid(row=11, column=0,sticky="ew")
        save_btn.pack(side=RIGHT)

    def display_delete_win(self,master):
        delete_frame = tk.Frame(self.manager_win)
        delete_frame.grid(row = 1,column = 0)


        delete_window = Toplevel(self.manager_win)
        st.place_window_center(delete_window,master,150,70)

        delete_lbl = tk.Label(delete_window, text = "Enter a sample ID to delete: ")
        delete_lbl.pack()
        id_to_delete = tk.StringVar()
        delete_entry = tk.Entry(delete_window,textvariable= id_to_delete)
        delete_entry.pack()


        delete_btn = tk.Button(delete_window, text = "delete",command = lambda: st.delete_sample(int(id_to_delete.get())))
        delete_btn.pack()

    def print_label_window(self,master):
        print_label_window = Toplevel(self.manager_win)
        st.place_window_center(print_label_window,master,150,70)

        print_lbl = tk.Label(print_label_window, text="Enter a sample ID to print: ")
        print_lbl.pack()
        id_to_print = tk.IntVar()
        print_entry = tk.Entry(print_label_window, textvariable=id_to_print)
        print_entry.pack()

        print_label_btn = tk.Button(print_label_window, text="print",
                                    command=lambda: st.print_label_data(id_to_print.get()))
        print_label_btn.pack()

    def output_result(self,master):
        info_frame = tk.LabelFrame(self.manager_win, text="sample info QC check:")
        info_frame.grid(row=0, column=2)

        # child window
        QC_window = Toplevel(self.manager_win)
        st.place_window_center(QC_window,master,300,70)

        QC_label = tk.Label(QC_window, text="For which sample would you like to check the results?")
        QC_label.pack()

        sample_id = tk.StringVar()
        sample_num_entry = tk.Entry(QC_window, textvariable=sample_id)
        sample_num_entry.pack()

        enter_btn = tk.Button(QC_window, text="Enter",
                              command=lambda: st.fill_sample_info(int(sample_id.get()), info_frame,1))
        enter_btn.pack()



def save_new_sample_db(new_id,sort,contact,name,address,tests,field_frame):
    New_Sample = Sample(new_id[0]['ID'], sort, contact, name, address, tests)
    New_Sample.save_to_file()
    st.write_sample_db()
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




def output_result():
    pass
class production_window:
    def __init__(self,master):
        self.production_win = tk.Toplevel()
        st.place_window_center(self.production_win,master,700,250)
       # ex_lbl = tk.Label(self.win,text = "hello world")
       # ex_lbl.pack()
     #   '''
        label_frame = tk.LabelFrame(self.production_win, text="Working Sample")
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
        button_frame = tk.LabelFrame(self.production_win, text="Actions:")
        button_frame.grid(row=1, column=0, padx=20, pady=0, sticky="w")

        result_info_frame = tk.LabelFrame(self.production_win, text="Test Results:")
        result_info_frame.grid(row=0, column=1, padx=20, pady=0)

        sample_info_frame = tk.LabelFrame(self.production_win, text="Sample Info:")
        sample_info_frame.grid(row=0, column=2, padx=20, pady=0)

        ex_lbl = tk.Label(result_info_frame)
        ex_lbl.pack()

        results_btn = tk.Button(button_frame, text="Enter Results", command=lambda: st.fill_results_window(sample_id_var.get(), test_index.get(),result_info_frame,update_btn,sample_info_frame))
        results_btn.grid(row=0, column=0, padx=5, pady=5)

        out_btn = tk.Button(button_frame, text="Check Out",command=lambda: st.check_out(sample_id_var.get(), test_index.get(), tech_name.get()))
        out_btn.grid(row=0, column=2, padx=5, pady=5)

        in_btn = tk.Button(button_frame, text="Check In",command=lambda: st.check_in(sample_id_var.get(), test_index.get(),name_entry))
        in_btn.grid(row=0, column=3, padx=5, pady=5)

        update_btn = tk.Button(result_info_frame, text="Update",command=lambda: st.save_test_result_db(sample_id_var.get(), test_index.get(),update_btn))
      #  '''

root = tk.Tk()
root.eval('tk::PlaceWindow . center')
window = start_window(root)
root.mainloop()



















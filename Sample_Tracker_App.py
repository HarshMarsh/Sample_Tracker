#This script is an attempt to revamp the way the sample tracker works into a more pleasing and efficient tabbed method where there are multiple pages the user can visit
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
from PIL import Image, ImageTk

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

class login_window:
    def __init__(self,master):
        # child window
        self.login_window = tk.Frame(master)
        self.login_window.pack()
       # st.place_window_center(self.login_window,master,220,200)
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
           # display_manager_window = manager_window(master)
            logged_in = True
        except:
            print("login failed")
            tk.messagebox.showerror('Login', 'Login failed: Invalid email or password')
        if logged_in:
            self.login_window.destroy()
            populate_window(True,master)
            is_manager = True
class start_window:
    def __init__(self,master):
        self.frame = tk.Frame(master)
        manager_flag = False
        lbl1 = tk.Label(self.frame, text="Select the mode you would like to enter:")
        lbl1.pack(padx = 20, pady = 10)
        production_btn = tk.Button(self.frame, text = "Production mode",command = lambda : self.production_mode(master))
        production_btn.pack(padx = 50, pady = 10)

        manager_btn = tk.Button(self.frame, text = "Manager mode",command = lambda : self.manager_mode(master))
        manager_btn.pack(padx = 50, pady = 10)

        self.frame.pack(padx = 10, pady = 10)
    def production_mode(self,master):
        manager_flag = False

        self.frame.destroy()
        populate_window(False,master)
       # prod_window = production_window(master)

    def manager_mode(self,master):
        manager_flag = True

        self.frame.destroy()
        login_window(master)
      #  login_win = login_window(master)


#make a function for each page
def enter_results_page():
    enter_results_frame = tk.Frame(main_frame)
    enter_results_frame.pack(pady=20)


    label_frame = tk.LabelFrame(main_frame, text="Working Sample")
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

    result_info_frame = tk.LabelFrame(main_frame, text="Test Results:")
    result_info_frame.grid(row=0, column=1, padx=20, pady=0)

    sample_info_frame = tk.LabelFrame(main_frame, text="Sample Info:")
    sample_info_frame.grid(row=0, column=2, padx=20, pady=0)

    # Create and configure a button frame if needed
    button_frame = tk.LabelFrame(main_frame,text="Actions")
    button_frame.grid(row=1, column=0, padx=20, pady=5, sticky="W")  # Use "sticky" to align to the left (west)

    results_btn = tk.Button(button_frame, text="Enter Results",command=lambda: st.fill_results_window(sample_id_var.get(), test_index.get(),result_info_frame,update_btn,sample_info_frame))
    results_btn.grid(row=0, column=0, padx=5, pady=5)

    update_btn = tk.Button(result_info_frame, text="Update",
                           command=lambda: st.save_test_result_db(sample_id_var.get(), test_index.get(), update_btn))

    out_btn = tk.Button(button_frame, text="Check Out",command=lambda: st.check_out(sample_id_var.get(), test_index.get(), tech_name.get()))
    out_btn.grid(row=0, column=2, padx=5, pady=5)

    in_btn = tk.Button(button_frame,text="Check In",command=lambda: st.check_in(sample_id_var.get(), test_index.get(),name_entry))
    in_btn.grid(row=0, column=3, padx=5, pady=5)

def search_sample_page():
    # make wrappers(sections) to add the scroll bars to instead of putting it on main window
    wrapper1 = LabelFrame(main_frame)
    wrapper2 = LabelFrame(main_frame)

    # make a canvas
    mycanvas = Canvas(wrapper1)
    mycanvas.pack(side=LEFT, fill="both", expand="yes")

    yscrollbar = tk.Scrollbar(wrapper1, orient="vertical", command=mycanvas.yview)
    yscrollbar.pack(side=RIGHT, fill="y")

    mycanvas.configure(yscrollcommand=yscrollbar.set)

    myframe = Frame(mycanvas)
    mycanvas.create_window((0, 0), window=myframe, anchor="nw")

    options = [
        'name',
        'kind',
        'date'
    ]

    search_param = tk.StringVar()
    # selected_test.set("Type-1")
    dropdown = OptionMenu(main_frame, search_param, *options)
    #    dropdown.grid(row=10, column=0,sticky="ew")
    dropdown.pack()

    # Create an Entry field for the technician's name
    search_data = tk.StringVar()
    search_data_entry = Entry(main_frame)
    search_data_entry.pack()

    search_button = Button(main_frame, text="search",
                           command=lambda: search_technician(myframe, formatted_data, search_param.get(),
                                                             search_data_entry.get())).pack()

    wrapper1.pack(fill="both", expand="yes", padx=10, pady=10)

    formatted_data = []

    print("\n\n\nformatted data: ", formatted_data)

    myframe.bind('<Configure>', lambda e: mycanvas.configure(scrollregion=mycanvas.bbox('all')))

def search_technician(myframe, formatted_data, search_param, search_data):
        print("search param is ", search_param, " data is ", search_data)
        date_flag = True
        technician_name = "Katie B."
        search_kind = "tall fescue"
        # search_date = "2023-12-19"
        # Clear previous data
        for widget in myframe.winfo_children():
            widget.destroy()

        ref = db.reference("/sample_info")
        query_result = ref.order_by_child('tests').get()

        if query_result:
            for product_id, product_data in query_result.items():
                tests = product_data.get('tests', [])
                for test in tests:
                    print(test['in_time'])

                    if (search_param == 'name' and test.get('tech_name') == search_data) or (
                            search_param == 'kind' and product_data['kind'] == search_data) or (
                            search_param == 'date' and (search_data in test['in_time'])):
                        substr = f"ID: {product_data['id']}"
                        if (search_param == 'date'):
                            for i in range(len(formatted_data)):
                                if substr in formatted_data[i]:
                                    date_flag = False
                        if search_param != 'date' or (date_flag == True and search_param == 'date'):
                            formatted_info = f"ID: {product_data['id']} | Type: {product_data['kind']}\n"
                            formatted_info += f"Name: {product_data['name']} | Email: {product_data['email']}\n"
                            formatted_info += f"Address: {product_data['address']}\n"

                            for i, test_data in enumerate(tests):
                                formatted_info += f"Test {i + 1}: "
                                formatted_info += f"Tech: {test_data['tech_name']} | In: {test_data['in_time']} | Out: {test_data['out_time']} | "
                                if search_data in test_data['in_time'] or search_data in test_data['out_time']:
                                    print("date match!")
                                for key, value in test_data.items():
                                    if key not in ['tech_name', 'in_time', 'out_time']:
                                        formatted_info += f"{key}: {value} | "
                                formatted_info += "\n"

                            formatted_data.append(formatted_info)

            for i in range(len(formatted_data)):
                label_text = StringVar()
                label_text.set(formatted_data[i])
                label = Label(myframe, textvariable=label_text, justify=LEFT)
                label.pack()
def new_sample_page():
        new_sample_frame = tk.Frame(main_frame)
        new_sample_frame.pack()
        field_frame = tk.LabelFrame(new_sample_frame, text="fields")
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
                                 command=lambda: st.add_test_list(tests, test_list_entry, selected_test.get()))
        #    add_test_btn.grid(row=10, column=1,padx = 20,sticky="ew")
        add_test_btn.pack(side=LEFT, padx=10)

        save_btn = tk.Button(field_frame, text="Save",
                             command=lambda: st.save_new_sample_db(new_id, sort_var.get(), email_var.get(), name_var.get(),
                                                                address_var.get(), tests, field_frame))
        #    save_btn.grid(row=11, column=0,sticky="ew")
        save_btn.pack(side=RIGHT)




def delete_sample_page():
    delete_sample_frame = tk.Frame(main_frame)
    delete_sample_frame.pack(pady=20)
    delete_lbl = tk.Label(delete_sample_frame, text="Enter a sample ID to delete: ")
    delete_lbl.pack(pady=20)
    id_to_delete = tk.StringVar()
    delete_entry = tk.Entry(delete_sample_frame, textvariable=id_to_delete)
    delete_entry.pack()

    delete_btn = tk.Button(delete_sample_frame, text="delete", command=lambda: st.delete_sample(int(id_to_delete.get())))
    delete_btn.pack(pady=20)

def print_label_page():
    print_label_window = tk.Frame(main_frame)
    print_label_window.pack()
    print_lbl = tk.Label(print_label_window, text="Enter a sample ID to print: ")
    print_lbl.pack()
    id_to_print = tk.IntVar()
    print_entry = tk.Entry(print_label_window, textvariable=id_to_print)
    print_entry.pack()

    print_label_btn = tk.Button(print_label_window, text="print",
                                command=lambda: st.print_label_data(id_to_print.get()))
    print_label_btn.pack()


def push_results_page():
    info_frame = tk.LabelFrame(main_frame, text="sample info QC check:")
    info_frame.grid(row=0, column=2)


    QC_label = tk.Label(info_frame, text="For which sample would you like to check the results?")
    QC_label.pack()

    sample_id = tk.StringVar()
    sample_num_entry = tk.Entry(info_frame, textvariable=sample_id)
    sample_num_entry.pack()

    enter_btn = tk.Button(info_frame, text="Enter",
                          command=lambda: st.fill_sample_info(int(sample_id.get()), info_frame, 1))
    enter_btn.pack()
def hide_indicators():
    enter_results_indicate.config(bg = "#c3c3c3")
    new_sample_indicate.config(bg="#c3c3c3")
    search_sample_indicate.config(bg="#c3c3c3")
    delete_sample_indicate.config(bg="#c3c3c3")
    print_label_indicate.config(bg="#c3c3c3")
    push_results_indicate.config(bg="#c3c3c3")

def delete_pages():
    for frame in main_frame.winfo_children():
        frame.destroy()
#description: This function makes it to where page indicator is only shown when the
# respective tab is selected
def indicate(lb,page):
    hide_indicators()
    lb.config(bg='#158aff')
    delete_pages()
    page()
def populate_window(manager_flag,master):
    master.geometry("500x500")


    enter_results_indicate.place(x=3, y=50, width=5, height=40)
    enter_results_btn = tk.Button(options_frame, text='Enter Results', font=('Bold', 15), fg='#158aff', bd=0, bg='#c3c3c3',command=lambda: indicate(enter_results_indicate, enter_results_page))
    enter_results_btn.place(x=10, y=56)

    search_sample_indicate.place(x=3, y=100, width=5, height=40)
    search_sample_btn = tk.Button(options_frame, text='Search Sample', font=('Bold', 15), fg='#158aff', bd=0,bg='#c3c3c3', command=lambda: indicate(search_sample_indicate, search_sample_page))
    search_sample_btn.place(x=10, y=100)

    if manager_flag is True:
        new_sample_indicate.place(x=3, y=150, width=5, height=40)
        new_sample_btn = tk.Button(options_frame, text='New Sample', font=('Bold', 15), fg='#158aff', bd=0, bg='#c3c3c3', command=lambda: indicate(new_sample_indicate, new_sample_page))
        new_sample_btn.place(x=10, y=150)



        delete_sample_indicate.place(x=3, y=200, width=5, height=40)
        delete_sample_btn = tk.Button(options_frame, text='Delete Sample', font=('Bold', 15), fg='#158aff', bd=0, bg='#c3c3c3', command=lambda: indicate(delete_sample_indicate, delete_sample_page))
        delete_sample_btn.place(x=10, y=200)

        print_label_indicate.place(x=3, y=250, width=5, height=40)
        print_label_btn = tk.Button(options_frame, text='Print Label', font=('Bold', 15), fg='#158aff', bd=0,bg='#c3c3c3',command=lambda: indicate(print_label_indicate, print_label_page))
        print_label_btn.place(x=10, y=250)

        push_results_indicate.place(x=3, y=300, width=5, height=40)
        push_results_btn = tk.Button(options_frame, text='Push Results', font=('Bold', 15), fg='#158aff', bd=0,bg='#c3c3c3', command=lambda: indicate(push_results_indicate, push_results_page))
        push_results_btn.place(x=10, y=300)


    options_frame.pack(side=tk.LEFT)
    options_frame.pack_propagate(False)
    options_frame.configure(width=150, height=600)


    main_frame.pack(side=tk.LEFT)
    main_frame.pack_propagate(False)
    main_frame.configure(height=700, width=600)


root = tk.Tk()
root.title("Sample Tracking System")

ico = Image.open('logo.png')
photo = ImageTk.PhotoImage(ico)
root.wm_iconphoto(False, photo)

# options frame is the sidebar housing the buttons for the different tasks
options_frame = tk.Frame(root, bg="#c3c3c3")
# main frame is the space where the functionality corresponding to the chosen option is shown
main_frame = tk.Frame(root, highlightbackground='black', highlightthickness=2)
enter_results_indicate = tk.Label(options_frame, text=' ', bg='#c3c3c3')
search_sample_indicate = tk.Label(options_frame, text=' ', bg='#c3c3c3')
new_sample_indicate = tk.Label(options_frame, text=' ', bg='#c3c3c3')
delete_sample_indicate = tk.Label(options_frame, text=' ', bg='#c3c3c3')
print_label_indicate = tk.Label(options_frame, text=' ', bg='#c3c3c3')
push_results_indicate = tk.Label(options_frame, text=' ', bg='#c3c3c3')

start_window(root)
root.mainloop()















#! /usr/bin/python2

from Tkinter import *
import ttk
from ScrolledText import ScrolledText
import re
import random
from threading import Thread, Lock
from findmegoogleip import FindMeGoogleIP
import logging


class Output:
    """A file-like object used to redirect output to Tkinter text"""
    def __init__(self, output_text):
        self.lock = Lock()
        self.output_text = output_text
        self.buffer = []
        self.buffer_size = 1

    def reset(self):
        self.buffer = []
        self.buffer_size = 1
        self.output_text.delete(1.0, END)

    def write(self, text):
        self.lock.acquire()
        text = text.strip()
        if len(text) > 0:
            self.buffer.append(text+"\n")

        # Every time ScrolledText.insert is called, it takes some memory(much more than I would expect).
        # The buffer size grows linearly to reduce the number of method calls.
        if len(self.buffer) >= self.buffer_size:
            self.real_flush()
            self.buffer_size += 1
        self.lock.release()

    def real_flush(self):
        try:
            self.output_text.insert('end', ''.join(self.buffer))
            self.output_text.see(END)
            self.buffer = []
        except TclError:
            pass

    def flush(self):
        pass


class App:
    def __init__(self, master):
        self.top_frame = Frame(master)
        self.top_frame.pack(side=TOP, padx=5, pady=5, fill=X, expand=NO)
        self.domain_label = Label(self.top_frame, text='Domain(s):')
        self.domain_label.pack(side=LEFT, fill=X, expand=NO)
        domain_list = ('kr', 'kr jp tw la vn th kh my ph sg id ru', 'us mx ca au nz', 'all')
        self.domain_text = ttk.Combobox(self.top_frame, values=domain_list)
        self.domain_text.pack(side=LEFT, fill=X, expand=YES)
        self.run_button = Button(self.top_frame, text='Run')
        self.run_button.pack(side=LEFT, padx=5, fill=X, expand=NO)
        self.update_button = Button(self.top_frame, text='Update')
        self.update_button.pack(side=LEFT, fill=X, expand=NO)

        self.bottom_frame = Frame(master)
        self.bottom_frame.pack(side=BOTTOM, padx=5, pady=5, fill=BOTH, expand=YES)
        self.output_text = ScrolledText(self.bottom_frame, height=25, width=100)
        self.output_text.config(font="consolas")
        self.output_text.pack(fill=BOTH, expand=YES)

        self.output_stream = Output(self.output_text)

        self.run_button.bind('<Button-1>', self.run)
        self.domain_text.bind('<Return>', self.run)
        self.update_button.bind('<Button-1>', self.update)
        self.is_running = False
        self.is_updating = False

    def update(self, event):
        Thread(target=self.update_dns_files).start()

    def update_dns_files(self):
        if not self.is_updating:
            self.is_updating = True
            self.output_stream.reset()
            self.update_button.configure(state=DISABLED)

            FindMeGoogleIP([]).update_dns_files()

            self.update_button.configure(state=ACTIVE)
            self.output_stream.real_flush()
            self.is_updating = False

    def run(self, event):
        Thread(target=self.find_me_google_ip).start()

    def find_me_google_ip(self):
        if not self.is_running:
            self.is_running = True
            self.output_stream.reset()
            self.run_button.configure(state=DISABLED)

            value = self.domain_text.get()
            if len(value.strip()) == 0:
                domains = [random.choice(FindMeGoogleIP.read_domains())]
            else:
                domains = re.split('\s+', value)
            FindMeGoogleIP(domains).run()

            self.run_button.configure(state=ACTIVE)
            self.output_stream.real_flush()
            self.is_running = False


root = Tk()
root.title('FindMeGoogleIP')
app = App(root)
logging.basicConfig(format='%(message)s', stream=app.output_stream, level=logging.INFO)
root.mainloop()

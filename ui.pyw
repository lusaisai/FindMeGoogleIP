#! /usr/bin/python3.4

from tkinter import *
from tkinter.scrolledtext import ScrolledText
import sys
import re
import random
from threading import Thread, Lock
from findmegoogleip import FindMeGoogleIP


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

    def write(self, text):
        self.lock.acquire()
        text = text.strip()
        if len(text) > 0:
            self.buffer.append(text+"\n")

        # Every time ScrolledText.insert is called, it takes some memory(much more than I would expect).
        # The buffer size grows linearly to reduce the number of method calls.
        if len(self.buffer) >= self.buffer_size:
            self.flush()
            self.buffer_size += 1
        self.lock.release()

    def flush(self):
        try:
            self.output_text.insert('end', ''.join(self.buffer))
            self.output_text.see(END)
            self.buffer.clear()
        except TclError:
            pass


class App:
    def __init__(self, master):
        self.top_frame = Frame(master)
        self.top_frame.pack(side=TOP, padx=5, pady=5, fill=X, expand=NO)
        self.domain_label = Label(self.top_frame, text='Domain(s):')
        self.domain_label.pack(side=LEFT, fill=X, expand=NO)
        self.domain_text = Entry(self.top_frame)
        self.domain_text.pack(side=LEFT, padx=10, fill=X, expand=YES)
        self.run_button = Button(self.top_frame, text='Run')
        self.run_button.pack(side=LEFT, fill=X, expand=NO)

        self.bottom_frame = Frame(master)
        self.bottom_frame.pack(side=BOTTOM, padx=5, pady=5, fill=BOTH, expand=YES)
        self.output_text = ScrolledText(self.bottom_frame, height=25, width=100)
        self.output_text.pack(fill=BOTH, expand=YES)

        sys.stdout = Output(self.output_text)

        self.run_button.bind('<Button-1>', self.run)
        self.domain_text.bind('<Return>', self.run)
        self.is_running = False

    def run(self, event):
        Thread(target=self.find_me_google_ip).start()

    def find_me_google_ip(self):
        if not self.is_running:
            self.is_running = True
            sys.stdout.reset()
            self.run_button.configure(state=DISABLED)

            value = self.domain_text.get()
            if len(value.strip()) == 0:
                domains = [random.choice(FindMeGoogleIP.read_domains())]
            else:
                domains = re.split('\s+', value)
            FindMeGoogleIP(domains).run()

            self.run_button.configure(state=ACTIVE)
            sys.stdout.flush()
            self.is_running = False

root = Tk()
root.title('FindMeGoogleIP')
app = App(root)
root.mainloop()

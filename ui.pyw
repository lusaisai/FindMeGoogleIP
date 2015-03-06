#! /usr/bin/python3.4

from tkinter import *
from tkinter.scrolledtext import ScrolledText
import sys
import re
import random
from threading import Thread
from findmegoogleip import FindMeGoogleIP


class Output:
    """A file-like object used to redirect output to Tkinter text"""
    def __init__(self, output_text):
        self.output_text = output_text

    def write(self, text):
        text = text.strip()
        if len(text) == 0:
            return
        else:
            self.output_text.insert('end', text+"\n")
            self.output_text.see(END)

    def flush(self):
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

    def run(self, event):
        value = self.domain_text.get()

        def execute():
            if len(value.strip()) == 0:
                domains = [random.choice(FindMeGoogleIP.read_domains())]
            else:
                domains = re.split('\s+', value)
            FindMeGoogleIP(domains).run()

        Thread(target=execute).start()


root = Tk()
root.title('FindMeGoogleIP')
app = App(root)
root.mainloop()

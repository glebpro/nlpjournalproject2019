#
#   A very basic clone of nvALT, a journalling application: http://brettterpstra.com/projects/nvalt/
#
#   @author Gleb Promokhov
#

from tkinter import *

class JournalGUI(Frame):
    """
    A basic GUI for the nvALT clone.
    """

    def __init__(self, parent=None, **kw):
        Frame.__init__(self, parent, kw)
        self.entries = {}
        self.makeWidgets()

    def add_entry(self, entry):
        self.entries[entry] = ""

    def makeWidgets(self):

        F1 = Frame(self)

        L1 = Label(F1, text="New Entry: ")
        L1.pack( side = LEFT)
        self.E1 = Entry(F1, bd = 1)
        self.E1.bind("<Return>", (lambda event: self.addNewEntry()))
        # self.E1.bind("<KeyRelease>", (lambda event: self.filterEntryList()))
        self.E1.pack(side = RIGHT)

        F1.pack()

        self.L1 = Listbox(self, selectmode = SINGLE)
        self.L1.bind('<<ListboxSelect>>', (lambda event: self.showNewEntryBody()))
        self.L1.pack()

        self.T1 = Text(self, bd = 5, bg = "grey")
        self.T1.bind("<KeyRelease>", (lambda event: self.updateEntryBody()))
        self.T1.pack()

    def addNewEntry(self):
        self.add_entry(self.E1.get())
        self.T1.delete(1.0,END)
        self.L1.insert(0, self.E1.get())
        self.L1.selection_clear(0, END)
        self.L1.selection_set(0)
        self.E1.delete(0, len(self.E1.get()))
        self.T1.focus()

    def updateEntryBody(self):
        key = self.L1.curselection()[0]
        key = self.L1.get(key)
        self.entries[key] = self.T1.get(1.0,END)

    def showNewEntryBody(self):
        key = self.L1.curselection()[0]
        key = self.L1.get(key)
        print(key)
        self.T1.delete(1.0,END)
        self.T1.insert(1.0, self.entries[key])

def main():
    root = Tk()
    jGUI = JournalGUI(root)
    jGUI.pack(side=TOP)
    root.mainloop()

if __name__ == '__main__':
    main()

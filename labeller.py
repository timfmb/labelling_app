import tkinter as tk
from PIL import Image, ImageTk
import shutil
import os
import csv


class Labeller:
    def __init__(self, input_path, output_path):
        self.input_path = input_path
        self.output_path = output_path
        self.filenames = []
        self.done_stack = []
        self.win = tk.Tk()
        self.win.geometry("1200x800") # set window size
        self.classified = 0
        self.total_input = 0
        self.result_string = tk.StringVar()
        self.result = tk.Label(self.win, textvariable=self.result_string)
        self.result_string.set(f'0/{self.total_input}')
        self.result.pack()
        self.panel = tk.Label(self.win, height=600)
        self.panel.pack()


    def progress(self):
        print(f'{self.classified}/{self.total_input}')


    def load_position(self):
        with open('state.csv', 'r') as csvfile:
            headers = ['position']
            reader = csv.DictReader(csvfile, headers)
            rows = [row for row in reader]
            current = rows[-1]
            self.classified = int(current['position'])
            return current['position']


    def save_position(self):
        with open('state.csv', 'a') as csvfile:
            headers = ['position']
            writer = csv.DictWriter(csvfile, headers)
            writer.writerow({'position':self.classified})

    
    def write_state_header(self):
        with open('state.csv', 'a') as csvfile:
            headers = ['position']
            writer = csv.DictWriter(csvfile, headers)
            writer.writeheader()


    def load_image(self):
        basewidth = 600
        img = Image.open(f'{self.input_path}/{self.filenames[-1]}')
        wpercent = (basewidth/float(img.size[0]))
        hsize = int((float(img.size[1])*float(wpercent)))
        img = img.resize((basewidth,hsize), Image.ANTIALIAS)
        img = ImageTk.PhotoImage(img)
        self.panel.img = img  # keep a reference so it's not garbage collected
        self.panel['image'] = img


    def next_image(self, category):
        filename = self.filenames.pop()
        self.done_stack.append(f'{self.output_path}/{category}/{filename}')
        self.load_image()


    def category_on_press(self, category):
        def wrapper(category=category):
            shutil.copy(f'{self.input_path}/{self.filenames[-1]}', f'{self.output_path}/{category}')
            self.next_image(category)
            self.classified += 1
            self.result_string.set(f'{self.classified}/{self.total_input}')
            self.progress()
            self.save_position()
            return
        return wrapper


    def add_categories(self, categories):
        buttons = []
        for category in categories:
            buttons.append(tk.Button(text=category, command=self.category_on_press(category)))
        self.buttons = buttons
        self.categories = categories


    def build_output_dirs(self):
        split_output_path = self.output_path.split('/')
        path_to_build = split_output_path[0]
        for i in range(len(split_output_path)):
            try:
                os.mkdir(path_to_build)
            except:
                pass
            path_to_build += '/'
            try:
                path_to_build += split_output_path[i+1]
            except:
                break
        for category in self.categories:
            try:
                os.mkdir(f'{self.output_path}/{category}')        
            except:
                pass

    def get_image_names(self):
        try:
            position = int(self.load_position())
            print(position)
            print(type(position))
        except:
            print('failed')
            position = 0
        filenames = os.listdir(self.input_path)
        self.total_input = len(filenames)
        self.result_string.set(f'{self.classified}/{self.total_input}')
        filenames = filenames[position:]
        filenames.reverse()
        self.progress()
        self.filenames = filenames


    def on_back_press(self):
        file_path = self.done_stack.pop()
        if '/' in file_path:
            os.remove(file_path)
            filename = file_path.split('/')[-1]
            print(filename)
        else:
            filename = file_path
    
        self.filenames.append(filename)
        self.classified -= 1
        self.save_position()
        self.result_string.set(f'{self.classified}/{self.total_input}')
        self.load_image()
        self.progress()

    def build_back_button(self):
        return tk.Button(text='back', command=self.on_back_press)


    def on_next_press(self):
        filename = self.filenames.pop()
        self.done_stack.append(filename)
        self.load_image()
        self.classified += 1
        self.result_string.set(f'{self.classified}/{self.total_input}')
        self.save_position()
        self.progress()
    
    def build_next_button(self):
        return tk.Button(text='next', command=self.on_next_press)


    def on_remove_press(self):
        filename = self.filenames.pop()
        os.remove(f'{self.input_path}/{filename}')
        self.load_image()


    def build_remove_button(self):
        return tk.Button(text='remove', command=self.on_remove_press, background='red')   


    def get_button_x(self, button_width, num):
        return 100 + num*button_width


    def build_ui(self):
        button_bar_width = 1000
        button_width = int(button_bar_width/len(self.buttons))
        num = 0

        back_button = self.build_back_button()
        next_button = self.build_next_button()
        remove_button = self.build_remove_button()
        back_button.place(y=300, x=50, height=50, width=100)
        next_button.place(y=300, x=1050, height=50, width=100)
        remove_button.place(y=650, x=550, height=50, width=150)

        for button in self.buttons:
            button.place(y=570, x=self.get_button_x(button_width, num), height=70, width=button_width)
            num +=1
        self.load_image()
        self.win.mainloop()


input_path = input('Input_path: ')
output_path = input('Output path: ')


labeller = Labeller(input_path, output_path)
labeller.write_state_header()
adding_categories = True
while adding_categories:
    add_category = input('Add category? y/n')
    if add_category == 'y':
        category = input('Category Name: ')
        labeller.add_categories([category])
    elif add_category == 'n':
        adding_categories = False
    else:
        continue

labeller.build_output_dirs()
labeller.get_image_names()
labeller.build_ui()


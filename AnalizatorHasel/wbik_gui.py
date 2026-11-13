import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter.scrolledtext import ScrolledText
from tkinter import font
from pathlib import Path


import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

from matplotlib.figure import Figure
import matplotlib.ticker as ticker

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Główna klasa GUI, tworzenie ramek
class View(tk.Tk):
    def __init__(self, model, controller):
        super().__init__()
        self.model = model
        self.controller = controller
        self.title("Analizator haseł")
        self.state('zoomed')
        self.screen_width = self.winfo_screenwidth()
        self.screen_height = self.winfo_screenheight()
        #self.geometry(f"{self.screen_width}x{self.screen_height}")
        self.style=ttk.Style(self)
        self.style.theme_use('clam')
        self.create_frames()
    
    def show_frame(self, context):
        frame = self.frames[context]
        frame.reload()
        frame.place(relx=0, rely=0, relwidth=1, relheight=1)
        frame.tkraise()
        
    def create_frames(self):
        self.frames = {}
        for F in (StatsPage, PsswdLenPage, DigitPosPage, CharsFreqPage, NumFreqPage, SpcsFreqPage, RepPsswdsPage, SpecialPosPage, AlphaPosPage):
            frame = F(self, self.model, self.controller, self.screen_width, self.screen_height)
            self.frames[F] = frame
        self.show_frame(StatsPage)

# Menu statystyk
class StatsPage(ttk.Frame):
    def __init__(self, master, model, controller, screen_width, screen_height):
        super().__init__(master)
        self.model = model
        self.controller = controller
        
        self.style = ttk.Style(self)
        self.style.configure('StatsPage.TLabel', font=('Segoe UI', 16), anchor=tk.CENTER, justify='center') 
        self.style.configure('StatsPage.TButton', font=('Segoe UI', 16), anchor=tk.CENTER, justify='center')
        self.style.configure('StatsPage_loaded.TLabel', font=('Segoe UI', 16))
        self.style.configure('StatsCaption.TLabel', font=('Segoe UI', 13), anchor='w', justify='left')
        self.style.configure('StatsValue.TLabel', font=('Segoe UI', 18, 'bold'), anchor='w', justify='left')
        
        self.subframe = ttk.Frame(self)
        self.subframe_info = ttk.Frame(self)
        self.subframe.place(relx=0.3, rely=0.35, relwidth=0.5, relheight=0.6, anchor='center')
        self.subframe_info.place(relx=0.75, rely=0.5, relwidth=0.25, anchor='center')

        self.loaded_label = ttk.Label(self, text="Brak załadowanych baz haseł", wraplength=0.8*screen_width, justify='left', style='StatsPage_loaded.TLabel')
        self.stat_labels = []
        for description in ("Łączna liczba haseł", "Cyfry", "Litery",
                            "Znaki specjalne", "Hasła o strukturze: najpierw litery, potem cyfry"):
            if description == "Cyfry":
                self.only_chars_heading = ttk.Label(
                    self.subframe_info, text="", style='StatsCaption.TLabel',
                    font=('Segoe UI', 13, 'bold'))
                self.only_chars_heading.pack(anchor='w', fill='x', pady=(4, 8))
            elif description.startswith("Hasła o strukturze:"):
                self.structure_separator = ttk.Separator(self.subframe_info, orient='horizontal')
                self.structure_separator.pack(fill='x', pady=(0, 12))
            caption = ttk.Label(self.subframe_info, text="", style='StatsCaption.TLabel')
            caption.pack(anchor='w', fill='x')
            value = ttk.Label(self.subframe_info, text="", style='StatsValue.TLabel')
            value.pack(anchor='w', fill='x', pady=(2, 12))
            self.stat_labels.append((description, caption, value))
        self.subframe_info.bind('<Configure>', self.resize_stats_labels)

        self.subframe.grid_propagate(False)

        ttk.Label(self.subframe, text="", style='StatsPage.TLabel').grid(row=0, column=0, sticky="nsew")
        ttk.Button(self.subframe, text="Załaduj bazy", command=self.get_db_callback, style='StatsPage.TButton').grid(row=0, column=1, sticky="nsew")
        ttk.Button(self.subframe, text="Wyczyść bazy", command=self.clean_db_callback, style='StatsPage.TButton').grid(row=0, column=2, sticky="nsew")
        ttk.Label(self.subframe, text="", style='StatsPage.TLabel').grid(row=1, column=0, sticky="nsew")
        ttk.Label(self.subframe, text="Opcje ogólne", style='StatsPage.TLabel').grid(row=1, column=1, columnspan=2, sticky="")
        #####
        ttk.Label(self.subframe, text="", style='StatsPage.TLabel').grid(row=2, column=0, sticky="nsew")
        ttk.Button(self.subframe, text="Długości haseł", command=self.controller.psswds_len_button, style='StatsPage.TButton').grid(row=2, column=1, sticky="nsew")
        ttk.Button(self.subframe, text="Powtarzające się hasła", command=self.controller.repeated_psswds_button, style='StatsPage.TButton').grid(row=2, column=2, sticky="nsew")
        ttk.Label(self.subframe, text="", style='StatsPage.TLabel').grid(row=3, column=0, sticky="nsew")
        ttk.Label(self.subframe, text="Pozycje", style='StatsPage.TLabel').grid(row=3, column=1, sticky="")
        ttk.Label(self.subframe, text="Częstość występowania", style='StatsPage.TLabel').grid(row=3, column=2, sticky="")
        ttk.Label(self.subframe, text="Cyfry", style='StatsPage.TLabel').grid(row=4, column=0, sticky="")
        ttk.Button(self.subframe, text="Pozycje cyfr w haśle", command=self.controller.digit_position_button, style='StatsPage.TButton').grid(row=4, column=1, sticky="nsew")
        ttk.Button(self.subframe, text="Najczęstsze cyfry", command=self.controller.numeric_frequency_button, style='StatsPage.TButton').grid(row=4, column=2, sticky="nsew")
        ttk.Label(self.subframe, text="Litery", style='StatsPage.TLabel').grid(row=5, column=0, sticky="")
        ttk.Button(self.subframe, text="Pozycje liter w haśle", command=self.controller.letter_position_button, style='StatsPage.TButton').grid(row=5, column=1, sticky="nsew")
        ttk.Button(self.subframe, text="Najczęstsze litery", command=self.controller.chars_frequency_button, style='StatsPage.TButton').grid(row=5, column=2, sticky="nsew")
        ttk.Label(self.subframe, text="Specjalne", style='StatsPage.TLabel').grid(row=6, column=0, sticky="")
        ttk.Button(self.subframe, text="Pozycje zn. specjalnych w haśle", command=self.controller.special_position_button, style='StatsPage.TButton').grid(row=6, column=1, sticky="nsew")
        ttk.Button(self.subframe, text="Najczęstsze znaki specjalne", command=self.controller.special_frequency_button, style='StatsPage.TButton').grid(row=6, column=2, sticky="nsew")

        self.subframe.columnconfigure(0, weight=1)
        self.subframe.columnconfigure(1, weight=1)
        self.subframe.columnconfigure(2, weight=1)
        
        for i in range(7):
            self.subframe.rowconfigure(i, weight=1)

        self.loaded_label.place(relx=0.1, rely=0.95, anchor='sw', relwidth=0.8)
                        
    def resize_stats_labels(self, event):
        self.only_chars_heading.configure(wraplength=max(1, event.width - 8))
        for description, caption, value in self.stat_labels:
            caption.configure(wraplength=max(1, event.width - 8))
            value.configure(wraplength=max(1, event.width - 8))

    def on_resize(self, event):
        # Automatyczna aktualizacja rozmiaru ramki w zależności od rozmiaru okna
        new_width = self.winfo_width() - 40  # Margines 20 pikseli z każdej strony
        new_height = self.winfo_height() - 40  # Margines 20 pikseli z każdej strony
        self.subframe.place_configure(width=new_width, height=new_height)
        
    def get_db_callback(self):
        self.controller.get_db_button()
        self.reload()

    def clean_db_callback(self):
        self.controller.clr_db_button()
        self.loaded_label.config(text="Brak załadowanych baz haseł", foreground='black')
        self.reload()

    def reload(self):
        psswds_nb = self.model.all_psswds_nb(self.model.psswds)
        if self.model.file_paths:
            count_text = f"{psswds_nb:,}".replace(',', ' ')
            display_text = f"Wczytane bazy: {len(self.model.file_paths)}  |  Łącznie haseł: {count_text}\n"
            display_text += " • ".join(Path(path).name for path in self.model.file_paths)
            self.loaded_label.config(text=display_text, foreground='green')
        else:
            self.loaded_label.config(text="Brak załadowanych baz haseł", foreground='black')
        numeric_nb = self.model.all_numeric_nb(self.model.psswds)
        alpha_nb = self.model.all_alpha_nb(self.model.psswds)
        spcs_nb = self.model.all_spcs_nb(self.model.psswds)
        alpha_plus_num_nb = self.model.alpha_plus_num_nb(self.model.psswds)
        counts = (psswds_nb, numeric_nb, alpha_nb, spcs_nb, alpha_plus_num_nb)
        self.only_chars_heading.config(text="Hasła zawierające tylko:" if psswds_nb else "")
        for index, ((description, caption, value), count) in enumerate(zip(self.stat_labels, counts)):
            if psswds_nb == 0:
                caption.config(text="")
                value.config(text="")
            else:
                caption.config(text=description)
                count_text = f"{count:,}".replace(',', ' ')
                if index > 0:
                    percentage = f"{count / psswds_nb * 100:.1f}".replace('.', ',')
                    count_text += f"  ({percentage}%)"
                value.config(text=count_text)
            
# Długości haseł        
class PsswdLenPage(ttk.Frame):
    def __init__(self, master, model, controller, screen_width, screen_height):
        super().__init__(master)
        self.model = model
        self.controller = controller
        self.master = master
        
        self.style = ttk.Style(self)
        self.style.configure('PsswdLenPage.TLabel', font=('Segoe UI', 18))
        self.style.configure('PsswdLenPage.TButton', font=('Segoe UI', 20))
        
        self.figure = Figure(figsize=(5, 4), dpi=100)
        self.plot = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, self)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.canvas.get_tk_widget().place(relx=0.5, rely=0.4, anchor='center', relwidth=0.7, relheight=0.7)

        ttk.Button(self, text="Wróć", command=lambda: self.master.show_frame(StatsPage), style='PsswdLenPage.TButton').place(relx=0.5, rely=0.95, anchor='center')

        self.scale = ttk.Scale(self, from_=10, to=20, orient='horizontal', command=self.scale_change, value=10) 
        self.range_from_label = ttk.Label(self, style='PsswdLenPage.TLabel')
        self.range_from_label.place(relx=0.2, rely=0.85, anchor='center')
        self.scale.place(relwidth=0.5, relx=0.5, rely=0.85, anchor='center')
        self.range_to_label = ttk.Label(self, style='PsswdLenPage.TLabel')
        self.range_to_label.place(relx=0.8, rely=0.85, anchor='center')
        self.range_info_label = ttk.Label(self, style='PsswdLenPage.TLabel', text='Ustaw kres osi poziomej:')
        self.range_info_label.place(relx=0.5, rely=0.8, anchor='center')
         
    def reload(self):
        
        self.scale.config(to=max(self.model.lengths.keys()))
        range_to = int(float(self.scale.get()))
        self.range_from_label.config(text=f"min {int(self.scale['from'])}")
        self.range_to_label.config(text=f"max {int(self.scale['to'])}")
        self.lengths_to_print = dict(filter(lambda item: item[0] <= range_to, self.model.lengths.items()))
        
        max_value = max(self.lengths_to_print.values())
        norm = mcolors.Normalize(vmin=0, vmax=max_value)
        cmap = plt.get_cmap('viridis')
        mycolor = [cmap(norm(value)) for value in self.lengths_to_print.values()]
        
        self.plot.clear()
        self.plot.bar(list(self.lengths_to_print.keys()), list(self.lengths_to_print.values()), edgecolor='black', color=mycolor)
        self.plot.set_title("Długości haseł w bazie", fontsize=20)
        self.plot.set_xlabel("Długość hasła", fontsize=15)
        self.plot.set_ylabel("Procentowy udział", fontsize=15)
        self.plot.tick_params(axis='both', which='major', labelsize=13)
        self.plot.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))
        self.plot.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))
        self.plot.xaxis.set_minor_locator(plt.MultipleLocator(1))
        self.plot.yaxis.set_minor_locator(plt.MultipleLocator(1))
        
        self.plot.set_xlim(left=0.5)
        self.plot.set_xlim(right=range_to+0.5)
        x_min, x_max = self.plot.get_xlim()

        if x_max <= 21:
            self.plot.xaxis.set_major_locator(plt.MultipleLocator(1))
        else:
            self.plot.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))
        self.canvas.draw()
        
    def scale_change(self, value):
        if self.scale.get() % 1 != 0:
            value = min(range(self.scale['from'], self.scale['to'] + 1), key=lambda x: abs(self.scale.get() - x)) #ttk
            self.scale.set(value)
        else:
            self.reload()
        
# Powtarzające się hasła        
class RepPsswdsPage(ttk.Frame):
    def __init__(self, master, model, controller, screen_width, screen_height):
        super().__init__(master)
        
        self.model = model
        self.controller = controller
        self.master = master
        
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        self.sorted_alphabetically = True
        
        self.style = ttk.Style(self)
        self.style.configure('RepPsswdsPage.TLabel', font=('Segoe UI', 20))
        self.style.configure('RepPsswdsPage.TButton', font=('Segoe UI', 20))

        self.init_widgets()
        
    def init_widgets(self):
        self.master.update()
        #self.n = 2
        self.info_label = ttk.Label(self)
        self.info_label.place(relx=0.5, rely=0.05, anchor ='center')
        search_frame = ttk.Frame(self)
        search_frame.place(relx=0.5, rely=0.13, anchor='center', relwidth=0.9)
        ttk.Label(search_frame, text="Dokładne hasło (wielkość liter ma znaczenie):").pack(anchor='w')
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, font=('Segoe UI', 14))
        search_entry.pack(side=tk.LEFT, fill='x', expand=True, pady=4)
        search_entry.bind('<Return>', lambda event: self.reload())
        ttk.Button(search_frame, text="Szukaj", command=self.reload).pack(side=tk.LEFT, padx=8)
        ttk.Button(search_frame, text="Pokaż wszystkie", command=self.clear_search).pack(side=tk.LEFT)
        self.text_area = ScrolledText(self, wrap=tk.WORD, width=2*30+1, font = ("Courier", 16))
        print(self.screen_width, self.screen_height)
        print(int(0.05*self.screen_width))
        self.text_area.place(relheight=0.62, relx=0.5, rely=0.52, anchor='center')
        self.text_area.configure(state='disabled')
        ttk.Button(self, text="Wróć", command=lambda: self.master.show_frame(StatsPage), style='RepPsswdsPage.TButton').place(relx=0.5, rely=0.95, anchor='center')
        self.sort_button = ttk.Button(self, text="Sortuj alfabetycznie", command=self.toggle_sort, style='RepPsswdsPage.TButton')
        self.sort_button.place(relx=0.05, rely=0.95, anchor='w')
        self.sort_info = ttk.Label(self, style='DigitPosPage.TLabel')
        self.sort_info.place(relx=0.05, rely=0.85, anchor='w')
        
    def clear_search(self):
        self.search_var.set('')
        self.reload()

    def toggle_sort(self):
        self.sorted_alphabetically = not self.sorted_alphabetically
        self.reload()

    def reload(self):
        query = self.search_var.get()
        self.info_label.config(text="Wynik wyszukiwania" if query else "Hasła powtórzone minimum 2 razy:", style='RepPsswdsPage.TLabel')
        self.text_area.configure(state='normal')
        self.text_area.delete('1.0', tk.END)
        
        if self.sorted_alphabetically:
            self.dict_to_print = dict(sorted(self.model.rep.items()))
            self.sort_button.config(text="Sortuj wg liczby powtórzeń", style='RepPsswdsPage.TButton')
            self.sort_info.config(text="Dane posortowano\nalfabetycznie")
        else:
            self.dict_to_print = dict(sorted(self.model.rep.items(), key=lambda item: item[1]))
            self.sort_button.config(text="Sortuj alfabetycznie", style='RepPsswdsPage.TButton')
            self.sort_info.config(text="Dane posortowano\nwg liczby powtórzeń")

        if query:
            count = self.model.psswds.count(query)
            result = f"Hasło: {query}\n\nLiczba wystąpień: {count}\n"
            if count == 0:
                result += "\nNie znaleziono tego hasła we wczytanych bazach."
            elif count == 1:
                result += "\nHasło występuje tylko raz — nie jest powtórzone."
        else:
            result = self.model.dict_to_str(self.dict_to_print, width=30) if self.dict_to_print else "Brak powtarzających się haseł."
        self.text_area.insert(tk.INSERT, result)
        self.text_area.configure(state='disabled')

# Pozycje cyfr w hasłach
class DigitPosPage(ttk.Frame):
    def __init__(self, master, model, controller, screen_width, screen_height):
        super().__init__(master)
        self.model = model
        self.controller = controller
        self.master = master
        
        self.style = ttk.Style(self)
        self.style.configure('DigitPosPage.TLabel', font=('Segoe UI', 18))
        self.style.configure('DigitPosPage.TButton', font=('Segoe UI', 20))
        
        self.figure = Figure(figsize=(5, 4), dpi=100)
        self.plot = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, self)
        self.canvas.get_tk_widget().place(relx=0.5, rely=0.4, anchor='center', relwidth=0.7, relheight=0.7)
        
        ttk.Button(self, text="Wróć", command=lambda: self.master.show_frame(StatsPage), style='DigitPosPage.TButton').place(relx=0.5, rely=0.95, anchor='center')
        self.range_from_label = ttk.Label(self, style='DigitPosPage.TLabel')
        self.range_from_label.place(relx=0.2, rely=0.85, anchor='center')
        self.range_to_label = ttk.Label(self, style='DigitPosPage.TLabel')
        self.range_to_label.place(relx=0.8, rely=0.85, anchor='center')
        self.scale = ttk.Scale(self, from_= 1, to=10, orient='horizontal', command=self.scale_change, value=8) 
        self.scale.place(relwidth=0.5, relx=0.5, rely=0.85, anchor='center')
        
        self.nb_label = ttk.Label(self, style='DigitPosPage.TLabel')
        self.nb_label.place(relx=0.90, rely=0.95, anchor='e')
        
        self.range_info_label = ttk.Label(self, style='DigitPosPage.TLabel', text='Wybierz długość hasła:')
        self.range_info_label.place(relx=0.5, rely=0.8, anchor='center')
        
    def reload(self):
        self.scale.config(to = len(max(self.model.psswds, key=len)))
        current_fml_length = int(float(self.scale.get()))
        self.fml_to_print = self.model.percentage_frequency2(self.model.first_middle_last(current_fml_length)[0], current_fml_length)
        self.range_from_label.config(text=f'min {len(min(self.model.psswds, key=len))}')
        self.range_to_label.config(text=f'max {len(max(self.model.psswds, key=len))}')
        self.nb_label.config(text=f'Wykres na podstawie {self.model.first_middle_last(current_fml_length)[1]} haseł z bazy')

        max_value = max(self.fml_to_print.values())
        norm = mcolors.Normalize(vmin=0, vmax=max_value)
        cmap = plt.get_cmap('viridis')
        mycolor = [cmap(norm(value)) for value in self.fml_to_print.values()]
        
        self.plot.clear()
        self.plot.bar(self.fml_to_print.keys(), self.fml_to_print.values(), edgecolor='black', color=mycolor)
        self.plot.set_title(f'Rozmieszczenie cyfr dla haseł o długości {current_fml_length}', fontsize=20)
        self.plot.set_xlabel("Pozycja cyfry w haśle", fontsize=15)
        self.plot.set_ylabel("Procentowy udział", fontsize=15)
        
        self.plot.tick_params(axis='both', which='major', labelsize=13)
        self.plot.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))
        self.plot.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))
        self.plot.xaxis.set_minor_locator(plt.MultipleLocator(1))
        self.plot.yaxis.set_minor_locator(plt.MultipleLocator(1))
        
        self.plot.set_xlim(left=0.5)
        self.plot.set_xlim(right=current_fml_length+0.5)
        x_min, x_max = self.plot.get_xlim()

        if x_max <= 21:
            self.plot.xaxis.set_major_locator(plt.MultipleLocator(1))
        else:
            self.plot.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))
            
        self.canvas.draw()
        
    def scale_change(self, value):
        if self.scale.get() % 1 != 0:
            value = min(range(self.scale['from'], self.scale['to'] + 1), key=lambda x: abs(self.scale.get() - x))
            self.scale.set(value)
        else:
            self.reload()
        
# Pozycje liter w hasłach
class AlphaPosPage(ttk.Frame):
    def __init__(self, master, model, controller, screen_width, screen_height):
        super().__init__(master)
        self.model = model
        self.controller = controller
        self.master = master
        
        self.style = ttk.Style(self)
        self.style.configure('AlphaPosPage.TLabel', font=('Segoe UI', 18))
        self.style.configure('AlphaPosPage.TButton', font=('Segoe UI', 20))

        self.currentcase = 'upper_lower'
        
        self.figure = Figure(figsize=(5, 4), dpi=100)
        self.plot = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, self)
        self.canvas.get_tk_widget().place(relx=0.5, rely=0.4, anchor='center', relwidth=0.7, relheight=0.7)
        
        ttk.Button(self, text="Wróć", command=lambda: self.master.show_frame(StatsPage), style='AlphaPosPage.TButton').place(relx=0.5, rely=0.95, anchor='center')
        self.range_from_label = ttk.Label(self, style='AlphaPosPage.TLabel')
        self.range_from_label.place(relx=0.2, rely=0.85, anchor='center')
        self.range_to_label = ttk.Label(self, style='AlphaPosPage.TLabel')
        self.range_to_label.place(relx=0.8, rely=0.85, anchor='center')
        self.scale = ttk.Scale(self, from_=1, to=10, orient='horizontal', command=self.scale_change, value=8) 
        self.scale.place(relwidth=0.5, relx=0.5, rely=0.85, anchor='center')
        
        self.range_info_label = ttk.Label(self, style='AlphaPosPage.TLabel', text='Wybierz długość hasła:')
        self.range_info_label.place(relx=0.5, rely=0.8, anchor='center')
        
        self.nb_label = ttk.Label(self, style='AlphaPosPage.TLabel')
        self.nb_label.place(relx=0.90, rely=0.95, anchor='e')

        self.case_label = ttk.Label(self, style='AlphaPosPage.TLabel', text='Litery:')
        self.case_label.place(relx=0.07, rely=0.4, anchor='center')

        self.lowercase_button = ttk.Button(self, text="Małe", command=self.lowercase, style='AlphaPosPage.TButton')
        self.lowercase_button.place(relx=0.07, rely=0.5, anchor='center')
        self.uppercase_button = ttk.Button(self, text="Duże", command=self.uppercase, style='AlphaPosPage.TButton')
        self.uppercase_button.place(relx=0.07, rely=0.6, anchor='center')
        self.allcase_button = ttk.Button(self, text="Małe i duże", command=self.allcase, style='AlphaPosPage.TButton')
        self.allcase_button.place(relx=0.07, rely=0.7, anchor='center')
         
    def lowercase(self):
        self.currentcase = 'lower'
        self.reload()
    
    def uppercase(self):
        self.currentcase = 'upper'
        self.reload()

    def allcase(self):
        self.currentcase = 'upper_lower'
        self.reload()

    def reload(self):
        self.scale.config(to=len(max(self.model.psswds, key=len)))
        current_fml_length = int(float(self.scale.get()))
        self.fml_to_print = self.model.percentage_frequency2(self.model.fml_alpha(current_fml_length, self.currentcase)[0], current_fml_length)
        self.range_from_label.config(text=f'min {len(min(self.model.psswds, key=len))}')
        self.range_to_label.config(text=f'max {len(max(self.model.psswds, key=len))}')
        self.nb_label.config(text=f'Wykres na podstawie {self.model.fml_alpha(current_fml_length, self.currentcase)[1]} haseł z bazy')

        max_value = max(self.fml_to_print.values())
        norm = mcolors.Normalize(vmin=0, vmax=max_value)
        cmap = plt.get_cmap('viridis')
        mycolor = [cmap(norm(value)) for value in self.fml_to_print.values()]
        
        self.plot.clear()
        self.plot.bar(self.fml_to_print.keys(), self.fml_to_print.values(), edgecolor = 'black', color=mycolor)
        if self.currentcase == 'upper_lower':
            self.plot.set_title(f'Rozmieszczenie liter dla haseł o długości {current_fml_length}', fontsize=20)
        elif self.currentcase == 'upper':
            self.plot.set_title(f'Rozmieszczenie dużych liter dla haseł o długości {current_fml_length}', fontsize=20)
        else:
            # self.currentcase == 'lower'
            self.plot.set_title(f'Rozmieszczenie małych liter dla haseł o długości {current_fml_length}', fontsize=20)
        self.plot.set_xlabel("Pozycja litery w haśle", fontsize=15)
        self.plot.set_ylabel("Procentowy udział", fontsize=15)
        
        self.plot.tick_params(axis='both', which='major', labelsize=13)
        self.plot.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))
        self.plot.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))
        self.plot.xaxis.set_minor_locator(plt.MultipleLocator(1))
        self.plot.yaxis.set_minor_locator(plt.MultipleLocator(1))
        
        self.plot.set_xlim(left=0.5)
        self.plot.set_xlim(right=current_fml_length+0.5)
        x_min, x_max = self.plot.get_xlim()

        if x_max <= 21:
            self.plot.xaxis.set_major_locator(plt.MultipleLocator(1))
        else:
            self.plot.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))
        
        self.canvas.draw()
        
    def scale_change(self, value):
        if self.scale.get() % 1 != 0:
            value = min(range(self.scale['from'], self.scale['to'] + 1), key=lambda x: abs(self.scale.get() - x)) #ttk
            self.scale.set(value)
        else:
            self.reload()
        
# Pozycje znaków specjalnych w hasłach
class SpecialPosPage(ttk.Frame):
    def __init__(self, master, model, controller, screen_width, screen_height):
        super().__init__(master)
        self.model = model
        self.controller = controller
        self.master = master
        
        self.style = ttk.Style(self)
        self.style.configure('SpecialPosPage.TLabel', font=('Segoe UI', 18))
        self.style.configure('SpecialPosPage.TButton', font=('Segoe UI', 20))
        
        self.figure = Figure(figsize=(5, 4), dpi=100)
        self.plot = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, self)
        self.canvas.get_tk_widget().place(relx=0.5, rely=0.4, anchor='center', relwidth=0.7, relheight=0.7)
        
        ttk.Button(self, text="Wróć", command=lambda: self.master.show_frame(StatsPage), style='SpecialPosPage.TButton').place(relx=0.5, rely=0.95, anchor='center')
        self.range_from_label = ttk.Label(self, style='SpecialPosPage.TLabel')
        self.range_from_label.place(relx=0.2, rely=0.85, anchor='center')
        self.range_to_label = ttk.Label(self, style='SpecialPosPage.TLabel')
        self.range_to_label.place(relx=0.8, rely=0.85, anchor='center')
        self.scale = ttk.Scale(self, from_= 1, to=10, orient='horizontal', command=self.scale_change, value=8) 
        self.scale.place(relwidth=0.5, relx=0.5, rely=0.85, anchor ='center')
        self.range_info_label = ttk.Label(self, style='SpecialPosPage.TLabel', text='Wybierz długość hasła:')
        self.range_info_label.place(relx=0.5, rely=0.8, anchor='center')
        
        self.nb_label = ttk.Label(self, style='SpecialPosPage.TLabel')
        self.nb_label.place(relx=0.90, rely=0.95, anchor='e')
        
    def reload(self):
        self.scale.config(to = len(max(self.model.psswds, key=len)))
        current_fml_length = int(float(self.scale.get()))
        self.fml_to_print = self.model.percentage_frequency2(self.model.fml_special(current_fml_length)[0], current_fml_length)
        self.range_from_label.config(text=f'min {len(min(self.model.psswds, key=len))}')
        self.range_to_label.config(text=f'max {len(max(self.model.psswds, key=len))}')
        self.nb_label.config(text=f'Wykres na podstawie {self.model.fml_special(current_fml_length)[1]} haseł z bazy')

        max_value = max(self.fml_to_print.values())
        norm = mcolors.Normalize(vmin=0, vmax=max_value)
        cmap = plt.get_cmap('viridis')
        mycolor = [cmap(norm(value)) for value in self.fml_to_print.values()]
        
        self.plot.clear()
        self.plot.bar(self.fml_to_print.keys(), self.fml_to_print.values(), edgecolor='black', color=mycolor)
        self.plot.set_title(f'Rozmieszczenie znaków specjalnych dla haseł o długości {current_fml_length}', fontsize=20)
        self.plot.set_xlabel("Pozycja znaku specjalnego w haśle", fontsize=15)
        self.plot.set_ylabel("Procentowy udział", fontsize=15)
        self.plot.tick_params(axis='both', which='major', labelsize=13)
        self.plot.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))
        self.plot.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))
        self.plot.xaxis.set_minor_locator(plt.MultipleLocator(1))
        self.plot.yaxis.set_minor_locator(plt.MultipleLocator(1))
        
        self.plot.set_xlim(left=0.5)
        self.plot.set_xlim(right=current_fml_length+0.5)
        x_min, x_max = self.plot.get_xlim()

        if x_max <= 21:
            self.plot.xaxis.set_major_locator(plt.MultipleLocator(1))
        else:
            self.plot.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))
        
        self.canvas.draw()
        
    def scale_change(self, value):
        if self.scale.get() % 1 != 0:
            value = min(range(self.scale['from'], self.scale['to'] + 1), key=lambda x: abs(self.scale.get() - x))
            self.scale.set(value)
        else:
            self.reload()

# Częstotliwość liter
class CharsFreqPage(ttk.Frame):
    def __init__(self, master, model, controller, screen_width, screen_height):
        super().__init__(master)
        
        self.model = model
        self.controller = controller
        self.master = master
        
        self.style = ttk.Style(self)
        self.style.configure('CharsFreqPage.TLabel', font=('Segoe UI', 18))
        self.style.configure('CharsFreqPage.TButton', font=('Segoe UI', 20))
        self.style.configure('hellinger.TButton', font=('Segoe UI', 14))
        
        self.figure = Figure(figsize=(5, 4), dpi=100)
        self.plot = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, self)
        self.canvas.get_tk_widget().place(relx=0.5, rely=0.4, anchor='center', relwidth=0.7, relheight=0.7)
        
        self.dict_dots = True # True dla kropek z danych słownikowych, False dla kropek z danych z tekstów, flaga przełączająca widok

        ttk.Button(self, text="Wróć", command=lambda: self.master.show_frame(StatsPage), style='CharsFreqPage.TButton').place(relx=0.5, rely=0.95, anchor='center')
        self.sort_button = ttk.Button(self, text="Przełącz rozkład referencyjny", command=self.toggle_view, style='CharsFreqPage.TButton')
        self.sort_button.place(relx=0.05, rely=0.95, anchor='w')
        
        
        
        self.hellinger_info = ttk.Label(self, text="Odległość Hellingera jest miarą służącą do określania podobieństwa między dwoma rozkładami prawdopodobieństwa. Dla obu takich samych rozkładów przyjmuje wartość 0, dla zupełnie różnych - wartość 1", style='hellinger.TButton')
        self.hellinger_info.place(relx=0.5, rely=0.8, anchor='center')
        self.hellinger_label = ttk.Label(self, style='CharsFreqPage.TLabel')
        self.hellinger_label.place(relx=0.5, rely=0.85, anchor ='center')
        
        self.nb_label = ttk.Label(self, style='CharsFreqPage.TLabel')
        self.nb_label.place(relx=0.90, rely=0.95, anchor='e')
        
        self.plot.tick_params(axis='both', which='major', labelsize=13)

    def toggle_view(self):
        self.dict_dots = not self.dict_dots
        self.reload()
        
    def reload(self):
        chartype_cnt = self.model.chartype_cnt('letter')
        self.nb_label.config(text=f'Wykres na podstawie {chartype_cnt} haseł z bazy')
        
        if self.dict_dots:
            chars_freq_to_print = dict(sorted(self.model.chars_freq.items(), key=lambda item: item[1], reverse=True)) # Sortowanie słownika po częstości występowania
            default_freq_to_print = {}
            for key in chars_freq_to_print:
                default_freq_to_print[key] = self.model.default_freq_unsorted[key]
                
            self.plot.clear()
            self.plot.bar(list(chars_freq_to_print.keys()), list(chars_freq_to_print.values()), edgecolor='black', color='#7FFF00', label="Litery najchętniej stosowane przez użytkowników")
            self.plot.set_xlabel('Litera', fontsize=15)
            self.plot.set_ylabel("Procentowy udział", fontsize=15)
            self.plot.scatter(list(default_freq_to_print.keys()), list(default_freq_to_print.values()), marker='o', edgecolor='black', color = 'red', label = "Rozkład częstości występowania liter w słowniku języka angielskiego")
            self.plot.legend(loc=(0.3, 0.8), fontsize='large')

            self.canvas.draw()
        else:
            chars_freq_to_print = dict(sorted(self.model.chars_freq.items(), key=lambda item: item[1], reverse=True)) # Sortowanie słownika po częstości występowania
            default_freq_to_print = {}
            for key in chars_freq_to_print:
                default_freq_to_print[key] = self.model.text_freq[key]
                
            self.plot.clear()
            self.plot.bar(list(chars_freq_to_print.keys()), list(chars_freq_to_print.values()), edgecolor='black', color='#7FFF00', label="Litery najchętniej stosowane przez użytkowników")
            self.plot.set_xlabel('Litera', fontsize=15)
            self.plot.set_ylabel("Procentowy udział", fontsize=15)
            self.plot.scatter(list(default_freq_to_print.keys()), list(default_freq_to_print.values()), marker='o', edgecolor='black', color = 'red', label = "Rozkład częstości występowania liter w tekstach języka angielskiego")
            self.plot.legend(loc=(0.3, 0.8), fontsize='large')

            self.canvas.draw()
            
        chars_freq_norm = self.model.normalize_frequency(chars_freq_to_print)
        ref_freq_norm = self.model.normalize_frequency(default_freq_to_print)
        
        hellinger = round(self.model.hellinger_distance(chars_freq_norm.values(), ref_freq_norm.values()), 4)
        self.hellinger_label.config(text=f"Odległość Hellingera (rozkład badany i standardowy): {hellinger}")

# Częstotliwość znaków specjalnych
class SpcsFreqPage(ttk.Frame):
    def __init__(self, master, model, controller, screen_width, screen_height):
        super().__init__(master)
        
        self.model = model
        self.controller = controller
        self.master = master
        
        self.style = ttk.Style(self)
        self.style.configure('SpcsFreqPage.TLabel', font=('Segoe UI', 18))
        self.style.configure('SpcsFreqPage.TButton', font=('Segoe UI', 20))
        
        self.figure = Figure(figsize=(5, 4), dpi=100)
        self.plot = self.figure.add_subplot(111) 
        self.canvas = FigureCanvasTkAgg(self.figure, self)
        self.canvas.get_tk_widget().place(relx=0.5, rely=0.4, anchor='center', relwidth=0.7, relheight=0.7)
        
        ttk.Button(self, text="Wróć", command=lambda: self.master.show_frame(StatsPage), style='SpcsFreqPage.TButton').place(relx=0.5, rely=0.95, anchor='center')
        
        self.nb_label = ttk.Label(self, style='SpcsFreqPage.TLabel')
        self.nb_label.place(relx=0.5, rely=0.85, anchor ='center')
        
    def reload(self):
        chartype_cnt = self.model.chartype_cnt('special')
        self.nb_label.config(text=f'Wykres na podstawie {chartype_cnt} haseł z bazy')
        
        spcs_freq_to_print = dict(sorted(self.model.spcs_freq.items(), key=lambda item: item[1], reverse=True)) # Sortowanie słownika po częstości występowania
        
        max_value = max(spcs_freq_to_print.values())
        norm = mcolors.Normalize(vmin=0, vmax=max_value)
        cmap = plt.get_cmap('viridis')
        mycolor = [cmap(norm(value)) for value in spcs_freq_to_print.values()]
        
        self.plot.clear()
        self.plot.bar(list(spcs_freq_to_print.keys()), list(spcs_freq_to_print.values()), edgecolor = 'black', color=mycolor)
        self.plot.set_title("Znaki specjalne najchętniej stosowane przez użytkowników", fontsize=20)
        self.plot.set_xlabel('Znak specjalny', fontsize=15)
        self.plot.set_ylabel("Procentowy udział", fontsize=15)
        
        self.plot.tick_params(axis='both', which='major', labelsize=13)
        self.canvas.draw()
        
# Częstotliwość występowania cyfr
class NumFreqPage(ttk.Frame):
    def __init__(self, master, model, controller, screen_width, screen_height):
        super().__init__(master)
        self.model = model
        self.controller = controller
        self.master = master
        
        self.style = ttk.Style(self)
        self.style.configure('NumFreqPage.TLabel', font=('Segoe UI', 18))
        self.style.configure('NumFreqPage.TButton', font=('Segoe UI', 20))
        
        self.figure = Figure(figsize=(5, 4), dpi=100)
        self.plot = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, self)
        self.canvas.get_tk_widget().place(relx=0.5, rely=0.4, anchor='center', relwidth=0.7, relheight=0.7)
        
        ttk.Button(self, text="Wróć", command=lambda: self.master.show_frame(StatsPage), style='NumFreqPage.TButton').place(relx=0.5, rely=0.95, anchor='center')
        
        self.nb_label = ttk.Label(self, style='NumFreqPage.TLabel')
        self.nb_label.place(relx=0.5, rely=0.85, anchor ='center')

    def reload(self):
        chartype_cnt = self.model.chartype_cnt('digit')
        self.nb_label.config(text=f'Wykres na podstawie {chartype_cnt} haseł z bazy')
        max_value = max(self.model.num_freq.values())
        norm = mcolors.Normalize(vmin=0, vmax=max_value)
        cmap = plt.get_cmap('viridis')
        mycolor = [cmap(norm(value)) for value in self.model.num_freq.values()]
                
        self.plot.clear()
        keys_to_display = list(self.model.num_freq.keys())
        self.plot.bar(list(self.model.num_freq.keys()), list(self.model.num_freq.values()), edgecolor='black', color=mycolor)
        self.plot.set_title("Cyfry najchętniej stosowane przez użytkowników", fontsize=20)
        self.plot.set_xlabel("Cyfra", fontsize=15)
        self.plot.set_ylabel("Procentowy udział", fontsize=15)
        self.plot.tick_params(axis='both', which='major', labelsize=13)
        
        self.canvas.draw()

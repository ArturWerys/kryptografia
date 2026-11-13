import tkinter as tk
import nltk
import math
import time
from datetime import datetime
import itertools
from tkinter import messagebox
import unidecode  # biblioteka do konwersji diakrytyków
import matplotlib.pyplot as plt
import re
import threading
import concurrent.futures
from itertools import product
from typing import List, Set
import os
from pathlib import Path
import sys

class PasswordStrengthChecker:
    def __init__(self, root):
        # Inicjalizacja komponentów GUI aplikacji
        self.root = root
        self.root.title("Sprawdzanie siły hasła")

        # Tworzenie i umieszczanie etykiety dla hasła
        self.password_label = tk.Label(root, text="Wprowadź hasło:")
        self.password_label.pack()

        # Widget do wprowadzania hasła, znaki zastąpione przez '*'
        self.password_entry = tk.Entry(root, width=60, show='*')
        self.password_entry.pack()
        self.show_password_var = tk.BooleanVar()

        show_password_check = tk.Checkbutton(root, text='Pokaż hasło', variable=self.show_password_var, onvalue=True,
                                             offvalue=False, command=self.toggle_password)
        show_password_check.pack()

        # Pole wyboru do przełączania widoczności hasła
        self.check_button = tk.Button(root, text="Sprawdź siłę hasła", command=self.check_password)
        self.check_button.pack()

        # Obszar tekstowy do wyświetlania wyników
        self.result_area = tk.Text(root, wrap=tk.WORD, height=35, width=80)
        self.result_area.pack()

        self.polish_words = self.load_words('polskie_slowa.txt')

    def toggle_password(self):
        # Funkcja przełączająca widoczność hasła
        if self.show_password_var.get():
            self.password_entry.config(show='')
        else:
            self.password_entry.config(show='*')
    def check_password_space(self, password):
        # Analiza składu hasła: małe litery, wielkie litery, cyfry, znaki specjalne
        has_lowercase = any(char.islower() for char in password)
        has_uppercase = any(char.isupper() for char in password)
        has_digits = any(char.isdigit() for char in password)
        has_special_chars = not password.isalnum()

        result = []
        result2 = 0
        if has_lowercase:
            result.append('małe litery (32 możliwe litery)')
            result2 += 32 #polskie
        if has_uppercase:
            result.append('duże litery (32 możliwe litery)')
            result2 += 32 #polskie
        if has_digits:
            result.append('cyfry (10 możliwych cyfr)')
            result2 += 10
        if has_special_chars:
            result.append('znaki specjalne (33 możliwe znaki)')
            result2 += 33

        return ', '.join(result), pow(result2, len(password))

    def calculate_strength(self, password):
        # Obliczanie siły hasła na podstawie entropii
        entropy = math.log2(self.check_password_space(password)[1])
        strength = "Bardzo słabe"
        if entropy >= 120:
            strength = "Bardzo silne"
        elif 119 >= entropy >= 60:
            strength = "Silne"
        elif 59 >= entropy >= 36:
            strength = "Słabe"
        return strength

    def find_ordered_sequences(self, password, type='alphabetical'):
        # Szukanie sekwencji uporządkowanych w haśle (alfabetycznych lub numerycznych) w obie stroby - abc orac cba, 123 oraz 321...
        sequences = []
        current_sequence = ''
        filtered_password = ''
        alphabet = ''
        reverse_alphabet = ''

        if type == 'alphabetical': #alfabetycznych
            filtered_password = ''.join(filter(str.isalpha, password.lower())) # Filtruje hasło do liter, przekształcając je na małe litery
            polish_chars = set('ąćęłńóśżź')
            if any(char in polish_chars for char in filtered_password):
                alphabet = 'aąbcćdeęfghijklłmnńoóprsśtuwyzźż' # Użycie polskiego alfabetu jeśli występują polskie znaki
                reverse_alphabet = alphabet[::-1]
            else:
                alphabet = 'abcdefghijklmnopqrstuvwxyz' # Użycie standardowego alfabetu angielskiego
                reverse_alphabet = alphabet[::-1]

        if type == 'numerical': #numerycznych
            filtered_password = ''.join(filter(str.isdigit, password)) # Filtruje hasło do cyfr
            alphabet = '0123456789'
            reverse_alphabet = alphabet[::-1]

        order_map = {char: (index, -index) for index, char in enumerate(alphabet)}
        reverse_order_map = {char: (index, -index) for index, char in enumerate(reverse_alphabet)}

        def get_next_expected(char, last_char):
            # Pomocnicza funkcja do określania czy znaki są sekwencyjne
            if char in order_map and last_char in order_map:
                if order_map[char][0] == order_map[last_char][0] + 1:
                    return 1  # następny w sekwencji
                elif reverse_order_map[char][0] == reverse_order_map[last_char][0] + 1:
                    return -1  # poprzedni w sekwencji
            return 0  # nie w sekwencji

        for char in filtered_password:
            if current_sequence:
                next_expected = get_next_expected(char, current_sequence[-1])
                if next_expected != 0:
                    current_sequence += char
                else:
                    if len(current_sequence) >= 2:
                        sequences.append(current_sequence)
                    current_sequence = char
            else:
                current_sequence = char

        if len(current_sequence) >= 2:
            sequences.append(current_sequence)

        return sequences

    def find_qwerty_sequences(self, word):
        # Szukanie sekwencji klawiaturowych w haśle
        # Definiujemy ciągi znaków dla każdego z rzędów klawiatury QWERTY
        qwerty_rows = [
            "-=qwertyuiop[]\\asdfghjkl;'zxcvbnm,./",
            "\][poiuytrewq';lkjhgfdsa/.,mnbvcxz",
            "|}{POIUYTREWQ\":LKJHGFDSA?><MNBVCXZ",
            "`1234567890-=",
            "=-0987654321`",
            "qazwsxedcrfvtgbyhnujmik,ol.p;/[']\\",
            "zaqxswcdevfrbgtnhymju,ki.lo/;p'[]\\",
            "1qaz2wsx3edc4rfv5tgb6yhn7ujm8ik,9ol.0p;/-['=]\\",
            "zaq1xsw2cde3vfr4bgt5nhy6mju7,ki8.lo9/;p0'[-]=\\",
            "]'/[;.pl,okmijnuhbygvtfcrdxeszwaq",
            "/'].;[,lpmkonjibhuvgycftxdrzseawq",
            "]'/=[;.-pl,0okmm9ijn8uhb7ygv6tfc5rdx4esz3wa2q1",
            "/'].;[=,lp-mko0nji9bhu8vgy7cft6xdr5zse4aw3q21",
            "qawzsexdrcftvgybhunjimko,lp.;[/']",
            "1q2aw3zse4xdr5cft6vgy7bhu8nji9mko0,lp-.;[=/']\\",
            "]'[/;p.lo,kimjunhybgtvfrcdexswzaq",
            "\\]='[-/;p0.lo9,ki8mju7nhy6bgt5vfr4cde3xsw2zaq1",
            "_+QWERTYUIOP{}|ASDFGHJKL:\"ZXCVBNM<>?\"",
            "QAZWSXEDCRFVTGBYHNUJMIK<OL>P:?{\"}|",
            "ZAQXSWCDEVFRBGTNHYMJU<KI>LO?:P\"{}|",
            "!QAZ@WSX#EDC$RFV%TGB^YHN&UJM*IK<(OL>)P:?_{\"+}|",
            "ZAQ!XSW@CDE#VFR$BGT%NHY^MJU&<KI*>LO(?:P)\"{_}+|",
            "}\"?{:>PL<OKMIJNUHBYGVTFCRDXESZWAQ}",
            "?\"}>:{<LPMKONJIBHUVGYCFTXDRZSEAWQ}",
            "}~\"?+{:>_PL<)OKM(IJN*UHB&YGV^TFC%RDX$ESZ#WA@Q!}"
            "?\"}>:{<LPMKONJIBHUVGYCFTXDRZSEAWQ",
            "QAWZSEXDRCFTVGYBHUNJIMKO<LP>:{?\"}|",
            "!Q@AW#ZSE$XDR%CFT^VGY&BHU*NJI(MKO)<LP_>:{+?\"}|",
            "}\"{?:P>LO<KIMJUNHYBGTVFRCDEXSWZAQ",
            "|}\"{_?:P)>LO(<KI*MJU&NHY^BGT%VFR$CDE#XSW@ZAQ!"


            "~!@#$%^&*()_+",
            "+_)(*&^%$#@!"
        ]

        results = []

        # Analiza każdego rzędu z osobna
        for row in qwerty_rows:
            max_sequences = []
            # Szukamy wszystkich możliwych sekwencji o długości co najmniej 3 znaki
            for start in range(len(row) - 2):
                for end in range(start + 3, len(row) + 1):
                    sub_seq = row[start:end]
                    index = word.find(sub_seq)
                    if index != -1:
                        # Sprawdzamy czy nowa sekwencja nie pokrywa się z już znalezionymi
                        overlaps = False
                        for i, (pos, seq) in enumerate(max_sequences):
                            if pos <= index < pos + len(seq) or pos < index + len(sub_seq) <= pos + len(seq):
                                # Jeśli nowa sekwencja jest dłuższa, zastępujemy starą
                                if len(sub_seq) > len(seq):
                                    max_sequences[i] = (index, sub_seq)
                                overlaps = True
                                break
                        if not overlaps:
                            max_sequences.append((index, sub_seq))
            # Dodajemy tylko najdłuższe sekwencje z rzędu
            results.extend(seq for _, seq in sorted(max_sequences, key=lambda x: x[1]))

        return results

    def check_middle_sequence(self, middle_part):
        # Sprawdza czy w środkowej części hasła znajdują się tylko cyfry lub znaki specjalne
        seq = ''
        first_index = None
        last_index = None

        for i, char in enumerate(middle_part):
            if not char.isalpha():
                if first_index is None:
                    first_index = i
                last_index = i

        if first_index is not None and last_index is not None:
            seq = middle_part[first_index:last_index + 1]

        if any(char.isalpha() for char in seq):
            return False
        else:
            return True

    def analyze_signs_placements(self, password):
        # Sprawdzanie, gdzie znajdują się cyfry i znaki specjalne
        digits_or_specials_at_start = bool(re.match(r'^[^a-zA-Z]+', password))
        digits_or_specials_at_end = bool(re.search(r'[^a-zA-Z]+$', password))
        middle_part = password.rstrip('0123456789!@#$%^&*()_+-=[]{}|;:\'",.<>?/`~').lstrip('0123456789!@#$%^&*()_+-=[]{}|;:\'",.<>?/`~')
        digits_or_specials_in_middle = any(not char.isalpha() for char in middle_part)
        wage = 5

        # Analiza, czy cyfry lub znaki specjalne są tylko na początku, końcu, początku i końcu
        position = 'w nieoczekiwanych miejscach'
        if digits_or_specials_at_start and not digits_or_specials_at_end and not digits_or_specials_in_middle:
            position = 'w typowym miejscu (tylko na początku)'
            wage = 1
        elif not digits_or_specials_at_start and digits_or_specials_at_end and not digits_or_specials_in_middle:
            position = 'w typowym miejscu (tylko na końcu)'
            wage = 0
        elif digits_or_specials_at_start and digits_or_specials_at_end and not digits_or_specials_in_middle:
            position = 'w typowych miejscach (tylko na początku i końcu)'
            wage = 2
        elif digits_or_specials_in_middle and not digits_or_specials_at_start and not digits_or_specials_at_end:
            if self.check_middle_sequence(middle_part):
                position = 'w typowym miejscu (tylko na środku)'
                wage = 4
            else:
                position = 'w nieoczekiwanych miejscach'
        return position, wage / 5

    def load_words(self, file_path):
        # Wczytuje listę słów z pliku do zestawu (set), usuwając z nich akcenty i konwertując na małe litery
        with open(file_path, 'r', encoding='utf-8', errors='replace') as file:
            words_set = set()
            for word in file:
                clean_word = word.strip().lower()
                if clean_word.isalpha():  # Sprawdza, czy słowo składa się tylko z liter
                    words_set.add(clean_word)
                    words_set.add(unidecode.unidecode(clean_word))
            return words_set

    def find_words_in_password(self, password):
        # Szuka słów ze słownika w haśle# Szuka słów ze słownika w haśle
        clean_password = ''.join(filter(str.isalpha, password.lower()))

        # Ładujemy listę słów
        try:
            # Spróbuj znaleźć zasób 'words'
            nltk.find('corpora/words')
        except LookupError:
            # Jeśli zasób nie jest dostępny, pobierz go
            nltk.download('words')

        # Angielskie słowa z NLTK
        english_words = set(nltk.corpus.words.words())

        # Zestaw polskich słów
        polish_words_set = set(self.polish_words)

        # Łączymy słowa z obu języków, z oznaczeniem ich pochodzenia
        word_list = {}
        for word in english_words:
            if len(word) >= 3:  # Filtrujemy słowa mające co najmniej 3 litery
                word_list[word] = 'słownik ANG'
        for word in polish_words_set:
            if len(word) >= 3:  # Filtrujemy słowa mające co najmniej 3 litery
                word_list[word] = 'słownik PL'

        found_words = []

        # Szukamy najdłuższych słów w haśle
        start = 0
        while start < len(clean_password):
            found_in_iteration = False
            for end in range(len(clean_password), start, -1):
                word = clean_password[start:end]
                if word in word_list:
                    source = word_list[word]  # Pobieramy źródło słowa
                    found_words.append((f"{word} ({source})"))
                    start = end  # Przeskakujemy do końca znalezionego słowa
                    found_in_iteration = True
                    break
            if not found_in_iteration:
                start += 1

        return found_words

    def check_randomness(self, password):
        # Sprawdza losowość hasła na podstawie występujących w nim sekwencji
        wage = 1
        sequence = self.find_ordered_sequences(password, 'alphabetical')
        if len(sequence) > 0:
            result = f"Sekwencje w kolejności alfabetycznej w haśle: {sequence}\n\n"
        else:
            result = f"Brak sekwencji w kolejności alfabetycznej w haśle.\n\n"
        sequence2 = self.find_ordered_sequences(password, 'numerical')
        sequence.extend(sequence2)
        if len(sequence2) > 0:
            result += f"Sekwencje w kolejności numerycznej w haśle: {sequence2}\n\n"
        else:
            result += f"Brak sekwencji w kolejności numerycznej w haśle.\n\n"
        qwerty = self.find_qwerty_sequences(password)
        wage -= (sum(len(s) for s in sequence) + sum(len(s) for s in qwerty)) / len(password)
        if len(qwerty) > 0:
            result += f"Sekwencje klawiaturowe w haśle: {set(qwerty)}\n\n"
        else:
            result += f"Brak sekwencji klawiaturowej w haśle.\n\n"
        found_words = self.find_words_in_password(password)
        if len(found_words) == 0:
            wage += 1
        for word in found_words:
            result += f"'{word}' jest słowem.\n\n"
        if not any(char.isdigit() for char in password) and password.isalnum():
            if sum(len(word) for word in found_words) == len(password) and len(found_words) == 1:
                result += f"Twoje hasło jest całkowicie nielosowe.\n"
            else:
                result += f"W skali od 0 do 2, gdzie 0 wskazuje całkowity brak losowości, a 2 całkowitą losowość, twoje hasło przyjmuje wartość {abs(wage):.2f}\n"
        else:
            signs_placement = self.analyze_signs_placements(password)
            result += f'Cyfry/znaki specjalne znajdują się {signs_placement[0]}.\n\n'
            wage += signs_placement[1]
            result += f"W skali od 0 do 3, gdzie 0 wskazuje całkowity brak losowości, a 3 całkowitą losowość, twoje hasło przyjmuje wartość {abs(wage):.2f}\n"
        return result

    def classify_input(self, input_string):
        # Klasyfikuje wprowadzone hasło na podstawie jego struktury (np. tylko litery, litery i cyfry itp.)
        pattern_classes_data = {
            'L+': 35.4925, 'L+N+': 28.27, 'N+': 14.6075, 'N+L+': 3.88,
            'U+': 2.445, 'L+N+L+': 1.8625, 'U+N+': 1.51, 'U+L+N+': 1.0975,
            'L+O+N+': 0.995, 'N+L+N+': 0.6125, 'L+O+L+': 0.3, 'Inne': 1
        }

        classes_data = [
            'L+ (same litery)', 'L+N+ (litery-cyfry)', 'N+ (same cyfry)', 'N+L+ (cyfry-litery)',
            'U+ (wielkie litery)', 'L+N+L+', 'U+N+', 'U+L+N+',
            'L+O+N+', 'N+L+N+', 'L+O+L+', 'Inne'
        ]

        pattern_descriptions = {
            'L': 'małe litery (lowercase)',
            'U': 'wielkie litery (uppercase)',
            'N': 'cyfry (numbers)',
            'O': 'inne (others) - znaki specjalne',
        }

        # Generowanie wzorca na podstawie pierwszego znaku i kolejnych zmian w typach znaków
        pattern = ''
        if input_string[0].isupper():
            pattern += 'U+'
        elif input_string[0].islower():
            pattern += 'L+'
        elif input_string[0].isdigit():
            pattern += 'N+'
        elif not input_string[0].isalnum():
            pattern += 'O+'
        for i in range(1, len(input_string)):
            if input_string[i].isupper() and not input_string[i - 1].isupper():
                pattern += 'U+'
            elif input_string[i].islower() and not input_string[i - 1].islower():
                pattern += 'L+'
            elif input_string[i].isdigit() and not input_string[i - 1].isdigit():
                pattern += 'N+'
            elif input_string[i - 1].isalnum() and not input_string[i].isalnum():
                pattern += 'O+'

        if pattern not in pattern_classes_data:
            pattern = 'Inne'

        # Wizualizacja danych za pomocą wykresu słupkowego
        pattern_index = list(pattern_classes_data.keys()).index(pattern)
        colors = ['blue' if i != pattern_index else 'red' for i in range(len(pattern_classes_data))]

        plt.figure(figsize=(14, 8))
        plt.bar(classes_data, pattern_classes_data.values(), color=colors)

        plt.title('Najbardziej typowe konstrukcje haseł')
        plt.xlabel('Wzorce typowych haseł')
        plt.ylabel('Częstość występowania wzorca [%]')

        plt.xticks(rotation=45, ha='right')

        handles = [plt.Line2D([0], [0], marker='o', color='green', label=f'{key}: {val}',
                              markerfacecolor='green', markersize=10) for key, val in pattern_descriptions.items()]
        plt.legend(handles=handles, title="Opis wzorców", loc='upper right')

        plt.tight_layout()
        plt.show()

    def time_unit(self, time):
        # Przelicza czas na odpowiednie jednostki w zależności od jego długości
        unit = "sekund"
        if time < 1:
            if time >= 1e-3:
                time *= 1e3
                unit = "milisekund (10^-3 sekundy)"
            elif time >= 1e-6:
                time *= 1e6
                unit = "mikrosekund (10^-6 sekundy)"
            elif time >= 1e-9:
                time *= 1e9
                unit = "nanosekund (10^-9 sekundy)"
            elif time >= 1e-12:
                time *= 1e12
                unit = "pikosekund (10^-12 sekundy)"
            elif time >= 1e-15:
                time *= 1e15
                unit = "femtosekund (10^-15 sekundy)"
            elif time >= 1e-18:
                time *= 1e18
                unit = "attosekund (10^-18 sekundy)"
            elif time >= 1e-21:
                time *= 1e21
                unit = "zeptosekund (10^-21 sekundy)"
            else:
                time *= 1e24
                unit = "joktosekund (10^-24 sekundy)"
        elif time > 100 and time <= 6000:
            time = time / 60
            unit = "minut"
        elif time > 6000 and time <= 360000:
            time = time / 3600
            unit = "godzin"
        elif time > 360000 and time <= 31536000:
            time = time / 86400
            unit = "dni"
        elif time > 31536000 and time <= 257126400:
            time = time / 86400
            unit = "miesięcy"
        elif time > 257126400:
            time = time / 31536000
            if time > 13.8e9:
                time = time / 13.8e9
                unit = "czasów życia wszechświata"
            else:
                time = self.format_number(time, True)
                unit = "lat"
                return f"{time} {unit}"

        if f"{time}".endswith('.0'):
            time = f"{time}"[:-2]
        else:
            time = f"{time:.2f}"
        return f"{time} {unit}"

    def cracking_time(self, combinations):
        # Oblicza szacowany czas potrzebny do złamania hasła przy użyciu różnych mocy obliczeniowych
        results = ""
        time = combinations / 40000000  # NVIDIA RTX 30xx
        results += f"Czas na złamanie hasła przy użyciu domowej karty graficznej za 3000 zł (NVIDIA RTX 30xx; hashrate 40MH/s): {self.time_unit(time)}\n\n"

        time = combinations / 630e18
        results += f"Czas na złamanie hasła przy użyciu mocy obliczeniowej sieci bitcoinów (hashrate 630EH/s): {self.time_unit(time)}\n\n"
        return results

    def format_number(self, num, Y=False):
        # Formatuje liczby do czytelnej postaci, szczególnie przy bardzo dużych wartościach
        if num < 10000:
            if Y:
                return f"{num:.2f}"
            else:
                return f"{num:}"
        else:
            # Przekształcanie liczby na notację naukową dla łatwiejszego odczytu
            exponent = len(str(abs(int(num)))) - 1
            base = num / (10 ** exponent)
            if num < 1000000:
                return f"{base:.2f}*10^{exponent}"
            else:
                return f"{base:.0f}*10^{exponent}"

    def check_password(self):
        # Główna funkcja wywoływana po naciśnięciu przycisku "Sprawdź siłę hasła"
        password = self.password_entry.get()
        self.result_area.delete(1.0, tk.END)

        # Analiza przestrzeni hasła i obliczenie liczby możliwych kombinacji
        password_space = self.check_password_space(password)[0]
        combinations = self.check_password_space(password)[1]

        # Obliczenie i ocena siły hasła
        strength = self.calculate_strength(password)

        # Obliczenie czasu potrzebnego do złamania hasła
        cracking_info = self.cracking_time(combinations)

        # Sprawdzenie losowości hasła
        randomness_info = self.check_randomness(password)

        # Formatowanie liczby kombinacji do czytelnej postaci
        combinations = self.format_number(combinations)

        # Zestawienie wyników i wyświetlenie ich w obszarze tekstowym
        result_text = f"Przestrzeń hasła: {password_space}.\n\nMaksymalna liczba kombinacji to {combinations}\n\nSiła hasła: {strength}\n\n{cracking_info}{randomness_info}"
        self.result_area.insert(tk.INSERT, result_text)

        # Wywołanie funkcji klasyfikującej wzorzec hasła
        self.classify_input(password)

class PasswordGenerator:
    def __init__(self, root):
        # Inicjalizacja interfejsu użytkownika dla generatora haseł
        self.passesgen = None
        self.passesgenWin = None
        self.root = root
        self.root.title("Generowanie haseł")

        # Tworzenie i pakowanie etykiet i pól do wprowadzania imienia, drugiego imienia i nazwiska
        self.label1 = tk.Label(root, text="Podaj imię:")
        self.label1.pack()
        self.entry1 = tk.Entry(root)
        self.entry1.pack()

        self.label2 = tk.Label(root, text="Podaj drugie imię (opcjonalne):")
        self.label2.pack()

        self.entry2 = tk.Entry(root)
        self.entry2.pack()

        self.label3 = tk.Label(root, text="Podaj nazwisko:")
        self.label3.pack()

        self.entry3 = tk.Entry(root)
        self.entry3.pack()

        # Tworzenie i pakowanie pól do wprowadzania daty urodzenia
        self.frame = tk.Frame(root)
        self.frame.pack()
        self.label4 = tk.Label(self.frame, text="Podaj datę urodzenia:")
        self.label4.pack()
        self.label41 = tk.Label(self.frame, text="Dzień:")
        self.label41.pack(side=tk.LEFT)
        self.entry41 = tk.Entry(self.frame, width=5)
        self.entry41.pack(side=tk.LEFT)
        self.label42 = tk.Label(self.frame, text="Miesiąc:")
        self.label42.pack(side=tk.LEFT)
        self.entry42 = tk.Entry(self.frame, width=5)
        self.entry42.pack(side=tk.LEFT)
        self.label43 = tk.Label(self.frame, text="Rok:")
        self.label43.pack(side=tk.LEFT)
        self.entry43 = tk.Entry(self.frame, width=5)
        self.entry43.pack(side=tk.LEFT)

        # Tworzenie i pakowanie pola do wprowadzenia ulubionej rzeczy
        self.label5 = tk.Label(root, text="Nazwa/imię twojej ulubionej rzeczy/sympatii/zwierzaka:")
        self.label5.pack()

        self.entry5 = tk.Entry(root)
        self.entry5.pack()

        # Przycisk do generowania haseł
        self.check_button = tk.Button(root, text="Wygeneruj hasła", command=self.generate)
        self.check_button.pack()

        # Etykieta opisująca transformacje stosowane do generacji haseł
        self.label6 = tk.Label(root, height=20, width=70, text=f"\n\nDo generacji haseł stosowane są następujące transformacje:\n\n" \
                        f"1. Zmiana formatów daty.\n\n" \
                        f"2. Zamiana liter małych na duże.\n\n" \
                        f"2. Zamiana liter dużych na małe.\n\n" \
                        f"4. Zamiana podobnych graficznie znaków:\n\n" \
                        f"a - @\n" \
                        f"o - 0\n" \
                        f"e - 3\n" \
                        f"i - 1\n" \
                        f"l - !\n" \
                        f"s - $\n" \
                        f"s - 5\n" \
                        f"z - 2\n")
        self.label6.pack()

        # Obszar tekstowy do wyświetlania wyników generacji haseł
        self.result_area = tk.Text(root, wrap=tk.WORD, height=20, width=90)
        self.result_area.pack()

    def apply_transformations(self, word: str, chunk_size: int = 10000, max_transformations: int = 1000) -> Set[str]:
        # Mapa transformacji dla określonych liter
        transformations = {
            'a': ['@'],
            'o': ['0'],
            'e': ['3'],
            'i': ['1'],
            'l': ['!'],
            's': ['$', '5'],
            'z': ['2']
        }

        # Funkcja pomocnicza do generowania wszystkich możliwych transformacji dla danej litery
        def generate_transformations(char: str):
            char_lower = char.lower()
            return [char, char.upper()] + transformations.get(char_lower, [])

        # Lista list wszystkich możliwych transformacji dla każdej litery
        all_transformed = [generate_transformations(char) for char in word]

        # Funkcja do generowania transformacji w danym zakresie
        def generate_chunk(start: int, end: int, max_transformations: int) -> Set[str]:
            transformed_words = set()
            count = 0
            for combo in itertools.islice(itertools.product(*all_transformed), start, end):
                if count >= max_transformations:
                    break
                transformed_words.add(''.join(combo))
                count += 1
            return transformed_words

        transformed_words = set()

        # Obliczanie ilości wszystkich możliwych kombinacji
        total_combinations = 1
        for transforms in all_transformed:
            total_combinations *= len(transforms)

        # Przygotowanie kawałków do przetworzenia
        chunks = [(i, min(i + chunk_size, total_combinations)) for i in range(0, total_combinations, chunk_size)]

        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = []
            for start, end in chunks:
                # Dodaj zadania do wykonania w wątkach
                futures.append(executor.submit(generate_chunk, start, end, max_transformations))

            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                transformed_words.update(result)
                # Przerwij, jeśli osiągnięto limit liczby transformacji
                if len(transformed_words) >= max_transformations:
                    break

        # Dodaj oryginalne słowo do zbioru wyników
        transformed_words.add(word)

        return transformed_words

    def generate_date_formats(self, date_str):
        # Generowanie różnych formatów daty z podanego ciągu daty
        date_formats = ["%d%m%Y", "%m%d%Y", "%d/%m/%Y", "%m/%d/%Y", "%Y-%m-%d",
                        "%d-%m-%Y", "%Y/%m/%d", "%m-%d-%Y"]

        formatted_dates = []
        for date_format in date_formats:
            formatted_date = date_str.strftime(date_format)
            formatted_dates.append(formatted_date)

        return formatted_dates

    def combine_strings(self, *lists):
        # Kombinowanie list stringów w możliwe kombinacje
        all_combinations = product(*lists)
        combined_strings = []
        count = 0
        for combination in all_combinations:
            combined_strings.append(''.join(combination))
            count+=1
            if count > 15:
                break
        # combined_strings = [''.join(combination) for combination in set(all_combinations)]  # używamy set() aby usunąć duplikaty
        return combined_strings

    def combine_lists(self, elements):
        # Generowanie kombinacji indeksów na podstawie liczby elementów
        if len(elements) == 7:
            values = [0, 1, 2, 3, 4, 5, 6]
        else:
            values = [0, 1, 2, 3, 4, 5, 6, 7]
        result = []
        for r in range(2, len(values) + 1):
            combs = product(values, repeat=r)
            for comb in combs:
                if len(set(comb)) == len(comb):  # Filtracja kombinacji z powtórzeniami
                    result.append(comb)
        return result

    def generate_passwords(self, first_name, middle_name, last_name, fav, day, month, year):
        # Główna funkcja generująca hasła na podstawie wprowadzonych danych
        birth_date = datetime.strptime(day+month+year, "%d%m%Y")
        if middle_name != "":
            elements = [first_name.lower(), middle_name.lower(), last_name.lower(), birth_date, fav.lower(), day, month, year]
        else:
            elements = [first_name.lower(), last_name.lower(), birth_date, fav.lower(), day, month, year]

        passwords = set()
        start_time = time.time()  # Start odmierzania czasu

        combinations = {}
        counts = {}

        for pos, elem in enumerate(elements):
            if elem not in {birth_date, day, month, year}:
                combinations[pos] = self.apply_transformations(elem)
                counts[pos] = len(combinations[pos])
            elif elem == birth_date:
                combinations[pos] = self.generate_date_formats(elem)
            else:
                combinations[pos] = elem
            passwords.update(combinations[pos])

        combined_lists = self.combine_lists(elements)
        # Ustawienie maksymalnej wartości paska postępu
        while len(passwords) < 2000000:
            previous_length = len(passwords)  # Zapisz bieżącą liczbę haseł
            for cl in combined_lists:
                args = [combinations[i] for i in cl]
                combined = self.combine_strings(*args)
                passwords.update(combined)
                # Przerwij, jeśli liczba haseł się nie zmieniła
                if previous_length == len(passwords):
                    break
                if len(passwords) > 2000000:
                    break
            # Przerwij, jeśli liczba haseł się nie zmieniła
            if previous_length == len(passwords):
                break

        end_time = time.time()  # Koniec odmierzania czasu
        elapsed_time = end_time - start_time

        return passwords, elapsed_time, counts

    def get_valid_input(self, user_input, validation_func, error_message):
        # Walidacja danych wejściowych
        if validation_func(user_input):
            return user_input
        else:
            messagebox.showerror("Błąd", error_message)
            return None

    def validate_name(self, input_str):
        # Prosta walidacja, czy ciąg jest niepusty
        return bool(input_str.strip())

    def validate_date(self, input_str):
        # Walidacja, czy podana data jest poprawna
        if not input_str.strip():
            return False
        try:
            datetime.strptime(input_str, "%d%m%Y")
            return True
        except ValueError:
            return False

    def setup_window(self):
        # Ustawienie okna dla wyświetlenia wygenerowanych haseł
        self.passesgenWin = tk.Toplevel(self.root)
        self.passesgenWin.title("Lista Haseł")

        # Utworzenie Scrollbar i przypisanie jego funkcji do widoku y Text widgetu
        scrollbar = tk.Scrollbar(self.passesgenWin)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.passesgen = tk.Text(self.passesgenWin, height=40, width=80, wrap="word")
        self.passesgen.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Skonfiguruj Text i Scrollbar, aby współpracowały razem
        self.passesgen.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.passesgen.yview)

    def auto_scroll(self):
        # Automatyczne przewijanie listy haseł
        if self.auto_scrolling:
            self.passesgen.see(tk.END)
            self.passesgen.after(1, self.auto_scroll)
        else:
            self.passesgen.see(tk.END)

    def print_passwords_iteratively(self, passwords, index=0):
        # Iteracyjne wyświetlanie haseł w interfejsie użytkownika
        if index < len(passwords):
            self.passesgen.insert(tk.END, passwords[index] + "\n")
            self.passesgen.see(tk.END)
            self.passesgen.after(70, lambda: self.print_passwords_iteratively(passwords, index + 1))
        else:
            self.auto_scrolling = False

    def display_passwords(self, passwords):
        # Wyświetlanie wygenerowanych haseł
        self.auto_scrolling = True  # Start auto-scrolling
        self.passesgen.delete(1.0, tk.END)
        passwords = sorted(passwords, key=len)
        with open('WygenerowaneHasła.txt', 'w', encoding='utf-8', errors='replace') as file:
            for password in passwords:
                file.write(password + '\n')
        # if len(passwords) > 400:
        #     # Wyświetl wszystkie hasła oprócz ostatnich 400
        #     for password in passwords[:-400]:
        #         self.passesgen.insert(tk.END, password + "\n")
            # Rozpocznij iteracyjne wyświetlanie ostatnich 400 haseł
        # self.print_passwords_iteratively(passwords[-400:], 0)

        # Podziel hasła na partie i wyświetlaj je stopniowo
        chunk_size = 10000  # Liczba haseł na raz
        for i in range(0, len(passwords), chunk_size):
            chunk = passwords[i:i + chunk_size]
            self.passesgen.insert(tk.END, "\n".join(chunk) + "\n")
            self.passesgen.update_idletasks()  # Aktualizacja interfejsu po każdym kroku

    def time_unit(self, time):
        # Przelicza czas na odpowiednie jednostki w zależności od jego długości
        unit = "sekund"
        if time < 1:
            if time >= 1e-3:
                time *= 1e3
                unit = "milisekund (10^-3 sekundy)"
            elif time >= 1e-6:
                time *= 1e6
                unit = "mikrosekund (10^-6 sekundy)"
            elif time >= 1e-9:
                time *= 1e9
                unit = "nanosekund (10^-9 sekundy)"
            elif time >= 1e-12:
                time *= 1e12
                unit = "pikosekund (10^-12 sekundy)"
            elif time >= 1e-15:
                time *= 1e15
                unit = "femtosekund (10^-15 sekundy)"
            elif time >= 1e-18:
                time *= 1e18
                unit = "attosekund (10^-18 sekundy)"
            elif time >= 1e-21:
                time *= 1e21
                unit = "zeptosekund (10^-21 sekundy)"
            else:
                time *= 1e24
                unit = "joktosekund (10^-24 sekundy)"
        elif time > 100 and time <= 6000:
            time = time / 60
            unit = "minut"
        elif time > 6000 and time <= 360000:
            time = time / 3600
            unit = "godzin"
        elif time > 360000 and time <= 31536000:
            time = time / 86400
            unit = "dni"
        elif time > 31536000 and time <= 257126400:
            time = time / 86400
            unit = "miesięcy"
        elif time > 257126400:
            time = time / 31536000
            if time > 13.8e9:
                time = time / 13.8e9
                unit = "czasów życia wszechświata"
            else:
                time = self.format_number(time, True)
                unit = "lat"
                return f"{time} {unit}"

        if f"{time}".endswith('.0'):
            time = f"{time}"[:-2]
        else:
            time = f"{time:.2f}"
        return f"{time} {unit}"

    def generate(self):
        # Główna funkcja wywoływana przez przycisk "Wygeneruj hasła"
        self.result_area.delete(1.0, tk.END) # Czyszczenie obszaru wyników

        # Walidacja wprowadzonych danych
        first_name = self.get_valid_input(self.entry1.get(), self.validate_name, "Imię jest wymagane.")
        middle_name = self.entry2.get()
        last_name = self.get_valid_input(self.entry3.get(), self.validate_name, "Nazwisko jest wymagane.")
        self.get_valid_input(self.entry41.get()+self.entry42.get()+self.entry43.get(), self.validate_date,"Podano niepoprawny format daty.")
        fav = self.get_valid_input(self.entry5.get(), self.validate_name, "To pole jest wymagane.")

        threading.Thread(target=self.run_generation, args=(first_name, middle_name, last_name, fav, self.entry41.get(), self.entry42.get(), self.entry43.get())).start()

    def run_generation(self, first_name, middle_name, last_name, fav, day, month, year):
        # Generowanie haseł
        passwords, elapsed_time, counts = self.generate_passwords(first_name, middle_name, last_name, fav, day, month, year)

        # Przygotowanie tekstu z wynikami
        countsText = f"Wygenerowano {counts[0]} kombinacji podanego imienia.\n\n"
        if len(counts) == 4:
            countsText += f"Wygenerowano {counts[1]} kombinacji podanego drugiego imienia.\n\n" \
                          f"Wygenerowano {counts[2]} kombinacji podanego nazwiska.\n\n" \
                         f"Wygenerowano 8 kombinacji podanej daty.\n\n" \
                         f"Wygenerowano {counts[4]} kombinacji podanego ulubieńca.\n\n"
        else:
            countsText += f"Wygenerowano {counts[1]} kombinacji podanego nazwiska.\n\n" \
                         f"Wygenerowano 8 kombinacji podanej daty.\n\n" \
                         f"Wygenerowano {counts[3]} kombinacji podanego ulubieńca.\n\n"

        # Obliczenie czasu potrzebnego do złamania haseł
        searching_time = self.time_unit(len(passwords) / 40000000)

        result_text = f"Wygenerowano {len(passwords)} unikalnych haseł.\n\n" + countsText + f"Czas generowania haseł: {elapsed_time:.2f} sekund\n\n" \
                      "Czas łamania wygenerowanych haseł przy użyciu domowej karty graficznej za 3000 zł (NVIDIA RTX 30xx; hashrate 40MH/s): "+searching_time+"\n\n\n" \

        self.result_area.insert(tk.INSERT, result_text)

        # Wyświetlanie haseł w nowym oknie
        self.setup_window()
        self.display_passwords(list(passwords))



def check_if_file_exists(filename, error_message):
    # Sprawdzanie czy potrzebny plik z polskim słownikiem znajduje się w folderze

    # Sprawdź, czy uruchomiono program jako plik wykonywalny
    if getattr(sys, 'frozen', False):
        # Aplikacja uruchomiona z pliku .exe
        directory = Path(sys.executable).parent
    else:
        # Aplikacja uruchomiona jako skrypt Pythona
        directory = Path(__file__).parent

    file_path = os.path.join(directory, filename)

    # Sprawdź, czy plik istnieje02,
    if os.path.isfile(file_path):
        return True
    else:
        messagebox.showerror("Błąd", error_message)
        return None

def launch_password_strength_checker():
    # Tworzy nowe okno i uruchamia w nim moduł sprawdzający siłę hasła
    if check_if_file_exists("polskie_slowa.txt",
                             "Polski słownik nie został znaleziony.\nDodaj do folderu, w którym znajduje się aplikacja, poprawny plik tekstowy."):
        new_window = tk.Toplevel(root)
        PasswordStrengthChecker(new_window)

def launch_password_generator():
    # Tworzy nowe okno i uruchamia w nim moduł generatora haseł
    new_window = tk.Toplevel(root)
    PasswordGenerator(new_window)

if __name__ == "__main__":
    # Ustawienia głównego okna aplikacji
    root = tk.Tk()
    root.geometry("400x200")
    root.title("Bezpieczeństwo haseł")

    # Przycisk do uruchomienia modułu sprawdzającego siłę hasła
    btn_strength_checker = tk.Button(root, text="Sprawdź siłę hasła", command=launch_password_strength_checker)
    btn_strength_checker.pack(fill='x', padx=50, pady=10)  # Użyj 'pack' z wypełnieniem poziomym

    # Przycisk do uruchomienia modułu generatora haseł
    btn_password_generator = tk.Button(root, text="Generator haseł", command=launch_password_generator)
    btn_password_generator.pack(fill='x', padx=50, pady=10)  # Użyj 'pack' z wypełnieniem poziomym

    # Etykieta informacyjna o przetwarzaniu danych
    label = tk.Label(root,
                     text="Wszelkie informacje wprowadzane do programu nie są zapisywane ani trwale przechowywane. \nSą one przetwarzane wyłącznie tymczasowo w pamięci programu podczas jego działania.", wraplength=350)
    label.pack(fill='x', padx=10, pady=10)  # Użyj 'pack' z wypełnieniem poziomym

    # Pętla główna aplikacji, utrzymuje otwarte okno
    root.mainloop()
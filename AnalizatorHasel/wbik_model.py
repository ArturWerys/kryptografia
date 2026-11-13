# Obliczanie statystyk
class Model:
    def __init__(self):
        self.default_freq_unsorted = {    # Częstość występowania liter w słowniku języka angielskiego w procentach
        'e': 11.1607,                     # Żródło: https://www3.nd.edu/~busiforc/handouts/cryptography/letterfrequencies.html
        'a': 8.4966,
        'r': 7.5809,
        'i': 7.5448,
        'o': 7.1635,
        't': 6.9509,
        'n': 6.6544,
        's': 5.7351,
        'l': 5.4893,
        'c': 4.5388,
        'u': 3.6308,
        'd': 3.3844,
        'p': 3.1671,
        'm': 3.0129,
        'h': 3.0034,
        'g': 2.4705,
        'b': 2.0720,
        'f': 1.8121,
        'y': 1.7779,
        'w': 1.2899,
        'k': 1.1016,
        'v': 1.0074,
        'x': 0.2902,
        'z': 0.2722,
        'j': 0.1965,
        'q': 0.1962
        }

        self.text_freq = {      # Częstość występowania liter w tekstach angielskojęzycznych w procentach
        'a' : 8.2,              # Źródło: https://en.wikipedia.org/wiki/Letter_frequency -> texts
        'b' : 1.5,
        'c' : 2.8,
        'd' : 4.3,
        'e' : 12.7,
        'f' : 2.2,
        'g' : 2.0,
        'h' : 6.1,
        'i' : 7.0,
        'j' : 0.15,
        'k' : 0.77,
        'l' : 4.0,
        'm' : 2.4,
        'n' : 6.7,
        'o' : 7.5,
        'p' : 1.9,
        'q' : 0.095,
        'r' : 6.0,
        's' : 6.3,
        't' : 9.1,
        'u' : 2.8,
        'v' : 0.98,
        'w' : 2.4,
        'x' : 0.15,
        'y' : 2.0,
        'z' : 0.074
        }
        
        self.psswds = []
        self.lengths_percent = {}
        self.rep = {}
        self.file_paths = [] # Aktualizowane w kontrolerze
        
    # Wczytywanie bazy .txt, UTF-8, wiersz = hasło
    def load_psswds_db(self, filepath):
        with open(filepath, 'r', encoding='utf-8') as file:
            for line in file:
                if line and not line.isspace():
                    self.psswds.append(line.strip())

    # Częstotliwość występowania konkretnych długości haseł w bazie
    def length_dist(self, max_length):
        self.lengths = {nb: 0 for nb in range(1, max_length + 1)} # Podobne do numeric_dist
        for psswd in self.psswds:
            if len(psswd) not in self.lengths:
                self.lengths[len(psswd)] = 1
                for i in range(len(psswd)-1, max_length, -1):
                    if i not in self.lengths:
                        self.lengths[i] = 0
            else:
                self.lengths[len(psswd)] += 1
                    
    # Powtórzenia haseł
    def repeated_passwords(self):
        self.rep = {}
        items_del_keys = []
        for psswd in self.psswds:
            if psswd not in self.rep.keys():
                self.rep.setdefault(psswd, 1)
            else:
                self.rep[psswd] += 1
        for key in self.rep.keys():
            if self.rep[key] == 1:
                items_del_keys.append(key)
        for key in items_del_keys:
            del self.rep[key]
        sorted_rep_keys = sorted(self.rep.keys())
        self.rep = {key: self.rep[key] for key in sorted_rep_keys}

    # Liczba haseł składających się jedynie ze znaków specjalnych
    def all_spcs_nb(self, psswds):
        ctr = 0
        for psswd in psswds:
            ctr += 1
            for char in psswd:
                if char not in """`~!@#$%^&*()-_=+[{]};:"'"'"''\'|,<.>/?""":
                    ctr -= 1
                    break
                else:
                    continue
        return ctr

    # Liczba haseł składających się jedynie z cyfr
    def all_numeric_nb(self, psswds):
        ctr = 0
        for psswd in psswds:
            if psswd.isnumeric():
                ctr += 1
        return ctr
       
    # Liczba haseł składających się jedynie z liter
    def all_alpha_nb(self, psswds):
        ctr = 0
        for psswd in psswds:
            if psswd.isalpha():
                ctr += 1
        return ctr
        
    # Liczba haseł o strukturze: litery + cyfry
    def alpha_plus_num_nb(self, psswds):
        ctr = 0
        for psswd in psswds:
            check_letters = True
            letter_occurred = False
            digit_occurred_after = False
            wrong_seq = False
            for char in psswd:
                if char.isalpha() and check_letters == True:
                    letter_occurred = True
                elif char.isdigit() and letter_occurred:
                    digit_occurred_after = True
                    check_letters = False
                else:
                    wrong_seq = True
                    break
            if letter_occurred and digit_occurred_after and not wrong_seq:
                ctr += 1
        return ctr
        
    # Liczba haseł
    def all_psswds_nb(self, psswds):
        return len(psswds)

    # Rozmieszczenie cyfr dla haseł length-znakowych        
    def first_middle_last(self, length):
        cnt = 0 #
        first_middle_last = {i: 0 for i in range(1, length + 1)}
        for psswd in self.psswds:
            if len(psswd) == length:
                cnt_flag = False #
                for index, char in enumerate(psswd, start=1):
                    if char.isnumeric():
                        cnt_flag = True #
                        first_middle_last[index] += 1
                if cnt_flag: #
                    cnt += 1
        return first_middle_last, cnt
        
    # Rozmieszczenie liter, małych liter, dużych liter dla haseł length-znakowych        
    def fml_alpha(self, length, alpha_type='upper_lower'):
        cnt = 0
        first_middle_last = {i: 0 for i in range(1, length + 1)}
        for psswd in self.psswds:
            if len(psswd) == length:
                cnt_flag = False #
                for index, char in enumerate(psswd, start=1):
                    if alpha_type == 'upper_lower':
                        if char.isalpha():
                            cnt_flag = True #
                            first_middle_last[index] += 1
                    elif alpha_type == 'upper':
                        if char.isalpha() and char.isupper():
                            cnt_flag = True #
                            first_middle_last[index] += 1
                    else: 
                        # alpha_type == 'lower'
                        if char.isalpha() and char.islower():
                            cnt_flag = True #
                            first_middle_last[index] += 1
                if cnt_flag: #
                    cnt += 1
        return first_middle_last, cnt
        
    # Rozmieszczenie znaków specjalnych dla haseł length-znakowych        
    def fml_special(self, length):
        cnt = 0
        first_middle_last = {i: 0 for i in range(1, length + 1)}
        for psswd in self.psswds:
            if len(psswd) == length:
                cnt_flag = False #
                for index, char in enumerate(psswd, start=1):
                    if char in """`~!@#$%^&*()-_=+[{]};:"'"'"''\'|,<.>/?""":
                        cnt_flag = True #
                        first_middle_last[index] += 1
                if cnt_flag: #
                    cnt += 1
        return first_middle_last, cnt

    # Częstotliwość występowania cyfr
    def numeric_frequency(self):
        self.num_freq = {}
        for number in "0123456789":
            self.num_freq.setdefault(number, 0)
            for psswd in self.psswds:
                for letter in psswd:
                    if number == letter:
                        self.num_freq[number] += 1

    # Zlicza wszystkie hasła w któ©ych przynajmniej raz wystąpił dany typ znaku                    
    def chartype_cnt(self, chartype):
        cnt = 0
        digits = "0123456789"
        letters = "abcdefghijklmnopqrstuvwxyz"
        specials = """`~!@#$%^&*()-_=+[{]};:"'"'"''\'|,<.>/?"""
        for psswd in self.psswds:
            cnt_flag = False
            for character in psswd:
                if chartype == 'letter':
                    if character.lower() in letters:
                        cnt_flag = True
                elif chartype == 'digit':
                    if character in digits:
                        cnt_flag = True
                elif chartype == 'special':
                    if character in specials:
                        cnt_flag = True
            if cnt_flag:
                cnt += 1
        return cnt
                    

    # Konwersja słownika na listę do wyświetlenia                    
    def dict_to_str(self, disp_dict, width = 30):
        disp_str = ""
        disp_str += "\n"
        for key, value in disp_dict.items():
            key_disp = key.ljust(width-2)
            value_disp = str(value).rjust(width-2)
            disp_str += "  " + key_disp + ": " + value_disp + "  " + "\n\n"
        disp_str += "\n"
        return disp_str

    # Częstotliwość występowania liter
    def chars_frequency(self):
        self.chars_freq = {}
        for character in "abcdefghijklmnopqrstuvwxyz":
            self.chars_freq.setdefault(character, 0)
            for psswd in self.psswds:
                for letter in psswd:
                    if character == letter.lower():
                        self.chars_freq[character] += 1

    # Częstotliwość występowania znaków specjalnych
    def special_frequency(self):
        self.spcs_freq = {}
        for character in """`~!@#$%^&*()-_=+[{]};:"'"'"''\'|,<.>/?""":
            self.spcs_freq.setdefault(character, 0)
            for psswd in self.psswds:
                for special in psswd:
                    if character == special:
                        self.spcs_freq[character] += 1
 
    # Zamiana częstości wystąpień w wartościach słownika na procenty wszystkich wystąpień
    def percentage_frequency(self, stats):
        all_chars = 0
        stats_percentage = {}
        for value in stats.values():
            all_chars += value
        if all_chars == 0:
            return stats # Wszystkie wartości słownika są zerowe więc stats (w procentach) == stats
        else:
            for key in stats.keys():
                stats_percentage[key] = stats[key]/all_chars*100
            return stats_percentage
        
        # Zamiana częstości wystąpień w wartościach słownika na procenty wszystkich haseł danej długości
    def percentage_frequency2(self, stats, length):
        stats_percentage = {}
        psswds_of_length = 0
        for psswd in self.psswds:
            if len(psswd) == length:
                psswds_of_length += 1
        if psswds_of_length == 0:
            return {key: 0 for key in stats}
        for key in stats.keys():
            stats_percentage[key] = stats[key]/psswds_of_length*100
        return stats_percentage
        
    # Zamiana częstości wystąpień na wartości znormalizowane (na potrzeby kolorowania wykresów)
    def normalize_frequency(self, stats):
        all_chars = 0
        stats_norm = {}
        for value in stats.values():
            all_chars += value
        if all_chars == 0:
            return stats
        else:
            for key in stats.keys():
                stats_norm[key] = stats[key]/all_chars     
            return stats_norm
        
    # Odległość Hellingera - ocena podobieństwa 2 rozkładów, zwraca zero dla identycznych rozkładów, 1 dla maksymalnie różnych
    def hellinger_distance(self, distr1, distr2):
        distance = sum((distr1_val ** 0.5 - distr2_val ** 0.5) ** 2 for distr1_val, distr2_val in zip(distr1, distr2))
        distance = (0.5 * distance) ** 0.5
        return distance

    # Odstające długością hasło dla fortinet-2021_passwords.txt
    def debug_longest_password(self):
        longest = ""
        for psswd in self.psswds:
            if len(psswd) > len(longest):
                longest = psswd
        print("Najdłuższe hasło w bazie, znaków:", len(longest), ", hasło:", longest)

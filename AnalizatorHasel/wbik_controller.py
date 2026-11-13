from wbik_model import *
from wbik_gui import *

# Wyzwalanie obliczania wymaganych parametrów modelu po wciśnięciu przycisku z opcji
class Controller:
    def __init__(self):
        self.model = Model()
        self.view = View(self.model, self)
    
    def psswds_len_button(self):
        self.model.length_dist(max_length=30)
        self.model.lengths = self.model.percentage_frequency(self.model.lengths)
        self.view.show_frame(PsswdLenPage)
    
    def repeated_psswds_button(self):
        self.model.repeated_passwords()
        self.view.show_frame(RepPsswdsPage)
        
    def get_db_button(self):
        self.model.file_paths.extend(filedialog.askopenfilenames(filetypes=[("Pliki tekstowe", "*.txt")]))
        if self.model.file_paths:
            for path in self.model.file_paths:
                self.model.load_psswds_db(path)
            self.model.debug_longest_password()
            
    def clr_db_button(self):
        self.model.file_paths = []
        self.model.psswds = []
    
    def digit_position_button(self):
        # first_middle_last obliczane i aktualizowane przy wywołaniu GUI DigitPosPage
        self.view.show_frame(DigitPosPage)
        
    def letter_position_button(self):
        # first_middle_last obliczane i aktualizowane przy wywołaniu GUI DigitPosPage
        self.view.show_frame(AlphaPosPage)
        
    def special_position_button(self):
        # first_middle_last obliczane i aktualizowane przy wywołaniu GUI DigitPosPage
        self.view.show_frame(SpecialPosPage)

    def chars_frequency_button(self):
        self.model.chars_frequency()
        self.model.chars_freq = self.model.percentage_frequency(self.model.chars_freq)
        self.view.show_frame(CharsFreqPage)

    def numeric_frequency_button(self):
        self.model.numeric_frequency()
        self.model.num_freq = self.model.percentage_frequency(self.model.num_freq)
        self.view.show_frame(NumFreqPage)
        
    def special_frequency_button(self):
        self.model.special_frequency()
        self.model.spcs_freq = self.model.percentage_frequency(self.model.spcs_freq)
        self.view.show_frame(SpcsFreqPage)
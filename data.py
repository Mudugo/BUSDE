from enum import Enum
import re

import PyPDF2

DEFINING_CHARACTERISTICS = "Características definidoras"
RELATED_FACTORS = "Fatores relacionados"
RISK_FACTORS = "Fatores de risco"
DEFINITION = "Definição"


class Diagnose:
    def __init__(self):
        self.domain = ""
        self.clazz = ""
        self.code = ""
        self.title = ""
        self.date = ""
        self.map = {}
        pass


class Line:
    def __init__(self, text, font, fontsize):
        self.text = text
        self.font = font
        self.fontsize = fontsize

    def is_key(self):
        return self.text in [DEFINING_CHARACTERISTICS, RELATED_FACTORS, RISK_FACTORS, DEFINITION]

    def should_ignore(self):
        if self.font["/BaseFont"] == "/AAAAAD+TimesNewRomanPS-BoldItalicMT":
            return True

        return False


def read_pdf(file_path):
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        pages = reader.pages

        lines = []
        for i in range(137, 464):

            def visitor(text, cm_matrix, tm_matrix, font, font_size):
                if text == "" or text == " " or text == "\n":
                    return

                lines.append(Line(text, font, font_size))

            pages[i].extract_text(visitor_text=visitor)

    return lines


def process_diagnose(lines, ln):
    diagnose = Diagnose()

    diagnose.domain = lines[ln].text + " " + lines[ln + 1].text

    ln += 2
    diagnose.clazz = lines[ln].text + " " + lines[ln + 1].text

    ln += 2
    diagnose.code = lines[ln].text

    ln += 1
    while not lines[ln].text.startswith("("):
        diagnose.title += lines[ln].text
        ln += 1

    # ln is now the line with the date
    diagnose.date = re.sub(r'\(|\)', '', lines[ln].text)
    
    key = None
    while True:
        ln += 1

        if ln >= len(lines):
            break

        if lines[ln].text.startswith("Domínio"):
            break

        if lines[ln].is_key():
            key = lines[ln].text
            diagnose.map[key] = []
        elif key is not None:
            if lines[ln].should_ignore():
                continue
            if lines[ln].text != "Literatura original de apoio disponível em " and lines[ln].text != "www.nanda.org":
                text = lines[ln].text
                if text.strip() == "a":
                    text = "ª"
                    diagnose.map[key].append(text)
                else:
                   diagnose.map[key].append(text)
            continue

    return diagnose


def load_diagnoses():
    lines = read_pdf('NANDA.pdf')
    diagnoses = []

    for i in range(len(lines)):
        line = lines[i]
        if re.match(r"Domínio \d+[.:]", line.text):
            diagnose = process_diagnose(lines, i)
            diagnoses.append(diagnose)

    return diagnoses


def find_diagnose_by_code(diagnoses, code):
    for diagnose in diagnoses:
        if diagnose.code == code:
            return diagnose

    return None


def find_diagnose_by_defining_characteristic(diagnoses, characteristic):
    target = diagnoses
    list = []

    for diagnose in target:
        if DEFINING_CHARACTERISTICS in diagnose.map:
            if characteristic[0] in diagnose.map[DEFINING_CHARACTERISTICS]:
                list.append(diagnose)

    for c in characteristic:
        list = [diagnose for diagnose in list if c in diagnose.map[DEFINING_CHARACTERISTICS]]

    return list

# BRAILLEBOOK Copyright (C) 2025 Daniel A.L.
# Contact: caminodelaserpiente.py@gmail.com

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.



from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO
import fitz  # PyMuPDF
from PIL import Image
import io

# Definición de dimensiones en puntos
CELL_WIDTH = 0.227 * 28.35 # Ancho de la celda en puntos
CELL_HEIGHT = 0.612 * 28.35 # Altura de la celda en puntos
HORIZONTAL_GAP = 0.4 * 28.35 # Espacio entre celdas en puntos
VERTICAL_GAP = 0.4 * 28.35 # Espacio entre renglones en puntos
POINT_RADIUS = 0.03 * 28.35 # Radio de los puntos en puntos (ajustado a un tamaño más pequeño)
# Separación adicional entre las columnas dentro de una celda
COLUMN_SEPARATION = 0.26 * 28.35 # Ajusta esta separación horizontal en puntos
# Separación adicional entre filas dentro de una celda
ROW_SEPARATION = 0.24 * 28.35 # Ajusta esta separación vertical en puntos


def _binary_to_braille(binary):
    """Convert a 6-bit binary string to a visual Braille cell representation."""
    braille_cell = [
        binary[0] + binary[1], # Top two points
        binary[2] + binary[3], # Middle two points
        binary[4] + binary[5] # Bottom two points
    ]
    return braille_cell


def _draw_braille_cell(c, x, y, braille_cell):
    """Draw a Braille cell on the canvas with adjusted point separation."""
    # Coordenadas de los puntos en la celda con separación entre columnas y filas
    point_positions = [
        (x + COLUMN_SEPARATION / 2, y + 2 * ROW_SEPARATION + POINT_RADIUS), # Punto 1 (superior izquierda)
        (x + COLUMN_SEPARATION / 2 + COLUMN_SEPARATION, y + 2 * ROW_SEPARATION + POINT_RADIUS), # Punto 4 (superior derecha)
        (x + COLUMN_SEPARATION / 2, y + ROW_SEPARATION + POINT_RADIUS), # Punto 2 (central izquierda)
        (x + COLUMN_SEPARATION / 2 + COLUMN_SEPARATION, y + ROW_SEPARATION + POINT_RADIUS), # Punto 5 (central derecha)
        (x + COLUMN_SEPARATION / 2, y + POINT_RADIUS), # Punto 3 (inferior izquierda)
        (x + COLUMN_SEPARATION / 2 + COLUMN_SEPARATION, y + POINT_RADIUS) # Punto 6 (inferior derecha)
    ]

    for i, pos in enumerate(point_positions):
        if braille_cell[i // 2][i % 2] == '1':
            c.circle(pos[0], pos[1], POINT_RADIUS, fill=1)


def create_braille_pdf(text, mirror=False):
    """Create a PDF with Braille text."""
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    start_x = 1.683 * 28.35 # Comienza a 1.683 cm desde el borde izquierdo
    start_y = height - .96 * 28.35  # Comienza a .96 cm desde el borde superior
    x = start_x
    y = start_y

    # Aplicar transformación para impresión en espejo
    if mirror:
        c.translate(width, 0)
        c.scale(-1, 1)

    braille_uppercase_marker = '010001'
    braille_number_marker = '010111'

    braille_alphabet = {
        'a': '100000', 'b': '101000', 'c': '110000', 'd': '110100', 'e': '100100',
        'f': '111000', 'g': '111100', 'h': '101100', 'i': '011000', 'j': '011100',
        'k': '100010', 'l': '101010', 'm': '110010', 'n': '110110', 'o': '100110',
        'p': '111010', 'q': '111110', 'r': '101110', 's': '011010', 't': '011110',
        'u': '100011', 'v': '101011', 'w': '011101', 'x': '110011', 'y': '110111',
        'z': '100111', ' ': '000000',

        'á': '101111', 'é': '011011', 'í': '010010', 'ó': '010011', 'ú': '011111'
    }

    braille_numbers = {
        '0': '011100', '1': '100000', '2': '101000', '3': '110000', '4': '110100',
        '5': '100100', '6': '111000', '7': '111100', '8': '101100', '9': '011000'
    }

    braille_punctuation = {
        ',': '001000', '.': '000010', ';': '001010', ':': '001100',
        '¿': '001001', '?': '001001', '¡': '001110', '!': '001110', 
        '“': '001011', '”': '001011', '(': '101001', ')': '010110',
        '-': '000011',
    }

    lines = text.split('\n')

    for line in lines:
        x = start_x
        num_cells = 0
        for char in line:
            if num_cells >= 30:
                # Mover a la siguiente línea si se alcanzan 30 celdas
                x = start_x
                y -= CELL_HEIGHT + VERTICAL_GAP
                if y < 1.6 * 28.35:
                    c.showPage()
                    y = height - 1.2 * 28.35
                num_cells = 0

            if char.isupper():
                braille_cell = _binary_to_braille(braille_uppercase_marker)
                _draw_braille_cell(c, x, y, braille_cell)
                x += CELL_WIDTH + HORIZONTAL_GAP
                num_cells += 1
                char = char.lower()
                if char in braille_alphabet:
                    braille_binary = braille_alphabet[char]
                    braille_cell = _binary_to_braille(braille_binary)
                    _draw_braille_cell(c, x, y, braille_cell)
                    x += CELL_WIDTH + HORIZONTAL_GAP
                    num_cells += 1

            elif char.isdigit():
                braille_cell = _binary_to_braille(braille_number_marker)
                _draw_braille_cell(c, x, y, braille_cell)
                x += CELL_WIDTH + HORIZONTAL_GAP
                num_cells += 1
                if char in braille_numbers:
                    braille_binary = braille_numbers[char]
                    braille_cell = _binary_to_braille(braille_binary)
                    _draw_braille_cell(c, x, y, braille_cell)
                    x += CELL_WIDTH + HORIZONTAL_GAP
                    num_cells += 1
            
            elif char in braille_punctuation:
                braille_binary = braille_punctuation[char]
                braille_cell = _binary_to_braille(braille_binary)
                _draw_braille_cell(c, x, y, braille_cell)
                x += CELL_WIDTH + HORIZONTAL_GAP
                num_cells += 1

            else:
                if char.lower() in braille_alphabet:
                    braille_binary = braille_alphabet[char.lower()]
                    braille_cell = _binary_to_braille(braille_binary)
                    _draw_braille_cell(c, x, y, braille_cell)
                    x += CELL_WIDTH + HORIZONTAL_GAP
                    num_cells += 1

        y -= CELL_HEIGHT + VERTICAL_GAP
        if y < 1.6 * 28.35:
            c.showPage()
            y = height - 1.2 * 28.35

    c.save()
    buffer.seek(0)
    return buffer


def pdf_to_image(pdf_file, page_number=0):
    """
    Convert the specified page of a PDF file to an image.
    """
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    page = doc.load_page(page_number)
    pix = page.get_pixmap()
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    return img_bytes

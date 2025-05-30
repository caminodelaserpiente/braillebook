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
import fitz # PyMuPDF
from PIL import Image
import io

# --- Definición de Constantes Basadas en el Estándar Braille ---

# Factor de conversión de pulgadas a puntos (1 pulgada = 72 puntos)
INCHES_TO_POINTS = 72

# Dimensiones estándar del braille (en pulgadas)
DOT_DIAMETER_INCHES = 0.057  # Diámetro del punto
DOT_SPACING_INCHES = 0.09    # Espaciado entre centros de puntos (horizontal y vertical dentro de una celda)
CHARACTER_PITCH_INCHES = 0.24 # Paso horizontal de celda a celda (distancia de inicio de una celda a inicio de la siguiente)
LINE_PITCH_INCHES = 0.4      # Paso vertical de línea a línea (distancia de inicio de una línea a inicio de la siguiente)

# Dimensiones derivadas en puntos
POINT_RADIUS = (DOT_DIAMETER_INCHES / 2) * INCHES_TO_POINTS # Radio de un punto de braille
COLUMN_SEPARATION = DOT_SPACING_INCHES * INCHES_TO_POINTS  # Distancia horizontal entre centros de puntos (columnas izquierda y derecha)
ROW_SEPARATION = DOT_SPACING_INCHES * INCHES_TO_POINTS     # Distancia vertical entre centros de puntos (filas)

# Dimensiones de avance de celda (paso para el movimiento del "cursor")
CELL_ADVANCE_WIDTH = CHARACTER_PITCH_INCHES * INCHES_TO_POINTS
CELL_ADVANCE_HEIGHT = LINE_PITCH_INCHES * INCHES_TO_POINTS

# Márgenes para tamaño carta (US Letter: 8.5 x 11 pulgadas)
LEFT_MARGIN_POINTS = .8 * INCHES_TO_POINTS
TOP_MARGIN_POINTS = .28 * INCHES_TO_POINTS
RIGHT_MARGIN_POINTS = .4 * INCHES_TO_POINTS
BOTTOM_MARGIN_POINTS = 1.0 * INCHES_TO_POINTS

# Dimensiones de la página US Letter en puntos
US_LETTER_WIDTH_POINTS = 8.5 * INCHES_TO_POINTS  # 612 puntos
US_LETTER_HEIGHT_POINTS = 11 * INCHES_TO_POINTS # 792 puntos

# Calcular el número máximo de celdas por línea y líneas por página
AVAILABLE_WIDTH_FOR_TEXT = US_LETTER_WIDTH_POINTS - LEFT_MARGIN_POINTS - RIGHT_MARGIN_POINTS
MAX_CELLS_PER_LINE = int(AVAILABLE_WIDTH_FOR_TEXT / CELL_ADVANCE_WIDTH)

AVAILABLE_HEIGHT_FOR_TEXT = US_LETTER_HEIGHT_POINTS - TOP_MARGIN_POINTS - BOTTOM_MARGIN_POINTS
# Calcular MAX_LINES_PER_PAGE dinámicamente para asegurar que quepan en la página
MAX_LINES_PER_PAGE = int(AVAILABLE_HEIGHT_FOR_TEXT / CELL_ADVANCE_HEIGHT)

if MAX_CELLS_PER_LINE < 1:
    MAX_CELLS_PER_LINE = 1
if MAX_LINES_PER_PAGE < 1:
    MAX_LINES_PER_PAGE = 1

# Ajustes finos manuales para el interlineado de cada línea.
# Estos valores se sumarán a CELL_ADVANCE_HEIGHT para cada línea.
# Puedes modificar estos valores para ajustar el desfase.
# El índice 0 corresponde a la primera línea después del margen superior.
# El tamaño de esta lista corresponde a MAX_LINES_PER_PAGE.
# Con los márgenes actuales, caben 24 líneas. Si necesitas más, ajusta TOP_MARGIN_POINTS y BOTTOM_MARGIN_POINTS.
LINE_ADJUSTMENTS = [0.0] * MAX_LINES_PER_PAGE
LINE_ADJUSTMENTS[2] = -0.2 # Ajuste para la cuarta línea (índice 3)
LINE_ADJUSTMENTS[4] = -0.2 # Ajuste para la cuarta línea (índice 3)
LINE_ADJUSTMENTS[5] = -0.9 # Ajuste para la cuarta línea (índice 3)
LINE_ADJUSTMENTS[5] = -0.9 # Ajuste para la cuarta línea (índice 3)
LINE_ADJUSTMENTS[7] = -.6 # Ajuste para la cuarta línea (índice 3)
LINE_ADJUSTMENTS[8] = -.9 # Ajuste para la cuarta línea (índice 3)


# Ejemplo de cómo podrías ajustar las primeras líneas si fuera necesario:
# LINE_ADJUSTMENTS[0] = 0.0 # Ajuste para la primera línea (por defecto 0)
# LINE_ADJUSTMENTS[1] = 0.5 # Ajuste para la segunda línea (ejemplo: moverla 0.5 puntos más abajo)
# LINE_ADJUSTMENTS[2] = -0.2 # Ajuste para la tercera línea (ejemplo: moverla 0.2 puntos más arriba)


# --- Mapeo de Caracteres Braille (Grado 1) ---
braille_uppercase_marker = '010001'
braille_number_marker = '010111'

braille_alphabet = {
    'a': '100000', 'b': '101000', 'c': '110000', 'd': '110100', 'e': '100100',
    'f': '111000', 'g': '111100', 'h': '101100', 'i': '011000', 'j': '011100',
    'k': '100010', 'l': '101010', 'm': '110010', 'n': '110110', 'o': '100110',
    'p': '111010', 'q': '111110', 'r': '101110', 's': '011010', 't': '011110',
    'u': '100011', 'v': '101011', 'w': '011101', 'x': '110011', 'y': '110111',
    'z': '100111', ' ': '000000', # El espacio en braille es una celda vacía

    'á': '101111', 'é': '011011', 'í': '010010', 'ó': '010011', 'ú': '011111',
    'ñ': '110101'
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

# --- Funciones de Dibujo Braille ---

def _binary_to_braille(binary_string):
    """
    Convierte una cadena binaria de 6 bits en un formato de celda Braille.
    """
    if len(binary_string) != 6:
        raise ValueError("La cadena binaria debe tener 6 bits.")
    braille_cell = [
        binary_string[0] + binary_string[1],
        binary_string[2] + binary_string[3],
        binary_string[4] + binary_string[5]
    ]
    return braille_cell


def _draw_braille_cell(c, x, y_top_of_cell, braille_cell_data):
    """
    Dibuja una celda Braille en las coordenadas especificadas.
    x es la coordenada X de la esquina izquierda de la celda.
    y_top_of_cell es la coordenada Y de la parte superior de la celda.
    """
    # Las coordenadas Y en ReportLab aumentan hacia arriba.
    # Si y_top_of_cell es la parte superior, los puntos se dibujan "hacia abajo" desde allí.
    point_positions = [
        # Posiciones de los puntos dentro de la celda Braille (superior izquierda a inferior derecha)
        # Punto 1 (superior izquierda)
        (x + POINT_RADIUS, y_top_of_cell - POINT_RADIUS),
        # Punto 4 (superior derecha)
        (x + COLUMN_SEPARATION + POINT_RADIUS, y_top_of_cell - POINT_RADIUS),
        # Punto 2 (medio izquierda)
        (x + POINT_RADIUS, y_top_of_cell - (ROW_SEPARATION + POINT_RADIUS)),
        # Punto 5 (medio derecha)
        (x + COLUMN_SEPARATION + POINT_RADIUS, y_top_of_cell - (ROW_SEPARATION + POINT_RADIUS)),
        # Punto 3 (inferior izquierda)
        (x + POINT_RADIUS, y_top_of_cell - (2 * ROW_SEPARATION + POINT_RADIUS)),
        # Punto 6 (inferior derecha)
        (x + COLUMN_SEPARATION + POINT_RADIUS, y_top_of_cell - (2 * ROW_SEPARATION + POINT_RADIUS))
    ]

    for i, pos in enumerate(point_positions):
        # Verifica si el bit correspondiente en braille_cell_data es '1' para dibujar el punto
        # Los índices de braille_cell_data son 'fila' y 'columna' (0,0), (0,1), (1,0), (1,1), (2,0), (2,1)
        if braille_cell_data[i // 2][i % 2] == '1':
            c.circle(pos[0], pos[1], POINT_RADIUS, fill=1)


def create_braille_pdf(text, mirror=False):
    """
    Crea un documento PDF con texto convertido a Braille.
    Args:
        text (str): El texto de entrada a convertir.
        mirror (bool): Si es True, el PDF se generará en modo espejo (útil para impresión en relieve).
    Returns:
        BytesIO: Un objeto BytesIO que contiene el PDF generado.
    """
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Posición inicial X: Margen izquierdo
    x = LEFT_MARGIN_POINTS
    # Posición inicial Y: La coordenada Y de la parte superior de la primera línea de braille.
    # Esta 'y' representará la parte superior de la celda Braille actual.
    y = height - TOP_MARGIN_POINTS

    # Aplicar transformación de espejo si se solicita
    if mirror:
        c.translate(width, 0)
        c.scale(-1, 1)

    current_braille_line_count = 0 # Contador de líneas de braille generadas en la página actual
    num_cells_in_current_braille_line = 0 # Contador de celdas en la línea de braille actual

    # Función auxiliar para avanzar a la siguiente línea de braille
    def move_to_next_braille_line():
        nonlocal x, y, current_braille_line_count, num_cells_in_current_braille_line
        x = LEFT_MARGIN_POINTS # Reiniciar X al margen izquierdo
        
        # Incrementar el contador de línea para obtener el índice de la siguiente línea
        current_braille_line_count += 1 

        # Aplicar ajuste para la nueva línea si el índice está dentro de los límites de LINE_ADJUSTMENTS
        adjustment = 0.0
        if current_braille_line_count < len(LINE_ADJUSTMENTS):
            adjustment = LINE_ADJUSTMENTS[current_braille_line_count]
        
        y -= (CELL_ADVANCE_HEIGHT + adjustment) # Mover Y a la siguiente línea (restamos porque Y disminuye hacia abajo)
        num_cells_in_current_braille_line = 0 # Reiniciar contador de celdas

        # Manejo de salto de página
        if current_braille_line_count >= MAX_LINES_PER_PAGE:
            c.showPage() # Iniciar nueva página
            y = height - TOP_MARGIN_POINTS # Reiniciar Y para la nueva página
            current_braille_line_count = 0 # Reiniciar contador de líneas para la primera línea de la nueva página

    # Iterar sobre cada carácter del texto de entrada
    for char_index, char in enumerate(text):
        if char == '\n':
            # Si encontramos un salto de línea explícito, forzamos un avance a la siguiente línea de braille
            # solo si la línea actual no está vacía o si es la primera línea (para evitar saltos dobles al inicio).
            # Esta condición asegura que un '\n' siempre avance la línea, incluso si es el primer carácter.
            # Y que un segundo '\n' consecutivo genere una línea vacía.
            move_to_next_braille_line()
            continue # Pasar al siguiente carácter

        # Lógica para avanzar a la siguiente línea si la actual está llena
        if num_cells_in_current_braille_line >= MAX_CELLS_PER_LINE:
            move_to_next_braille_line()

        # Determinar el binario braille y marcadores
        braille_binary = None
        is_uppercase = False
        is_digit = False

        # Procesamiento de mayúsculas, números y puntuación
        if char.isupper():
            is_uppercase = True
            char_lower = char.lower()
            if char_lower in braille_alphabet:
                braille_binary = braille_alphabet[char_lower]
        elif char.isdigit():
            is_digit = True
            if char in braille_numbers:
                braille_binary = braille_numbers[char]
        elif char in braille_punctuation:
            braille_binary = braille_punctuation[char]
        elif char.lower() in braille_alphabet: # Manejo de minúsculas y caracteres acentuados
            braille_binary = braille_alphabet[char.lower()]
        # Si el carácter no se puede mapear, simplemente se ignora.

        # Dibujar el marcador de mayúsculas si es necesario
        if is_uppercase:
            braille_cell_data = _binary_to_braille(braille_uppercase_marker)
            # Pasamos 'y' directamente, que ahora es la parte superior de la celda.
            _draw_braille_cell(c, x, y, braille_cell_data)
            x += CELL_ADVANCE_WIDTH
            num_cells_in_current_braille_line += 1
            # Verificar de nuevo si el marcador llenó la línea y necesita un salto de línea
            if num_cells_in_current_braille_line >= MAX_CELLS_PER_LINE:
                move_to_next_braille_line()

        # Dibujar el marcador de número si es necesario
        if is_digit:
            braille_cell_data = _binary_to_braille(braille_number_marker)
            # Pasamos 'y' directamente, que ahora es la parte superior de la celda.
            _draw_braille_cell(c, x, y, braille_cell_data)
            x += CELL_ADVANCE_WIDTH
            num_cells_in_current_braille_line += 1
            # Verificar de nuevo si el marcador llenó la línea y necesita un salto de línea
            if num_cells_in_current_braille_line >= MAX_CELLS_PER_LINE:
                move_to_next_braille_line()

        # Dibujar el carácter braille real
        if braille_binary:
            braille_cell_data = _binary_to_braille(braille_binary)
            # Pasamos 'y' directamente, que ahora es la parte superior de la celda.
            _draw_braille_cell(c, x, y, braille_cell_data)
            x += CELL_ADVANCE_WIDTH
            num_cells_in_current_braille_line += 1
    
    # Asegurar que la última línea de braille se guarde, incluso si no llenó la página
    c.save()
    buffer.seek(0)
    return buffer


def pdf_to_image(pdf_file, page_number=0):
    """
    Convierte la página especificada de un archivo PDF a una imagen PNG.
    Args:
        pdf_file (BytesIO): Objeto BytesIO que contiene los datos del PDF.
        page_number (int): El número de página a convertir (0-indexado).
    Returns:
        BytesIO: Un objeto BytesIO que contiene la imagen PNG.
    """
    # Asegúrate de que el buffer esté al inicio antes de leerlo
    pdf_file.seek(0)
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    page = doc.load_page(page_number)
    pix = page.get_pixmap()
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    doc.close() # Es buena práctica cerrar el documento
    return img_bytes

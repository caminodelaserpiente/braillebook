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



import streamlit as st


from app.utils.braillebook import pdf_to_image, create_braille_pdf
from interface.assets.utils import files


# Initialize session state for text if not already set
if 'text' not in st.session_state:
    st.session_state.text = ""


def header():
    with st.container():
        st.title("BRAILLEBOOK")
        st.write("---")


def body():
    # Load the text file from sidebar
    with st.sidebar:
        path_txt = files.load_txt()

    if path_txt:
        # Read the content of the file and update session state
        text = files.select_txt(path_txt)
        st.session_state.text = text

    with st.container():
        col1, col2 = st.columns(2)

        with col1:
            # Input field for text, reflects the session state
            input_text = st.text_area(
                "Enter text here:",
                height=200,
                value=st.session_state.text,
                key='text_area_input',  # Key to reference the text area input in session_state
                on_change=lambda: st.session_state.update({'text': st.session_state.text_area_input})  # Update session state
            )
            st.session_state.text = input_text

            # Only update session state directly if text_area_input changes
            if st.session_state.text:
                # Create mirrored Braille PDF for download
                pdf_buffer_mirror = create_braille_pdf(st.session_state.text, mirror=True)
                # Create normal Braille PDF for preview
                pdf_buffer_normal = create_braille_pdf(st.session_state.text, mirror=False)

                st.download_button(
                    label="Download Braille PDF",
                    data=pdf_buffer_mirror,
                    file_name="braille_text.pdf",
                    mime="application/pdf"
                )
                st.write("Braille PDF Generated. Preview it here:")
                # Ensure pdf_buffer_normal is reset to the start
                pdf_buffer_normal.seek(0)
        
        with col2:
            try:
                img_bytes = pdf_to_image(pdf_buffer_normal)
                st.image(img_bytes, caption="Preview of the Braille PDF", use_container_width=True)
            except Exception as e:
                st.warning(f"No displaying preview")

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



import os
import tempfile
import zipfile
import time

import streamlit as st


def load_txt():
    """
    Allows users to upload TXT files using Streamlit.

    Returns:
        dict or None: A dictionary with a temporary directory and a list of names of uploaded TXT files if TXT files were uploaded successfully, or None if no files were uploaded.
    """
    with st.expander("Load txt", expanded=True):
        path_files = {'temp_dir': tempfile.mkdtemp(), # Temporary directory to store the files
                      'files': []} # List to store the names of uploaded CSV files

        uploaded_files = st.file_uploader("Choose an txt...",
                                          type=["txt"],
                                          accept_multiple_files=True,
                                          key="txt_uploader")

        if uploaded_files:
            for uploaded_file in uploaded_files:
                original_filename = uploaded_file.name
                temp_file_path = os.path.join(path_files['temp_dir'], original_filename)
                with open(temp_file_path, "wb") as temp_file:
                    temp_file.write(uploaded_file.read())
                path_files['files'].append(original_filename)
            st.success(".txt files uploaded successfully!")
            return path_files
        else:
            st.warning("No txt files uploaded.")
            return None



def select_txt(uploaded_files_info):
    """
    Selects and reads the content of a TXT file from the uploaded files.

    Args:
        uploaded_files_info (dict or None): Dictionary returned by the load_txt() function, which contains information about the uploaded files and the temporary directory.

    Returns:
        str or None: Content of the selected file as a string, or None if no TXT file was loaded or if an error occurred.
    """
    if uploaded_files_info is not None and uploaded_files_info.get('files'):
        selected_file = st.selectbox("Select a CSV file:", uploaded_files_info['files'])
        file_path = os.path.join(uploaded_files_info['temp_dir'], selected_file)
        
        # Open the file and read its content
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            return content
        except Exception as error:
            st.error(f"Error reading the file: {error}")
            return None
    else:
        st.warning("No files have been uploaded.")
        return None

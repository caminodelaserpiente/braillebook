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


def css(): 
    # Ocultar pie de página
    st.markdown(
        """
        <style>
        footer {
            visibility: hidden;
        }
        </style>

        <style>
            .st-emotion-cache-15yi2hn > div:nth-child(1) > p:nth-child(2) {
                display: none;
            }
        </style>

        """,
        unsafe_allow_html=True
    )

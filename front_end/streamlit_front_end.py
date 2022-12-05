import pandas as pd
import streamlit as st

from analyser.analyser import Analyser
from pdf_processing.pdf_parser import PdfRetriever, PdfParser


class StreamlitFrontEnd:
    """
    This class is concerned with visualising the data. It uses Streamlit to allow the user access to the Analyser class
    and visualises the outputs of any analysis.
    """
    def __init__(self):
        self.pdf_retriever = PdfRetriever()
        self.pdf_parser = PdfParser()
        self.laptime_analyser = Analyser()

    def run(self):
        """
        A method to form the Streamlit UI.
        """
        # session selection
        session_df = self._session_selection()
        self.laptime_analyser.data(session_df)
        pass

    def _session_selection(self) -> pd.DataFrame:
        """
        A method to retrieve the PDF for the selected session.
        :return: The dataframe containing the data from the selected PDF
        """
        races = [
            "QAT", "INA", "ARG", "AME", "POR", "SPA", "FRA", "ITA", "CAT", "GER", "NED", "GBR", "AUT", "RSM", "ARA",
            "JPN", "THA", "AUS", "MAL", "VAL"
        ]
        with st.form('my_form'):
            col1, col2, col3 = st.columns(3)
            with col1:
                year = st.selectbox("Select year", range(2010, 2023))
            with col2:
                race = st.selectbox("Select race", races)
            with col3:
                session = st.selectbox("Select session", ["FP1", "FP2", "FP3", "FP4"])
            submit = st.form_submit_button("Get session")

        fname = self.pdf_retriever.retrieve_file(year, race, session)

        session_file = st.file_uploader("Session file", type=["pdf"])
        if session_file:
            dframe = self.pdf_parser.parse_pdf(session_file)
        else:
            dframe = self.pdf_parser.parse_pdf(fname)

        return dframe

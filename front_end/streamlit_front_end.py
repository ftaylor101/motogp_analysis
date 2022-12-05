import pandas as pd
import streamlit as st

from analyser.analyser import Analyser
from pdf_processing.pdf_parser import PdfRetriever, PdfParser


class StreamlitFrontEnd:
    """
    This class is concerned with visualising the data. It uses Streamlit to allow the user access to the Analyser class
    and visualises the outputs of any analysis.
    """
    RACES = [
            "QAT", "INA", "ARG", "AME", "POR", "SPA", "FRA", "ITA", "CAT", "GER", "NED", "GBR", "AUT", "RSM", "ARA",
            "JPN", "THA", "AUS", "MAL", "VAL"
        ]

    def __init__(self):
        self.pdf_retriever = PdfRetriever()
        self.pdf_parser = PdfParser()
        self.laptime_analyser = Analyser()

        # show status of the Analyser
        # todo use callback to properly update the status notification
        if 'key' not in st.session_state:
            st.session_state['key'] = "No status"
        st.write(f"Analyser status is: {st.session_state['key']}")
        # notes
        st.write("**2012 QAT FP4 does not exist, get a 404 error trying to download it.**")

    def run(self):
        """
        A method to form the Streamlit UI.
        """
        # session selection
        session_df = self._session_selection()
        self.laptime_analyser.data = session_df

        st.write("TESTING:")
        st.dataframe(self.laptime_analyser.data)
        st.session_state['key'] = self.laptime_analyser.status

    def _session_selection(self) -> pd.DataFrame:
        """
        A method to retrieve the PDF for the selected session.
        :return: The dataframe containing the data from the selected PDF
        """
        form = st.form('my_form')
        col1, col2, col3 = st.columns(3)
        with col1:
            year = form.selectbox("Select year", range(2010, 2023))
        with col2:
            race = form.selectbox("Select race", self.RACES)
        with col3:
            session = form.selectbox("Select session", ["FP1", "FP2", "FP3", "FP4"])
        submit = form.form_submit_button("Get session")

        session_file = st.file_uploader("Session file", type=["pdf"])
        if submit:
            fname = self.pdf_retriever.retrieve_file(year, race, session)
            dframe = self.pdf_parser.parse_pdf(fname)
            print("hit once")
        elif session_file:
            dframe = self.pdf_parser.parse_pdf(session_file)
            print("Hit twice")
        else:
            st.error("No file found")
            dframe = pd.DataFrame()
            print("Hit thrice")
        return dframe

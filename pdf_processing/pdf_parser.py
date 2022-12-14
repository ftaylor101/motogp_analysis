import fitz
import re
import pandas as pd
import streamlit as st
import altair as alt
import numpy as np
import os
import wget


class PdfRetriever:
    """
    This class is for retrieving the MotoGP PDFs.
    """
    def __init__(self):
        self.year = None
        self.race = None
        self.session = None

    def retrieve_file(self, year: str, race: str, session: str) -> str:
        """
        Gets the PDF from the website.

        :param year:
        :param race:
        :param session:
        :return: The pdf name saved locally
        """
        self.year = year
        self.race = race
        self.session = session
        url = f"https://resources.motogp.com/files/results/{self.year}/{self.race}/MotoGP/{self.session}/Analysis.pdf"
        name = f"{year}_{race}_{session}.pdf"

        if os.path.isfile(name):
            st.write("File exists locally")
            file_name = name
        else:
            st.write("Downloading PDF...")
            file_name = wget.download(url, name)
        return file_name


class PdfParser:
    """
    This class reads in MotoGP free practice session PDFs and extracts the lap time data for each rider and makes it
    available for use via a Pandas dataframe.
    """
    def __init__(self):
        self.threshold = 1000

    @staticmethod
    def _min_to_seconds(laptime: str) -> float:
        """
        Convert a lap time given as a string in minutes'seconds.milliseconds into a float in seconds.

        :param laptime: the time in m'ss.000
        :return: the lap time as a float in seconds ss.000
        """
        minsec = laptime.split("'")
        sec = round(int(minsec[0]) * 60 + float(minsec[1]), 3)
        return sec

    def parse_pdf(self, file: str) -> pd.DataFrame:
        """
        This method accepts a PDF and returns a dataframe with all riders and their lap times and tyre information.
        :param file: the file path including file name and extension to the practice session file.

        :return: a dataframe
        """
        with fitz.Document(file) as doc:
            text = ""
            for page in doc:
                text += page.get_text()

        riders = re.findall("[A-Z][a-z]+ [A-Z??]{2,}", text)
        data_dict = re.split("[A-Z][a-z]+ [A-Z??]{2,}", text)  # text data from each rider

        all_lapt = []
        for rider in data_dict:
            rider_lapt = re.findall("\d'\d\d.\d\d\d", rider)  # all laptimes from each rider
            all_lapt.append(rider_lapt)

        fastest_lap = all_lapt[-1][0]  # do I need to check here: fastest_lap = all_lapt[-2][0]
        fastest_lap_sec = self._min_to_seconds(fastest_lap)
        threshold_time = fastest_lap_sec * self.threshold

        check_dupl = []  # see if there are any duplicate names for the riders
        lapt_summary = []
        for i in range(1, len(riders) + 1):
            if riders[i - 1] not in check_dupl:
                check_dupl.append(riders[i - 1])
                all_lapt_sec = []
                for laptime in all_lapt[i]:
                    lapt_sec = self._min_to_seconds(laptime)
                    # laptimes faster than the fastest lap or slower than the slowest threshold will not be counted
                    # threshold is the fastest lap * 1.03 (I made this up, don't know if there is a better threshold)
                    if (lapt_sec >= fastest_lap_sec) and (lapt_sec <= threshold_time):
                        all_lapt_sec.append(lapt_sec)
            else:
                # the duplicate names only happens when a rider set the fastest laptime
                # so proceed as usual, but discard the 1st encountered laptime
                for laptime in all_lapt[i][1:]:
                    lapt_sec = self._min_to_seconds(laptime)
                    if (lapt_sec >= fastest_lap_sec) and (lapt_sec <= threshold_time):
                        all_lapt_sec.append(lapt_sec)
                continue
            try:
                # the regex matches manufacturers name as well as riders name
                # in the case it doesn't match the riders, there will be no laptime
                # the try except is used to avoid errors caused by no laptime
                if not all_lapt[i]:
                    check_dupl.remove(check_dupl[-1])
                    continue
                else:
                    lapt_summary.append(all_lapt_sec)
            except:
                check_dupl.remove(check_dupl[-1])

        # put lists into dict and print outputs
        data_dict = dict(zip(check_dupl, lapt_summary))

        rider_list = list()
        all_laps = list()

        for rider in list(data_dict.keys()):
            laps = data_dict[rider]
            for lap in laps:
                rider_list.append(rider)
                all_laps.append(lap)

        df = pd.DataFrame(list(zip(rider_list, all_laps)))
        df.columns = ["Riders", "LapTimes"]

        return df


def analyser(data: pd.DataFrame):
    """
    A function that performs analysis on a dataframe with lots of lap times.
    """
    # plot laptimes by rider
    unique_riders = data["Riders"].unique()
    selected_riders = st.multiselect("Pick riders to compare", unique_riders)
    st.write("You selected: ", selected_riders)

    rider_laps = data[data["Riders"].isin(selected_riders)]
    grouped_df = rider_laps.groupby("Riders")

    st.dataframe(rider_laps)
    rider_laps["LapNumber"] = range(1, len(rider_laps) + 1)
    lap_numbers = np.arange(1, len(rider_laps) + 1)
    st.text(lap_numbers)

    line_chart = alt.Chart(
        rider_laps, title="Rider lap times").mark_line(point=True).encode(
        x=alt.X('LapNumber:Q'),
        y=alt.Y(
            'LapTimes:Q',
            title=f"Lap times (seconds) - lower is better"
        )
    ).interactive()
    st.altair_chart(line_chart)

    # display the dataframe
    show_raw_data = st.checkbox(label="Show lap time data")
    if show_raw_data:
        st.dataframe(data)


if __name__ == "__main__":
    parser = PdfParser()
    pdfs = PdfRetriever()

    races = [
        "QAT", "INA", "ARG", "AME", "POR", "SPA", "FRA", "ITA", "CAT", "GER", "NED", "GBR", "AUT", "RSM", "ARA", "JPN",
        "THA", "AUS", "MAL", "VAL"
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

    fname = pdfs.retrieve_file(year, race, session)

    session_file = st.file_uploader("Session file", type=["pdf"])
    if session_file:
        dframe = parser.parse_pdf(session_file)
    else:
        dframe = parser.parse_pdf(fname)
    analyser(dframe)

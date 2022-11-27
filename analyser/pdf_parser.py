import fitz
import re
import pandas as pd


class PdfParser:
    """
    This class reads in MotoGP free practice session PDFs and extracts the lap time data for each rider and makes it
    available for use via a Pandas dataframe.
    """
    def __init__(self):
        self.threshold = 1.03

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
        with fitz.open(file) as doc:
            text = ""
            for page in doc:
                text += page.get_text()

        riders = re.findall("[A-Z][a-z]+ [A-ZÑ]{2,}", text)
        data = re.split("[A-Z][a-z]+ [A-ZÑ]{2,}", text)  # text data from each rider

        all_lapt = []
        for rider in data:
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
        data = dict(zip(check_dupl, lapt_summary))

        df = pd.DataFrame(data)

        return df


if __name__ == "__main__":
    parser = PdfParser()
    dframe = parser.parse_pdf("../data/2022-2INA-FP4.pdf")

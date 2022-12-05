# The main entry point to this analysis application
from front_end.streamlit_front_end import StreamlitFrontEnd


if __name__ == "__main__":
    ui = StreamlitFrontEnd()
    ui.run()

"""
File: hoopstatsappModified.py

Modified version of the Basketball Stats Analyzer.
"""

from hoopstatsview import HoopStatsView
import pandas as pd


def cleanStats(frame):
    for column in frame.columns:
        if frame[column].astype(str).str.contains('-').any():
            new_cols = frame[column].astype(str).str.split('-', expand=True)
            made_col = column + "M" 
            att_col = column + "A"    
            frame[made_col] = pd.to_numeric(new_cols[0], errors='coerce')
            frame[att_col] = pd.to_numeric(new_cols[1], errors='coerce')

            frame.drop(columns=[column], inplace=True)

    return frame


def main():
    print("Program started")
    frame = pd.read_csv("cleanbrogdonstats.csv")
    print("CSV loaded")

    frame = cleanStats(frame)  
    print("Data cleaned")

    app = HoopStatsView(frame)
    print("GUI initialized")
    app.mainloop()  


if __name__ == "__main__":
    main()

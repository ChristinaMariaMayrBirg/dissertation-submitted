from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


# Get the files from the path provided in the OP

META_INFO_NR_ROWS = 3
if __name__ == "__main__":
    path = "count_data"
    files = Path(path).glob('*.txt')

    df__ = pd.DataFrame()

    time_slots = {"14:30:00": "15:00:00",
                  "15:20:00": "15:50:00",
                  "16:05:00": "16:35:00"}

    for f in files:
        data = pd.read_csv(f, skiprows=META_INFO_NR_ROWS)
        meta = pd.read_csv(f)[:META_INFO_NR_ROWS]
        meta_ = meta.values[1][0].split(f"Start: ")[1]
        time_slot = meta_.split(f" ")[1]
        date = meta_.split(f" ")[0]
        end_time = date + " " + time_slots[time_slot]

        df = pd.to_datetime(data.values.ravel())
        df = df[df < end_time]

        df = pd.DataFrame( index=df , columns=["Crossed"], data= np.ones(len(df))).reset_index()
        day = df['index'].dt.day.unique()[0]
        df['index'] = df['index'].dt.minute

        line_name = meta.values[1][0].split(f"Start: 2020-10-{day} ")[-1] + " \n " + meta.columns.to_list()[0].split("Messposition: ")[-1]
        df[line_name] = df['index']

        if day == 29:
            df__ = pd.concat([df__, df[line_name]], axis=1)
        else:
            raise ValueError(f"Day : {day}")


    df__ = df__.reindex(sorted(df__.columns), axis=1)
    df__IN = df__.filter(regex='-IN')

    fig = df__IN.hist(layout=(3, 3), figsize=(10, 5), sharey=True, bins=29 )
    plt.setp(fig, ylim=(0, 40))
    plt.tight_layout()
    plt.savefig("output/Day29_IN.png")
    plt.show()
    plt.close()

    counts = df__IN.count().reset_index(name="counts_total")
    meta = counts["index"].str.split( pat = "\n" , expand=True, )
    counts = pd.concat([meta, counts["counts_total"]], axis=1)
    counts = pd.pivot(counts, index=[0], columns=1, values="counts_total")
    counts[" M-B-IN-cleaned"] = counts[" M-B2-IN"] - counts[" M-A-IN"]
    counts["prob_short"] = counts[" M1-(EFG)-IN"] / ( counts[" M-B-IN-cleaned"] + counts[" M1-(EFG)-IN"] )

    plt.plot( ( counts[" M-B-IN-cleaned"] + counts[" M1-(EFG)-IN"] ) ,  counts["prob_short"], marker="o")
    plt.xlabel("Number of arrivals (estimate)")
    plt.ylabel("Probability: short route")
    plt.savefig("output/Correlation.png")
    plt.show()
    plt.close()


    counts.to_latex("output/pedestrian_counts.tex")








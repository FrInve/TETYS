import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import pandas as pd
import seaborn as sns


def plot_events(events):
    for year, desc in events.items():
        plt.axvline(x=year, linestyle='--', color='r',alpha=0.3)
        plt.text(year, 1000, desc, rotation=90, color='r', alpha=0.75)
    #plt.show()

def get_covid_data(start_date='2019-12-01', end_date='2022-12-30'):
    url = "https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/cases_deaths/biweekly_cases.csv"
    df = pd.read_csv(url)

    df['Global COVID-19 Cases'] = df['World']
    df = df[['date','Global COVID-19 Cases']]
    df['date'] = pd.to_datetime(df['date'])
    df = df.set_index('date')

    mask = (df.index >= start_date) & (df.index <= end_date)
    filtered_df = df.loc[mask]
    return filtered_df

@ticker.FuncFormatter
def major_formatter(x, pos):
    return f"{x/1000000:.0f}"

@ticker.FuncFormatter
def major_formatter_perc(x,pos):
    return f"{x*100:.1f}"

def plot_covid_cases(covid_df, ax):
    line_plot = sns.lineplot(x=covid_df.index.values, y=covid_df['Global COVID-19 Cases'].values, data=covid_df, ax=ax, alpha=0.3)
    plt.fill_between(covid_df.index.values, covid_df['Global COVID-19 Cases'].values, alpha=0.1)
    ax.yaxis.set_major_formatter(major_formatter)
    return line_plot

def reduce_x_ticks(ax):
    """ USELESS
    """
    for label in ax.get_xticklabels():
        text = label.get_text()
        text = text[:4]
        label.set_text(text)
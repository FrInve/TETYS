from pydantic import BaseModel
from typing import List, Tuple
import pandas as pd


class Topic(BaseModel):
    id: int
    terms: List[Tuple[str, float]]
    start_date: str
    end_date: str
    frequency: str
    absolute_frequencies: List[int]
    relative_frequencies: List[float]
    rankings: List[int]


class TimeSeriesHolder:
    def __init__(
        self,
        df_absolute_frequencies: str,
        df_relative_frequencies: str,
    ):
        self.df_absolute_frequencies = pd.read_csv(df_absolute_frequencies)
        self.df_absolute_frequencies = self.prepare_dataframe(
            self.df_absolute_frequencies, round=True
        )

        self.df_relative_frequencies = pd.read_csv(df_relative_frequencies)
        self.df_relative_frequencies = self.prepare_dataframe(
            self.df_relative_frequencies
        )
        self.init_rankings()

    @staticmethod
    def prepare_dataframe(df: pd.DataFrame, round: bool = False) -> pd.DataFrame:
        df["Date"] = pd.to_datetime(df["Date"])
        df.set_index("Date", inplace=True)
        df.fillna(0, inplace=True)
        if df.index.freqstr is None:
            new_index = pd.date_range(df.index[0], df.index[-1], freq="7D")
            df = (
                df.reindex(df.index.union(new_index))
                .interpolate(method="time")
                .reindex(new_index)
            )
        if round:
            df = df.round(0).astype(int)
        return df

    def init_rankings(self):
        self.rankings = self.df_absolute_frequencies.rank(
            axis=1, ascending=False, method="min"
        )

    def get_topic(
        self, topic_id: int, resolution: str, start_date: str, end_date: str
    ) -> Tuple[List[float], List[float], List[int]]:
        start_date = pd.to_datetime(start_date, format="%Y-%m-%d")
        end_date = pd.to_datetime(end_date, format="%Y-%m-%d")
        print(resolution)
        return (
            self.df_absolute_frequencies.loc[start_date:end_date, str(topic_id)]
            .resample(resolution)
            .sum()
            .to_list(),
            self.df_relative_frequencies.loc[start_date:end_date, str(topic_id)]
            .resample(resolution)
            .mean()
            .to_list(),
            self.rankings.loc[start_date:end_date, str(topic_id)]
            .resample(resolution)
            .last()
            .to_list(),
        )

    def get_starting_date(self) -> str:
        return self.df_absolute_frequencies.index[0].strftime("%Y-%m-%d")

    def get_ending_date(self) -> str:
        return self.df_absolute_frequencies.index[-1].strftime("%Y-%m-%d")

    def get_frequency(self) -> str:
        return self.df_absolute_frequencies.index.freqstr

    def get_trending_topics(self) -> List[str]:
        # Get rankings of topics for the last available date
        top10_topics = self.rankings.iloc[-1].sort_values().index[:11]
        top10_topics = top10_topics[top10_topics != "-1"][:10]
        return top10_topics.tolist()


class Terms(BaseModel):
    id: int
    terms: List[Tuple[str, float]]

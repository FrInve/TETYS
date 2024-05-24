from pydantic import BaseModel
import pandas as pd
from typing import List, Tuple


class Context(BaseModel):
    name: str  # metadata - ID of context
    events: List[Tuple[str, str]]  # List[(str, str)]  # date, description
    background_data: List[Tuple[str, float]]  # List[(str, float)]  # date, value
    background_axis_name: str


class ContextHolder:
    def __init__(
        self,
        name,
        background_trend_path: str,
        background_trend_title: str,
        events_path: str,
    ):
        self.name = name

        self.background_trend = pd.read_csv(background_trend_path)
        self.background_trend["Date"] = pd.to_datetime(self.background_trend["Date"])
        self.background_trend.set_index("Date", inplace=True)

        self.background_trend_title = background_trend_title

        self.events = pd.read_csv(events_path)
        self.events["Date"] = pd.to_datetime(self.events["Date"])
        self.events.set_index("Date", inplace=True)

    def to_model(self) -> Context:
        return Context(
            name=self.name,
            events=self.events.apply(
                lambda x: (x.name.strftime("%Y-%m-%d"), x["Event"]), axis=1
            ).tolist(),
            # []
            #     (str(date), event)
            #     for date, event in zip(self.events.index, self.events["Event"])
            # ],
            background_data=self.background_trend.apply(
                lambda x: (x.name.strftime("%Y-%m-%d"), x["Value"]), axis=1
            ).tolist(),
            # [
            #     (str(date), value) for date, value in self.background_trend.itertuples()
            # ],
            background_axis_name=self.background_trend_title,
        )

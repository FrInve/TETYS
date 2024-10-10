from pydantic import BaseModel, Field
from typing import List
from scipy import stats


class TestResult(BaseModel):
    p_value: float
    statistic: float


class SingleTopicTwoIntervalTestForm(BaseModel):
    project_id: str
    topic_id: int
    first_interval_values: List[float]
    second_interval_values: List[float]


class SingleTopicTwoIntervalTest:
    def __init__(self, form: SingleTopicTwoIntervalTestForm):
        self.project_id = form.project_id
        self.topic_id = form.topic_id
        self.first_interval_values = form.first_interval_values
        self.second_interval_values = form.second_interval_values
        self.result = None

    def compute(self):
        # Compute the p-value
        self.result = stats.kruskal(
            self.first_interval_values, self.second_interval_values
        )

    def get_result(self):
        return TestResult(p_value=self.result.pvalue, statistic=self.result.statistic)


class SingleTopicMultipleIntervalTestForm(BaseModel):
    project_id: str
    topic_id: int
    number_of_intervals: int
    interval_values: List[List[float]] = Field(..., min_items=2)


class SingleTopicMultipleIntervalTest:
    def __init__(self, form: SingleTopicMultipleIntervalTestForm):
        self.project_id = form.project_id
        self.topic_id = form.topic_id
        self.number_of_intervals = form.number_of_intervals
        self.interval_values = form.interval_values
        self.result = None

    def compute(self):
        # Compute the p-value
        self.result = stats.kruskal(*self.interval_values)

    def get_result(self):
        return TestResult(p_value=self.result.pvalue, statistic=self.result.statistic)

from pydantic import BaseModel, Field
from typing import List
from scipy import stats
from scikit_posthocs import posthoc_dunn
import numpy as np


class TestResult(BaseModel):
    p_value: float
    statistic: float
    p_values_post_hoc: List[float] = None
    idx_of_intervals_that_are_different: List[int] = None


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
        if self.result.pvalue < 0.05:
            # Compute the post-hoc test
            self.post_hoc_result = posthoc_dunn(self.interval_values, p_adjust="holm")

            # True if each p-value of the bottom of the upper triangular matrix (diag k=1) is less than 0.05
            is_different_intervals = [False] + list(
                np.diag(self.post_hoc_result.le(0.10).to_numpy(), k=1)
            )
            self.idx_of_intervals_that_are_different = [
                i + 1
                for i, is_different in enumerate(is_different_intervals)
                if is_different
            ]

    def get_result(self):
        if self.result.pvalue < 0.05:
            return TestResult(
                p_value=self.result.pvalue,
                statistic=self.result.statistic,
                p_values_post_hoc=[
                    self.post_hoc_result.iloc[i - 2, i - 1]  # idx start from one
                    for i in self.idx_of_intervals_that_are_different
                ],
                idx_of_intervals_that_are_different=self.idx_of_intervals_that_are_different,
            )
        else:
            return TestResult(
                p_value=self.result.pvalue, statistic=self.result.statistic
            )

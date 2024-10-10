# from typing import List
# from functools import lru_cache
# from utils import logger
# import os


# @lru_cache()
# def get_projects(path: str) -> List[str]:
#     try:
#         return os.listdir(path)  # return a list of projects in the path
#     except FileNotFoundError:
#         logger.info("No projects found in the path")
#         return []

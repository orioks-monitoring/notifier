import os
import pathlib
import traceback
from typing import Union


class CommonHelper:
    @staticmethod
    def is_correct_convert_to_float(x) -> bool:
        try:
            float(x)
            return True
        except ValueError:
            return False

    @staticmethod
    def safe_delete(path: Union[str, pathlib.Path]) -> None:
        try:
            os.remove(path)
        except FileNotFoundError:
            pass

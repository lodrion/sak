"""functions for working with lists and structures"""

from typing import Any, Dict, List


def reorient_dict_of_lists(dict_of_lists: Dict[str, List[Any]]) -> List[Dict[str, Any]]:
    """Take a structure of lists and make a list of structures from it"""
    keys = list(dict_of_lists.keys())
    return [dict(zip(keys, values)) for values in zip(*dict_of_lists.values())]

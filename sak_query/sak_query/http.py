"""Utilities for getting data from web APIs"""
from typing import Any, Dict, List

import requests

class HTTPAPISession:

    def __init__(self, max_retries: int = 1) -> None:
        """Initialize requests session with given number of retries."""
        self._session = requests.Session()
        self._session.mount("http://", requests.adapters.HTTPAdapter(max_retries=max_retries))
        self._session.mount("https://", requests.adapters.HTTPAdapter(max_retries=max_retries))

    def data_from_get(self, *args: List, **kwargs: Dict[str, str]) -> Any:
        """Get json data from the API given args/kwargs. Raise on error."""
        response = self._session.get(*args, **kwargs)
        response.raise_for_status()
        return response.json()

    def data_from_post(self, *args: List, **kwargs: Dict[str, str]) -> Any:
        """Get json data from the API by POSTing given args/kwargs. Raise on error."""
        response = self._session.post(*args, **kwargs)
        response.raise_for_status()
        return response.json()

    def text_from_get(self, *args: List, **kwargs: Dict[str, str]) -> str:
        """Get text from the API given args/kwargs. Raise on error."""
        response = self._session.get(*args, **kwargs)
        response.raise_for_status()
        return response.text

    def text_from_post(self, *args: List, **kwargs: Dict[str, str]) -> str:
        """Get text from the API given args/kwargs. Raise on error."""
        response = self._session.post(*args, **kwargs)
        response.raise_for_status()
        return response.text

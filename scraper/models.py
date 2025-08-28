"""Data models for the web scraper"""

from dataclasses import dataclass
from typing import List

@dataclass
class ScrapedPage:
    url: str
    title: str
    content: str
    links: List[str]
    meta_description: str = ""
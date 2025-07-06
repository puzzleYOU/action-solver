from enum import StrEnum
from typing import Self

from dataloader import PresentationModel


class Locale(PresentationModel):
    language_code: str
    country_code: str


class SizeUnit(StrEnum):
    CM = "cm"
    MM = "mm"
    PX = "px"


class Size(PresentationModel):
    width: int
    height: int
    unit: SizeUnit


class Image(PresentationModel):
    size: Size
    thumbnail_image_url: str
    original_image_url: str


class Author(PresentationModel):
    prename: str
    surname: str
    titles: list[str]


class Rating(PresentationModel):
    score: float
    author: str | None
    summary: str
    detail: str | None


class Book(PresentationModel):
    isbn: str
    title: str
    locale: Locale
    authors: list[Author]
    previews: list[Image]
    ratings: list[Rating]
    related_books: list[Self]

from pathlib import Path

import pyudon
import polars as pl


class ImageDirectory:
    def __init__(self, path: Path) -> None:
        self._path = path

    def get_image(self, name: str) -> pyudon.Image:
        img_path = self._path / name
        with img_path.open("rb") as f:
            image = pyudon.Image(f.read())

        return image


class DeckDefine:
    DTYPES = {
        "name": pl.Utf8,
        "image_top": pl.Utf8,
        "image_bottom": pl.Utf8,
        "number_of": pl.Int8
    }
    REQUIRED_COLUMNS = list(DTYPES.keys())

    def __init__(self, name: str, df: pl.DataFrame) -> None:
        self._name = name
        self._df = df

        self._validate()

    def _validate(self) -> None:
        if not set(self.REQUIRED_COLUMNS).issubset(set(self._df.columns)):
            raise ValueError("Missing the required column(s).\n"
                             f"required: {self.REQUIRED_COLUMNS}\n"
                             f"actual  : {self._df.columns}")

        dtypes_dict = {column: dtype for column, dtype in zip(self._df.columns, self._df.dtypes)}
        if dtypes_dict != self.DTYPES:
            raise ValueError("dtype(s) does not match the expected.\n"
                             f"expected: {self.DTYPES}\n"
                             f"actual  : {dtypes_dict}")

    def get_deck(self, image_dict: ImageDirectory, card_size: int = 2) -> pyudon.Deck:
        cards = []
        for row_dict in self._df.rows(named=True):
            image_top = image_dict.get_image(row_dict["image_top"])
            image_bottom = image_dict.get_image(row_dict["image_bottom"])
            cards.append(pyudon.Card(
                row_dict["name"],
                image_top,
                image_bottom,
                card_size
            ))
        deck = pyudon.Deck(self._name, cards)

        return deck


class DecksDefine:
    DTYPES = {
        "name": pl.Utf8,
        "image_top": pl.Utf8,
        "image_bottom": pl.Utf8,
        "deck": pl.Utf8,
        "number_of": pl.Int8
    }
    REQUIRED_COLUMNS = list(DTYPES.keys())

    def __init__(self, df: pl.DataFrame) -> None:
        self._df = df

        self._validate()

    def _validate(self) -> None:
        if not set(self.REQUIRED_COLUMNS).issubset(set(self._df.columns)):
            raise ValueError("Missing the required column(s).\n"
                             f"required: {self.REQUIRED_COLUMNS}\n"
                             f"actual  : {self._df.columns}")

        dtypes_dict = {column: dtype for column, dtype in zip(self._df.columns, self._df.dtypes)}
        if dtypes_dict != self.DTYPES:
            raise ValueError("dtype(s) does not match the expected.\n"
                             f"expected: {self.DTYPES}\n"
                             f"actual  : {dtypes_dict}")

    @property
    def unique_deck_names(self) -> list[str]:
        return self._df.get_column("deck").unique().to_list()

    def get_deck(self, deck_name: str, card_size: int = 2):
        df = self._df.filter(
            pl.col("deck") == deck_name
        )
        df = df.drop("deck")
        deck_define = DeckDefine(deck_name, df)
        deck = deck_define.get_deck(card_size)

        return deck

    @classmethod
    def generate_template(cls) -> pl.DataFrame:
        blank_data_dict = {key: [None] for key in cls.DTYPES.keys()}

        df = pl.DataFrame(blank_data_dict)

        return df

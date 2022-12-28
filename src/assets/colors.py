import enum

__all__: tuple[str, ...] = (
    "Colors",
    "BackgroundColors",
    "Styles",
    "AnsiBuilder",
)


class Colors(enum.IntEnum):
    GRAY = 30
    RED = 31
    GREEN = 32
    YELLOW = 33
    BLUE = 34
    MAGENTA = 35
    CYAN = 36
    WHITE = 37


class BackgroundColors(enum.IntEnum):
    FIREFLY_DARK_BLUE = 40
    ORANGE = 41
    MARBLE_BLUE = 42
    GREYISH_TURQUOISE = 43
    GRAY = 44
    INDIGO = 45
    LIGHT_GRAY = 47
    WHITE = 48


class Styles(enum.IntEnum):
    NORMAL = 0
    BOLD = 1
    UNDERLINE = 4


class AnsiBuilder:
    def __init__(
        self,
        string: str = "",
        *,
        color: Colors | None = None,
        background_color: BackgroundColors | None = None,
        style: Styles | None = None,
    ) -> None:
        self.string = string
        self.color = color
        self.background_color = background_color
        self.style = style

    def __call__(self, text: str) -> str:
        buckets: list[str] = []
        if self.color is not None:
            buckets.append(str(self.color))
        if self.background_color is not None:
            buckets.append(str(self.background_color))
        if self.style is not None:
            buckets.append(str(self.style))
        return f"\033[{';'.join(buckets)}m{text}" if buckets else text

    def __str__(self) -> str:
        return self.format_text(self.string)

    def __add__(self, other: "AnsiBuilder") -> "AnsiBuilder":
        return AnsiBuilder(
            string=self.string.replace("\n```", "") + other.string.replace("```ansi\n", ""),
            color=self.color or other.color,
            background_color=self.background_color or other.background_color,
            style=self.style or other.style,
        )

    def write(self, string: str) -> None:
        self.string += string

    def format_text(self, text: str, *, block: bool = False) -> str:
        return f"```ansi\n{self(text)}\n```" if block else self(text)

    @classmethod
    def to_ansi(cls, string: str, *colors: Colors | BackgroundColors | Styles, block: bool = False) -> str:
        text = f"\033[{';'.join(str(color) for color in colors)}m{string}"
        return f"```ansi\n{text}\n```" if block else text

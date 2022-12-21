import enum

__all__: tuple[str, ...] = ("Buttons",)


class Buttons(enum.Enum):
    NEXT = "<:rightArrow:989136803284004874>"
    PREVIOUS = "<:leftArrow:989134685068202024>"
    FIRST = "<:DoubleArrowLeft:989134953142956152>"
    LAST = "<:DoubleArrowRight:989134892384256011>"
    STOP = "<:dustbin:989150297333043220>"

from .categories import Categories
from .colors import AnsiBuilder, BackgroundColors, Colors, Styles
from .languages import Languages
from .sites import Sites, ValidSites
from .terms import Termer

__all__: tuple[str, ...] = (
    "Languages",
    "Categories",
    "Termer",
    "ValidSites",
    "Sites",
    "Colors",
    "BackgroundColors",
    "Styles",
    "AnsiBuilder",
    "TIPS",
)

TIPS: tuple[str, ...] = (
    "You can translate to all languages supported by google translate",
    "Use pokemon terms in Pokemon novels to get correct pokemon name",
    "You can get novels from certain category with library search command",
    "Review a novel you liked or disliked with library review command",
    "You can use multi-translate to translate multiple novels",
    "See your ranking in leaderboard",
    "If you would like bot to have any new feature , you can suggest in suggest command",
    "If you found any bugs in bot, you can report in suggest command",
    "Split any large novel into smaller files using split command",
    "Discord message link in translation only works if  bot has access to the message link",
    "Bot can translate novel from all discord attachment link ",
    "Get a random novel from library using library random command",
)

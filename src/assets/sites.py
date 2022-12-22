import dataclasses
import enum
import re
import typing as t

if t.TYPE_CHECKING:
    from bs4 import BeautifulSoup

__all__: tuple[str, ...] = (
    "ValidSites",
    "Sites",
)


class ValidSites(enum.Enum):
    """Valid sites for crawling"""

    TRXS = "trxs"
    TONGRENQUAN = "tongrenquan"
    FFXS = "ffxs"
    BIXIANGE = "bixiange"
    POWANJUAN = "powanjuan"
    BIQUGEABC = "biqugeabc"
    UUKANSHU = "uukanshu"
    QBTR = "qbtr"
    SJKS88 = "sjks88"
    SHU69 = "69shu"
    PTWXZ = "ptwxz"
    JPXS = "jpxs"
    NOVELSKNIGHT = "novelsknight"
    XKLXSW = "xklxsw"
    YOUYOUKANSHU = "youyoukanshu"
    TXT520 = "txt520"
    READWN = "readwn"
    NOVELMT = "novelmt"
    WUXIAX = "wuxiax"
    FANNOVELS = "fannovels"
    XBIQUGE = "xbiquge"
    TXT2015 = "2015txt"
    NOVELFULL = "novelfull"
    KSW4 = "4ksw"
    READLIGHTNOVEL = "readlightnovel"
    SHUBAOW = "shubaow"
    SHU630 = "630shu"
    AKSHU8 = "akshu8"
    QCXXS = "qcxxs"
    KRMTL = "krmtl"
    SOXSCC = "soxscc"
    MXINDINGDIANXSW = "m.xindingdianxsw"
    WWWXINDINGDIANXSW = "www.xindingdianxsw"
    METRUYENCV = "metruyencv"

    @staticmethod
    def rearrange(urls: list[str]) -> list[str]:
        return list(
            dict.fromkeys(sorted(urls, key=lambda x: int(re.search(r"\d+", x.split("/")[-1]).group(0))))  # type: ignore
        )

    @classmethod
    def all_sites(cls) -> list[str]:
        """Returns all sites in a list"""
        sites: list[str] = []
        for site in cls:
            sites.append(str(site.value))
        return sites

    @classmethod
    def is_valid(cls, url: str) -> bool:
        """Returns whether a site is valid"""
        for site in cls.all_sites():
            if site in url:
                return True
        return False

    @classmethod
    def format_link(cls, link: str) -> str:
        link = link.rstrip("/ ")
        if str(cls.SHU69.value) in link and "txt" in link:
            return link.replace("/txt", "").replace(".htm", "/")
        elif str(cls.PTWXZ.value) in link and "bookinfo" in link:
            return link.replace("bookinfo", "html").rstrip(".html")
        elif str(cls.XKLXSW.value) in link and "www" in link:
            return link.replace("www", "m")
        else:
            return link

    @classmethod
    def get_urls(cls, soup: "BeautifulSoup", url: str) -> list[str]:
        """Returns all urls from a soup"""
        url = url.rstrip(".html").rstrip(".htm/")
        suffix = url.split("/")[-1]
        midfix = url.replace(f"/{suffix}", "").split("/")[-1]
        prefix = url.replace(f"/{midfix}/{suffix}", "")
        urls: list[str] = []
        if str(cls.SHU69.value) in url:
            for a in soup.find_all("a"):
                if f"/{suffix}/" in str(a.get("href")) and "http" in str(a.get("href")):
                    urls.append(a["href"])
        elif str(cls.PTWXZ.value) in url or str(cls.XBIQUGE.value) in url:
            for a in soup.find_all("a"):
                if ".html" in str(a.get("href")) and "/" not in str(a.get("href")):
                    urls.append(f"{prefix}/{midfix}/{suffix}/{a['href']}")
            urls = cls.rearrange(urls) if str(cls.XBIQUGE.value) in url else urls
        elif str(cls.UUKANSHU.value) in url:
            pattern = re.compile(r"id=(\d+)")
            if "sj." in url or "t." in url:
                num = pattern.search(suffix).group(1)  # type: ignore
                tid = f"read.aspx?tid={num}"
                for a in soup.find_all("a"):
                    if tid in str(a.get("href")) and "sid=" in str(a.get("href")):
                        urls.append(f"{prefix}/{midfix}/{a['href']}")
                urls = list(dict.fromkeys(urls))
            else:
                for a in soup.find_all("a"):
                    if f"{suffix}" in str(a.get("href")) and ".html" in str(a.get("href")):
                        urls.append(f"{prefix}{a['href']}")
                urls = cls.rearrange(urls)
        elif str(cls.NOVELSKNIGHT.value) in url:
            for a in soup.find_all("a"):
                if f"{suffix}" in str(a.get("href")) and "chapter" in str(a.get("href")):
                    urls.append(a["href"])
        elif str(cls.XKLXSW.value) in url:
            for a in soup.find_all("a"):
                if ".html" in str(a.get("href")):
                    urls.append(f"{prefix}/{midfix}/{suffix}/{a['href']}")
            urls = cls.rearrange(urls)
        elif str(cls.NOVELFULL.value) in url:
            for a in soup.find_all("a"):
                if f"{suffix}" in str(a.get("href")) and "chapter" in str(a.get("href")):
                    urls.append(f"{prefix}/{midfix}/{a['href']}")
        elif str(cls.READLIGHTNOVEL.value) in url:
            for a in soup.find_all("a"):
                if f"{suffix}" in str(a.get("href")) and "chapter" in str(a.get("href")):
                    link = a.get("href")
                    number = int(re.search(r"chapter-\d+", link).group(0).replace("chapter-", ""))  # type: ignore
                    urls = [f"{prefix}/{midfix}/{suffix}/chapter-{n}.html" for n in range(0, number + 1)]
                    break
        elif str(cls.SHUBAOW.value) in url:
            for a in soup.find_all("a"):
                if f"/{suffix}" in str(a.get("href")):
                    urls.append(f"{prefix}/{midfix}/{a['href']}")
            urls = cls.rearrange(urls)
        elif str(cls.SHU630.value) in url:
            for a in soup.find_all("a"):
                if f"/{suffix}/" in str(a.get("href")):
                    urls.append(f"{prefix}/{a['href']}")
        elif str(cls.AKSHU8.value) in url:
            for a in soup.find_all("a"):
                if (
                    f"/{suffix}/" in str(a.get("href"))
                    and "http" in str(a.get("href"))
                    and ".html" in str(a.get("href"))
                ):
                    urls.append(a.get("href"))
            urls = cls.rearrange(urls)
        elif str(cls.QCXXS.value) in url or str(cls.WWWXINDINGDIANXSW.value) in url:
            for a in soup.find_all("a"):
                if (
                    f"/{midfix}/" in str(a.get("href"))
                    and ".html" in str(a.get("href"))
                    and "index" not in str(a.get("href"))
                ):
                    name = f"www.{cls.QCXXS.value}" if str(cls.QCXXS.value) in url else cls.WWWXINDINGDIANXSW.value
                    urls.append(f"https://{name}.com{a['href']}")
            urls = cls.rearrange(urls)
        elif str(cls.KRMTL.value) in url:
            spans = soup.find_all("span")
            chapters = [span for span in spans if "Chapter" in span.text]
            chapters = [int(s.group(0)) for chapter in chapters if (s := re.search(r"\d+", chapter.text))]
            max_chapter = max(chapters)
            urls = [f"{prefix}/{midfix}/{suffix}/{n}" for n in range(1, max_chapter + 1)]
        elif str(cls.METRUYENCV.value) in url:
            urls = [url.get("href") for url in soup.find_all("a") if "/chuong-" in str(url.get("href"))]
            max_chapter = max([int(url.split("-")[-1]) for url in urls])
            urls = [f"{prefix}/{midfix}/{suffix}/chuong-{n}" for n in range(1, max_chapter + 1)]
        else:
            for a in soup.find_all("a"):
                if f"/{suffix}" in str(a.get("href")):
                    urls.append(f"{prefix}/{a['href']}")
            if str(cls.TXT2015.value) in url:
                urls = cls.rearrange([i for i in urls if "/book/" in i])
            elif str(cls.YOUYOUKANSHU.value) in url:
                urls = cls.rearrange(urls)
            elif any(
                x in url for x in map(str, (cls.READWN.value, cls.NOVELMT.value, cls.WUXIAX.value, cls.FANNOVELS.value))
            ):
                max_num = max([int(x.split("_")[-1].rstrip(".html")) for x in urls if "_" in x])
                urls = [f"{prefix}/{midfix}/{suffix}_{n}.html" for n in range(1, max_num + 1)]
        return [re.sub(r"(?<!:)//", "/", link) for link in urls]


@dataclasses.dataclass(frozen=True, kw_only=True)
class Site:
    name: str
    url_css: str = "* ::text"
    title_css: tuple[str, ...] = ("title", "title ::text")
    next_css: tuple[str, ...] | None = None

    @classmethod
    def default(cls) -> "Site":
        return cls(name="", url_css="* ::text", title_css=("title", "title ::text"), next_css=None)


class Sites(enum.Enum):
    Bixiange = Site(
        name="bixiange",
        url_css="p ::text",
        title_css=(".desc>h1", ""),
    )
    SJ_Uukanshu = Site(
        name="sj.uukanshu",
        url_css="#read-page p ::text",
        title_css=(".bookname", "#divContent >h3 ::text"),
    )
    T_Uukanshu = Site(
        name="t.uukanshu",
    )
    Uukanshu_CC = Site(
        name="uukanshu.cc",
        url_css=".bbb.font-normal.readcotent ::text",
        next_css=(".booktitle", "h1 ::text"),
    )
    Ptwxz = Site(
        name="ptwxz",
        title_css=("title", "title ::text"),
    )
    Uukanshu = Site(
        name="uukanshu",
        url_css=".contentbox ::text",
        title_css=("title", "h1#timu ::text"),
    )
    Trxs_ME = Site(
        name="trxs.me",
        url_css=".read_chapterDetail ::text",
        title_css=(".infos>h1:first-child", ""),
    )
    Youyoukanshu = Site(
        name="youyoukanshu",
        url_css="#content > article ::text",
        title_css=(
            "#content > div.page.hidden-xs.hidden-sm > a:nth-child(3)",
            "#content > div.readtop > div.pull-left.hidden-lg > a > font > font",
        ),
    )
    Trxs_CC = Site(
        name="trxs.cc",
        url_css=".read_chapterDetail ::text",
        next_css=(".infos>h1:first-child", ""),
    )
    Qbtr = Site(
        name="qbtr",
        url_css=".read_chapterDetail ::text",
        title_css=(".infos>h1:first-child", ""),
    )
    Tongrenquan = Site(
        name="tongrenquan",
        url_css=".read_chapterDetail ::text",
        title_css=(".infos>h1:first-child", ""),
    )
    Biqugeabc = Site(
        name="biqugeabc",
        url_css=".text_row_txt >p ::text",
    )
    Jpxs = Site(
        name="jpxs",
        url_css="read_chapterDetail p ::text",
        title_css=(".infos>h1:first-child", ""),
    )
    Powanjun = Site(
        name="powanjun",
        url_css="content p::text",
        title_css=("title", ""),
    )
    Ffxs = Site(
        name="ffxs",
        url_css="content p::text",
        title_css=("title", ""),
    )
    Sjks = Site(
        name="sjks",
        url_css="content p::text",
        title_css=(".box-artic>h1", ""),
    )
    Txt520 = Site(
        name="txt520",
        url_css="div.content > p ::text",
        title_css=("title", ""),
    )
    Shu69 = Site(
        name="69shu",
        url_css=".txtnav ::text",
        title_css=(".bread>a:nth-of-type(3)", "title ::text"),
    )
    Readwn = Site(
        name="readwn",
        url_css=".chapter-content ::text",
        next_css=(
            "#chapter-article > header > div > aside > nav > div.action-select > a.chnav.next",
            "#chapter-article > header > div > div > h1 > a",
        ),
    )
    Novelmt = Site(
        name="novelmt.com",
        url_css=".chapter-content ::text",
        next_css=(
            "#chapter-article > header > div > aside > nav > div.action-select > a.chnav.next",
            "#chapter-article > header > div > div > h1 > a",
        ),
    )
    Wuxiax = Site(
        name="wuxiax.com",
        url_css=".chapter-content ::text",
        next_css=(
            "#chapter-article > header > div > aside > nav > div.action-select > a.chnav.next",
            "#chapter-article > header > div > div > h1 > a",
        ),
    )
    Fannovels = Site(
        name="fannovels.com",
        url_css=".chapter-content ::text",
        next_css=(
            "#chapter-article > header > div > aside > nav > div.action-select > a.chnav.next",
            "#chapter-article > header > div > div > h1 > a",
        ),
    )
    Novelsknight = Site(
        name="novelsknight",
        url_css="div.epcontent.entry-content > p ::text",
    )
    Vbiquge = Site(
        name="vbiquge",
        url_css="#rtext ::text",
    )
    Txt2015 = Site(
        name="2015txt",
        url_css="#cont-body ::text",
    )
    Ksw = Site(
        name="4ksw",
        url_css="div.panel-body.content-body.content-ext ::text",
    )
    Novelfull = Site(
        name="novelfull",
        url_css="#chapter-content ::text",
        next_css=("#next_chap", "#chapter > div > div > a"),
    )
    Novelroom = Site(
        name="novelroom",
        url_css="div.reading-content ::text",
        next_css=(
            "#manga-reading-nav-foot > div > div.select-pagination > div > div.nav-next > a",
            "#manga-reading-nav-head > div > div.entry-header_wrap > div > div.c-breadcrumb > ol > li:nth-child(2) > a",
        ),
    )
    Readlightnovel = Site(
        name="readlightnovel",
        url_css="#growfoodsmart ::text",
        next_css=(
            "#ch-page-container > div > div.col-lg-8.content2 > div > div:nth-child(6) > ul > li:nth-child(3) > a",
            "#ch-page-container > div > div.col-lg-8.content2 > div > div:nth-child(1) > div > div > h1",
        ),
    )
    Shubaow = Site(
        name="shubaow",
        url_css="#nr1 ::text",
        next_css=(
            "#novelcontent > div.page_chapter > ul > li:nth-child(4) > a",
            "#novelbody > div.head > div.nav_name > h1 > font > font",
        ),
    )
    Xklxsw = Site(
        name="xklxsw",
        url_css="#nr1 ::text",
    )
    Shu630 = Site(
        name="630shu",
        url_css="#nr1 ::text",
        next_css=("#pb_next", "title"),
    )
    Akshu8 = Site(
        name="akshu8",
        url_css="#content ::text",
        next_css=("#container > div > div > div.reader-main > div.section-opt.m-bottom-opt > a:nth-child(5)", "title"),
    )
    Wnmtl = Site(
        name="wnmtl",
        url_css="#reader > div > div.chapter-container ::text",
        next_css=("#nextBtn", "#navBookName"),
    )
    Qcxxs = Site(
        name="qcxxs",
        url_css="body > div.container > div.row.row-detail > div > div ::text",
        next_css=(
            "body > div.container > div.row.row-detail > div > div > div.read_btn > a:nth-child(4)",
            "body > div.container > div.row.row-detail > div > h2 > a:nth-child(3)",
        ),
    )

    @classmethod
    def url_css_from_link(cls, link: str) -> str:
        for site in cls:
            if site.value.name in link:
                return site.value.url_css
        return Site.default().url_css

    @classmethod
    def title_css_from_link(cls, link: str) -> tuple[str, ...]:
        for site in cls:
            if site.value.name in link:
                return site.value.title_css
        return Site.default().title_css

    @classmethod
    def next_css_from_link(cls, link: str) -> tuple[str, ...] | None:
        for site in cls:
            if site.value.name in link:
                return site.value.next_css
        return Site.default().next_css

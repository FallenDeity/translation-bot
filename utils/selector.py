
class CssSelector:

    def findURLCSS(link):
        if "bixiange" in link:
            return "p ::text"
        elif "sj.uukanshu" in link or "t.uukanshu" in link:
            return "#read-page p ::text"
        elif "uukanshu.cc" in link:
            return ".bbb.font-normal.readcotent ::text"
        elif "uukanshu" in link:
            return ".contentbox ::text"
        elif (
                "trxs.me" in link
                or "trxs.cc" in link
                or "qbtr" in link
                or "tongrenquan" in link
        ):
            return ".read_chapterDetail ::text"
        elif "biqugeabc" in link:
            return ".text_row_txt >p ::text"
        elif "uuks" in link:
            return "div#contentbox > p ::text"
        elif "jpxs" in link:
            return ".read_chapterDetail p ::text"
        elif "powanjuan" in link or "ffxs" in link or "sjks" in link:
            return ".content p::text"
        elif "txt520" in link:
            return "div.content > p ::text"
        elif "69shu" in link:
            return ".txtnav ::text"
        elif "ptwxz" in link:
            return "* ::text"
        elif "shu05" in link:
            return "#htmlContent ::text"
        elif "readwn" in link or "novelmt.com" in link or "wuxiax.com" in link or "fannovels.com" in link or "novelmtl.com" in link:
            return ".chapter-content ::text"
        elif "novelsemperor" in link or "novelsknight.com" in link:
            return "div.epcontent.entry-content > p ::text"
        elif "www.vbiquge.co" in link:
            return "#rtext ::text"
        elif "2015txt.com" in link:
            return "#cont-body ::text"
        elif "4ksw.com" in link:
            return "div.panel-body.content-body.content-ext ::text"
        elif "novelfull.com" in link:
            return "#chapter-content ::text"
        elif "novelroom.net" in link:
            return "div.reading-content ::text"
        elif "readlightnovel" in link:
            return "#growfoodsmart ::text"
        elif "m.qidian" in link:
            return "#chapterContent ::text"
            #         elif "read.qidian" in link or "book.qidian" in link or "www.qidian" in link:
            #             return "p ::text"
        elif "www.youyoukanshu.com" in link:
            return "#content > article ::text"
        elif "fanqienovel.com" in link:
            return "div.muye-reader-content.noselect ::text"
        elif "m.shubaow.net" in link or "m.longteng788.com/" in link or "m.xklxsw.com" in link or "m.630shu.net" in link:
            return "#nr1 ::text"
        elif "www.xindingdianxsw.com/" in link:
            return "p ::text"
        elif "m.akshu8.com" in link or "soruncg.com" in link or "www.630shu.net" in link or "www.yifan.net" in link or "www.soxscc.net" in link or "feixs.com" in link:
            return "#content ::text"
        elif "www.wnmtl.org" in link:
            return "#reader > div > div.chapter-container ::text"
        elif "m.yifan.net" in link:
            return "#chaptercontent ::text"
        elif "www.qcxxs.com" in link:
            return "body > div.container > div.row.row-detail > div > div ::text"
        elif "m.soxscc.net" in link:
            return "#chapter > div.content ::text"
        elif "metruyencv.com" in link:
            return "#article ::text"
        elif "www.gonet.cc" in link:
            return "body > div.container > div.row.row-detail > div > div ::text"
        elif "www.ops8.com" in link:
            return "#BookText ::text"
        elif "m.77z5.com" in link or "m.lw52.com" in link:
            return "#chaptercontent ::text"
        elif "mtl-novel.net" in link or "novelnext.com" in link:
            return "#chr-content ::text"
        elif "ncode.syosetu.com" in link:
            return "#novel_p ::text"
        elif "m.75zw.com/" in link:
            return "#chapter > div.a75zwcom_i63c9e1d ::text"
        else:
            return "* ::text"

    def findchptitlecss(link):
        if (
                "trxs.me" in link
                or "trxs.cc" in link
                or "tongrenquan" in link
                or "qbtr" in link
                or "jpxs" in link
        ):
            return [".infos>h1:first-child", ""]
        elif "txt520" in link or "powanjuan" in link or "ffxs" in link:
            return ["title", ""]
        elif "bixiange" in link:
            return [".desc>h1", ""]
        elif "sjks" in link:
            return [".box-artic>h1", ""]
        elif "sj.uukanshu" in link or "t.uukanshu" in link:
            return [".bookname", "#divContent >h3 ::text"]
        elif "uukanshu.cc" in link:
            return [".booktitle", "h1 ::text"]
        elif "biqugeabc" in link or "ptwxz" in link:
            return ["title", "title ::text"]
        elif "uuks" in link:
            return [".jieshao_content>h1", "h1#timu ::text"]
        elif "uukanshu" in link:
            return ["title", "h1#timu ::text"]
        elif "69shu" in link:
            return [".bread>a:nth-of-type(3)", "title ::text"]
        elif "m.qidian" in link:
            return ["#header > h1", ""]
        elif "m.soxscc.net" in link:
            return ["title", "#chapter > h1 ::text"]
        elif "www.soxscc.net" in link:
            return ["#info > h1", "body > div.content_read > div > div.bookname > h1 ::text"]
        elif "www.ops8.com" in link:
            return ["div.book-title", "#BookCon > h1"]
        elif "feixs.com" in link:
            return ["title", "#main > "
                                                                                                   "div.bookinfo.m10.clearfix > div.info > p.chaptertitle ::text"]
        else:
            return ["title", "title ::text"]

    def find_next_selector(link):
        if "readwn" in link or "wuxiax.co" in link or "novelmt.com" in link or "fannovels.com" in link or "novelmtl.com" in link:
            return ["#chapter-article > header > div > aside > nav > div.action-select > a.chnav.next", "#chapter-article > header > div > div > h1 > a"]
        elif "novelfull.com" in link:
            return ["#next_chap", "#chapter > div > div > a"]
        elif "novelroom.net" in link:
            return ["#manga-reading-nav-foot > div > div.select-pagination > div > div.nav-next > a", "#manga-reading-nav-head > div > div.entry-header_wrap > div > div.c-breadcrumb > ol > li:nth-child(2) > a"]
        elif "readlightnovel" in link:
            return ["#ch-page-container > div > div.col-lg-8.content2 > div > div:nth-child(6) > ul > li:nth-child(3) > a", "#ch-page-container > div > div.col-lg-8.content2 > div > div:nth-child(1) > div > div > h1"]
        elif "www.youyoukanshu.com" in link:
            return ["#content > div.page.hidden-xs.hidden-sm > a:nth-child(3)", "#content > div.readtop > div.pull-left.hidden-lg > a > font > font"]
        elif "m.shubaow.net" in link:
            return ["#novelcontent > div.page_chapter > ul > li:nth-child(4) > a", "#novelbody > div.head > div.nav_name > h1 > font > font"]
        elif "m.xindingdianxsw.com" in link:
            return ["#chapter > div:nth-child(9) > a:nth-child(3)", "#chapter > div.path > a:nth-child(2)"]
        elif "www.xindingdianxsw.com" in link:
            return ["#A3", "div.con_top > a:nth-child(3)"]
        elif "m.longteng788.com/" in link:
            return ["#pb_next", "#_52mb_h1"]
        elif "m.75zw.com/" in link:
            return ["#chapter > div.pager.z1 > a:nth-child(3)", "#chapter > div.path > a:nth-child(3) > font > font"]
        elif "www.wnmtl.org" in link:
            return ["#nextBtn", "#navBookName"]
        elif "m.akshu8.com" in link or "soruncg.com" in link:
            return ["#container > div > div > div.reader-main > div.section-opt.m-bottom-opt > a:nth-child(5)", "title"]
        elif "m.77z5.com" in link:
            return ["#pt_next", "#top > span > font > font:nth-child(3)"]
        elif "m.yifan.net/" in link:
            return ["#pb_next", "#read > div.header > span.title"]
        elif "www.yifan.net" in link:
            return ["#book > div.content > div:nth-child(5) > ul > li:nth-child(3) > a", "title"]
        elif "m.630shu.net" in link:
            return ["#pb_next", "title"]
        # elif "m.soxscc.net" in link:
        #     return ["#chapter > div.pager > a:nth-child(3)", "#bookname"]
        elif "www.qcxxs.com" in link:
            return ["body > div.container > div.row.row-detail > div > div > div.read_btn > a:nth-child(4)", "body > div.container > div.row.row-detail > div > h2 > a:nth-child(3)"]
        elif "www.gonet.cc" in link:
            return ["body > div.container > div.row.row-detail > div > div > div.read_btn > a:nth-child(4)", "body > div.container > div.row.row-detail > div > h2 > a:nth-child(3) > font > font"]
        elif "mtl-novel.net" in link:
            return ["#next_chap", "#chapter > div > div > a"]
        else:
            return [None, "title"]

class CssSelector:

    # def findURLCSS(link): if "m.bixiange.me" in link: return "#mycontent ::text" if "bixiange" in link or "bixiang"
    # in link: return "p ::text" elif "sj.uukanshu" in link or "t.uukanshu" in link: return "#read-page ::text" elif
    # "uukanshu.cc" in link: return ".bbb.font-normal.readcotent ::text" elif "uukanshu" in link: return "#contentbox
    # ::text" elif ( "trxs.me" in link or "trxs.cc" in link or "qbtr" in link or "tongrenquan" in link ): return
    # ".read_chapterDetail ::text" elif "biqugeabc" in link: return ".text_row_txt >p ::text" # elif "uuks" in link:
    #     return "div#contentbox > p ::text" elif "jpxs" in link: return ".read_chapterDetail p ::text" elif
    #     "powanjuan" in link or "ffxs" in link or "sjks" in link: return ".content p::text" elif "txt520" in link:
    #     return "div.content > p ::text" elif "69shu" in link: return ".txtnav ::text" elif "ptwxz" in link: return
    #     "* ::text" elif "shu05" in link: return "#htmlContent ::text" elif "readwn" in link or "novelmt.com" in
    #     link or "wuxiax.com" in link or "fannovels.com" in link or "novelmtl.com" in link or "www.wuxiap.com" in
    #     link or "www.wuxiau.com" in link: return ".chapter-content ::text" elif "novelsemperor" in link or
    #     "novelsknight.com" in link: return "* ::text" elif "www.vbiquge.co" in link or "www.wfxs.com.tw" in link:
    #     return "#rtext ::text" elif "2015txt.com" in link: return "#cont-body ::text" elif "4ksw.com" in link:
    #     return "div.panel-body.content-body.content-ext ::text" elif "novelfull.com" in link: return
    #     "#chapter-content ::text" elif "novelroom.net" in link: return "div.reading-content ::text" elif
    #     "readlightnovel" in link: return "#growfoodsmart ::text" elif "m.qidian" in link or "m.bqg28.cc" in link:
    #     return "#chapterContent ::text" #         elif "read.qidian" in link or "book.qidian" in link or
    #     "www.qidian" in link: #             return "p ::text" elif "www.youyoukanshu.com" in link or
    #     "www.piaoyuxuan.com" in link or "www.dongliuxiaoshuo.com" in link: return "#content > div.content ::text"
    #     elif "fanqienovel.com" in link: return "div.muye-reader-content.noselect ::text" elif "m.shubaow.net" in
    #     link or "m.longteng788.com/" in link or "m.xklxsw.com" in link or "m.630shu.net" in link or "m.ddxs.com" in
    #     link: return "#nr1 ::text" elif "www.xindingdianxsw.com/" in link: return "p ::text" elif "m.akshu8.com" in
    #     link or "soruncg.com" in link or "www.630shu.net" in link\ or "www.yifan.net" in link or "www.soxscc.net"
    #     in link or "feixs.com" in link \ or "www.tsxsw.net" in link or "www.ttshu8.com" in link or "www.szhhlt.com"
    #     in link\ or "www.bqg789.net" in link or "www.9xzw.com" in link or "www.28zww.cc" in link: return "#content
    #     ::text" elif "www.wnmtl.org" in link: return "#reader > div > div.chapter-container ::text" elif
    #     "m.yifan.net" in link: return "#chaptercontent ::text" elif "www.qcxxs.com" in link: return "body >
    #     div.container > div.row.row-detail > div > div ::text" elif "m.soxscc.net" in link or "m.ttshu8.com" in
    #     link: return "#chapter > div.content ::text" elif "metruyencv.com" in link: return "#article ::text" elif
    #     "www.gonet.cc" in link: return "body > div.container > div.row.row-detail > div > div ::text" elif
    #     "www.ops8.com" in link: return "#BookText ::text" elif "m.77z5.com" in link or "m.lw52.com" in link: return
    #     "#chaptercontent ::text" elif "mtl-novel.net" in link or "novelnext.com" in link or "novelbin.net" in link
    #     or "novelbin.net" in link: return "#chr-content ::text" elif "ncode.syosetu.com" in link: return
    #     "#novel_honbun ::text" elif "m.75zw.com/" in link: return "#chapter > div.a75zwcom_i63c9e1d ::text" elif
    #     "www.webnovelpub.com" in link: return "#chapter-container ::text" elif "m.tsxsw.net" in link: return "#nr
    #     ::text" elif "www.4ksw.com/" in link: return "div.panel-body.content-body.content-ext ::text" elif
    #     "tw.ixdzs.com" in link: return "#page > article ::text" elif "www.shulinw.com/" in link: return
    #     "#htmlContent ::text" elif "ranobes.com" in link: return "div.block.story.shortstory ::text" elif
    #     "m.bqg789.net" in link or "m.biquzw789.org" in link: return "#novelcontent ::text" elif "boxnovel.com" in
    #     link or "bonnovel.com" in link: return "div.cha-content ::text" elif "www.asxs.com" in link: return
    #     "#contents ::text" elif "www.72xsw.net" in link: return "div.box_box ::text" elif "www.31dv.com" in link:
    #     return "#booktxt ::text" elif "1stkissnovel.org" in link: return "div.entry-content > div > div > div >
    #     div.text-left ::text" #elif "www.libraryofakasha.com" in link: #   return "div.chapter-content ::text"
    #     #elif "sangtacviet.vip" in link: #   return ".contentbox ::text" elif "www.novelcool.com" in link: return
    #     "p ::text" elif"novelcool.org/" in link: return "p ::text" elif "m.sywx8.com" in link: return "#nr ::text"
    #     elif "www.tadu.com" in link: return "#partContent ::text" else: return "* ::text"

    def findURLCSS(link):
        domain_mappings = {
            "m.bixiange.me": "#mycontent ::text",
            "bixiange": "p ::text",
            "bixiang": "p ::text",
            "sj.uukanshu": "#read-page ::text",
            "t.uukanshu": "#read-page ::text",
            "uukanshu.cc": ".bbb.font-normal.readcotent ::text",
            "uukanshu": "#contentbox ::text",
            "trxs.me": ".read_chapterDetail ::text",
            "trxs.cc": ".read_chapterDetail ::text",
            "qbtr": ".read_chapterDetail ::text",
            "tongrenquan": ".read_chapterDetail ::text",
            "biqugeabc": ".text_row_txt >p ::text",
            # "uuks": "div#contentbox > p ::text",
            "jpxs": ".read_chapterDetail p ::text",
            "powanjuan": ".content p::text",
            "ffxs": ".content p::text",
            "sjks": ".content p::text",
            "txt520": "div.content > p ::text",
            "69shu": ".txtnav ::text",
            "ptwxz": "* ::text",
            "shu05": "#htmlContent ::text",
            "readwn": ".chapter-content ::text",
            "novelmt.com": ".chapter-content ::text",
            "wuxiax.com": ".chapter-content ::text",
            "fannovels.com": ".chapter-content ::text",
            "novelmtl.com": ".chapter-content ::text",
            "www.wuxiap.com": ".chapter-content ::text",
            "www.wuxiau.com": ".chapter-content ::text",
            "wuxiabee": ".chapter-content ::text",
            "novelsemperor": "* ::text",
            "novelsknight.com": "* ::text",
            "www.vbiquge.co": "#rtext ::text",
            "www.wfxs.com.tw": "#rtext ::text",
            "2015txt.com": "#cont-body ::text",
            "4ksw.com": "div.panel-body.content-body.content-ext ::text",
            "novelfull.com": "#chapter-content ::text",
            "novelroom.net": "div.reading-content ::text",
            "readlightnovel": "#growfoodsmart ::text",
            "m.qidian": "#chapterContent ::text",
            "m.bqg28.cc": "#chapterContent ::text",
            # "read.qidian": "p ::text",
            # "book.qidian": "p ::text",
            # "www.qidian": "p ::text",
            "www.youyoukanshu.com": "#content > div.content ::text",
            "www.piaoyuxuan.com": "#content > div.content ::text",
            "www.dongliuxiaoshuo.com": "#content > div.content ::text",
            "fanqienovel.com": "div.muye-reader-content.noselect ::text",
            "m.shubaow.net": "#nr1 ::text",
            "m.longteng788.com/": "#nr1 ::text",
            "m.xklxsw.com": "#nr1 ::text",
            "m.630shu.net": "#nr1 ::text",
            "m.ddxs.com": "#nr1 ::text",
            "www.xindingdianxsw.com/": "p ::text",
            "m.akshu8.com": "#content ::text",
            "soruncg.com": "#content ::text",
            "www.630shu.net": "#content ::text",
            "www.yifan.net": "#content ::text",
            "www.soxscc.net": "#content ::text",
            "feixs.com": "#content ::text",
            "www.tsxsw.net": "#content ::text",
            "www.ttshu8.com": "#content ::text",
            "www.szhhlt.com": "#content ::text",
            "www.bqg789.net": "#content ::text",
            "www.9xzw.com": "#content ::text",
            "www.28zww.cc": "#content ::text",
            "www.wnmtl.org": "#reader > div > div.chapter-container ::text",
            "m.yifan.net": "#chaptercontent ::text",
            "www.qcxxs.com": "body > div.container > div.row.row-detail > div > div ::text",
            "m.soxscc.net": "#chapter > div.content ::text",
            "m.ttshu8.com": "#chapter > div.content ::text",
            "metruyencv.com": "#article ::text",
            "www.gonet.cc": "body > div.container > div.row.row-detail > div > div ::text",
            "www.ops8.com": "#BookText ::text",
            "m.77z5.com": "#chaptercontent ::text",
            "m.lw52.com": "#chaptercontent ::text",
            "mtl-novel.net": "#chr-content ::text",
            "novelnext.com": "#chr-content ::text",
            "novelbin.net": "#chr-content ::text",
            "ncode.syosetu.com": "#novel_honbun ::text",
            "m.75zw.com/": "#chapter > div.a75zwcom_i63c9e1d ::text",
            "www.webnovelpub.com": "#chapter-container ::text",
            "m.tsxsw.net": "#nr ::text",
            "www.4ksw.com/": "div.panel-body.content-body.content-ext ::text",
            "tw.ixdzs.com": "#page > article ::text",
            "www.shulinw.com/": "#htmlContent ::text",
            "ranobes.com": "div.block.story.shortstory ::text",
            "m.bqg789.net": "#novelcontent ::text",
            "m.biquzw789.org": "#novelcontent ::text",
            "boxnovel.com": "div.cha-content ::text",
            "bonnovel.com": "div.cha-content ::text",
            "www.asxs.com": "#contents ::text",
            "www.72xsw.net": "div.box_box ::text",
            "www.31dv.com": "#booktxt ::text",
            "1stkissnovel.org": "div.entry-content > div > div > div > div.text-left ::text",
            # "www.libraryofakasha.com": "div.chapter-content ::text",
            # "sangtacviet.vip": ".contentbox ::text",
            "www.novelcool.com": "p ::text",
            "novelcool.org/": "p ::text",
            "m.sywx8.com": "#nr ::text",
            "www.tadu.com": "#partContent ::text",
            "www.biquge.bz/": "#content ::text",
            "www.yuyouku.com": "#txtContent ::text",
            "m.yuyouku.com": "#content ::text",
            "m.biquzw789.net": "#novelcontent ::text",
            "www.biquzw789.net": "#content ::text",
            "pandamtl.com/": "div.bixbox.episodedl > div > div.epcontent.entry-content ::text",
            "www.bookbl.com": "#content > div.content ::text",
            "www.60ks.cc": "#content ::text",
            "m.qbxsw.com": "#chapter > div.content ::text",
            "www.qbxsw.com": "#content ::text",
            "www.14sw.com": "#content ::text",
            "m.14sw.com": "#ChapterView ::text",
            "noblemtl.com": "div.epcontent.entry-content ::text"
        }

        for domain, css_selector in domain_mappings.items():
            if domain in link:
                return css_selector

        return "* ::text"

    def findchptitlecss(link):
        domain_mappings = {
            "trxs.me": [".infos>h1:first-child", ""],
            "trxs.cc": [".infos>h1:first-child", ""],
            "tongrenquan": [".infos>h1:first-child", ""],
            "qbtr": [".infos>h1:first-child", ""],
            "jpxs": [".infos>h1:first-child", ""],
            "ffxs8.com": ["body > div.detail.clearfix > div > div.info-desc > div.desc-detail > h1", ""],
            "txt520": ["title", ""],
            "ffxs": ["title", ""],
            "bixiang": [".desc>h1", ""],
            "powanjuan": [".desc>h1", ""],
            "sjks": [".box-artic>h1", ""],
            "sj.uukanshu": [".bookname", "#divContent >h3 ::text"],
            "t.uukanshu": [".bookname", "#divContent >h3 ::text"],
            "uukanshu.cc": [".booktitle", "h1 ::text"],
            "uuks": [".jieshao_content>h1", "h1#timu ::text"],
            "uukanshu": ["title", "h1#timu ::text"],
            "69shu": [".bread>a:nth-of-type(3)", "title ::text"],
            "m.qidian": ["#header > h1", ""],
            "m.soxscc.net": ["title", "#chapter > h1 ::text"],
            "m.ttshu8.com": ["title", "#chapter > h1 ::text"],
            "www.soxscc.net": ["#info > h1", "body > div.content_read > div > div.bookname > h1 ::text"],
            "www.bqg789.net": ["#info > h1", "body > div.content_read > div > div.bookname > h1 ::text"],
            "www.ops8.com": ["div.book-title", "#BookCon > h1"],
            "feixs.com": ["title", "#main > div.bookinfo.m10.clearfix > div.info > p.chaptertitle ::text"],
            "m.tsxsw.net": ["title", "h2 ::text"],
            "www.tsxsw.net": ["div.articleinfo > div.r > div.l2 > div > h1", "title ::text"],
            "tw.ixdzs.com": ["h1", "title ::text"],
            "www.asxs.com": ["#a_main > div.bdsub > dl > dd.info > div.book > div.btitle > h1",
                             "#amain > dl > dd:nth-child(2) > h1 ::text"],
            "www.72xsw.net": ["div.title > h1", "div > h1 ::text"],
            "www.9xzw.com": ["#info > div > h1", "div.bookname > h1 ::text"],
            "m.ddxs.com": ["body > div.header > h2 > font > font", "#nr_title ::text"],
            "www.31dv.com": ["#info > h1", "#wrapper > article > h1 ::text"],
            "www.biquge.bz/": ["#info > h1", "#wrapper > div.content_read > div > div.bookname > h1 ::text"],
            "www.yuyouku.com": ["#btop-info > div.container > article > div > ul > li:nth-child(1) > h1", "#h1 > h1 ::text"],
            "m.yuyouku.com": ["#btop-info > div.body > div > section > div.novel-cover > dl > dt", "#content > h1 ::text"],
            "m.biquzw789.net": ["body > div.main > div.catalog > div.catalog1 > h1", "#novelbody > div.nr_function > h1 ::text"],
            "www.biquzw789.net": ["#info", "#wrapper > div.content_read > div > div.bookname > h1 ::text"],
            "www.bookbl.com": ["h1", "#content > h1 ::text"],
            "www.60ks.cc": ["#bookinfo > div.bookright > div.booktitle > h1", "#center > div.title > h1 ::text"],
            "m.60ks.cc": ["#_52mb_h1 > a", "#nr_title ::text"],
            "m.qbxsw.com": ["#read > div.main > div.detail > p.name", "#chapter > h1 ::text"],
            "www.qbxsw.com": ["#info > h1", "body > div.content_read > div > div.bookname > h1 ::text"],
            "www.14sw.com": ["#info > h1", "#main > h1 ::text"],
            "m.14sw.com": ["body > div.container > div.mod.detail > div.bd.column-2 > div.right > h1", "body > div.container > h1 ::text"],
            "noblemtl.com": ["div.infox > h1", "div.epheader > h1 ::text"]
        }
        for domain, ret_array in domain_mappings.items():
            if domain in link:
                return ret_array

        return ["title", "title ::text"]
        # if ( "trxs.me" in link or "trxs.cc" in link or "tongrenquan" in link or "qbtr" in link or "jpxs" in link ):
        # return [".infos>h1:first-child", ""] elif "ffxs8.com" in link: return ["body > div.detail.clearfix > div >
        # div.info-desc > div.desc-detail > h1", ""] elif "txt520" in link or "ffxs" in link: return ["title",
        # ""] elif "bixiang" in link or "powanjuan" in link: return [".desc>h1", ""] elif "sjks" in link: return [
        # ".box-artic>h1", ""] elif "sj.uukanshu" in link or "t.uukanshu" in link: return [".bookname", "#divContent
        # >h3 ::text"] elif "uukanshu.cc" in link: return [".booktitle", "h1 ::text"] elif "uuks" in link: return [
        # ".jieshao_content>h1", "h1#timu ::text"] elif "uukanshu" in link: return ["title", "h1#timu ::text"] elif
        # "69shu" in link: return [".bread>a:nth-of-type(3)", "title ::text"] elif "m.qidian" in link: return [
        # "#header > h1", ""] elif "m.soxscc.net" in link or "m.ttshu8.com" in link: return ["title", "#chapter > h1
        # ::text"] elif "www.soxscc.net" in link or "www.bqg789.net" in link: return ["#info > h1",
        # "body > div.content_read > div > div.bookname > h1 ::text"] elif "www.ops8.com" in link: return [
        # "div.book-title", "#BookCon > h1"] elif "feixs.com" in link: return ["title", "#main >
        # div.bookinfo.m10.clearfix > div.info > p.chaptertitle ::text"] elif "m.tsxsw.net" in link: return ["title",
        # "h2 ::text"] elif "www.tsxsw.net" in link: return ["div.articleinfo > div.r > div.l2 > div > h1",
        # "title ::text"] elif "tw.ixdzs.com" in link: return ["h1", "title ::text"] elif "www.asxs.com" in link:
        # return ["#a_main > div.bdsub > dl > dd.info > div.book > div.btitle > h1", "#amain > dl > dd:nth-child(2) >
        # h1 ::text"] elif "www.72xsw.net" in link: return ["div.title > h1", "div > h1 ::text"] elif "www.9xzw.com"
        # in link: return ["#info > div > h1", "div.bookname > h1 ::text"] elif "m.ddxs.com" in link: return ["body >
        # div.header > h2 > font > font", "#nr_title ::text"] elif "www.31dv.com" in link: return ["#info > h1",
        # "#wrapper > article > h1 ::text"] else: return ["title", "title ::text"]

    def find_next_selector(link):
        domain_mappings = {
            "readwn": ["#chapter-article > header > div > aside > nav > div.action-select > a.chnav.next",
                       "#chapter-article > header > div > div > h1 > a"],
            "novelfull.com": ["#next_chap", "#chapter > div > div > a"],
            "novelroom.net": ["#manga-reading-nav-foot > div > div.select-pagination > div > div.nav-next > a",
                              "#manga-reading-nav-head > div > div.entry-header_wrap > div > div.c-breadcrumb > ol > "
                              "li:nth-child(2) > a"],
            "readlightnovel": [
                "#ch-page-container > div > div.col-lg-8.content2 > div > div:nth-child(6) > ul > li:nth-child(3) > a",
                "#ch-page-container > div > div.col-lg-8.content2 > div > div:nth-child(1) > div > div > h1"],
            "www.youyoukanshu.com": ["None", "#content > div.readtop > div.pull-left.hidden-lg > a > font"],
            "m.shubaow.net": ["#novelcontent > div.page_chapter > ul > li:nth-child(4) > a",
                              "#novelbody > div.head > div.nav_name > h1 > font > font"],
            "m.xindingdianxsw.com": ["#chapter > div:nth-child(9) > a:nth-child(3)",
                                     "#chapter > div.path > a:nth-child(2)"],
            "www.xindingdianxsw.com": ["#A3", "div.con_top > a:nth-child(3)"],
            "m.longteng788.com/": ["#pb_next", "#_52mb_h1"],
            "m.75zw.com/": ["#chapter > div.pager.z1 > a:nth-child(3)",
                            "#chapter > div.path > a:nth-child(3) > font > font"],
            "www.wnmtl.org": ["#nextBtn", "#navBookName"],
            "m.akshu8.com": ["#container > div > div > div.reader-main > div.section-opt.m-bottom-opt > a:nth-child(5)",
                             "title"],
            "m.77z5.com": ["#pt_next", "#top > span > font > font:nth-child(3)"],
            "m.yifan.net/": ["#pb_next", "#read > div.header > span.title"],
            "www.yifan.net": ["#book > div.content > div:nth-child(5) > ul > li:nth-child(3) > a", "title"],
            "m.630shu.net": ["#pb_next", "title"],
            "www.qcxxs.com": ["body > div.container > div.row.row-detail > div > div > div.read_btn > a:nth-child(4)",
                              "body > div.container > div.row.row-detail > div > h2 > a:nth-child(3)"],
            "www.gonet.cc": ["body > div.container > div.row.row-detail > div > div > div.read_btn > a:nth-child(4)",
                             "body > div.container > div.row.row-detail > div > h2 > a:nth-child(3) > font > font"],
            "mtl-novel.net": ["#next_chap", "#chapter > div > div > a"],
            "ranobes.com": ["#next", "#dle-speedbar > span > font:nth-child(2) > span:nth-child(4) > a > span"],
            "booktoki216.com": ["#goNextBtn", "title"],
            "boxnovel.com": ["None",
                             "#manga-reading-nav-head > div > div.entry-header_wrap > div > div.c-breadcrumb > ol > "
                             "li:nth-child(2) > a"],
            "www.szhhlt.com": ["None", "body > div.container > header > h1 > label > a"],
            "69shu": ["None", "title"],
            "www.69shuba.com": ["None", "title"],
            "novelbin.net": ["None", "#chapter > div > div > a"],
            "1stkissnovel.org": ["None", "#chapter-heading"],
            "sangtacviet.vip": ["None", "title"],
            "m.sywx8.com": ["None", "head > meta:nth-child(9)"],
            "novelmtl.com": ["#chapter-article > header > div > aside > nav > div.action-select > a.chnav.next",
                             "#chapter-article > header > div > div > h1 > a"],
            "www.wuxiabee.com": ["#chapter-article > header > div > aside > nav > div.action-select > a.chnav.next",
                                 "#chapter-article > header > div > div > h1 > a"],
            "www.wuxia": ["#chapter-article > header > div > aside > nav > div.action-select > a.chnav.next",
                          "#chapter-article > header > div > div > h1 > a"],
            "fannovels.com": ["#chapter-article > header > div > aside > nav > div.action-select > a.chnav.next",
                              "#chapter-article > header > div > div > h1 > a"],
            "www.dongliuxiaoshuo.com": ["None", "#content > div.readtop > div.pull-left.hidden-lg > a > font"],
            "soruncg.com": ["#container > div > div > div.reader-main > div.section-opt.m-bottom-opt > a:nth-child(5)",
                            "title"],
            "novelnext.com": ["#next_chap", "#chapter > div > div > a"],
            "bonnovel.com": ["None",
                             "#manga-reading-nav-head > div > div.entry-header_wrap > div > div.c-breadcrumb > ol > li:nth-child(2) > a"],
            "pandamtl.com/": ["#post-9256 > div.bixbox.episodedl > div > div.navimedia > div.left > div > div:nth-child(3) > a", "#post-9256 > div.bixbox.episodedl > div > div.epheader > h1"]
            # "www.novelcool.com": ["None",  "div.chapter-reading-section-list > div > div > h2"],
            # "m.bqg789.net": ["#nextpage", "#novelbody > div.head > div.nav_name > h1"],
        }
        for domain, ret_array in domain_mappings.items():
            if domain in link:
                return ret_array

        return [None, "title"]
        # if "readwn" in link or "wuxiax.co" in link or "novelmt.com" in link or "fannovels.com" in link or
        # "novelmtl.com" in link or "www.wuxiap.com" in link or "www.wuxiau.com" in link: return ["#chapter-article >
        # header > div > aside > nav > div.action-select > a.chnav.next", "#chapter-article > header > div > div > h1
        # > a"] elif "novelfull.com" in link: return ["#next_chap", "#chapter > div > div > a"] elif "novelroom.net"
        # in link: return ["#manga-reading-nav-foot > div > div.select-pagination > div > div.nav-next > a",
        # "#manga-reading-nav-head > div > div.entry-header_wrap > div > div.c-breadcrumb > ol > li:nth-child(2) >
        # a"] elif "readlightnovel" in link: return ["#ch-page-container > div > div.col-lg-8.content2 > div >
        # div:nth-child(6) > ul > li:nth-child(3) > a", "#ch-page-container > div > div.col-lg-8.content2 > div >
        # div:nth-child(1) > div > div > h1"] elif "www.youyoukanshu.com" in link or "www.dongliuxiaoshuo.com" in
        # link: return ["None", "#content > div.readtop > div.pull-left.hidden-lg > a > font"] elif "m.shubaow.net"
        # in link: return ["#novelcontent > div.page_chapter > ul > li:nth-child(4) > a", "#novelbody > div.head >
        # div.nav_name > h1 > font > font"] elif "m.xindingdianxsw.com" in link: return ["#chapter > div:nth-child(9)
        # > a:nth-child(3)", "#chapter > div.path > a:nth-child(2)"] elif "www.xindingdianxsw.com" in link: return [
        # "#A3", "div.con_top > a:nth-child(3)"] elif "m.longteng788.com/" in link: return ["#pb_next", "#_52mb_h1"]
        # elif "m.75zw.com/" in link: return ["#chapter > div.pager.z1 > a:nth-child(3)", "#chapter > div.path >
        # a:nth-child(3) > font > font"] elif "www.wnmtl.org" in link: return ["#nextBtn", "#navBookName"] elif
        # "m.akshu8.com" in link or "soruncg.com" in link: return ["#container > div > div > div.reader-main >
        # div.section-opt.m-bottom-opt > a:nth-child(5)", "title"] elif "m.77z5.com" in link: return ["#pt_next",
        # "#top > span > font > font:nth-child(3)"] elif "m.yifan.net/" in link: return ["#pb_next",
        # "#read > div.header > span.title"] elif "www.yifan.net" in link: return ["#book > div.content >
        # div:nth-child(5) > ul > li:nth-child(3) > a", "title"] elif "m.630shu.net" in link: return ["#pb_next",
        # "title"] # elif "m.soxscc.net" in link: #     return ["#chapter > div.pager > a:nth-child(3)", "#bookname"]
        # elif "www.qcxxs.com" in link: return ["body > div.container > div.row.row-detail > div > div > div.read_btn
        # > a:nth-child(4)", "body > div.container > div.row.row-detail > div > h2 > a:nth-child(3)"] elif
        # "www.gonet.cc" in link: return ["body > div.container > div.row.row-detail > div > div > div.read_btn >
        # a:nth-child(4)", "body > div.container > div.row.row-detail > div > h2 > a:nth-child(3) > font > font"]
        # elif "mtl-novel.net" in link or "novelnext.com" in link: return ["#next_chap", "#chapter > div > div > a"]
        # elif "ranobes.com" in link: return ["#next", "#dle-speedbar > span > font:nth-child(2) > span:nth-child(4)
        # > a > span"] elif "booktoki216.com" in link: return ["#goNextBtn", "title"] elif "boxnovel.com" in link or
        # "bonnovel.com" in link: return ["None", "#manga-reading-nav-head > div > div.entry-header_wrap > div >
        # div.c-breadcrumb > ol > li:nth-child(2) > a"] elif "www.szhhlt.com" in link: return ["None",
        # "body > div.container > header > h1 > label > a"] elif "69shu" in link: return ["None", "title"] elif
        # "novelbin.net" in link: return ["None", "#chapter > div > div > a"] elif "1stkissnovel.org" in link: return
        # ["None", "#chapter-heading"] elif "sangtacviet.vip" in link: return ["None", "title"] elif "m.sywx8.com" in
        # link: return ["None", "head > meta:nth-child(9)"] # elif "www.novelcool.com" in link: #     return ["None",
        # "div.chapter-reading-section-list > div > div > h2"] # elif "m.bqg789.net" in link: #     return [
        # "#nextpage", "#novelbody > div.head > div.nav_name > h1"] else: return [None, "title"]

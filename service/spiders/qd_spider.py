# -*- coding: utf-8 -*-
"""
Created on 2023-04-13 15:28:24
---------
@summary:
---------
@author: tychen
"""

import json
import re

import cn2an
import feapder
from feapder.db.mysqldb import MysqlDB
from feapder.utils.log import log

bookpath = r"D:\OneDrive\Backup\EBook\zxcs"
xpath_description = "//div[@class='book-intro']/p/text()"
url_description = "https://book.qidian.com/info/{}/#Catalog"
url_bookindex = "https://m.qidian.com/book/{}/catalog/?source=pc_jump"
url_reviewsummary = "https://read.qidian.com/ajax/chapterReview/reviewSummary?_csrfToken={}&bookId={}&chapterId={}"
url_reviewlist = "https://read.qidian.com/ajax/chapterReview/reviewList?_csrfToken={}&bookId={}&chapterId={}&segmentId={}&type=2&page=1&pageSize=60"

tb_books = "tb_books"
tb_chapters = "tb_chapters"
tb_segments = "tb_segments"
tb_comments = "tb_comments"


class QdSpider(feapder.AirSpider):
    __custom_setting__ = dict(
        SPIDER_MAX_RETRY_TIMES=0,
        SPIDER_SLEEP_TIME=[2, 5],
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db = MysqlDB()

    def start_requests(self):
        # status=0 添加任务
        # status=1 爬取中
        # status=2 爬取完成

        # 添加小说到数据库
        task_list = self.db.find(
            f"select bookid, filename from {tb_books} where status=0"
        )
        for task in task_list:
            log.debug(f"添加小说到数据库 {task[1]}")
            self.insert_book(task[0], task[1])

        # 更新小说信息
        task_list = self.db.find(f"select bookid, title from {tb_books} where status=1")
        for task in task_list:
            log.debug(f"更新小说信息 {task[1]}")
            self.update_description(task[0])
            self.update_chapters(task[0])

        # 更新段落ID，然后爬取评论
        task_list = self.db.find(
            "select c.bookid, c.chapterid, c.chapternum, b.title, c.title"
            f"  from {tb_chapters} c"
            f"  left join {tb_books} b"
            "    on c.bookid = b.bookid"
            " where c.status=0"
        )
        log.debug(f"开始爬取评论 章节数：{len(task_list)}")
        for task in task_list:
            yield feapder.Request(
                url_reviewsummary.format(self.csrfToken, task[0], task[1]),
                bookid=task[0],
                chapterid=task[1],
                chapternum=task[2],
                booktitle=task[3],
                chaptertitle=task[4],
                callback=self.parse_reviewsummary,
            )
            break

    def parse_reviewsummary(self, request, response):
        """
        更新段落ID
        """

        reviewsummary = response.json["data"]["list"]
        segment_num = 0

        for s in reviewsummary:
            segment = {}
            segment["segmentid"] = s["segmentId"]
            segment["chapterid"] = request.chapterid
            segment_exsist = self.db.find(
                f"select 1 from {tb_segments}"
                f" where segmentnum={segment_num} "
                f"   and chapternum={request.chapternum} "
                f"   and bookid='{request.bookid}' ",
                limit=1,
            )
            if segment_exsist is not None:
                self.db.update_smart(
                    tb_segments,
                    segment,
                    condition=f"segmentnum={segment_num} "
                    f"      and chapternum={request.chapternum} "
                    f"      and bookid='{request.bookid}'",
                )
            else:
                segment["bookid"] = request.bookid
                segment["chapternum"] = request.chapternum
                segment["segmentnum"] = segment_num
                self.db.add_smart(tb_segments, segment)
            segment_num += 1
        log.debug(f"更新段落ID {request.booktitle} {request.chaptertitle}")

        task_list = self.db.find(
            "select segmentid "
            f" from {tb_segments} "
            f"where bookid='{request.bookid}' "
            f"  and chapterid='{request.chapterid}' "
            "   and segmentid is not null "
            "   and status=0 "
            " order by segmentid "
        )
        for task in task_list:
            yield feapder.Request(
                url_reviewlist.format(
                    self.csrfToken, request.bookid, request.chapterid, task[0]
                ),
                bookid=request.bookid,
                chapterid=request.chapterid,
                booktitle=request.booktitle,
                chaptertitle=request.chaptertitle,
                segmentid=task[0],
                callback=self.parse_reviewlist,
            )

    def parse_reviewlist(self, request, response):
        reviewlist = response.json["data"]["list"]
        comments = []
        comment_distinct = []
        for c in reviewlist:
            review_exsist = self.db.find(
                f"select 1 from {tb_comments} where reviewid='{c['reviewId']}'",
                limit=1,
            )
            if review_exsist is not None:
                continue
            if c["content"] in comment_distinct:
                continue
            comment_distinct.append(c["content"])

            comment = {}
            comment["reviewid"] = c["reviewId"]
            comment["segmentid"] = c["segmentId"]
            comment["chapterid"] = request.chapterid
            comment["bookid"] = request.bookid
            comment["cbid"] = c["cbid"]
            comment["ccid"] = c["ccid"]
            comment["guid"] = c["guid"]
            comment["userid"] = c["userId"]
            comment["nickname"] = c["nickName"]
            comment["content"] = c["content"]
            comment["status"] = c["status"]
            comment["createtime"] = c["createTime"]
            comment["quotereviewid"] = c["quoteReviewId"]
            comment["quotecontent"] = c["quoteContent"]
            comment["quoteguid"] = c["quoteGuid"]
            comment["quoteuserid"] = c["quoteUserId"]
            comment["quotenickname"] = c["quoteNickName"]
            comment["type"] = c["type"]
            comment["likecount"] = c["likeCount"]
            comment["level"] = c["level"]
            comment["imagepre"] = c["imagePre"]
            comment["imagedetail"] = c["imageDetail"]
            comment["rootreviewid"] = c["rootReviewId"]
            comment["rootreviewreplycount"] = c["rootReviewReplyCount"]
            comment["ipaddress"] = c["ipAddress"]
            comments.append(comment)

        if len(comments) > 0:
            self.db.add_batch_smart("comments", comments)
            log.debug(
                f"爬取评论 {len(comments)}条， {request.booktitle} "
                f"{request.chaptertitle} 第{request.segmentid}段"
            )
        self.db.update_smart(
            "segments", {"status": 1}, f"segmentid={request.segmentid}"
        )

        count_unfinished = self.db.find(
            "select count(1) from segments where status=0 "
            f"  and chapterid='{request.chapterid}' and bookid='{request.bookid}'",
            limit=1,
        )
        if count_unfinished[0] == 0:
            self.db.update_smart(
                "chapters", {"status": 1}, f"chapterid={request.chapterid}"
            )
            log.debug(f"整章评论爬取结束 {request.booktitle} request.chaptertitle")

    def update_chapters(self, bookid):
        """
        更新章节ID
        """
        response = feapder.Request(url_bookindex.format(bookid)).get_response()
        self.csrfToken = response.cookies.get("_csrfToken")
        pattern = re.compile(r"g_data.volumes = .*?(?=;)")
        volumes_json = (
            pattern.search(response.text).group(0).replace("g_data.volumes = ", "")
        )
        volumes = json.loads(volumes_json)
        pattern = re.compile(r"\d+")
        for volume in volumes:
            for c in volume["cs"]:
                chapter = {}
                chapter["chapterid"] = c["id"]
                chapter["updatetime"] = c["uT"]
                chapter_num_result = pattern.search(c["cN"])
                if not chapter_num_result:
                    continue
                chapter_num = chapter_num_result.group(0)
                self.db.update_smart(
                    "chapters",
                    chapter,
                    condition=f"chapternum={chapter_num} and bookid='{bookid}'",
                )

    def update_description(self, bookid):
        """
        更新小说简介
        """

        book_description = self.db.find(
            "select description from books where bookid='{bookid}'", limit=1
        )
        if book_description[0] is None:
            response = feapder.Request(url_description.format(bookid)).get_response()
            description = response.xpath(xpath_description).extract_first()
            self.db.update_smart(
                "books",
                {"description": description.strip().replace("\u3000", "")},
                condition=f"bookid='{bookid}'",
            )

    def insert_book(self, bookid, bookfile):
        """
        添加小说到数据库
        """

        filename = bookpath + "\\" + bookfile
        with open(filename, "r", encoding="utf-8") as f:
            lines = f.readlines()
        chapters = []
        segments = []
        chapter_num = 0
        segment_num = 0
        pattern = re.compile("^第.*?(?=章)")
        for line in lines:
            matched = pattern.match(line)
            if matched:
                cn_num = matched.group(0)[1:]
                chapter_num = cn2an.cn2an(cn_num, "normal")
                chapter = {}
                chapter["bookid"] = bookid
                chapter["chapternum"] = chapter_num
                chapter["title"] = line.replace("\n", "")
                chapters.append(chapter)
                segment_num = 0
                log.debug(cn_num.ljust(5, "　") + "　|　" + str(chapter_num).ljust(4, " "))
            elif chapter_num > 0:
                if line == "\n":
                    continue
                segment_num += 1
                segment = {}
                segment["bookid"] = bookid
                segment["chapternum"] = chapter_num
                segment["segmentnum"] = segment_num
                segment["content"] = line.replace("\n", "")
                segments.append(segment)
            if line == "\u3000\u3000（全书完）\n":
                break
        self.db.add_batch_smart("chapters", chapters)
        self.db.add_batch_smart("segments", segments)
        self.db.update_smart("books", {"status": 1}, condition=f"bookid='{bookid}'")


if __name__ == "__main__":
    QdSpider().start()

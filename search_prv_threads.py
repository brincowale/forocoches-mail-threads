# coding: utf-8
from pymongo import MongoClient
from grab.spider import Spider, Task
import string
import logging
import requests
import forocoches_config as config

class Forocoches(Spider):

    def prepare(self):
        self.client = MongoClient(config.mongodb['uri'])
        self.db = self.client.forocoches
        self.BASE_URL = 'http://m.forocoches.com/foro/'  # use the mobile phone website as base url
        self.REQUIRED_WORDS = ['+prv', '+hd', '+pvr', '+ prv', '+ hd', '+ pvr', 'chollo', 'gratis']
        self.UNWANTED_WORDS = ['+18', 'tema serio', 'tocho', 'semiserio', 'temaserio']

    def task_generator(self):
        # urls of categories to look for new interesting threads
        index_urls = [
            'http://www.forocoches.com/foro/forumdisplay.php?f=2&page=',
            'http://www.forocoches.com/foro/forumdisplay.php?f=17&page=',
            'http://www.forocoches.com/foro/forumdisplay.php?f=27&page=',
            'http://www.forocoches.com/foro/forumdisplay.php?f=23&page='
        ]
        for i in range(len(index_urls)):
            yield Task('get_number_pages', url=index_urls[i])

    def task_get_number_pages(self, grab, task):
        # get the number of pages in each category
        number_of_pages = int(grab.doc.select("//table[@class='tborder']//td[@nowrap='nowrap']/a")
                              .attr("href").split("page=")[1]) + 1
        # send to extract data each url per page
        for i in range(1, number_of_pages):
            yield Task('extract_data', url=task.url + str(i))

    def task_extract_data(self, grab, task):
        # for each thread in the current page
        for thread in grab.doc.select("//a[starts-with(@href, 'showthread.php?t=')]"):
            title = thread.select(".").text().lower()
            # save into database any link that contains any REQUIRED_WORDS but zero UNWANTED_WORDS
            if any(item in title for item in self.REQUIRED_WORDS) and not any(item in title for item in self.UNWANTED_WORDS):
                url = thread.select(".").attr('href')
                self.insert_in_database(title, url)
            # look for any threat that has rated with 5 starts and doesn't contains any UNWANTED_WORDS
            elif not any(item in title for item in self.UNWANTED_WORDS):
                try:
                    if thread.select('../../div[@class="smallfont"]/span/img').attr('src') == '//st.forocoches.com/foro/images/rating/rating_5.gif':
                        url = thread.select(".").attr('href')
                        self.insert_in_database(title, url)
                except Exception:
                    logging.debug("Thread doesn't have 5 stars")

    def send_mail(self):
        msg = ""
        # look for any thread in the database that was not sent yet
        cursor = self.db.threads.find({"new": True})
        for document in cursor:
            msg += document.get('title').encode('utf-8') + '-' + document.get('url').encode('utf-8') + '\r\n'
        if cursor.count() > 0:
            # send email with new threads
            requests.post(
                config.mailgun['url'],
                auth=("api", config.mailgun['apikey']),
                data={"from": config.mailgun['from'],
                "to": config.mailgun['to'],
                "subject": "Hilos +prv +hd forocoches",
                "text": msg})
            self.db.threads.update({"new": True}, {"$set": {"new": False}}, upsert=False, multi=True)

    def insert_in_database(self, title, url):
        try:
            self.db.threads.insert({"title": string.capwords(title), "url": url, "new": True, "url": self.BASE_URL + url})
        except Exception:
            logging.debug("Thread url already exists, is not a new thread")


if __name__ == '__main__':
    #logging.basicConfig(level=logging.DEBUG)
    bot = Forocoches(thread_number=10, network_try_limit=10, task_try_limit=10)
    bot.run()
    bot.send_mail()
    bot.client.close()

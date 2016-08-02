# coding: utf-8
from pymongo import MongoClient
from grab.spider import Spider, Task
import string
import logging
import requests
import json


class SearchThreads(Spider):

    def prepare(self):
        """
        Create connection with database
        """
        self.client = None # databse here

    def task_generator(self):
        """
        Read config.json file and get the subforums url
        Call the next time one time per subforum
        """
        subforums_url = self.config['subforums']
        for i in range(len(subforums_url)):
            yield Task('get_number_pages_subforum', url=subforums_url[i])

    def task_get_number_pages_subforum(self, grab, task):
        """
        This task read how many pages has the specified subforum
        Call the next task one time per page
        """
        number_of_pages = int(grab.doc.select("//table[@class='tborder']//td[@nowrap='nowrap']/a")
                              .attr("href").split("page=")[1]) + 1
        for i in range(1, number_of_pages):
            yield Task('extract_data_from_threads', url=task.url + str(i))

    def task_extract_data_from_threads(self, grab, task):
        # xpath: get all threads (title and url)
        for thread in grab.doc.select("//a[starts-with(@href, 'showthread.php?t=')]"):
            title = thread.select(".").text().lower()
            if any(item in title for item in self.config['required_words_in_title']) \
                    and not any(item in title for item in self.config['avoid_words_in_title']):
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

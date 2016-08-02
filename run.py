from search_threads import SearchThreads
import json

class Run:
    def load_config_file(self, config_file):
        with open(config_file, encoding="utf8") as config_file:
            return json.load(config_file)

if __name__ == '__main__':
    run = Run()
    run.load_config_file('config.json')
    bot = SearchThreads(thread_number=10, network_try_limit=10, task_try_limit=10)
    bot.run()
    bot.send_mail()
    bot.client.close()

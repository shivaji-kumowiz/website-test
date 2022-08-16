from selenium import webdriver
import logging
import concurrent.futures
import time
class WebsiteSelenium:
    def __init__(self, url):
        self.url = url
        firefox_options = webdriver.firefox.options.Options()
        firefox_options.headless = True
        self.driver = webdriver.Firefox(options=firefox_options)

    def get_page_urls(self):
        self.driver.get(self.url)
        urls_set = set()
        for a in self.driver.find_elements("xpath", ".//a"):
            if (
                    a.get_attribute("href") is not None
                    and "http" in a.get_attribute("href")
                    and "kumowiz" in a.get_attribute("href")
                    and "github" not in a.get_attribute("href")
                    and "zip" not in a.get_attribute("href")
                    and "https://discuss.dgraph.io/t/" not in a.get_attribute("href")
                    and "https://discuss.dgraph.io/u/" not in a.get_attribute("href")
                    and "https://discuss.dgraph.io/tag/" not in a.get_attribute("href")
                    and "https://discuss.dgraph.io/c/" not in a.get_attribute("href")
                    and "https://discuss.dgraph.io/badges/" not in a.get_attribute("href")
                    and "https://dgraph.io/docs/" not in a.get_attribute("href")
                    and "https://dgraph.io/blog/post" not in a.get_attribute("href")

            ):
                urls_set.add(a.get_attribute("href"))
        return urls_set


def get_page_urls(url):
    my_logger.info(f"\nchecking {url}")
    website_selenium_obj = WebsiteSelenium(url=url)
    try:
        urls = website_selenium_obj.get_page_urls()
        my_logger.info(f"page loaded ")
        my_logger.info(f"obtained {len(urls)} urls")
    except Exception as e:
        my_logger.error("Url: "+ url+" " + "parentUrls: "+ ",".join(urlsParentInfo[url])+" error => "+ str(e))
        urls = set()
    website_selenium_obj.driver.close()
    return url,urls


def recurse_check(url):
    urls = set()
    urls.add(url)
    visited_page_urls = dict()
    while len(urls) > 0:
        urlList=[]
        y = 0
        if (len(urls) >= 1 and len(urls) < 8):
            y = len(urls)
        else:
            y = 8
        for x in range(y):
            urlList.append(urls.pop())
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
            futures =[]
            for url1 in urlList:
                if url1 in visited_page_urls and visited_page_urls[url1] is True:
                    continue
                else:
                    futures.append(executor.submit(get_page_urls, url=url1))
            for future in concurrent.futures.as_completed(futures):
                parentUrl,tmp_urls = future.result()
                #set parent url for the child url received
                for childUrl in tmp_urls:
                    try:
                        parentList = urlsParentInfo[childUrl]
                    except Exception as e:
                        parentList = []
                    parentList.append(parentUrl)
                    urlsParentInfo[childUrl] = parentList
                visited_page_urls[parentUrl] = True
                urls.update(tmp_urls)
        my_logger.info(f"total pending urls count {len(urls)}")
        my_logger.info(f"total crawled urls count {len(visited_page_urls)}")
    return visited_page_urls


urlsParentInfo = dict()


def get_logger(
        LOG_FORMAT     = '%(levelname)-1s %(message)s',
        LOG_NAME       = '',
        LOG_FILE_INFO  = 'out.log',
        LOG_FILE_ERROR = 'out.err'):

    log           = logging.getLogger(LOG_NAME)
    log_formatter = logging.Formatter(LOG_FORMAT)
    # comment this to suppress console output
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(log_formatter)
    log.addHandler(stream_handler)
    file_handler_info = logging.FileHandler(LOG_FILE_INFO, mode='w')
    file_handler_info.setFormatter(log_formatter)
    file_handler_info.setLevel(logging.INFO)
    log.addHandler(file_handler_info)
    file_handler_error = logging.FileHandler(LOG_FILE_ERROR, mode='w')
    file_handler_error.setFormatter(log_formatter)
    file_handler_error.setLevel(logging.ERROR)
    log.addHandler(file_handler_error)
    log.setLevel(logging.INFO)

    return log

if __name__ == "__main__":
    start = time.time()
    my_logger = get_logger()
    visited_page_urls = recurse_check(url="https://www.kumowiz.com")
    my_logger.info("\n\n**********\n\n")
    my_logger.info("routes:")
    for key, value in visited_page_urls.items():
        logging.info(key)

    end = time.time()
    my_logger.info("The time of execution of above program is :", end - start)


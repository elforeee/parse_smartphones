import os

import pandas as pd
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings


if __name__ == "__main__":

    if not os.path.isfile("phonedata.csv"):
        process = CrawlerProcess(get_project_settings())
        process.crawl("ozon")
        process.start()

    version_list = pd.read_csv("phonedata.csv", usecols=[1])
    version_distribution = version_list.value_counts("os_version")
    for os_version, frequency in version_distribution.items():
        print(os_version, "-", frequency)

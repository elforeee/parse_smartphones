import scrapy
from scrapy.exceptions import CloseSpider
from scrapy_selenium import SeleniumRequest

from ozonscraper.items import PhoneItem

AMOUNT_OF_DEVICES_TO_SCRAPE = 100


class OzonSpider(scrapy.Spider):
    name = "ozon"
    allowed_domains = ["ozon.ru"]
    start_urls = [
        "https://www.ozon.ru/category/telefony-i-smart-chasy-15501/?sorting=rating"
    ]

    def __init__(self, category=None, *args, **kwargs):
        super(OzonSpider, self).__init__(*args, **kwargs)
        self.items_scraped = 0
        self.url = "https://www.ozon.ru"

    def parse(self, response, **kwargs):
        devices = response.css("div.i1x.xi1")
        for device in devices:
            device_type = device.css("span.tsBody400Small font::text").get()
            if device_type == "Смартфон":
                relative_url = device.css("a::attr(href)").get()
                device_url = f"{self.url}{relative_url}"
                yield SeleniumRequest(
                    url=device_url, callback=self.parse_device_page, wait_time=10
                )
                self.items_scraped += 1
                if self.items_scraped == AMOUNT_OF_DEVICES_TO_SCRAPE:
                    raise CloseSpider(f"Scraped {AMOUNT_OF_DEVICES_TO_SCRAPE} devices")

        relative_next_page = response.css(
            "a.e9m.b200-a0.b200-b6.b200-b1::attr(href)"
        ).get()
        next_page_url = f"{self.url}{relative_next_page}"
        yield response.follow(next_page_url)

    def parse_device_page(self, response):
        phone_item = PhoneItem()
        phone_item["url"] = response.url
        device_os_a_tag = response.xpath(
            "//dl[contains(., 'Операционная система')]//a/text()"
        ).get()
        device_os_dd_tag = response.xpath(
            "//dl[contains(., 'Операционная система')]/dd/text()"
        ).get()
        phone_item["os"] = device_os_a_tag or device_os_dd_tag or "OS not specified"
        os_version = response.xpath(
            f"//dl[contains(., 'Версия {phone_item['os']}')]//dd/text()"
        ).get()
        os_version_a_tag = response.xpath(
            f"//dl[contains(., 'Версия {phone_item['os']}')]//dd/a/text()"
        ).get()
        phone_item["os_version"] = (
            os_version
            or os_version_a_tag
            or f"{phone_item['os']} version not specified"
        )
        yield phone_item

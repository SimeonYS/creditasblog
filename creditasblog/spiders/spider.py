import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import CreditasblogItem
from itemloaders.processors import TakeFirst
pattern = r'(\xa0)?'

class CreditasblogSpider(scrapy.Spider):
	name = 'creditasblog'
	start_urls = ['https://www.creditas.cz/blog/']

	def parse(self, response):
		post_links = response.xpath('//a[@class="position-absolute linkSkupina"]/@href').getall()
		yield from response.follow_all(post_links, self.parse_links)

	def parse_links(self, response):
		links = response.xpath('//h3/a/@href').getall()
		yield from response.follow_all(links, self.parse_post)

	def parse_post(self, response):
		date = response.xpath('//div[@class="c-article-detail__article"]/text() | //article[@class="article_perex"]//div[@class="info"]/text()').get()
		date = ''.join(el.strip() for el in date if el.strip())
		title = response.xpath('//h1[@class="c-article-detail__title"]/text() | //h2/span/text()').get()
		content = response.xpath('//div[@class="c-article-detail__perex"]//text()').getall() + response.xpath('//div[@class="c-article-detail__text"]//text()').getall()
		if not content:
			content = response.xpath('//div[@class="perex-body"]//text()').getall() + response.xpath('//div[@class="text_text text"]').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=CreditasblogItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()

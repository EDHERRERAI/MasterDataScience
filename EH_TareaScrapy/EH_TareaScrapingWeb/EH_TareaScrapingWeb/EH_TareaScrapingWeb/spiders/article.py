# -*- coding: utf-8 -*-
import scrapy
from EH_TareaScrapingWeb.items import articles, article


class ArticleSpider(scrapy.Spider):
    name = 'article'
    allowed_domains = ['catalog.data.gov']
    start_urls = ['https://catalog.data.gov/dataset']

    custom_settings = {
        'FEED_FORMAT' : 'json',
        'FEED_URI' : 'file:/Users/edgarherrera/Desktop/Proyectos/MaestriaDataScience/DataAcquisitation_1/Tareas/EH_TareaScrapy/EH_TareaScrapingWeb/EH_FileOutput.json'
    }

    def parse(self, response):
        host = self.allowed_domains[0]

        conteo = 1

        for link in response.css(".dataset-heading > a"):
            link = f"{link.attrib.get('href')}"
            title = link
            yield response.follow(link,callback=self.parse_detail, meta={'link' : link,'title':title})
            if conteo == 25:
                break
            conteo=conteo+1

    def parse_detail(self,response):
        items = articles()
        item = article()

        items["link"] = response.meta["link"]
        item["title"] = response.meta["title"]
        item["paragraph"] = list()
#<p class="dataset-organization">National Oceanic and Atmospheric Administration, Department of Commerce —</p>
        for text in response.css(".notes > p").extract():
            item["paragraph"].append(text)
        
        item["paragraph"] = item["paragraph"][0]

        items["body"] = item
        return items

 
 
# -*- coding: utf-8 -*-
import scrapy
from scrapy_splash import SplashRequest
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule


class JobsSpider(CrawlSpider):
    name = 'jobs'
    allowed_domains = ['builtinla.com/jobs']

    script = '''
        function main(splash, args)
            splash.private_mode_enabled = false
            
            splash:on_request(function(request)
                request:set_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.116 Safari/537.36')
            end)
            
            url = args.url
            assert(splash:go(url))
            assert(splash:wait(3))            
            
            
            return {
                html = splash:html()
            }
        end
    '''

    def start_requests(self):
        yield SplashRequest(url="https://www.builtinla.com/jobs?f%5B0%5D=job-category_operations-operations-management", callback=self.parse, endpoint="execute", args={
            'lua_source': self.script
        })

    def parse(self, response):
        for link in response.xpath("//div[@class='wrap-view-page']/a"):
            yield {
                'job_link': link.xpath(".//@href").get()
            }
            

        next_page = response.xpath("//li[@class='pager__item pager__item--next']/a/@href").get()
        if next_page:
            absolute_url = f"https://www.builtinla.com/jobs{next_page}"
            yield SplashRequest(url=absolute_url, callback=self.parse, dont_filter=True, endpoint='execute', args={
                'lua_source': self.script
            })

    rules = (
        Rule(LinkExtractor(allow=r'Items/'),
             callback='parse_item', follow=True),
    )

    def parse_item(self, response):
        item = {}
        #item['domain_id'] = response.xpath('//input[@id="sid"]/@value').get()
        #item['name'] = response.xpath('//div[@id="name"]').get()
        #item['description'] = response.xpath('//div[@id="description"]').get()
        return item

# -*- coding: utf-8 -*-
import scrapy
from scrapy_splash import SplashRequest
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule


class JobsSpider(CrawlSpider):
    name = 'jobs'
    allowed_domains = ['builtinla.com/jobs']

    # script = '''
    #     function main(splash, args)
    #     assert(splash:go(args.url))
    #     assert(splash:wait(0.5))
    #     return {
    #         html = splash:html()
    #         }
    #     end
    # '''

    script = '''
        function main(splash, args)
        splash:on_request(function(request)
            if request.url:find('css') then
                request.abort()
            end
        end)
        splash.images_enabled = false
        splash.js_enabled = false
        assert(splash:go(args.url))
        assert(splash:wait(0.5))
        return splash:html()
        end
    '''

    def start_requests(self):
        my_url = "https://www.builtinla.com/jobs?f%5B0%5D=job-category_developer-engineer-python&f%5B1%5D=job-category_developer-engineer-ruby-on-rails"
        #my_url ="https://www.builtinla.com/jobs?f%5B0%5D=job-category_operations-operations-management"
        yield SplashRequest(url=my_url, callback=self.parse, endpoint="execute", args={
            'lua_source': self.script
        })

    def parse(self, response):
        for link in response.xpath("//div[@class='wrap-view-page']/a"):
            url = link.xpath(".//@href").get()
            abs_url = f"https://www.builtinla.com{url}"

            yield scrapy.Request(
                url=abs_url,
                headers={
                    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36"
                },
                callback=self.parse_item,
                dont_filter=True
            )

            
        next_page = response.xpath("//li[@class='pager__item pager__item--next']/a/@href").get()
        if next_page:
            absolute_url = f"https://www.builtinla.com/jobs{next_page}"
            yield SplashRequest(url=absolute_url, callback=self.parse, dont_filter=True, endpoint='execute', args={
                'lua_source': self.script
            })

    rules = (
        Rule(LinkExtractor(allow=r'job/'),
             callback='parse_item', follow=True),
    )

    def parse_item(self, response):
        response
        item = {}
        item['start_url'] = response.request.url
        item['title'] = response.xpath('//h1[@class="node-title"]/span/text()').get()
        item['company'] = response.xpath('//div[@class="field__item"]/a/text()').get()
        item['company_link'] = 'https://www.builtinla.com' + response.xpath('//div[@class="field__item"]/a/@href').get()
        item['location'] = response.xpath('//div[@class="job-info"]/span/text()').get()
        yield item

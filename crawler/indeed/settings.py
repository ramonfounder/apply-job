
BOT_NAME = 'indeed'

SPIDER_MODULES = ['indeed.spiders']
NEWSPIDER_MODULE = 'indeed.spiders'



ROBOTSTXT_OBEY = False


SCRAPEOPS_API_KEY = ''


SCRAPEOPS_PROXY_ENABLED = True


EXTENSIONS = {
'scrapeops_scrapy.extension.ScrapeOpsMonitor': 500, 
}


DOWNLOADER_MIDDLEWARES = {

    'scrapeops_scrapy.middleware.retry.RetryMiddleware': 550,
    'scrapy.downloadermiddlewares.retry.RetryMiddleware': None,

    'indeed.middlewares.ScrapeOpsProxyMiddleware': 725,
}

CONCURRENT_REQUESTS = 1

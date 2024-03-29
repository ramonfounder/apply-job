import re
import json
import scrapy
from urllib.parse import urlencode

# https://ca.indeed.com/jobs?q=software+engineer+%24110%2C000&l=Toronto%2C+ON&sc=0kf%3Aattr%286M28R%7CEVPJU%7CFGY89%7CJB2WC%7CNGEEK%7CX62BT%7CXH9RQ%252COR%29attr%28DSQF7%29jt%28fulltime%29%3B&rbl=Toronto%2C+ON&jlid=aaab304de0fc22ae&fromage=7&lang=en&vjk=90edd91c0f4a25ae
class IndeedSearchSpider(scrapy.Spider):
    name = "indeed_search"
    custom_settings = {
        'FEEDS': {'data/%(name)s_%(time)s.csv': {'format': 'csv', }}
    }

    def get_indeed_search_url(self, keyword, location, offset=0):
        parameters = {"q": keyword, "l": location, "filter": 0, "start": offset}
        return "https://www.indeed.com/jobs?" + urlencode(parameters)

    def start_requests(self):
        keyword_list = ['software engineer',
                        'java developer',
                        'senior software engineer',
                        'Software Architech',
                        'backend developer']
        location_list = ['Toronto, ON']
        for keyword in keyword_list:
            for location in location_list:
                indeed_jobs_url = self.get_indeed_search_url(keyword, location)
                yield scrapy.Request(url=indeed_jobs_url, callback=self.parse_search_results,
                                     meta={'keyword': keyword, 'location': location, 'offset': 0})

    def parse_search_results(self, response):
        location = response.meta['location']
        keyword = response.meta['keyword']
        offset = response.meta['offset']
        script_tag = re.findall(r'window.mosaic.providerData\["mosaic-provider-jobcards"\]=(\{.+?\});', response.text)
        if script_tag is not None:
            json_blob = json.loads(script_tag[0])

            ## Extract Jobs From Search Page
            jobs_list = json_blob['metaData']['mosaicProviderJobCardsModel']['results']
            for index, job in enumerate(jobs_list):
                yield {
                    'keyword': keyword,
                    'location': location,
                    'page': round(offset / 10) + 1 if offset > 0 else 1,
                    'position': index,
                    'company': job.get('company'),
                    'companyRating': job.get('companyRating'),
                    'companyReviewCount': job.get('companyReviewCount'),
                    'highlyRatedEmployer': job.get('highlyRatedEmployer'),
                    'jobkey': job.get('jobkey'),
                    'jobTitle': job.get('title'),
                    'jobLocationCity': job.get('jobLocationCity'),
                    'jobLocationPostal': job.get('jobLocationPostal'),
                    'jobLocationState': job.get('jobLocationState'),
                    'maxSalary': job.get('estimatedSalary').get('max') if job.get('estimatedSalary') is not None else 0,
                    'minSalary': job.get('estimatedSalary').get('min') if job.get('estimatedSalary') is not None else 0,
                    'salaryType': job.get('estimatedSalary').get('max') if job.get(
                        'estimatedSalary') is not None else 'none',
                    'pubDate': job.get('pubDate'),
                }

            ## Paginate Through Jobs Pages
            if offset == 0:
                meta_data = json_blob["metaData"]["mosaicProviderJobCardsModel"]["tierSummaries"]
                num_results = sum(category["jobCount"] for category in meta_data)
                if num_results > 1000:
                    num_results = 50

                for offset in range(10, num_results + 10, 10):
                    url = self.get_indeed_search_url(keyword, location, offset)
                    yield scrapy.Request(url=url, callback=self.parse_search_results,
                                         meta={'keyword': keyword, 'location': location, 'offset': offset})

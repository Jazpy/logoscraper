import requests
import multiprocessing
import re
import sys
from bs4 import BeautifulSoup as bs

class Scraper:
    '''
    Represents a parallel scraper for multiple websites.

    Attributes:
        cores (int): How many cores to use in parallel, capped
            at multiprocessing.cpu_count().
        candidates (int): Max logo candidates to return for each URL.

    Methods:
        scrape(): Will initiate parallel scraping of the given URLs
        scraper_worker(): Handles request, parsing, and scraping for
            a single URL.
    '''


    def __init__(self, cores=1, candidates=3):
        '''
        Sets Scraper attributes.

        Parameters:
            cores (int): Number of cores to use, capped by
                multiprocessing.cpu_count()
            candidates(int): Max number of logo candidates to return
                for each website.
        '''
        self.cores      = min(multiprocessing.cpu_count(), cores)
        self.candidates = candidates

        # Internal regex expression for scraping
        ext = '(?:\.jpg|\.jpeg|\.png|\.svg|\.gif|\.webp)'
        self.__regex = re.compile(r'(?i)https?[^<>\s\'\"=]+' + ext + r'\b')

        # User agent so we don't get as many 403s
        self.__headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0'}


    def scrape(self, urls):
        '''
        Scrapes the given URLs, each URL is given its own process, where
        the GET request, and required parsing / searching is executed
        by the worker process.

        Parameters:
            urls (list of str): URLs to scrape.

        Returns:
            list of list of str. Elements are lists of strings for candidate
                logo web resources.

                Example:
                    [['google.com/logo.png']),
                     ['foo.com/logo.png', 'foo.com/foo.png'])]
        '''
        print(f'Beginning to scrape with {self.cores} processes...\n')
        with multiprocessing.Pool(self.cores) as pool:
            results = pool.map(self.scraper_worker, urls)
        return results


    def scraper_worker(self, url):
        '''
        Simple wrapper for the request, parsing, and scraping of a URL.

        Parameters:
            url (str): URL to scrape.

        Returns:
            list of strings. Each string is a candidate for the URL's logo.
        '''

        try:
            candidates = self.__find_candidates(url)
        except Exception as e:
            # Log error and return empty list if something goes wrong
            print(f'Exception while scraping {url=}: {repr(e)}\n',
                file=sys.stderr)
            return []

        print(f'Successfully scraped {url=}')
        return candidates


    # Uses beautifulsoup to find img elements
    def __find_tagged_images(self, text):
        ret = []

        # Get all <img>
        tagged_images = bs(text, 'html.parser').find_all('img')
        for image in tagged_images:
            attr_dic = image.attrs

            # Images without a src are meaningless for this purpose
            if 'src' not in attr_dic:
                continue

            # Append any images that have logo somewhere in the element
            for key in attr_dic:
                if 'logo' in key:
                    ret.append(image['src'])
                    break

            # Early exit if we have enough candidates
            if len(ret) >= self.candidates:
                return ret

        return ret


    # Uses regex to find untagged images
    def __find_raw_images(self, text):
        # Get all image web resources with the regex defined in init()
        raw_images = re.findall(self.__regex, text)
        return raw_images


    def __make_get_request(self, url):
        # Make web request, handle error codes
        if not (url.startswith('http://') or url.startswith('https://')):
            url = f'http://{url}'

        response = requests.get(url, headers=self.__headers, timeout=10)

        # Raise exception if GET was unsuccessful
        if response.status_code != 200:
            err_str = (f'GET request to {url=} was unsuccessful. ',
                f'Error code = {response.status_code}')
            raise RuntimeError(err_str)

        # Else we just return the text
        return response.text


    # Main workhorse for the scraping, makes the request and tries the
    # following three ways to find images that can be the logo:
    #
    #   1. img elements that are tagged to be the logo in some way.
    #   2. Any image web resources that contain the word logo.
    #   3. The first image web resource on the homepage.
    def __find_candidates(self, url):
        ret = []

        # Make GET request and store webpage text
        html_text = self.__make_get_request(url)

        # First heuristic, tagged images
        ret.extend(self.__find_tagged_images(html_text))
        missing = self.candidates - len(ret)

        # Early exit if we found multiple tagged images
        if missing <= 0:
            return ret

        # If we're missing some candidates, try second heuristic
        raw_images  = self.__find_raw_images(html_text)

        # Split into generic and logo images, based on filename (also dedupe)
        generic_images = []
        logo_images    = []
        for img in raw_images:
            if img in ret:
                continue

            if 'logo' in img.lower():
                logo_images.append(img)
            else:
                generic_images.append(img)

        # Only get as many as needed to fill the return list
        if len(logo_images) >= missing:
            ret.extend(logo_images[:missing])
        else:
            ret.extend(logo_images)

        # If we're here, we'll only append the first generic image and return
        if len(ret) < self.candidates and generic_images:
            ret.append(generic_images[0])

        return ret

import file_utils
import argparse
from scraping import Scraper

def main():
    # Get arguments
    args        = handle_args()
    websites_fp = args['websites']
    num_cores   = args['cores']
    out_dir     = args['out_dir']

    # Instantiate Scraper object
    scraper = Scraper(num_cores)

    # Begin scraping the available websites
    urls = file_utils.get_urls(websites_fp)
    logos = scraper.scrape(urls)

    # Output results
    file_utils.write_results(out_dir, logos)


def handle_args():
    '''Simple argparse object'''
    parser = argparse.ArgumentParser(description='Logo Scraper.')

    parser.add_argument('-w', '--websites', required=True,
        help='File with URLs to scrape, one per line.', type=str)
    parser.add_argument('-c', '--cores', default=1,
        help='Number of cores to use.', type=int)
    parser.add_argument('-o', '--out-dir', default='./',
        help='Output directory.', type=str)

    return vars(parser.parse_args())


if __name__ == '__main__':
    main()

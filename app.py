import os

import requests
from lxml import html
import urllib.request


class ScrapeBanglaAcademy:

    ACADEMY_URL = 'http://library.banglaacademy.org.bd'
    LINK_CLASS = '0'  # potentially bad! we check that entries are all li
    APPEND_BASE = 'page/'
    BOOK_H3_CLASS = 'product-title'
    P_HREF = 'cart'
    ADD_SUFFIX_PDF = 'files/res/downloads/book.pdf'
    FILE_LIST = 'downloaded.txt'

    @staticmethod
    def page_exists(uri):
        page = requests.get(uri)
        if page.status_code == 404:
            return False
        return True

    @staticmethod
    def get_tree_for_page(uri):
        page = requests.get(uri)
        tree = html.fromstring(page.content)
        return tree

    def scrape_url_list(self):
        print('Scraping URL list from root...')
        tree = self.get_tree_for_page(uri=self.ACADEMY_URL)
        link_li = tree.find_class(self.LINK_CLASS)
        category_list = []
        for li in link_li:
            new_link = li.cssselect('a')
            link_url = new_link[0].get('href')
            category_list.append(link_url)
            can_go = True
            page_no = 2
            while can_go:
                next_page = str(link_url) + self.APPEND_BASE + str(page_no)
                if self.page_exists(next_page):
                    category_list.append(next_page)
                    page_no = page_no + 1
                else:
                    can_go = False
        print('Found ' + str(len(category_list)) + ' category pages')
        return category_list

    def get_book_links(self, cat_list):

        print('Getting individual book pages..')
        book_url_list = []
        for link in cat_list:
            tree = self.get_tree_for_page(uri=link)
            link_h3 = tree.find_class(self.BOOK_H3_CLASS)
            for book_pg in link_h3:
                new_link = book_pg.cssselect('a')
                book_url_list.append(new_link[0].get('href'))
        print('Found ' + str(len(book_url_list)) + ' books in all categories')
        return book_url_list

    def get_pdf_urls(self, book_page_list):
        print('Generating PDF URIs for all books...')
        book_pdf_links = []
        for link in book_page_list:
            tree = self.get_tree_for_page(uri=link)
            link_p = tree.find_class(self.P_HREF)
            for book_pdf in link_p:
                pdf_base_url = book_pdf[0].get('href')
                if pdf_base_url[-1] == '/':
                    pdf_full_url = pdf_base_url + self.ADD_SUFFIX_PDF
                    book_pdf_links.append(pdf_full_url)
                    print(pdf_full_url)
        print('Valid URLs found for ' + str(len(book_pdf_links)) + ' books')

        return set(book_pdf_links)

    def get_no_download_url(self, book_pdfs):
        with open(self.FILE_LIST) as f:
            pdfs = f.read().splitlines()
        return list(set(book_pdfs) - set(pdfs))

    def download(self, download_list):
        for url in download_list:
            title = os.path.join('pdfs', url.replace(self.ADD_SUFFIX_PDF, '').split('/')[-2] + '.pdf')
            print('Downloading ' + title)
            with open(self.FILE_LIST, 'a') as f:
                f.write(url + '\n')
            urllib.request.urlretrieve(url, title)

    def run(self):
        category_list = self.scrape_url_list()
        book_list = self.get_book_links(category_list)
        book_pdfs = self.get_pdf_urls(book_list)
        to_download = self.get_no_download_url(book_pdfs)
        self.download(to_download)


if __name__ == '__main__':
    ScrapeBanglaAcademy().run()

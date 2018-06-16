import sys
import os
import re
import argparse
import bs4

from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.utils import ImageReader

from selenium_helper import get_chapters_list_html, get_image_urls


parser = argparse.ArgumentParser(description="Download manga from kissmanga.com in pdf format",
                                 usage='%(prog)s url [-o output_dir]')

parser.add_argument('url', help='Manga url')
parser.add_argument("-o", default='output/',
                    help="Output dir path")

args = parser.parse_args()
manga_url = args.url
output_dir = args.o

DOMAIN = 'http://kissmanga.com'


def get_chapters(manga_url):

    page = get_chapters_list_html(manga_url)
    if not page:
        print 'Failed to load chapters'
        sys.exit(0)
    soup = bs4.BeautifulSoup(page, "lxml")
    table = soup.find('table', attrs={"class": "listing"})

    data = []
    for row in table.find_all('tr'):
        cells = row.find_all("td")
        if not cells:
            continue
        a_tag = cells[0].find('a')
        data.append({
            "chapter_name": re.sub('[^\w\s-]', '', a_tag.get_text().strip().replace(':', " -")),
            "link": DOMAIN + a_tag['href'] if not a_tag['href'].startswith(DOMAIN) else a_tag['href']
        })
    return data


def generate_pdf(chapter_name, images, out_file_path):
    canvas = Canvas(out_file_path)
    canvas.setTitle(chapter_name)
    for img_url in images:
        print 'downloading image: ', img_url
        image = ImageReader(img_url)
        canvas.setPageSize(image.getSize())
        canvas.drawImage(image, x=0, y=0)
        canvas.showPage()
    canvas.save()


def download_chapter(chapter):
    out_file_path = "%s/%s.pdf" % (output_dir, chapter['chapter_name'])
    if os.path.exists(out_file_path):
        print 'Already exists: %s' % out_file_path
        return

    images = get_image_urls(url=chapter['link'])
    if not images:
        print "Failed to get chapter image urls"
        return

    generate_pdf(chapter['chapter_name'], images, out_file_path)


def main():

    global manga_url, output_dir

    if not manga_url.startswith(DOMAIN):
        print "Manga url is not supported."
        print "Only kissmanga.com is supported."
        sys.exit(0)

    if manga_url.endswith('/'):
        manga_url = manga_url[:-1]

    output_dir = os.path.join(output_dir, manga_url.split('/')[-1].lower())

    print 'Manga url: %s' % manga_url
    print 'Output dir: %s' % output_dir

    if not os.path.isdir(output_dir):
        os.makedirs(output_dir)

    chapters = get_chapters(manga_url)

    for chapter in chapters:
        print "\n"
        print "====================================================="
        print chapter['chapter_name']
        download_chapter(chapter)


if __name__ == "__main__":
    main()

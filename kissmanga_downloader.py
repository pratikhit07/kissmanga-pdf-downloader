import sys
import os
import json
import re

import requests
import bs4

from reportlab.pdfgen import canvas
from PIL import Image

from selenium_helper import get_chapters_list_html, get_image_urls

DOMAIN = 'http://kissmanga.com'
output_dir = 'output/'


def write_json(data, dir_name, file_name):

    if not os.path.isdir(dir_name):
        os.makedirs(dir_name)

    with open(os.path.join(dir_name, '%s.json' % file_name), 'w') as f:
        f.write(json.dumps(data, indent=2))


def get_chapters(manga_url):
    if os.path.exists(os.path.join(output_dir, 'chapters.json')):
        with open(os.path.join(output_dir, 'chapters.json')) as f:
            return json.load(f)

    page = get_chapters_list_html(manga_url)
    if not page:
        return None
    soup = bs4.BeautifulSoup(page, "lxml")
    table = soup.find('table', attrs={"class": "listing"})

    data = []
    for row in table.find_all('tr'):
        cells = row.find_all("td")
        if not cells:
            continue
        a_tag = cells[0].find('a')
        data.append({
            "chapter": re.sub('[^\w\s-]', '', a_tag.get_text().strip().replace(':', " -")),
            "link": DOMAIN + a_tag['href'] if not a_tag['href'].startswith(DOMAIN) else a_tag['href']
        })
    write_json(data, output_dir, 'chapters')
    return data


def get_images(chapter_url, dir_name, file_name):
    if os.path.exists(os.path.join(dir_name, file_name+'.json')):
        with open(os.path.join(dir_name, file_name+'.json')) as f:
            return json.load(f)

    images = get_image_urls(chapter_url)
    if not images:
        return []

    write_json(data=images, dir_name=dir_name, file_name=file_name)
    return images


def create_pdf(images, dir_name, file_name):
    c = canvas.Canvas(os.path.join(dir_name, file_name) + '.pdf')
    c.setTitle(file_name)
    for imgPath in images:
        with Image.open(imgPath) as loadedImage:
            w, h = loadedImage.size
        c.setPageSize((w, h))
        c.drawImage(imgPath, x = 0, y = 0)
        c.showPage()
    c.save()


def download_images_and_crate_pdf(images, dir_name, file_name):
    if os.path.exists(os.path.join(dir_name, file_name+'.pdf')):
        print 'Already exists: ', os.path.join(dir_name, file_name+'.pdf')
        return

    try:
        new_img_list = []
        for image_url in images:
            img_name = image_url.split("/")[-1]

            if not os.path.exists(os.path.join(dir_name, img_name)):
                print 'downloading image: ', image_url
                img_data = requests.get(image_url).content
                with open(os.path.join(dir_name, img_name), 'wb') as f:
                    f.write(img_data)

            new_img_list.append(
                os.path.abspath(os.path.join(dir_name, img_name))
            )
        create_pdf(
            images=new_img_list,
            dir_name=dir_name,
            file_name=file_name
        )
        print 'Success: ', os.path.join(dir_name, file_name)
        return True
    except Exception as e:
        import traceback
        traceback.print_exc()
    return False


def download_chapter(chapter):
    images = get_images(
            chapter_url=chapter['link'],
            dir_name=os.path.join(output_dir, chapter['chapter']),
            file_name="%s_%s" % (chapter['chapter'], 'images')
        )

    return download_images_and_crate_pdf(
        images=images,
        dir_name=os.path.join(output_dir, chapter['chapter']),
        file_name=chapter['chapter']
    )


def main():

    if len(sys.argv) <= 1:
        print "Manga url not found."
        sys.exit(0)

    manga_url = sys.argv[1]

    if not manga_url.startswith(DOMAIN):
        print "Manga url is not supported."
        print "Only kissmanga.com is supported."
        sys.exit(0)

    if manga_url.endswith('/'):
        manga_url = manga_url[:-1]
    global output_dir
    output_dir = os.path.join(output_dir, manga_url.split('/')[-1].lower())

    print 'Manga url: ', manga_url
    print 'Output dir: ', output_dir


    if not os.path.isdir(output_dir):
        os.makedirs(output_dir)

    chapters = get_chapters(manga_url)

    for chapter in chapters:
        print "\n"
        print "====================================================="
        print chapter['chapter']
        download_chapter(chapter)


if __name__ == "__main__":
    main()

# kissmanga-pdf-downloader
Download manga from kissmanga in pdf format.]


## Requirements:
python2 

pip

## Installing dependancies:
https://www.makeuseof.com/tag/install-pip-for-python/
```bash
pip install -r requirements.txt
```

## How to use script:
```python
python kissmanga_downloader.py "http://kissmanga.com/Manga/One-Piece"
```
## Output:
Pdf will download chapter wise and stored in output directory.

## How it Works:
Selenium is used to control a headless chrome browser running in background, in order to fetch html, and chapter wise image urls are retrieved. The images are then downloaded and converted in pdf. Currently it only supports kissmanga.com

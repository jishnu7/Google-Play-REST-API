#! /usr/bin/env python
# Copyright 2012 Jishnu Mohan <jishnu7@gmail.com>

from flask import Flask, jsonify, request, Response
import urllib2
import httplib
from BeautifulSoup import BeautifulSoup

app = Flask(__name__)


@app.errorhandler(404)
def not_found(error=None):
    message = {
        'status': 404,
        'message': 'Not Found: ' + request.url,
    }
    resp = jsonify(message)
    resp.status_code = 404
    return resp


@app.route('/')
def home():
    msg = 'Usage: /app/info/id. <br/>eg: /app/info/com.google.android.gm'
    resp = Response(msg, status=200, mimetype='text/html')
    return resp


@app.route('/app/info/<app_id>')
@app.route('/app/info/<app_id>/<language>')
def app_info(app_id, language='en_US'):
    print app_id
    url_play = 'https://play.google.com'
    link = url_play + '/store/apps/details?id=' + app_id
    request = urllib2.Request(link, headers={'Accept-Language': language})

    try:
        web = urllib2.urlopen(request).read()
    except urllib2.HTTPError, e:
        return not_found(e)
    except urllib2.URLError, e:
        return not_found(e)
    except httplib.HTTPException, e:
        return not_found(e)
    except Exception:
        return not_found()

    data = BeautifulSoup(web)
    meta_data = data.find('div', {'class': 'doc-metadata'})
    desc_div = data.find('div', {'id': 'doc-original-text'})
    screenshots = data.findAll('img', {'itemprop': 'screenshot'})

    if meta_data is None:
        return not_found()

    app_name = meta_data.find(itemprop='name')['content']
    app_image = meta_data.find(itemprop='image')['content']

    app_dev_meta = meta_data.find(itemprop='author')
    app_dev = app_dev_meta.find(itemprop='name')['content']
    app_dev_url = app_dev_meta.find(itemprop='url')['content']
    app_rating = meta_data.find(itemprop='ratingValue')['content']
    app_rating_count = meta_data.find(itemprop='ratingCount')['content']
    app_updated = meta_data.find(itemprop='datePublished').next
    app_version = meta_data.find(itemprop='softwareVersion').next
    app_os = meta_data.find(itemprop='operatingSystems').next.next.next
    app_downloads = meta_data.find(itemprop='numDownloads').next
    app_size = meta_data.find(itemprop='fileSize').next
    app_price = meta_data.find(itemprop='price')['content']
    app_contentrating = meta_data.find(itemprop='contentRating').next
    app_desc = desc_div.text
    app_screenshots = [img['src'].split("=")[0] for img in screenshots]

    app_data = {
        'name': app_name,
        'image': app_image,
        'author': app_dev,
        'author_url': url_play + app_dev_url,
        'ratingValue': app_rating,
        'ratingCount': app_rating_count,
        'datePublished': app_updated,
        'softwareVersion': app_version,
        'operatingSystems': app_os,
        'numDownloads': app_downloads,
        'fileSize': app_size,
        'price': app_price,
        'contentRating': app_contentrating,
        'description': app_desc,
        'screenshots': app_screenshots,
    }
    resp = jsonify(app_data)
    resp.status_code = 200
    return resp

if __name__ == '__main__':
    app.run(debug=True)

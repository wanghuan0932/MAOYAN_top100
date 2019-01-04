# -*- coding : utf-8 -*-
import requests, time, re, json, os
from requests import RequestException

headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'
    }

def get_one_page(url):
    try:
        response = requests.get(url, headers = headers)
        if response.status_code == 200:
            return response.text
        return None
    except RequestException as e:
        return None

#影片排名，名称，主演，上映时间，上映地区，评分，海报地址
def parse_one_page(html):
    pattern = re.compile('<dd>.*?board-index.*?>(.*?)</i>.*?title="(.*?)".*?data-src="(.*?)@160w.*?star">\\n\s+(.*?)\\n\s+</p>.*?'
                         'releasetime">(.*?)</p>.*?integer">(.*?)</i>.*?fraction">(.*?)</i></p>', re.S)
    items = re.findall(pattern, html)
    #print(type(items)) #list
    #print(items)
    for item in items:
        actor = re.sub('主演：', '', item[3])
        time = re.sub('上映时间：|\(.*?\)', '', item[4])
        locate = re.sub('上映时间：|\d{4}-\d{2}-\d{2}|\(|\)', '', item[4])
        if locate == '':
            locate = '中国内地'
            pass
        yield {
            'rank': item[0],
            'name': item[1],
            'actor': actor,
            'time': time,
            'locate': locate,
            'score': item[5] + item[6],
            'img': item[2],
        }

def write_to_file(item):
    with open('result.txt', 'a', encoding = 'utf-8') as f:
        print('TOP' + item.get('rank') + '：' + '\n')
        print(item)
        f.write('TOP' + item.get('rank') + '：' + '\n')
        f.write(json.dumps(item, indent=2, ensure_ascii = False) + '\n')

def save_img(item, file_path = '海报'):
    img_url, img_name, img_rank = item.get('img'), item.get('name'), item.get('rank')
    content = requests.get(img_url).content
    file_suffix = os.path.splitext(img_url)[-1]
    try:
        if not os.path.exists(file_path):
            os.mkdir(file_path)
        file_name = '{}{}{}{}{}'.format(file_path, os.sep, img_rank +'.', img_name, file_suffix)
        with open(file_name, 'wb') as f:
            print('下载成功:', file_name)
            f.write(content)
            pass
    except IOError as e:
            print('文件操作失败', e)
    except Exception as e:
        print('错误 ：', e)


#filename = '{}{}{}{}'.format(file_path, os.sep, file_name, file_suffix)

def main(offset):
    url = 'http://maoyan.com/board/4?offset=' + str(offset)
    html = get_one_page(url)
    for item in parse_one_page(html):
        #print(type(item)) #dict
        write_to_file(item)
        save_img(item)

if __name__ == '__main__':
    for i in range(10):
        main(offset = i * 10)
        time.sleep(1)

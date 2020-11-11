import re
import urllib
import urllib.request

from bs4 import BeautifulSoup


def main():
    baseurl = 'https://movie.douban.com/top250?start='
    getData(baseurl)


# 除了换行符之外的任何字符 .
# 0次或无数次 *
# 0次或1次 ?  ?">
findlink = re.compile(r'<a href="(.*?">)')  # compile()生成创建正则表达式对象，表示规则
findImgSrc = re.compile(r'<img.*src="(.*?")', re.S)  # re.S让换行符包括在字符串中
findTitle = re.compile(r'<span class="title">(.*)</span>')
findRating = re.compile(r'<span class="rating_num" property="v:average">(.*)</span>')
findJudge = re.compile(r'<span>(\d*)人评价</span>')
findInq = re.compile(r'<span class="inq">(.*)</span>')
findBd = re.compile(r'<p class="">(.*)</p>', re.S)


def getData(baseurl):
    datalist = []
    for i in range(0, 1):
        url = baseurl + str(i * 25)
        html = askUrl(url)

        soup = BeautifulSoup(html, 'html.parser')
        # 查找符合要求的字符串，形成列表
        # class为item的div，内部所有的元素(包括此div)
        for item in soup.find_all('div', class_='item'):
            # 查看详情
            data = []  # 保存一部电影的所有信息
            item = str(item)
            link = re.findall(findlink, item)[0]  # re库用来通过正则表达式查找指定的字符串
            data.append(link)

            imgSrc = re.findall(findImgSrc, item)[0]
            data.append(imgSrc)

            titles = re.findall(findTitle, item)
            if (len(titles) == 2):
                ctitle = titles[0]
                data.append(ctitle)
                otitle = titles[1].replace('/', '')
                data.append(otitle)
            else:
                data.append(titles[0])
                data.append(' ')  # 留空
            rating = re.findall(findRating, item)[0]
            data.append(rating)

            judge = re.findall(findJudge, item)[0]
            data.append(judge)

            inqs = re.findall(findInq, item)
            if len(inqs) != 0:
                inq = inqs[0].replace('。', '')
                data.append(inq)
            else:
                data.append('')

            bd = re.findall(findBd, item)[0]
            bd = re.sub('<br(\s+)?/>(\s+)?', ' ', bd)
            bd = re.sub('/', ' ', bd)
            data.append(bd)
            break


def askUrl(url):
    head = {
        'User-Agent': 'Mozilla / 5.0(Windows NT 10.0;Win64;x64) AppleWebKit / 537.36(KHTML, likeGecko) Chrome / '
                      '86.0.4240.183Safari / 537.36 ',
        'Cookie': 'bid=79IDAEXzhI4; dbcl2="226411055:cJIHqisuKR4"; ck=EOxf; push_noty_num=0; push_doumail_num=0; '
                  '__utma=30149280.502041821.1605077189.1605077189.1605077189.1; __utmc=30149280; '
                  '__utmz=30149280.1605077189.1.1.utmcsr=accounts.douban.com|utmccn=('
                  'referral)|utmcmd=referral|utmcct=/; __utmt=1; __utmv=30149280.22641; '
                  '__utmb=30149280.2.10.1605077189; _pk_ses.100001.4cf6=*; '
                  '__utma=223695111.620409013.1605077196.1605077196.1605077196.1; __utmb=223695111.0.10.1605077196; '
                  '__utmc=223695111; __utmz=223695111.1605077196.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); '
                  '__yadk_uid=XFxqlcMWRa8jb2KkjfvxYuEE3jjvJrz3; '
                  '__gads=ID=9bf8692f92e3b9d0-2240ac8bafc400fe:T=1605077197:RT=1605077197:S'
                  '=ALNI_MZfIZd9XjthZl9zoUT2KSdYQF-Ybg; '
                  '_pk_id.100001.4cf6=15e4d3f2ebee9dab.1605077196.1.1605077212.1605077196. '
    }
    request = urllib.request.Request(url, headers=head)
    html = ''
    try:
        res = urllib.request.urlopen(request)
        html = res.read().decode('utf-8')
    except urllib.error.URLError as e:
        if hasattr(e, 'code'):
            print(e.code)
        if hasattr(e, 'reason'):
            print(e.reason)
    return html


main()

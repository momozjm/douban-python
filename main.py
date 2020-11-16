import re
import sqlite3
import urllib
import urllib.request

import xlwt
from bs4 import BeautifulSoup


def main():
    baseurl = "https://movie.douban.com/top250?start="
    datalist = getData(baseurl)
    # savepath = '豆瓣电影250.xls'
    # saveData(datalist, savepath)
    dbpath = 'movie.db'
    saveData2DB(datalist, dbpath)


# 除了换行符之外的任何字符 .
# 0次或无数次 *
# 0次或1次 ?  ?">
findlink = re.compile(r'<a href="(.*?">)')  # compile()生成创建正则表达式对象，表示规则
findImgSrc = re.compile(r'<img.*src="(.*?")', re.S)  # re.S让换行符包括在字符串中
findTitle = re.compile(r'<span class="title">(.*)</span>')
findRating = re.compile(r'<span class="rating_num" property="v:average">(.*)</span>')
findJudge = re.compile(r'<span>(\d*)人评价</span>')
findInq = re.compile(r'<span class="inq">(.*)</span>')
findBd = re.compile(r'<p class="">(.*?)</p>', re.S)


def getData(baseurl):
    datalist = []
    for i in range(0, 10):
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
            data.append(bd.strip())
            datalist.append(data)
    return datalist


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


def saveData(datalist, savepath):
    print(111, datalist)
    book = xlwt.Workbook(encoding="utf-8", style_compression=0)  # 创建workbook对象
    sheet = book.add_sheet('豆瓣电影top250', cell_overwrite_ok=True)  # 创建工作表
    col = ('电影详情链接', '图片链接', '影片中文名', '影片外文名', '评分', '评价数', '简介', '相关信息')
    for i in range(0, 8):
        sheet.write(0, i, col[i])
    for i in range(0, 250):
        print("第%d条" % (i + 1))
        data = datalist[i]
        for j in range(0, 8):
            sheet.write(i + 1, j, data[j])

    book.save(savepath)  # 保存数据表


def saveData2DB(datalist, dbpath):
    init_db(dbpath)
    conn = sqlite3.connect(dbpath)
    cur = conn.cursor()

    for data in datalist:
        for index in range(len(data)):
            if index == 0 or index == 1:
                data[index] = "啊"
            if index == 4 or index == 5:
                continue
            data[index] = '"' + data[index] + '"'
        sql = '''
            insert into movie250 (
                info_link, pic_link, cname, ename, score, rated, introduction, info
            )
        values(%s)
        '''%",".join(data)
        print(sql)
        cur.execute(sql)
        conn.commit()
    cur.close()
    conn.close()


def init_db(dbpath):
    # 初始化数据库
    sql = '''
        create table movie250
        (
            id integer primary key autoincrement,
            info_link text,
            pic_link text,
            cname varchar,
            ename varchar,
            score numeric,
            rated numeric,
            introduction text,
            info text
        )
    '''  # 创建数据表
    conn = sqlite3.connect(dbpath)
    cursor = conn.cursor()  # 获取游标
    cursor.execute(sql)  # 执行sql语句
    conn.commit()        # 提交数据库操作
    conn.close()         # 关闭数据库操作


if __name__ == '__main__':
    main()
    print('完毕')

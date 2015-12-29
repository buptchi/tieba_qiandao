#!/usr/bin/python
# -*-coding:utf-8-*-
__author__ = 'chi'

import requests
import re
import sqlite3
import os
import pwd
import bs4

url_tieba = "http://tieba.baidu.com"
url_sign = 'http://tieba.baidu.com/sign/add'                    # use method POST
url_tbs = 'http://tieba.baidu.com/dc/common/tbs'
url_tieba_like = "http://tieba.baidu.com/f/like/mylike"

url_baidu = "http://www.baidu.com"
url_login = "https://passport.baidu.com/v2/?login"              # use method POST
url_passport = "https://passport.baidu.com/center?_t=1450842895"
url_get_tokan = "https://passport.baidu.com/v2/api/?getapi&class=login&tpl=mn&tangram=true"

# the path of cookies is different from browser and operating system, you can change it
chrome_cookies = ".config/google-chrome/Default/Cookies"
firefox_cookies = ".mozilla/firefox/t7w6k21p.default/cookies.sqlite"

# cookies name and host in cookies.sqlite
require_cookies = ['H_PS_PSSID','LONGID','BAIDUID', 'BDUSS',
                   'TIEBA_USERTYPE', 'TIEBAUID', 'bdshare_firstime', 'BIDUPSID', 'PSTM', 'BDTUJIAID']
require_cookies_host = ['.baidu.com', '.tieba.baidu.com']

# global var
s = requests.Session()
cookies = {}
herders_firefox = {
    'Host': "tieba.baidu.com",
    'User-Agent': "Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:40.0) Gecko/20100101 Firefox/40.0",
    'Connection': "keep-alive",
}


def get_cookies():
    global cookies
    cookie_file = os.path.join(pwd.getpwuid(1000).pw_dir, firefox_cookies)
    conn = sqlite3.connect(cookie_file)
    cur = conn.cursor()
    for cookie_host in require_cookies_host:
        sql = 'SELECT host, name, value, path FROM moz_cookies WHERE (host="%s") ORDER BY host' % cookie_host
        cur.execute(sql)
        results = cur.fetchall()
        if len(results):
            for row in results:
                cookies[row[1]] = row[2]
        else:
            print "sql query have 0 result"
    cur.close()
    conn.close()


def get_like_tieba():
    global s
    r = s.get(url_tieba_like, headers=herders_firefox, cookies=cookies)
    ss = bs4.BeautifulSoup(r.text)
    dd = ss.find_all('a')[0::3]
    likes = {}
    for d in dd:
        likes[d['title']] = d['href']
    return likes


def get_tbs():
    global s
    r = s.get(url_tbs, headers=herders_firefox, cookies=cookies)
    tbs = re.search('"tbs":"(?P<tbs>.*?)"', r.text).group('tbs')
    if tbs:
        return tbs
    else:
        print "have not get tbs"


def get_sign(likes, tbs):
    global s
    herders_firefox['Content-Type'] = "application/x-www-form-urlencoded; charset=UTF-8"
    herders_firefox['X-Requested-With'] = "XMLHttpRequest"
    herders_firefox['Prama'] = "no-cache"
    herders_firefox['Cache-Control'] = "no-cache"
    herders_firefox['Accept-Language'] = "en-US,en;q=0.5"
    herders_firefox['Accept-Encoding'] = "gzip, deflate"

    for title, href in likes.items():
        post_data = {'ie': 'utf8', 'kw': title, 'tbs': tbs}
        herders_firefox['Referer'] = url_tieba+href+"&fr=index"
        try:
            r = s.post(url_sign, data=post_data, headers=herders_firefox, cookies=cookies)
            j = r.json()

            if j['error'] == '':
                user_sign_rank = int(j['data']['uinfo']['user_sign_rank'])
                cont_sign_num = int(j['data']['uinfo']['cont_sign_num'])
                cout_total_sing_num = int(j['data']['uinfo']['cout_total_sing_num'])
                print u"在贴吧《%s》签到成功 " % title
                print u"签到成功,第%d个签到,连续签到%d天,累计签到%d天" %(user_sign_rank, cont_sign_num, cout_total_sing_num)
            else:
                print u"在贴吧《%s》签到失败 " % title
                print "no:      " + repr(j['no'])
                print "error:   "+j['error']
                print "data:    "+j['data']
        except requests.RequestException, e:
            print e


def main():
    get_cookies()
    likes = get_like_tieba()
    tbs = get_tbs()
    get_sign(likes, tbs)

if __name__ == "__main__":
    main()

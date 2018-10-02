#coding=utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf8')
import requests
import HTMLParser
from xml.dom.minidom import parse
import xml.dom.minidom
from email.utils import parseaddr, formataddr
import smtplib
import datetime
from pyquery import PyQuery as pq
from email.mime.image import MIMEImage
from bs4 import BeautifulSoup
import nltk
from wordcloud import WordCloud, ImageColorGenerator
import jieba.analyse
from email.mime.multipart import MIMEMultipart
import matplotlib.pyplot as plt
from scipy.misc import imread
from email.mime.text import MIMEText
from email.header import Header


def parse_index():
    nowtime = datetime.datetime.now()
    printtime = nowtime.strftime('%Y-%m-%d')
    time = nowtime+ datetime.timedelta(days=-7)
    time = time.strftime('%Y-%m-%d')
    session = requests.Session()
    data = {
        'os_username': 'xxxxx', #在此填写JIRA用户名
        'os_password': 'xxxxx', #在此填写JIRA密码
    }
    session.post(url='http://jira.xxxxx.com/rest/gadget/1.0/login', data=data) #在此填写JIRA的URL
    Jira_Contents = session.get('http://jira.xxxxx.com/sr/jira.issueviews:searchrequest-xml/temp/SearchRequest.xml?jqlQuery=assignee+%3D+currentUser%28%29+AND+%28%28created+>%3D+'+time+'+AND+created+<%3Dnow%28%29%29+OR+%28updated+>%3D'+time+'+AND+updated+<%3Dnow%28%29%29%29+order+by+updated+DESC&tempMax=1000')
    print Jira_Contents

    with open ('jira.xml','w') as f:
        f.write(Jira_Contents.content)
        f.close()
    DOMTree = xml.dom.minidom.parse('jira.xml')
    root = DOMTree.documentElement
    channels = root.getElementsByTagName('item')
    output = ''
    output2 = ''
    output += str('统计创建或更新时间段：')+time+str(' 至 ')+printtime+'\n'
    i = 0
    for item in channels:
        output += '--------------------------\n'
        output += '类型: '+item.getElementsByTagName('type')[0].childNodes[0].nodeValue+'\n'
        output += '状态: '+item.getElementsByTagName('status')[0].childNodes[0].nodeValue+'\n'
        output += '标题: '+item.getElementsByTagName('summary')[0].childNodes[0].nodeValue+'\n'
        output += '描述: '+item.getElementsByTagName('description')[0].childNodes[0].nodeValue+'\n'
        if item.toxml().find('comments')>0 :
            output += '备注: '+item.getElementsByTagName('comment')[0].childNodes[0].nodeValue+'\n'
        output += '创建时间: '+item.getElementsByTagName('created')[0].childNodes[0].nodeValue+'\n'
        output += '修改时间：'+item.getElementsByTagName('updated')[0].childNodes[0].nodeValue+'\n'
        i = i+1

        output2 += item.getElementsByTagName('summary')[0].childNodes[0].nodeValue+'\n'
        output2 += item.getElementsByTagName('description')[0].childNodes[0].nodeValue+'\n'
        if item.toxml().find('comments')>0 :
            output2 += item.getElementsByTagName('comment')[0].childNodes[0].nodeValue+'\n'
    output = output.replace('<p>','').replace('</p>','').replace('<span class="nobr">','')\
        .replace('\n\n','\n').replace(' +0800','').replace('<ol>','').replace('</li>','').replace('</ol>','').replace('<li>','')
    output += str('--------------------------\n本周共涉及任务点：')+str(i)+str('个。\n高频内容参见词云附件。')
    output2 = output2.replace('<p>','').replace('</p>','')
    print output
    with open('output.txt', 'w') as f:
        f.write(output)
        f.close()
    with open('output2.txt', 'w') as f:
        f.write(output2)
        f.close()
    return output

def sendMail():

    nowtime = datetime.datetime.now()
    printtime = nowtime.strftime('%Y-%m-%d')
    time = nowtime + datetime.timedelta(days=-7)
    starttime = time.strftime('%Y-%m-%d')
    output = parse_index()
    my_sender = 'xxxx'  # 在此填写发件人邮箱
    my_receiver = 'xxxx'  # 在此填写收件人邮箱账号
    try:
        msg = MIMEMultipart('related')
        msg.attach(MIMEText(output, 'plain', 'utf-8'))
        msg['From'] = formataddr(["xxxx", my_sender])
        msg['To'] = formataddr(["", my_receiver])
        msg['Subject'] = "Jira周报:"+starttime+' ~ '+printtime
        mail_Msg = '<img src="cid:image1"/>'
        fp = open('Cloud.png', 'rb')
        msgImage = MIMEImage(fp.read())
        fp.close()
        msgImage.add_header('Content-Disposition', 'attachment', filename='WordCloud.png')
        msg.attach(msgImage)
        server = smtplib.SMTP("smtp.163.com", 25) #在此填写邮箱SMTP
        server.login(my_sender, "xxxx") #在此填写邮箱密码
        server.sendmail(my_sender, [my_receiver, ], msg.as_string())
        server.quit()
        print("邮件发送成功")
    except smtplib.SMTPException:
        print("无法发送邮件")


def genWordCloud():

    f = open('output2.txt','r').read()
    cut_text = " ".join(jieba.cut(f))

    wordCloud = WordCloud(
        font_path = 'kh.ttf',
        background_color = 'white',width=2000,height=1680).generate(cut_text)

    plt.imshow(wordCloud,interpolation='bilinear')
    plt.axis("off")
    plt.savefig('Cloud')


if __name__ == '__main__':
    sendMail()
    genWordCloud()

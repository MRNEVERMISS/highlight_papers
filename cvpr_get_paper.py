import uuid
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
import requests
from bs4 import BeautifulSoup
from lxml import etree
import time
import io
import socket
import csv
import threading
import os
import arxiv

def download_arxiv_paper(id_item, save_path, filename):
    paper = next(arxiv.Search(id_list=[id_item]).results())
    paper.download_pdf(dirpath=save_path,filename=filename)

def get_paper_url( url, url_txt ):
    url_txt_writer = open(url_txt,'a')

    # chrome_options = webdriver.ChromeOptions()
    # prefs = {"profile.managed_default_content_settings.images":2}
    # chrome_options.add_experimental_option("prefs",prefs)
    #
    # option = webdriver.ChromeOptions()
    # option.add_experimental_option('excludeSwitches',['enable-automation'])

    # wb =webdriver.Chrome(options=chrome_options)
    option = webdriver.ChromeOptions()
    # 设置为开发者模式
    option.add_experimental_option('excludeSwitches', ['enable-automation'])

    option.add_argument("--disable-blink-features=AutomationControlled")


    wb = webdriver.Chrome(options=option)

    wb.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
        'source': 'Object.defineProperty(navigator, "webdriver", {get: () => undefined})'
    })
    #wb =webdriver.Chrome(options=chrome_options)

    wb.maximize_window()
    wb.get(url)
    wb.implicitly_wait(5)

    data = wb.page_source
    time.sleep(3)

    page_all = []
    page_all.append(data)
    html = etree.HTML(data)

    class_number = html.xpath('/html/body/div[1]/div[2]/div/div[3]/div/div/div')
    for num_class in range(1, len(class_number)+1,1):
        if num_class > len(class_number):
            break
        link_number = html.xpath('/html/body/div[1]/div[2]/div/div[3]/div/div/div['+str(num_class)+']/table/tbody/tr')
        for num in range(1,len(link_number)+1,1):
            if num > len(link_number):
                break
            links = html.xpath('/html/body/div[1]/div[2]/div/div[3]/div/div/div['
                               +str(num_class)+']/table/tbody/tr['+str(num)+']/td[4]/a')
            for link in links:
                url_txt_writer.write(link.get("href")+"\n")

    url_txt_writer.close()

def parse_url_txt( url_txt, save_path ):
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    with open( url_txt ) as infile:
        lines = infile.readlines()
        for line in lines:
            url = line.strip()

            if url.endswith(".pdf"):
                try:
                    req = requests.get(url)
                    time.sleep(10)
                    bytes_io = io.BytesIO(req.content)
                    filename = uuid.uuid4().hex
                    with open(save_path+filename+".pdf","wb") as file:
                        file.write((bytes_io.getvalue()))

                except:
                    continue
            elif 'arxiv' in url:
                try:
                    id_item = url.split('abs/')[1]
                    filename = uuid.uuid4().hex+".pdf"
                    download_arxiv_paper(id_item,save_path,filename)

                except:
                    continue


if __name__=="__main__":
    years = ['2017','2018','2019','2020','2021','2022','2023']
    url_txt = "link.txt"
    for year in years:
        year = year.strip()
        url = 'https://gaplab.cuhk.edu.cn/cvpapers/#/'+str(year)+'cvpr'
        get_paper_url(url,url_txt)

    # url_txt = "link.txt"
    # save_path = './papers/'
    # parse_url_txt(url_txt,save_path)
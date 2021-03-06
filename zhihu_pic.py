from urllib.request import urlopen as uReq
import urllib.request
import urllib.request as urr
from bs4 import BeautifulSoup as soup
from time import sleep
import json
import os
from random import randrange
from threading import Thread

q_lst = ['20958648']

for q in q_lst:
    q_num = q

    headers={
     'User-Agent':'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/46.0.2490.76 Mobile Safari/537.36',
    }

    # building urls
    my_url = 'https://www.zhihu.com/api/v4/questions/'+q_num+'/answers?include=data%5B%2A%5D.is_normal%2Cadmin_closed_comment%2Creward_info%2Cis_collapsed%2Cannotation_action%2Cannotation_detail%2Ccollapse_reason%2Cis_sticky%2Ccollapsed_by%2Csuggest_edit%2Ccomment_count%2Ccan_comment%2Ccontent%2Ceditable_content%2Cvoteup_count%2Creshipment_settings%2Ccomment_permission%2Ccreated_time%2Cupdated_time%2Creview_info%2Crelevant_info%2Cquestion%2Cexcerpt%2Crelationship.is_authorized%2Cis_author%2Cvoting%2Cis_thanked%2Cis_nothelp%2Cis_labeled%2Cis_recognized%2Cpaid_info%2Cpaid_info_content%3Bdata%5B%2A%5D.mark_infos%5B%2A%5D.url%3Bdata%5B%2A%5D.author.follower_count%2Cbadge%5B%2A%5D.topics&limit=5&offset=0&platform=desktop&sort_by=default'
    temp_url = 'https://www.zhihu.com/question/'+q_num

    uClient = urr.Request(my_url, headers=headers)
    with uReq(uClient) as response:
        page_html = response.read()

    uClient2 = uReq(temp_url)
    temp_html = uClient2.read()
    uClient2.close()
    temp_soup = soup(temp_html, "html.parser")
    temp_header = temp_soup.h1

    folder_name = temp_header.get_text()

    if folder_name[-1] == '?':
        folder_name = folder_name[0:-1]

    is_end = False

    img_links = []

    while is_end == False:
        # sleep(randrange(5, 25)/10)
        print('Next page ...')
        aa = json.loads(page_html)
        # three big category: ad_info, data, paging
        paging = aa["paging"]
        data = aa['data']
        for i in data:
            # sleep(randrange(1,3))
            # find all img
            content = i['content']
            page_soup = soup(content, "html.parser")
            # j = json.loads(uClient.read())
            # print(page_soup.h1)
            containers = page_soup.findAll('img',{"class": "origin_image zh-lightbox-thumb"})
            print('Captured: ' + str(len(containers)))

            for j in containers:
                img_links.append(j['src'])
            print("Total: " + str(len(img_links)))

        # check if everything is ended after the processing step
        is_end = paging['is_end']
        my_url = paging['next']

        # get the next url in queue
        uClient = uReq(my_url)
        page_html = uClient.read()
        uClient.close()

    print('All links captured ...')

    # enter current dir and create a folder
    current_directory = os.getcwd()
    final_directory = os.path.join(current_directory, folder_name)
    if not os.path.exists(final_directory):
        os.makedirs(final_directory)

    os.chdir(final_directory)

    # save 2 dir, links need to be list; 2 inputs in tot
    def save2dir(links):
        for jj in range(len(links)):
            local = str(links[jj][26:61]) + '.jpg'
            urllib.request.urlretrieve(links[jj], local)

    # divide up the total targets into all cores in computer
    cpu_num = os.cpu_count()
    por_num = 1
    if len(img_links) < cpu_num:
        por_num = len(img_links)
        por_qua = 1
        remainder = 0
    else:
        por_num = cpu_num
        por_qua = len(img_links) // (cpu_num - 1)
        remainder = len(img_links) % (cpu_num - 1)

    # create multiple processes to get links faster
    threads = []
    for i in range(por_num):
        if remainder == 0:
            t = Thread(target=save2dir, args=(img_links[(i * por_qua):((i + 1) * por_qua)],))
        else:
            if i != por_num - 1:
                t = Thread(target=save2dir, args=(img_links[(i * por_qua):((i + 1) * por_qua)],))
            else:
                t = Thread(target=save2dir, args=(img_links[(i * por_qua):(i * por_qua) + remainder],))
        t.start()
        threads.append(t)
    for j in threads:
        j.join()

    os.chdir(current_directory)
    print('Everything finished lol')

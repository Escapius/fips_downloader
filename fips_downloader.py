# -*- coding: utf-8 -*-

from selenium import webdriver
from selenium.common import exceptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
import json
import requests
import time
from xhtml2pdf import pisa
import traceback
import cStringIO
import urllib

driver = webdriver.PhantomJS()
wait = WebDriverWait(driver, 10)
lib_dict = {u'НПМ': 'RUPM', u'ФПМ': 'RUPM', u'РИ': 'RUPAT', u'ЗИЗ': 'RUPAT', u'НИЗ': 'RUPAT'}
font_face_rule = u'''@font-face {font-family: WipoUniExt; /* Гарнитура шрифта */
    									src: url(http://www.fips.ru/cdfi/Fonts/WipoUni.ttf); /* Для IE5-8 */
    									src: local(WipoUniExt), url(http://www.fips.ru/cdfi/Fonts/WipoUni.ttf);
    									/* Для остальных браузеров */}'''.encode('cp1251')
try:
    driver.get('http://www1.fips.ru/wps/portal/IPS_Ru')
    wait.until(expected_conditions.presence_of_element_located(('id', 'groupDbN_1'))).click()
    for checkbox_name in ['RUPATABRU', 'RUPATAP', 'RUPAT_NEW', 'RUPMAB', 'RUPM_NEW', 'IMPIN']:
        wait.until(expected_conditions.presence_of_element_located(('name', checkbox_name))).click()
    wait.until(expected_conditions.presence_of_element_located(('id', 'searchPanelTab'))).click()
    search_area = wait.until(expected_conditions.presence_of_element_located(('name', 'queryTextArea')))
    wait.until(expected_conditions.visibility_of(search_area))
    search_area.send_keys(u'Стенд испытания турбокомпрессоров')
    head_of_fieldlist = wait.until(expected_conditions.presence_of_element_located(('id', 'fieldsListHead')))
    head_of_fieldlist.find_element(by='id', value='dijit_form_Button_1').click()
    result_info = wait.until(expected_conditions.presence_of_element_located(('id', 'ipsSerachResultInfo')))
    result_info = wait.until(expected_conditions.visibility_of(result_info))
    total_count = result_info.find_element(by='id', value='IPS_TotalCount')
    print(total_count.text)
    hitlist = driver.find_element(by='id', value='hitList')
    list_of_link = [link for link in hitlist.find_elements_by_tag_name(name='a')]
    for link in list_of_link:
        doc_num = link.find_element_by_class_name('dvNumDoc').text
        lib = link.find_element_by_class_name('dvLibrary').text
        db = lib_dict[lib]
        title = link.find_element_by_class_name('dvTitle').text
        doc_link = 'http://www1.fips.ru/fips_servl/fips_servlet?DB={0}&DocNumber={1}&TypeFile=html'.format(db, doc_num)
        start = time.time()
        while True:
            response = requests.get(doc_link)
            if u'Слишком быстрый просмотр документов' not in response.content.decode('cp1251'):
                break
            time.sleep(10)
        out_pdf = open(u'{0}({1}).pdf'.format(title, doc_num), 'wb')
        out_html = open(u'{0}({1}).html'.format(title, doc_num), 'wb')
        remove_index = response.content.find('@font-face')
        remove_content = response.content[remove_index:remove_index+261]
        content = response.content.replace(remove_content, '')
        try:
            pisa.showLogging()
            pdf = pisa.CreatePDF(src='Печать, print', dest=out_pdf)
            if pdf.err:
                print('ошибка')
            out_html.write(response.content)
        except Exception as e:
            traceback.print_exc()
            print(e)
        finally:
            out_pdf.close()
            out_html.close()
        break
except exceptions.InvalidElementStateException as e:
    print(type(e))
    print(json.loads(e.msg)[u'errorMessage'])
    for key, value in json.loads(e.msg)[u'request'].items():
        print('{0}---{1}'.format(key, value))
    driver.get_screenshot_as_file('errorshot.png')
except exceptions.NoSuchWindowException as e:
    print(type(e))
    for key, value in json.loads(e.msg)[u'request'].items():
        print('{0}---{1}'.format(key, value))
    driver.get_screenshot_as_file('errorshot.png')
except exceptions.WebDriverException as e:
    print(type(e))
    for key, value in json.loads(e.msg)[u'request'].items():
        print('{0}---{1}'.format(key, value))
    driver.get_screenshot_as_file('errorshot.png')
except Exception as e:
    print(type(e))
    print(e)
    driver.get_screenshot_as_file('errorshot.png')
finally:
    driver.quit()

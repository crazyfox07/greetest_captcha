# -*- coding:utf-8 -*-

import os
import time
import random
import PIL.Image as image
import PIL.ImageChops as imagechops
import time, re,  random

import requests
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup as bs


def get_merge_image(filename, location_list):
    """
    根据位置对图片进行合并还原
    :filename: 图片
    :location_list: 图片位置
    """
    im = image.open(filename)
    #new_im = image.new('RGB', (260, 116))
    im_list_upper = []
    im_list_down = []

    for location in location_list:
        if location['y'] == -58:
            im_list_upper.append(im.crop((abs(location['x']), 58, abs(location['x']) + 10, 166)))
        if location['y'] == 0:
            im_list_down.append(im.crop((abs(location['x']), 0, abs(location['x']) + 10, 58)))

    new_im = image.new('RGB', (260, 116))

    x_offset = 0
    for im in im_list_upper:
        new_im.paste(im, (x_offset, 0))
        x_offset += im.size[0]

    x_offset = 0
    for im in im_list_down:
        new_im.paste(im, (x_offset, 58))
        x_offset += im.size[0]
    return new_im


def get_image(driver, div):
    background_images = driver.find_elements_by_xpath(div)

    location_list = []

    imageurl = ''

    for background_image in background_images:
        location = {}

        location['x'] = int(re.findall("background-image: url\(\"(.*)\"\); background-position: (.*)px (.*)px;",background_image.get_attribute('style'))[0][1])
        location['y'] = int(re.findall("background-image: url\(\"(.*)\"\); background-position: (.*)px (.*)px;",background_image.get_attribute('style'))[0][2])
        imageurl = re.findall("background-image: url\(\"(.*)\"\); background-position: (.*)px (.*)px;",background_image.get_attribute('style'))[0][0]

        location_list.append(location)

    imageurl = imageurl.replace("webp", "jpg")

    #jpgfile = cStringIO.StringIO(urllib2.urlopen(imageurl).read())
    with open('p1.jpg','wb') as f:
        f.write(requests.get(imageurl).content)

    image = get_merge_image('p1.jpg', location_list)

    return image


def is_similar(image1, image2, x, y):
    """
    对比 RGB 值
    """
    pixel1 = image1.getpixel((x, y))
    pixel2 = image2.getpixel((x, y))

    for i in range(0, 3):
        if abs(pixel1[i] - pixel2[i]) >= 50:
            return False

    return True


def get_diff_location(image1, image2):
    """
    计算缺口的位置
    """
    for i in range(0, 260):
        for j in range(0, 116):
            if is_similar(image1, image2, i, j) == False:
                return i


def get_track(length):
    """
    根据缺口的位置模拟 x 轴移动的轨迹
    """
    list = []
    x = random.randint(0, 2)

    while length - x >= 5:
        list.append(x)

        length = length - x
        x = random.randint(0, 2)

    for i in range(length):
        list.append(1)

    return list


def geetest_crack(driver, keyword):
    """
    模拟鼠标操作破解滑块验证码
    """
    # 等待页面元素加载完成
    # WebDriverWait(driver, 30).until(lambda the_driver:the_driver.find_element_by_xpath("//div[@class='gt_slider_knob gt_show']").is_displayed())
    # WebDriverWait(driver, 30).until(lambda the_driver: the_driver.find_element_by_xpath("//div[@class='gt_cut_bg gt_show']").is_displayed())
    # WebDriverWait(driver, 30).until(lambda the_driver: the_driver.find_element_by_xpath("//div[@class='gt_cut_fullbg gt_show']").is_displayed())

    # 下载图片
    image1 = get_image(driver, "//div[@class='gt_cut_bg gt_show']/div")
    image2 = get_image(driver, "//div[@class='gt_cut_fullbg gt_show']/div")

    image1.save('p2.jpg')
    image2.save('p3.jpg')

    # 计算缺口的位置
    loc = get_diff_location(image1, image2)

    # 生成 x 的移动轨迹
    track_list = get_track(loc)

    # 找到滑动的圆球
    element = driver.find_element_by_xpath("//div[@class='gt_slider_knob gt_show']")
    location = element.location

    # 获取滑动圆球的高度
    y = location['y']

    # 模拟鼠标点击元素并按住不动
    #print u"第一步，点击元素"
    ActionChains(driver).click_and_hold(on_element=element).perform()
    time.sleep(0.15)

    y_delta = random.choice([-1, 1])

   # print u" 第二步，拖动元素"
    track_string = ""
    for track in track_list:
        # track_string = track_string + "{%d,%d}," % (track, y - 416)
        track_string = track_string + "{%d,%d}," % (track, y - 416 - 88)
        # xoffset=track+22:这里的移动位置的值是s相对于滑动圆球左上角的相对值，而轨迹变量里的是圆球的中心点，所以要加上圆球长度的一半。
        # yoffset=y-445:这里也是一样的。不过要注意的是不同的浏览器渲染出来的结果是不一样的，要保证最终的计算后的值是22，也就是圆球高度的一半
        if random.randint(1, 100) > 90:
            # ActionChains(driver).move_to_element_with_offset(to_element=element, xoffset=track+22, yoffset=y - 416).perform()
            ActionChains(driver).move_to_element_with_offset(to_element=element, xoffset=track+22, yoffset=y - 0).perform()
        else:
            y += y_delta
            # ActionChains(driver).move_to_element_with_offset(to_element=element, xoffset=track+22, yoffset=y - 416).perform()
            ActionChains(driver).move_to_element_with_offset(to_element=element, xoffset=track+22, yoffset=y - 0).perform()

        # 间隔时间也通过随机函数来获得
        time.sleep(random.randint(10, 50)/150)

    #print track_string
    # xoffset=21，本质就是向后退一格。这里退了5格是因为圆球的位置和滑动条的左边缘有5格的距离
    for _ in range(5):
        if y in range(-5, 6):
            # ActionChains(driver).move_to_element_with_offset(to_element=element, xoffset=21, yoffset=y - 416).perform()
            ActionChains(driver).move_to_element_with_offset(to_element=element, xoffset=21, yoffset=y - 416 - 88).perform()
        else:
            y -= y_delta
            # ActionChains(driver).move_to_element_with_offset(to_element=element, xoffset=21, yoffset=y - 416).perform()
            ActionChains(driver).move_to_element_with_offset(to_element=element, xoffset=21, yoffset=y - 416 - 88).perform()
        time.sleep(random.randint(5, 15)/100)

    #print u" 第三步，释放鼠标"
    ActionChains(driver).release(on_element=element).perform()

    time.sleep(3)

    soup = bs(driver.page_source, 'html.parser')

    #if soup.text.find(u'查询结果') > -1 or soup.text.find(u'查询到') > -1:
    if soup.find('div',class_='gt_holder gt_popup gt_show'):
        return False
    else:
        return True


def captchar_enter(driver,keyword):
    # cur_script_dir = os.path.split(os.path.realpath(__file__))[0]
    # driver_path = os.path.join(cur_script_dir, "chromedriver")
    # print driver_path
    # driver = webdriver.Chrome()#(executable_path=driver_path)
    driver.get("http://www.gsxt.gov.cn/index.html")
    #
    time.sleep(3)

    element = driver.find_element_by_id("keyword")
    element.clear()
    element.send_keys(keyword)
    element = driver.find_element_by_id("btn_query")
    element.click()
    time.sleep(1)
    flag = False
    retry_times = 0
    while not flag and retry_times < 5:
        flag = geetest_crack(driver, keyword)
        retry_times += 1

        time.sleep(2)
    #print flag

    return flag

if __name__ == '__main__':
    driver = webdriver.Chrome()
    captchar_enter(driver=driver,keyword=u"小米")

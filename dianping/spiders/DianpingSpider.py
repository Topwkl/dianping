
from scrapy.spiders import CrawlSpider

from dianping.items import FoodieItem
from scrapy.selector import Selector
from scrapy.http import Request

import sys
import random

reload(sys)
sys.setdefaultencoding('utf-8')

class DianpingSpider(CrawlSpider):

    name = "dianping"

    start_urls=[
        'http://www.dianping.com/memberlist/0/0'

    ]


    def parse(self, response):

        selector = Selector(response)

        infos = selector.xpath('//tr')

        for info in infos:
            nickname = info.xpath('td[1]/a/text()').extract()
            url = info.xpath('td[1]/a/@href').extract()

            comment_first = info.xpath('td[3]/text()').extract()
            comment_response = info.xpath('td[4]/text()').extract()
            flower = info.xpath('td[4]/text()').extract()
            if len(nickname)>0 :
                name =  nickname[0]
                detailurl =  'http://www.dianping.com'+url[0]

                cmt_first = comment_first[0]
                cmt_response = comment_response[0]
                fl =  flower[0]

                print detailurl


                yield Request(detailurl,callback=self.parse_details,meta={'nickname':name,'cmt_first':cmt_first,'cmt_response':cmt_response,'fl':fl})


        ###分页
        for p in range(2,7):
            url='http://www.dianping.com/memberlist/3/0?pg=%s'%p

            yield Request(url,callback=self.parse)



    def parse_details(self,response):

        foodItem = FoodieItem()

        foodItem['nickname']= response.meta['nickname']
        foodItem['comment_first'] = response.meta['cmt_first']
        foodItem['comment_response'] = response.meta['cmt_response']
        foodItem['flower'] = response.meta['fl']

        foodItem['url'] =response.url



        selector = Selector(response)
        infos = selector.xpath('//div[@id="J_UMoreInfoD"]/ul/li')

        if len(infos) >0 :
            for info in infos:
                item = info.xpath('em/text()').extract()
                content = info.xpath('text()').extract()

                if len(content) >0 :
                    item = str(item[0])
                    content = str(content[0]).strip()
                    if  item == '体型：':
                        foodItem['shape']=content
                    elif item == '恋爱状况：':
                        foodItem['love_situation'] = content
                    elif item == '生日：':
                        foodItem['birthday'] = content

                    elif item == '星座：':
                        foodItem['star_sign'] = content
                    elif item == '毕业大学：':
                        foodItem['college'] = content

                    elif item == '爱好：':
                        foodItem['hobby'] = content

                    elif item == '菜肴/菜系/餐厅：':
                        foodItem['foodtype'] = content
                    elif item == '行业职业：':
                        foodItem['occupation'] = content



                # print item[0]  ## 名称
                # print content[0]  ## 内容



        ###贡献值中的商户数
        shops = selector.xpath('//div[@id="J_lay_devote"]/p[2]/text()').extract()[0]
        foodItem['shops'] = shops

        fans = selector.xpath('//div[@class="user_atten"]/ul/li[2]/a/strong/text()').extract()[0]
        foodItem['fans'] = fans

        inter = selector.xpath('//div[@class="user_atten"]/ul/li[3]/strong/text()').extract()[0]
        foodItem['interaction'] = inter

        navs = selector.xpath('//div[@class="nav"]/ul/li/a/text()').extract()

        foodItem['comment_num'] = filter(str.isdigit,str(navs[1]))
        foodItem['collect_num'] = filter(str.isdigit, str(navs[2]))
        foodItem['loc_check'] = filter(str.isdigit, str(navs[3]))
        foodItem['pic_num'] = filter(str.isdigit, str(navs[4]))
        foodItem['note_num'] = filter(str.isdigit, str(navs[6]))

        # print filter(str.isdigit,str(navs[1]))  #点评
        # print filter(str.isdigit, str(navs[2])) #收藏
        # print filter(str.isdigit, str(navs[3])) #签到
        # print filter(str.isdigit, str(navs[4])) #图片
        # print filter(str.isdigit, str(navs[6])) #帖子

        level = selector.xpath('//div[@class="user-time"]/p[2]/text()').extract()[0]
        reg_time = selector.xpath('//div[@class="user-time"]/p[3]/text()').extract()[0]
        foodItem['level'] = level
        foodItem['reg_time'] = reg_time


        uinfos = selector.xpath('//div[@class="user-info col-exp"]')

        for info in uinfos:
            contribution = info.xpath('span[1]/@title').extract()[0]
            rank = info.xpath('span[1]/@class').extract()[0]


            foodItem['contribution'] = filter(str.isdigit,str(contribution))
            foodItem['rank'] = filter(str.isdigit,str(rank))


            loc = info.xpath('span[2]/text()').extract()
            if len(loc) >0 :
                foodItem['location'] = loc[0]
            else:
                foodItem['location'] =''

            gender = info.xpath('span[2]/i/@class').extract()
            if len(gender) > 0:
                foodItem['gender'] = gender[0]
            else:
                foodItem['gender'] = ''


        tags = info.xpath('span[3]/em/text()').extract()

        atag = ''
        for tag in tags:

            atag += tag +'\n'
        foodItem['tags'] = loc

        yield foodItem
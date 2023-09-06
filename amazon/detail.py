from playwright.sync_api import sync_playwright
import time
import re


class YouTubeScraperDetail:
    def __init__(self, index,video_id):
        self.id = index + 1
        self.domain_url = "https://www.youtube.com/watch?v="
        self.video_id = video_id
        self.target_url = self.domain_url + self.video_id
        self.out_detail = {'id':self.id,'video_url': self.target_url}
        self.error_flag = False

    def handle_response(self, page):
        try:
            page.wait_for_selector('tp-yt-paper-button#expand', state='visible')
            page.click('tp-yt-paper-button#expand')
            page.wait_for_selector('yt-formatted-string#info', state='visible')
            click_info = page.query_selector('yt-formatted-string#info')
            view_date_element = click_info.query_selector_all('span')
            self.out_detail["view"] = view_date_element[0].inner_text()
            self.out_detail["date"] = view_date_element[2].inner_text()
            print(f'view: {self.out_detail["view"]}')
            print(f'date: {self.out_detail["date"]}')
            description_element = page.query_selector('ytd-text-inline-expander#description-inline-expander')
            self.out_detail["description"] = description_element.inner_text()

            duration_element = page.query_selector('.ytp-time-duration')
            self.out_detail["duration"] = duration_element.inner_text()
            print(f'duration: {self.out_detail["duration"]}')
            # page.wait_for_selector('#segmented-like-button', state='visible',timeout=5000)
            # time.sleep(1)
            # like_element = page.query_selector('#segmented-like-button span[role="text"]')
            like_element = page.query_selector('#factoids yt-formatted-string:nth-child(1)')
            self.out_detail["liked"] = like_element.inner_text()
            print(f'liked: {self.out_detail["liked"]}')

            # page.wait_for_selector('#factoids', state='hideen')

            # page.wait_for_selector('#factoids yt-formatted-string', state='visible', timeout=10000)
            # page.wait_for_selector('#factoids', state='attached', timeout=5000)
            # time.sleep(5)
            # factoids_element = page.query_selector('#factoids')
            # elements = factoids_element.query_selector_all('yt-formatted-string')

            # i =0
            # while len(elements) <6 :
            #     i += 1
            #     print(f'ループ中 {i}回目')
            #     html_content = page.content()
            #     except_filename = './er/detail_error'+str(i)+ '.html'
            #     with open(except_filename, "w") as file:
            #         file.write(html_content)

            #     page.reload()
            #     # time.sleep(1)
            #     page.wait_for_selector('#factoids', state='attached', timeout=5000)
            #     factoids_element = page.query_selector('#factoids')
            #     elements = factoids_element.query_selector_all('yt-formatted-string')
            #     print(f'len(elements): {len(elements)}')
            # print(f'len(elements): {len(elements)}')
            
            # self.out_detail["liked"] = elements[0].inner_text()
            # self.out_detail["view"] = elements[2].inner_text()
            # date_yyyy = elements[5].inner_text() # 2023年
            # self.out_detail["yyyy"] = date_yyyy.replace("年","")
            # date_mmdd = elements[4].inner_text() # 9月30日
            # date_mmdd_list = re.split(r'月|日', date_mmdd)
            # self.out_detail["mm"] = date_mmdd_list[0]
            # self.out_detail["dd"] = date_mmdd_list[1]
            # description_element = page.query_selector('#description > yt-attributed-string')
            # description = description_element.inner_text()
            # self.out_detail["description"] = description

        except AttributeError as e:
            self.error_flag = True
            html_content = page.content()
            length_html_content = len(html_content)
            print(f'html文字数: {length_html_content}')
            except_filename = 'detail_error.html'
            with open(except_filename, "w") as file:
                file.write(html_content)
            print(f'エラーが発生しました。{except_filename}を確認してください。')
            print(e)
                

    def scrape(self):
        print(self.video_id)
        start_time = time.time()
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto(self.target_url)

            self.handle_response(page,)
            browser.close()
            

        # with open("detail.json", "w", encoding="utf-8") as file:
        #     json.dump(self.out_detail, file, ensure_ascii=False, indent=4)
        
        # length_html_content = len(html_content)
        # print(f'html文字数: {length_html_content}')
        processing_time = time.time() - start_time
        print(f'処理時間(s）: {round(processing_time,1)}')
        # print(f'detail: {self.out_detail}')
        return self.out_detail, self.error_flag

import selenium.webdriver
import time
import platform
import os
from psyduck_export import config
from psyduck_export import db_helper


class Helper:
    is_ready = False
    driver = None
    download_path = None
    zip_export_path = None
    zip_save_path = None
    driver_path = None
    option_path = None
    data_path = None
    data_root = None
    uuid = None

    export_url_list = []
    export_index = 0
    export_downloading = False

    def __init__(self, uuid):
        self.uuid = uuid

    @staticmethod
    def _create_dir(_dir):
        _dir = config.frozen_path(_dir)
        if not os.path.exists(_dir):
            os.mkdir(_dir)

    @staticmethod
    def _get_driver_name(name):
        if platform.system() == 'Windows' and not name.endswith('.exe'):
            name += ".exe"
        return name

    def __settings(self):
        self.is_ready = False
        self.data_root = config.frozen_path('user_data')
        self.data_path = config.frozen_path(os.path.join(self.data_root, self.uuid))
        self.driver_path = config.frozen_path(os.path.join(self.data_path, 'chromedriver'))
        self.option_path = config.frozen_path(os.path.join(self.data_path, 'chrome_option'))
        self.download_path = config.frozen_path(os.path.join(self.data_path, 'download'))
        self.zip_export_path = config.frozen_path('../static/{}.zip'.format(self.uuid))
        self.zip_save_path = config.frozen_path(config.zip_save_path)

    def __prepare(self):
        Helper._create_dir(self.data_root)
        Helper._create_dir(self.data_path)
        import shutil
        _raw_driver_path = config.frozen_path(os.path.join('chrome_driver', Helper._get_driver_name('chromedriver')))
        shutil.copyfile(_raw_driver_path, self.driver_path)
        Helper._create_dir(self.download_path)
        Helper._create_dir(self.zip_save_path)

    def __selenium_init(self):
        options = selenium.webdriver.ChromeOptions()
        options.add_argument("user-data-dir=" + self.option_path)
        options.add_argument('disable-infobars')
        options.add_argument('--mute-audio')
        options.add_argument('--disable-gpu')
        options.add_argument("--log-level=3")

        prefs = {
            "disable-popup-blocking": False,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "download.default_directory": self.download_path,
            "profile.default_content_settings.popups": 0,
            'profile.default_content_setting_values': {'notifications': 2},
        }

        from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
        cap = DesiredCapabilities.CHROME
        cap["pageLoadStrategy"] = "none"

        options.add_experimental_option("prefs", prefs)
        os.chmod(self.driver_path, 755)

        self.driver = selenium.webdriver.Chrome(options=options, executable_path=self.driver_path,
                                                desired_capabilities=cap)
        self.driver.set_window_size(1000, 750)
        self.reset_timeout()

    def init(self):
        self.__settings()
        self.__prepare()
        self.__selenium_init()
        self.is_ready = True

    def reset_timeout(self):
        self.driver.set_page_load_timeout(10)
        self.driver.set_script_timeout(10)

    def get(self, url, timeout=10, retry=3):
        self.driver.get(url)
        time.sleep(1)
        time_counter = 0
        retry_counter = 0
        while retry_counter < retry:
            while time_counter < timeout:
                result = self.driver.execute_script("return document.readyState")
                if result == 'complete':
                    return
                if result == 'interactive':
                    time.sleep(3)
                    return
                time_counter += 1
                time.sleep(1)
            retry_counter += 1
            print('timeout retry %d -> %s' % (retry_counter, url))
        raise Exception('timeout retry %d all failed -> %s' % (retry, url))

    def find(self, xpath):
        import selenium.common.exceptions
        try:
            el = self.driver.find_element_by_xpath(xpath)
        except selenium.common.exceptions.NoSuchElementException:
            return None
        return el

    def find_all(self, xpath):
        return self.driver.find_elements_by_xpath(xpath)

    def find_count(self, xpath):
        return len(self.find_all(xpath))

    def set_window_size(self, width, height):
        self.driver.set_window_size(width, height)

    def dispose(self):
        if self.driver is not None:
            self.driver.stop_client()
            self.driver.close()
            self.driver = None
        self.is_ready = False

    def check_login(self):
        self.get("https://i.csdn.net/#/uc/profile")
        if self.driver.current_url.find('https://i.csdn.net/#/uc/profile') != -1:
            return True
        return False

    def logout(self):
        self.get('https://passport.csdn.net/account/logout')

    def login(self, phone_num, verify_code):
        if self.driver.current_url != 'https://passport.csdn.net/login':
            self.get('https://passport.csdn.net/login')

    def __valid_download_url(self, url):
        # 暂时屏蔽验证
        return url != ''

    def download(self, url, qq_num=config.default_qq, qq_name=config.default_qq_name, qq_group=-1):
        step = 'begin download'
        try:
            step = 'url cut #'
            if url.find('#') != -1:
                url = url[0:url.index('#')]

            step = 'valid url'
            if not self.__valid_download_url(url):
                return self.__download_result(False, "无效的下载地址")

            step = 'get url'
            self.get(url)
            time.sleep(3)

            step = 'valid page'
            if self.find('//div[@class="error_text"]') is not None:
                return self.__download_result(False, self.find('//div[@class="error_text"]').text)

            step = 'get download info'
            info = self.__get_download_info()
            info['url'] = url
            info['qq_num'] = qq_num
            info['qq_name'] = qq_name
            info['qq_group'] = qq_group

            step = 'check already download'
            if self.__already_download(info['id']):
                step = 'already download set zip file name'
                info['filename'] = self.__get_file_name_in_zip_file(info['id'])
                step = 'save to db'
                self.__save_to_db(info)
                step = 'finish'
                return self.__download_result(True, "success", info)

            step = 'find download button'
            btn = self.find('//div[@class="dl_download_box dl_download_l"]/a[text()="VIP下载"]')
            vip_channel = True
            step = 'check download channel'
            if btn is None:
                vip_channel = False
            if not vip_channel:
                btn = self.find('//div[@class="dl_download_box dl_download_l"]/a[@class="direct_download"]')
            if btn is None:
                return self.__download_result(False, "该资源没有下载通道")

            step = 'clear download dir'
            self.__clear_download_dir()
            time.sleep(1)

            step = 'click download button'
            btn.click()
            time.sleep(1)

            step = 'check max count'
            if self.find('//div[@id="download_times"]').get_attribute('style').find('display: block;') != -1:
                return self.__download_result(False, 'CSDN今日下载次数已达上限（20），请明日在来下载。')

            step = 'find confirm download'
            if vip_channel:
                if self.find('//div[@id="vipIgnoreP"]').get_attribute('style').find('display: block;') != -1:
                    self.find('//div[@id="vipIgnoreP"]//a[@class="dl_btn vip_dl_btn"]').click()
                else:
                    pass  # 无弹窗情况（自己的资源）
            else:
                if self.find('//div[@id="noVipEnoughP"]').get_attribute('style').find('display: block;') != -1:
                    self.find('//div[@id="noVipEnoughP"]//a[@class="dl_btn js_download_btn"]').click()
                elif self.find('//div[@id="download"]').get_attribute('style').find('display: block;') != -1:
                    self.find('//div[@id="download"]//a[@class="dl_btn js_download_btn"]').click()
                elif self.find('//div[@id="noVipEnoughP"]').get_attribute('style').find('display: block;') != -1:
                    self.find('//div[@id="noVipEnoughP"]//a[@class="dl_btn js_download_btn"]').click()
                elif self.find('//div[@id="noVipEnoughP"]').get_attribute('style').find('display: block;') != -1:
                    self.find('//div[@id="noVipEnoughP"]//a[@class="dl_btn js_download_btn"]').click()
                elif self.find('//div[@id="noVipNoEnoughPNoC"]').get_attribute('style').find('display: block;') != -1:
                    return self.__download_result(False, "积分不足下载！")
                elif self.find('//div[@id="dl_lock"]').get_attribute('style').find('display: block;') != -1:
                    return self.__download_result(False, self.find('//div[@id="dl_lock"]').text)
                else:
                    pass  # 无弹窗情况（自己的资源）

                time.sleep(1)
                if self.find('//div[@id="dl_security_detail"]').get_attribute('style').find('display: block;') != -1:
                    # input('下载过于频繁，请输入验证码，并按任意键继续...')
                    # print('验证完成！继续下载任务中...')
                    return self.__download_result(False, "下载过于频繁，请输入验证码")

            step = 'wait for download'
            self.__wait_for_download()

            step = 'add filename to info'
            info['filename'] = os.path.basename(self.__get_tmp_download_file())

            step = 'zip file'
            self.__zip_file(info['id'])

            step = 'save to db'
            self.__save_to_db(info)

            step = 'finish'
            return self.__download_result(True, "success", info)
        except:
            import traceback
            traceback.print_exc()
            return self.__download_result(False, "error : %s" % step)

    def export_all(self):
        self.export_downloading = True
        format_url = 'https://download.csdn.net/my/uploads/1/{}'
        res_url = []
        for i in range(1, 100):
            _url = format_url.format(i)
            self.get(_url)
            if self.find('//dt[@class="empty_icons"]') is not None:
                break
            els = self.find_all('//div[@class="content"]/h3/a[@target="_blank"]')
            for el in els:
                if el.get_attribute('href') is None:
                    continue
                res_url.append(el.get_attribute('href'))
        self.export_url_list = res_url
        for i in range(0, len(res_url)):
            self.export_index = i
            self.download(res_url[i])
        self.export_downloading = False

    def __get_download_info(self):
        import datetime
        coin_el = self.find('//div[@class="dl_download_box dl_download_l"]/label/em')
        coin = 0 if coin_el is None else int(coin_el.text.strip())
        date_str = self.find('//strong[@class="size_box"]/span[1]').text.strip()[:10]
        info = {
            'id': self.find('//div[@id="download_top"]').get_attribute('data-id'),
            'title': self.find('//dl[@class="download_dl"]/dd/h3').get_attribute('title'),
            'description': self.find('//div[@class="pre_description"]').text.strip(),
            'type': self.find('//dl[@class="download_dl"]/dt/img').get_attribute('title'),
            'tag': self.find('//a[@class="tag"]').text.strip(),
            'coin': coin,
            'stars': self.find_count('//span[@class="starts"]//i[@class="fa fa-star yellow"]'),
            'upload_date': datetime.datetime.strptime(date_str, "%Y-%m-%d"),
            'size': self.find('//strong[@class="size_box"]/span[2]/em').text.strip(),
        }
        return info

    def __clear_download_dir(self):
        for f in os.listdir(self.download_path):
            os.remove(os.path.join(self.download_path, f))

    def __get_tmp_download_file(self):
        files = os.listdir(self.download_path)
        if len(files) <= 0:
            raise Exception('下载文件不存在！')
        elif len(files) > 1:
            raise Exception('下载目录存在多余文件！')
        return os.path.join(self.download_path, files[0])

    def __wait_for_download(self):
        time.sleep(3)  # wait for create file
        wait_time = 20
        last_size = os.path.getsize(self.__get_tmp_download_file())
        while wait_time > 0 and self.__get_tmp_download_file().endswith('.crdownload'):
            cur_size = os.path.getsize(self.__get_tmp_download_file())
            if cur_size == last_size:
                wait_time -= 1
            else:
                wait_time = 20
            time.sleep(1)

        if self.__get_tmp_download_file().endswith('.crdownload'):
            raise Exception('文件下载失败，请重试！')

    def __zip_file(self, _id):
        import zipfile
        zip_path = os.path.join(self.zip_save_path, "{0}.zip".format(_id))
        if os.path.exists(zip_path):
            os.remove(zip_path)
            print('zip exist, then delete!')
        with zipfile.ZipFile(zip_path, mode='w') as zipf:
            file_path = self.__get_tmp_download_file()
            zipf.write(file_path, os.path.basename(file_path))

    def __get_file_name_in_zip_file(self, _id):
        import zipfile
        zip_path = os.path.join(self.zip_save_path, "{0}.zip".format(_id))
        zipf = zipfile.ZipFile(zip_path)
        files = zipf.namelist()
        if len(files) != 1:
            return None
        return files[0]

    def __already_download(self, _id):
        zip_path = os.path.join(self.zip_save_path, "{0}.zip".format(_id))
        if os.path.exists(zip_path):
            file_name = self.__get_file_name_in_zip_file(_id)
            if file_name is not None and not file_name.endswith('.crdownload'):
                return True
        return False

    def __save_to_db(self, info):
        if not db_helper.exist_download(info['id']):
            db_helper.insert_download(info)

    def __download_result(self, success, message='', info=None):
        return {'success': success, 'message': message, 'info': info, }

    def get_user_info(self):
        try:
            self.get('https://download.csdn.net/my/vip')
            time.sleep(2)
            name = self.find('//div[@class="name"]/span').text.strip()
            is_vip = self.find('//a[@class="btn_vipsign"]') is None
            info = {
                'name': name,
                'vip': is_vip
            }
            if is_vip:
                remain = self.find('//div[@class="cardr"]/ul/li/span').text.strip()
                date = self.find('//div[@class="cardr"]/ul/li[2]/span').text.strip()
                info['remain'] = remain
                info['date'] = date
            else:
                remain = self.find('//ul[@class="datas clearfix"]//span').text.strip()
                info['remain'] = remain
            return info
        except:
            import traceback
            traceback.print_exc()
            return None

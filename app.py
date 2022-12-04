import os
import json
import tkinter
import datetime
import webbrowser
from tkinter import ttk, messagebox

import requests
from dateutil.relativedelta import relativedelta


if os.name == 'nt':
    home = os.getenv('USERPROFILE')
else:
    home = os.getenv('HOME')

desktop_path = os.path.join(home, 'Desktop')

def mkdir(directory):
    try:
        os.makedirs(f'{desktop_path}/{directory}')
    except FileExistsError:
        pass


class WellbiteDownload:
    def __init__(self):
        self.token = None
        self.months = []
        self.downloads = 30
        self.total_downloads = 100

        self.root = tkinter.Tk()
        self.root.geometry('720x540')
        self.root.title('Wellnote Downloader')

    def open_form(self):
        self.new_root = tkinter.Toplevel(self.root)
        self.new_root.geometry('720x540')
        self.new_root.title('Wellnoteにログインしてください')

    def destory_form(self):
        self.new_root.destroy()
        self.new_root.update()
    
    def __create_developer(self):
        text = tkinter.Label(self.root, text='Developed by @innovate_7110', foreground='#1DA1F2', cursor='star')
        text.place(x=260, y=420, anchor=tkinter.NW)
        text.bind("<Button-1>", lambda e:webbrowser.open_new('https://twitter.com/innovate_7110'))

    def __create_form(self):
        # mail address to login
        self.mail_label = tkinter.Label(self.new_root, text='メールアドレス')
        self.mail_label.place(x=100, y=100)
        self.mail_text = tkinter.Entry(self.new_root, width=30)
        self.mail_text.place(x=240, y=100)

        # password to login
        self.password_label = tkinter.Label(self.new_root, text='パスワード')
        self.password_label.place(x=100, y=160)
        self.password_text = tkinter.Entry(self.new_root, width=30)
        self.password_text.place(x=240, y=160)

        # login button
        self.login_button = tkinter.Button(
            self.new_root, text='ログイン', width=28)
        self.login_button.place(x=240, y=240)

        self.login_button.bind('<Button-1>', self.login)

    def __create_pulldown(self):
        # target month pulldown
        self.month_box = ttk.Combobox(values=self.months)
        self.month_box.pack(pady=50)
        self.month_box.set(self.months[0] if len(self.months) else '')

    def __create_download(self):
        # download button
        self.download_button = tkinter.Button(
            text='ダウンロード', command=self.download, width=20)
        self.download_button.pack(pady=50)

    def render(self):
        self.__create_form()
        self.__create_developer()
        self.root.mainloop()

    def login(self, event):
        res = requests.post(
            'https://auth.wellnote.jp/login',
            data=json.dumps({
                'login_id': self.mail_text.get(),
                'password': self.password_text.get(),
                'with_cookie': True
            }),
            headers={'Content-Type': 'application/json'}
        )

        if res.status_code == 200 and res.json().get('access_token'):
            self.token = res.json().get('access_token')

            messagebox.showerror(
                'ログイン成功',
                'ログインに成功しました。年月を指定してダウンロードしてください'
            )

            self.destory_form()

            self.get_months()
            self.__create_pulldown()
            self.__create_download()

        else:
            messagebox.showerror(
                'ログインエラー',
                'ログインに失敗しました。メールアドレスとパスワードが正しいかご確認ください。'
            )

    def get_months(self):
        res = requests.get(
            'https://api.wellnote.jp/v2/families',
            headers={
                'authorization': f'Bearer {self.token}'
            }
        )
        family_id = res.json().get('families')[0].get('family_id')

        res = requests.get(
            f'https://api.wellnote.jp/v2/families/{family_id}/album/available-months?tz=32400',
            headers={
                'authorization': f'Bearer {self.token}'
            }
        )
        raw_months = res.json().get('months')
        self.months += [month.replace('-', '/') for month in raw_months]

    def download(self):
        target_month = self.month_box.get()

        mkdir(f'wellnote/{target_month}')

        start_date = datetime.datetime.strptime(
            f'{target_month}/1', '%Y/%m/%d')
        end_date = start_date + \
            relativedelta(months=1) - datetime.timedelta(seconds=1)

        start_timestamp = int(start_date.timestamp())
        end_timestamp = int(end_date.timestamp())

        res = requests.get(
            f'https://api.wellnote.jp/v2/families/491408/album?from={start_timestamp}&to={end_timestamp}',
            headers={
                'authorization': f'Bearer {self.token}'
            }
        )

        if res.status_code == 200 and res.json().get('photos'):
            photos = res.json().get('photos')

            try:
                for photo in photos:
                    photo_url = photo.get('signature').get(
                        'content_url').format(size='p')

                    print(photo_url)
                    file_name = photo_url.split('/')[-1]
                    if not photo.get('is_video'):
                        file_name += '.jpg'

                    content = requests.get(photo_url).content
                    with open(f'{desktop_path}/wellnote/{target_month}/{file_name}', mode='wb') as f:
                        f.write(content)

                messagebox.showerror(
                    'ダウンロード完了', f'{target_month}のダウンロードが完了しました！')
            except:
                messagebox.showerror(
                    'ダウンロード失敗', f'{target_month}のダウンロードが途中で失敗しました。')
                pass

        else:
            messagebox.showerror('ダウンロードエラー', 'アルバム一覧の取得に失敗しました。')

        self.download_button['text'] = 'ダウンロード'


mkdir('wellnote')

nd = WellbiteDownload()
nd.open_form()
nd.render()

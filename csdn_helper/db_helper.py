from peewee import *
import datetime
import config
import os

db_dir = os.path.dirname(config.sqlite_db_path)
if not os.path.exists(db_dir):
    os.mkdir(db_dir)
db = SqliteDatabase(config.sqlite_db_path)


class Download(Model):
    class Meta:
        database = db

    id = CharField(primary_key=True, unique=True)
    url = CharField(null=True)
    title = CharField(null=True)
    type = CharField(null=True)
    size = CharField(null=True)
    tag = CharField(null=True)
    description = CharField(null=True)
    filename = CharField(null=True)
    coin = IntegerField(null=True)
    stars = IntegerField(null=True)
    upload_date = DateTimeField(null=True)
    qq_num = CharField(null=True)
    qq_group = CharField(null=True)
    qq_name = CharField(null=True)
    created_date = DateTimeField(null=True)


def check_table():
    if not db.table_exists("download"):
        db.create_tables([Download])


def insert_download(info):
    check_table()
    result = Download.create(id=info['id'], url=info['url'], title=info['title'], type=info['type'], coin=info['coin'],
                             stars=info['stars'], size=info['size'], tag=info['tag'], description=info['description'],
                             filename=info['filename'], upload_date=info['upload_date'], qq_num=info['qq_num'],
                             qq_name=info['qq_name'], qq_group=info['qq_group'], created_date=datetime.datetime.now())
    return result


def get_download(_id):
    check_table()
    return Download.select().where(Download.id == _id).first()


def exist_download(_id):
    return get_download(_id) is not None


def find_all(keyword, start_index=0, count=10):
    check_table()
    if keyword == '':
        return Download.select().limit(count).offset(start_index)
    return Download.select().where(Download.title.contains(keyword)).limit(count).offset(start_index)


def count_all(keyword):
    check_table()
    if keyword == '':
        return Download.select().count()
    return Download.select().where(Download.title.contains(keyword)).count()


def count_today(qq_num, qq_group):
    check_table()
    return Download.select().where((Download.qq_num == qq_num) & (Download.qq_group == qq_group)
                                   & (Download.created_date.year == datetime.datetime.now().year)
                                   & (Download.created_date.month == datetime.datetime.now().month)
                                   & (Download.created_date.day == datetime.datetime.now().day)).count()


def count_weekly(qq_num, qq_group):
    check_table()
    return Download.select().where((Download.qq_num == qq_num) & (Download.qq_group == qq_group)
                                   & (Download.created_date.year == datetime.datetime.now().year)
                                   & (datetime.datetime(Download.created_date.year, Download.created_date.month,
                                                        Download.created_date.day, 0, 0, 0).isocalendar()[1] ==
                                      datetime.datetime.now().isocalendar()[1])).count()


def count_month(qq_num, qq_group):
    check_table()
    return Download.select().where((Download.qq_num == qq_num) & (Download.qq_group == qq_group)
                                   & (Download.created_date.year == datetime.datetime.now().year)
                                   & (Download.created_date.month == datetime.datetime.now().month)).count()


def rank_qq(start_index=0, count=10):
    check_table()
    _all = Download.select()
    info = {}
    for a in _all:
        if a.qq_num in info:
            info[a.qq_num]['name'] = a.qq_name
            info[a.qq_num]['count'] += 1
            info[a.qq_num]['coin'] += a.coin
        else:
            info[a.qq_num] = {}
            info[a.qq_num]['name'] = a.qq_name
            info[a.qq_num]['qq'] = a.qq_num
            info[a.qq_num]['count'] = 1
            info[a.qq_num]['coin'] = a.coin
    info = sorted(info.items(), key=lambda d: d[1]['count'], reverse=True)
    result = []
    index = 0
    for fo in info:
        if start_index <= index < start_index + count:
            result.append((fo[0], fo[1]))
        index += 1
    return result

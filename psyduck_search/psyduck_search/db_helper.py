from peewee import *
import datetime
import os

db_path = os.path.join(os.path.dirname(__file__), 'psyduck_search.db')
db = SqliteDatabase(db_path)


class Resource(Model):
    class Meta:
        database = db

    id = CharField(primary_key=True, unique=True)
    url = CharField(null=True)
    title = CharField(null=True)
    description = CharField(null=True)
    stars = IntegerField(null=True)
    upload_date = DateTimeField(null=True)
    created_date = DateTimeField(null=True)


class Log(Model):
    class Meta:
        database = db

    uuid = CharField(null=True)
    keyword = CharField(null=True)
    pages = CharField(null=True)
    result = CharField(null=True)
    cost = CharField(null=True)
    created_date = DateTimeField(null=True)


def check_table():
    if not db.table_exists("resource"):
        db.create_tables([Resource])
    if not db.table_exists("log"):
        db.create_tables([Log])


def insert_log(info):
    check_table()
    result = Log.create(uuid=info['uuid'], keyword=info['keyword'], pages=info['pages'], result=info['result'],
                        cost=info['cost'], created_date=datetime.datetime.now())
    return result


def insert_download(info):
    check_table()
    result = Resource.create(id=info['id'], url=info['url'], title=info['title'], stars=info['stars'],
                             description=info['description'], upload_date=info['upload_date'],
                             created_date=datetime.datetime.now())
    return result


def get_download(_id):
    check_table()
    return Resource.select().where(Resource.id == _id).first()


def exist_download(_id):
    return get_download(_id) is not None


def find_download(keyword='', start_index=0, count=10):
    check_table()
    if keyword == '':
        return Resource.select().order_by(-Resource.created_date).offset(start_index).limit(count)
    return Resource.select().where(Resource.title.contains(keyword)).order_by(-Resource.created_date).offset(
        start_index).limit(count)


def count_download(keyword=''):
    check_table()
    if keyword == '':
        return Resource.select().count()
    return Resource.select().where(Resource.title.contains(keyword)).count()

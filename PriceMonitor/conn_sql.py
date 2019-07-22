#!/usr/bin/env python3
# coding=utf-8
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from PriceMonitor.create_db import Base, User, Monitor
import datetime
from PriceMonitor.CONFIG import UPDATE_TIME

#操作数据库类
class Sql(object):

    # 连接根目录下的db_demo.db数据库，echo为显示日志
    engine = create_engine('sqlite:///db_demo.db', echo=True)
    # engine = create_engine('mysql+pymysql://root:root@localhost/pricemonitor?charset=utf8&autocommit=true')

    Base.metadata.bind = engine
    #建立对话
    DBSession = sessionmaker(bind=engine)
    session = DBSession()

    # 调用这个方法时需要参数：user_name,email_address
    def write_user(self, user_name, email_address):
        # 实例化User类
        new_user = User(user_name=user_name, email=email_address)
        self.session.add(new_user)
        self.session.commit()

    #调用这个方法时需要参数：item_info(list)
    def write_item(self, item_info):  # item_id, user_price, user_id
        #获取当前时间
        time_now = datetime.datetime.now()
        #实例化Moinitor类
        new_item = Monitor(item_id=item_info[0], user_price=item_info[1], user_id=item_info[2], status=1, add_time=time_now, update_time=time_now)
        #将new_item添加到数据库。
        self.session.add(new_item)
        self.session.commit()

    def read_all_not_updated_item(self):
        #获取当前时间
        time_now = datetime.datetime.now()
        #创建一个空的列表，名字为：items_need
        items_need = []
        # 获取Monitor表的所有内容，items_all(list)
        items_all = self.session.query(Monitor).all()
        
        #循环取出list(items_all)的内容。
        for item_all in items_all:
            #创建一个空的集合
            item_need = {}
            
            #如果 item_all.status ==1
            if item_all.status == 1:
                # 时间差，当前时间天数减去上传到数据库时间的天数乘以86400加，当前时间秒数减去，上传到数据库秒数。
                time_delta = (time_now - item_all.update_time).days * 86400 + (time_now - item_all.update_time).seconds
                
                logging.info('%s\'s time delta: %s', item_all.item_id, time_delta)
                #如果 time_delta小于等于 600
                if time_delta >= UPDATE_TIME:
                    #将 item_all.column_id，item_all.item_id存入 item_need列表中。
                    item_need['column_id'] = item_all.column_id
                    item_need['item_id'] = item_all.item_id
                    #将 item_need,存入，items_need集合中。
                    items_need.append(item_need)
        return items_need
    # update_item_name,需要传入参数，column_id,item_name
    def update_item_name(self, column_id, item_name):
        #获取monitor表中 column_id.
        update_item = self.session.query(Monitor).get(column_id)
        update_item.item_name = item_name
        self.session.commit()

    def update_item_price(self, column_id, item_price):
        #获取当前时间
        time_now = datetime.datetime.now()
        update_item = self.session.query(Monitor).get(column_id)
        
        if update_item.item_price and update_item.item_price != item_price:  # if new price
            update_item.last_price = update_item.item_price
            update_item.discount = round(float(item_price) / float(update_item.last_price), 2)  # round(,2) set to 0.01
        update_item.item_price = item_price
        update_item.update_time = time_now
        self.session.commit()

    def update_item_subtitle(self, column_id, subtitle):
        update_item = self.session.query(Monitor).get(column_id)
        update_item.subtitle = subtitle
        self.session.commit()

    def update_item_plus_price(self, column_id, plus_price):
        update_item = self.session.query(Monitor).get(column_id)
        update_item.plus_price = plus_price
        self.session.commit()

    def update_item_max_price(self, column_id, highest_price):
        update_item = self.session.query(Monitor).get(column_id)
        update_item.highest_price = highest_price
        self.session.commit()

    def update_item_min_price(self, column_id, lowest_price):
        update_item = self.session.query(Monitor).get(column_id)
        update_item.lowest_price = lowest_price
        self.session.commit()

    def update_status(self, column_id):
        update_item = self.session.query(Monitor).get(column_id)
        update_item.status = 0
        self.session.commit()

    def check_item_need_to_remind(self):
        # items_alert = {column_id, item_id, user_price, item_price, name, email}
        items_alert = []
        items = self.session.query(Monitor).all()
        for item in items:
            item_alert = {}
            if item.status == 1 and item.user_price:
                if float(item.user_price) > float(item.item_price):
                    user = self.session.query(User).filter_by(column_id=item.user_id)
                    item_alert['email'] = user[0].email
                    item_alert['name'] = item.item_name
                    item_alert['item_price'] = item.item_price
                    item_alert['user_price'] = item.user_price
                    item_alert['item_id'] = item.item_id
                    item_alert['column_id'] = item.column_id
                    items_alert.append(item_alert)
        return items_alert


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    sql = Sql()

    # add user named 'test'
    sql.write_user('test', '1712340552@qq.com')

    # add test item
    # item_id, user_price, user_id
    sql.write_item(['100005857580', '2000', '1'])
    sql.write_item(['7437690','200','2'])

    # read all items needed update
    # print(sql.read_all_not_updated_item())


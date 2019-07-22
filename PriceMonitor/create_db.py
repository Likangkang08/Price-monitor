#!/usr/bin/env python3
# coding=utf-8
# import logging
from sqlalchemy import create_engine, Column, ForeignKey
from sqlalchemy import Integer, String, DateTime, Numeric, Boolean, BIGINT
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

#declarative_base() 创建了一个 BaseModel 类，这个类的子类可以自动与一个表关联。
Base = declarative_base()

#定义映射类User，继承创建的基本映射类Base
class User(Base):
    #指定本类映射到user表
    __tablename__ = 'user'
    #定义colum_id ,映射到colum_id,字段，为整数，主健
    column_id = Column(Integer, primary_key=True, autoincrement=True)
    #定义user_name映射到user_name字段，为字符串。
    user_name = Column(String(32), nullable=False, unique=True)
    email = Column(String(64), nullable=False, unique=True)

#定义映射类Monitor，继承创建的基本映射类Base
class Monitor(Base):
    #指定本类映射到tablename表
    __tablename__ = 'monitor'
    column_id = Column(Integer, primary_key=True, autoincrement=True)
    item_id = Column(BIGINT, nullable=False)
    item_name = Column(String(128))
    item_price = Column(String(32))
    user_price = Column(String(32))
    discount = Column(String(32))
    lowest_price = Column(String(32))
    highest_price = Column(String(32))
    last_price = Column(String(32))
    plus_price = Column(String(32))
    subtitle = Column(String(128))
    user_id = Column(Integer, ForeignKey('user.column_id'))
    note = Column(String(128))
    update_time = Column(DateTime)
    add_time = Column(DateTime)
    status = Column(Boolean, nullable=False)
    user = relationship(User)

if __name__ == '__main__':
    # logging.basicConfig(level=logging.DEBUG)
    engine = create_engine('sqlite:///db_demo.db', echo=True)
    # engine = create_engine('mysql+pymysql://root:root@localhost/pricemonitor?charset=utf8', echo=True)
    
    #BaseModel.metadata.create_all(engine) 会找到 BaseModel 的所有子类，并在数据库中建立这些表；drop_all() 则是删除这些表。
    Base.metadata.create_all(engine)

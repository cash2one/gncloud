# -*- coding: utf-8 -*-
import calendar
from datetime import *
from dateutil.relativedelta import relativedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ProcessPoolExecutor
from sqlalchemy import or_

from db.models import *
from db.models import GnInstanceStatus, GnUsers, GnTeam
from util.config import config


__author__ = 'nhcho'


class Invoice:
    def __init__(self, db_session=None):
        self.sql_session = db_session
        self.Invoice_sched = None
        self.scheduler = None

    def run(self):
        executors = {
            'default': {'type': 'threadpool', 'max_workers': 20},
            'processpool': ProcessPoolExecutor(max_workers=5)
        }
        job_defaults = { 'coalesce': False, 'max_instances': 3 }
        self.scheduler = BackgroundScheduler()
        self.scheduler.configure(executors=executors, job_defaults=job_defaults)
        self.scheduler.add_job(lambda : self.invoice_calc(), trigger='cron', day=1, hour=1)
        self.scheduler.start()

    def invoice_calc(self):
        sql_session = self.sql_session
        # validation date about create_time(start) to delete_time(delete)
        # if vm isn't deleted, delete_time is null or None. In this case, we will send invoice.
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        evalue_date = (datetime.datetime.now() - relativedelta(months=1)).strftime("%Y-%m-%d")
        year = int(evalue_date.split('-')[0])
        month = int(evalue_date.split('-')[1])
        last_day = calendar.monthrange(year,month)[1]

        start_day = (datetime.datetime.now() - relativedelta(months=1)).strftime("%Y-%m-01 00:00:00")
        end_day = (datetime.datetime.now() - relativedelta(months=1)).replace(day=last_day).strftime("%Y-%m-%d 23:59:59")
        print 'start day = %s, end day = %s' % (start_day, end_day)

        start_date = (datetime.datetime.now() - relativedelta(months=1)).replace(day=1, hour=0, minute=0, second=0)
        end_date = (datetime.datetime.now() - relativedelta(months=1)).replace(day=last_day, hour=23, minute=59, second=59)

        status = sql_session.query(GnInstanceStatus) \
            .filter(GnInstanceStatus.create_time <= end_day) \
            .filter(or_(GnInstanceStatus.delete_time == None, GnInstanceStatus.delete_time >= start_day)) \
            .order_by(GnInstanceStatus.team_code, GnInstanceStatus.author_id).all()
        if len(status) == 0:
            sql_session.commit()
            print 'No data'
            return

        all_text = None
        version = config.INVOICE_VER
        team_name = None
        team_code = None
        total_price = 0
        user_total = 0
        json_text = None
        day_count = 0;
        one_vm_price = 0;
        author_id = None
        author_text = None
        instance_list = None

        print ('year : %s, months : %s') % (year, month)

        for stat in status:
            team = sql_session.query(GnTeam).filter(GnTeam.team_code == stat.team_code).first()

            count_start_day = None
            count_end_day = None
            if stat.create_time > start_date:
                count_start_day = stat.create_time
            else:
                count_start_day = start_date

            if stat.delete_time is None or stat.delete_time > end_date:
                count_end_day = end_date
            elif stat.delete_time < end_date:
                count_end_day = stat.delete_time

            delta = count_end_day - count_start_day
            if stat.price_type == 'D':
                # add one day
                day_hour_count = delta.days + 1
            elif stat.price_type == 'H':
                day_hour_count = int(delta.total_seconds()/3600) + 1



            one_vm_price = day_hour_count * stat.price
            total_price += one_vm_price

            instance = " {'vm_id':'%s', 'price type': '%s', 'unit price':'%s', 'used':'%d', 'total price':'%d'}" \
                            %(stat.vm_id, stat.price_type, stat.price, day_hour_count, one_vm_price)

            if author_id != stat.author_id and author_id is not None:
                author_text = "{'user_id': '%s', 'instance_list': [%s] }" % (author_id, instance_list)
                if json_text is None:
                    json_text = "%s" % (author_text)
                else:
                    json_text = "%s,%s" % (json_text, author_text)
                author_id = stat.author_id
                author_text=None
                instance_list = instance
            elif author_id is None:
                author_id = stat.author_id
                instance_list = instance
            else:
                if instance_list is None:
                    instance_list = instance
                else:
                    instance_list = '%s,%s' % (instance_list, instance)

            if team.team_code != team_code and team_code is not None:
                all_text = ("{'version':'%s', 'year':'%s', 'month':'%s', 'calc day':'%s', 'team':'%s', 'team price':'%d', 'each user':[%s] }") \
                           % (version, year, month, today, team_code, total_price, json_text)
                invoid_result = GnInvoiceResult(year, month, team_code, all_text)
                sql_session.add(invoid_result)
                sql_session.commit()

                team_code = team.team_code
                team_name = team.team_name
                day_count = 0;
                one_vm_price = 0;
                total_price = 0;
                json_text = None
                print(all_text)
            elif team_code is None:
                team_code = team.team_code
                team_name = team.team_name
                author_id = stat.author_id
                instance = None

        author_text = "{'user_id': '%s', 'instance_list': [%s] }" % (author_id, instance_list)
        if json_text is None:
            json_text = "%s" % (author_text)
        else:
            json_text = "%s,%s" % (json_text, author_text)

        all_text = ("{'version':'%s', 'year':'%s', 'month':'%s', 'calc day':'%s', 'team':'%s', 'team price':'%d', 'each user':[%s] }") \
                   % (version, year, month, today, team_code, total_price, json_text)
        invoid_result = GnInvoiceResult(year, month, team_code, all_text)
        sql_session.add(invoid_result)
        sql_session.commit()

        print(all_text)
        sql_session.commit()
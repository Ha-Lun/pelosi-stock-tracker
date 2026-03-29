from peewee import Model,TextField, CharField, DateField, IntegerField, FloatField, DateTimeField
from datetime import datetime
from .db import get_database


class Trade(Model):
    ticker = CharField()
    issuer_name = CharField(null=True)
    transaction_type = CharField()
    transaction_date = DateField()
    disclosure_date = DateField()
    amount_range = CharField(null=True)
    amount_min = IntegerField(null=True)
    amount_max = IntegerField(null=True)
    price_at_trade = FloatField(null=True)
    created_at = DateTimeField(default=datetime.now)

    class Meta:
        database = get_database()
        table_name = "trades"


class Price(Model):
    ticker = CharField()
    date = DateField()
    open = FloatField()
    high = FloatField()
    low = FloatField()
    close = FloatField()
    volume = FloatField()

    class Meta:
        database = get_database()
        table_name = "prices"


class FetchLog(Model):
    fetch_date = DateTimeField(default=datetime.now)
    source = CharField()
    status = CharField()
    records_fetched = IntegerField(default=0)
    error_message = TextField(null=True)

    class Meta:
        database = get_database()
        table_name = "fetch_logs"



def insert_trade(trade_data):
    # Check for duplicates
    existing = Trade.get_or_none(
        (Trade.ticker == trade_data['ticker']) &
        (Trade.transaction_date == trade_data['transaction_date']) &
        (Trade.transaction_type == trade_data['transaction_type'])
    )

    if existing:
        return existing # If already exists, don't insert
    
    return Trade.create(**trade_data)

def get_trades(ticker = None, transaction_type = None, start_date = None, end_date = None):
    query = Trade.select()
    if ticker:
        query = query.where(Trade.ticker == ticker)
    if transaction_type:
        query = query.where(Trade.transaction_type == transaction_type)
    if start_date:
        query = query.where(Trade.transaction_date >= start_date)
    if end_date:
        query = query.where(Trade.transaction_date <= end_date)
    return list(query)

def insert_prices(price_list):
    if not price_list:
        return 0
    Price.insert_many(price_list).execute()
    return len(price_list)

def get_latest_fetch_date(source = None):
    query = FetchLog.select().where(FetchLog.status == "success")

    if source:
        query = query.where(FetchLog.source == source)
    
    last_log = query.order_by(FetchLog.fetch_date.desc()).get_or_none()

    if last_log:
        return last_log.fetch_date
    return None

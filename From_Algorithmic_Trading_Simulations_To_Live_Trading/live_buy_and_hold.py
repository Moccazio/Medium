# Run this file in terminal or interactive window
import os
os.environ['ZIPLINE_ROOT'] = os.path.join(os.getcwd(), '.zipline')
import yaml
import pytz
import pandas as pd
from datetime import datetime
import pandas_datareader.data as yahoo_reader
import warnings
warnings.filterwarnings('ignore')
from zipline.utils.calendars import get_calendar
from zipline.api import order_target, symbol
from zipline.data import bundles
from zipline import run_algorithm
from zipline.gens.brokers.alpaca_broker import ALPACABroker

def get_benchmark(symbol=None, start=None, end=None):
    bm = yahoo_reader.DataReader(symbol,
                                 'yahoo',
                                 pd.Timestamp(start),
                                 pd.Timestamp(end))['Close']
    bm.index = bm.index.tz_localize('UTC')
    return bm.pct_change(periods=1).fillna(0)


def initialize(context):
    pass


def handle_data(context, data):
    order_target(context.equity, 10)


def before_trading_start(context, data):
    context.equity = symbol("ASML")


if __name__ == '__main__':
    bundle_name = 'alpaca_api'
    bundle_data = bundles.load(bundle_name)

    with open("./alpaca.yaml", mode='r') as f:
        o = yaml.safe_load(f)
        os.environ["APCA_API_KEY_ID"] = o["key_id"]
        os.environ["APCA_API_SECRET_KEY"] = o["secret"]
        os.environ["APCA_API_BASE_URL"] = o["base_url"]
    broker = ALPACABroker()

    # Set the trading calendar
    trading_calendar = get_calendar('NYSE')

    start = pd.Timestamp(datetime(2021, 6, 4, tzinfo=pytz.UTC))
    end = pd.Timestamp.utcnow()

    run_algorithm(start=start,
                  end=end,
                  initialize=initialize,
                  handle_data=handle_data,
                  capital_base=10000,
                  benchmark_returns=get_benchmark(symbol="SPY",
                                                  start=start.date().isoformat(),
                                                  end=end.date().isoformat()),
                  bundle='alpaca_api',
                  broker=broker,
                  state_filename="./demo.state",
                  trading_calendar=trading_calendar,
                  before_trading_start=before_trading_start,
                  data_frequency='daily'
                  )        
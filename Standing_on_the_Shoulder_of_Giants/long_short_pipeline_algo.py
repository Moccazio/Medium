## Long Short
from pylivetrader.api import *
from pipeline_live.data.alpaca.factors import SimpleMovingAverage, AverageDollarVolume
from pipeline_live.data.alpaca.pricing import USEquityPricing
from zipline.pipeline import Pipeline
from logbook import Logger, StreamHandler
import sys
StreamHandler(sys.stdout).push_application()
log = Logger(__name__)
import logging
logging.basicConfig(filename='errlog.log',level=logging.WARNING,
                    format='%(asctime)s:%(levelname)s:%(message)s',)

def initialize(context):
    # Every day we rebalance 20 min before market close
    schedule_function(rebalance, date_rules.every_day(),time_rules.market_close(hours=0, minutes=20))
    my_pipe = make_pipeline()
    context.attach_pipeline(my_pipe,'my_pipeline')

def rebalance(context,data):
    for security in list(context.portfolio.positions.keys()):
            if security not in context.longs and security not in context.shorts and data.can_trade(security):
                try:
                    order_target_percent(security,0)
                except:
                    pass
    for security in context.longs:
        if data.can_trade(security):
            try:
                order_target_percent(security,context.long_weight)
            except:
                pass
    for security in context.shorts:
        if data.can_trade(security):
            try:
                order_target_percent(security, context.short_weight)
            except:
                pass

def compute_weights(context):
    if len(context.longs)==0:
        long_weight = 0
    else:
        long_weight = 0.5 / len(context.longs)

    if len(context.shorts)==0:
        short_weight = 0
    else:
        short_weight = 0.5 / len(context.shorts)
    return (long_weight, short_weight)

def before_trading_start(context,data):
    context.output = context.pipeline_output('my_pipeline')
    context.longs = context.output[context.output['longs']].index.tolist()
    context.shorts = context.output[context.output['shorts']].index.tolist()
    context.long_weight,context.short_weight = compute_weights(context)

def make_pipeline():
    # Dollar volume (30 Days) grab the info
    dollar_volume = AverageDollarVolume(window_length=30)
    # Grab the top 5% in avg dollar volume
    high_dollar_volume = dollar_volume.percentile_between(95,100)
    # 10 day mean close
    mean_10 = SimpleMovingAverage(inputs=[USEquityPricing.close],window_length=10,mask=high_dollar_volume)
    # 30 day mean close
    mean_30 = SimpleMovingAverage(inputs=[USEquityPricing.close],window_length=30,mask=high_dollar_volume)
    # Percent difference
    percent_difference = (mean_10-mean_30)/mean_30
    # List of shorts
    shorts = percent_difference < 0
    # List of longs
    longs = percent_difference > 0
    # Final mask/filter for anything in shorts or longs
    securities_to_trade = (shorts | longs)
    # Return pipeline
    return Pipeline(columns={
        'longs':longs,
        'shorts':shorts,
        'perc_diff':percent_difference
    },screen=securities_to_trade)

def handle_data(context, data):
    pass
import asyncio
from ib_insync import util
from logbook import ERROR, INFO, WARNING

from backtester import IB, DataSourceManager, Market
from logger import logger
from trader import CsvBlotter
from datastore import Store, ArcticStore
from saver import PickleSaver
from trader import Manager
from portfolio import FixedPortfolio, AdjustedPortfolio
from strategy import candles


log = logger(__file__[:-3], ERROR, ERROR)

start_date = '20180601'
end_date = '20191231'
cash = 120000
store = ArcticStore('TRADES_30_secs')
#store = Store()
source = DataSourceManager(store, start_date, end_date)
ib = IB(source, mode='db_only', index=-2)  # mode is: 'db_only' or 'use_ib'

util.logToConsole()
asyncio.get_event_loop().set_debug(True)

blotter = CsvBlotter(save_to_file=False, filename='backtest', path='backtests',
                     note=f'_{start_date}_{end_date}')
saver = PickleSaver('notebooks/freeze/backtest')
manager = Manager(ib, candles, FixedPortfolio, blotter=blotter,
                  saver=saver, sl_type='trailing',
                  contract_fields=['contract', 'micro_contract'],
                  portfolio_params={'target_vol': .5})
market = Market(cash, manager, reboot=False)
ib.run()
blotter.save()
manager.freeze()

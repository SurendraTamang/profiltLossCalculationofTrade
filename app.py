import pandas as pd
from collections import defaultdict, deque
from datetime import datetime

class Trade:
    """A class to represent a trade, which includes size, price, date, and fee."""
    def __init__(self, size, price, date, fee):
        self.size = size
        self.price = price
        self.date = date
        self.fee = fee

def convert_timestamp_to_date(timestamp):
    """A function to convert timestamp to date."""
    return datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%S.%fZ').date()

def calculate_daily_profit_or_loss(df):
    """A function to calculate daily profit or loss based on input dataframe."""
    assets = defaultdict(lambda: defaultdict(deque))  # 'asset' -> 'BUY'/'SELL' -> deque of Trade
    daily_profit_loss = defaultdict(lambda: defaultdict(float))  # 'date' -> 'asset' -> PnL

    for _, row in df.iterrows():
        date = convert_timestamp_to_date(row['createdAt'])
        side = row['side']
        market = row['market']
        price = row['price']
        size = row['size']

        # Open a new position or close an existing one
        if side == 'BUY':
            if assets[market]['SELL']:  # If there's a short position, close it
                trade = assets[market]['SELL'].popleft()
                pnl = (trade.price - price) * size - trade.fee - row['fee']  # PnL = (Sell price - Buy price) * size - Sell fee - Buy fee
                daily_profit_loss[date][market] += pnl  # Associate PnL with the closing position's date
            else:  # Open a long position
                assets[market]['BUY'].append(Trade(size, price, date, row['fee']))
        else:  # 'SELL'
            if assets[market]['BUY']:  # If there's a long position, close it
                trade = assets[market]['BUY'].popleft()
                pnl = (price - trade.price) * size - trade.fee - row['fee']  # PnL = (Sell price - Buy price) * size - Buy fee - Sell fee
                daily_profit_loss[date][market] += pnl  # Associate PnL with the closing position's date
            else:  # Open a short position
                assets[market]['SELL'].append(Trade(size, price, date, row['fee']))

    return daily_profit_loss


if __name__ == '__main__':
    df = pd.read_csv('upwork trades.csv')
    df = df.sort_values(by='createdAt')
    daily_profit_loss = calculate_daily_profit_or_loss(df)

    for date in sorted(daily_profit_loss.keys()):
        for market in daily_profit_loss[date]:
            print(f"Date: {date}, Asset: {market}, Profit/Loss: {daily_profit_loss[date][market]}")

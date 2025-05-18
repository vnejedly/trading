import pandas as pd


def moving_average(df: pd.DataFrame, column: str, period: int): 
    df[f'ma_{column}_{period}'] = df[column].rolling(window=period).mean()
    # df.dropna(inplace=True)
    # df.reset_index(inplace=True, drop=True)


def bollinger_bands(df: pd.DataFrame, price_type: str, period: int, std: float):
    def price(phase: str) -> str:
        return f'{price_type}_{phase}'
    
    typical_price = (df[price('h')] + df[price('l')] + df[price('c')]) / 3
    std_dev = typical_price.rolling(window=period).std()
    ma = typical_price.rolling(window=period).mean()

    df[f'bb_{price_type}_{period}_ma'] = ma
    df[f'bb_{price_type}_{period}_up'] = ma + (std_dev * std)
    df[f'bb_{price_type}_{period}_lo'] = ma - (std_dev * std)

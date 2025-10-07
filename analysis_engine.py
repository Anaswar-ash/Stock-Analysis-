
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from statsmodels.tsa.arima.model import ARIMA

def get_stock_data(ticker_symbol):
    """
    Fetches stock data from Yahoo Finance.
    """
    try:
        ticker = yf.Ticker(ticker_symbol)
        info = ticker.info
        hist = ticker.history(period="5y")
        if hist.empty:
            return None, None
        return info, hist
    except Exception as e:
        print(f"Error fetching stock data: {e}")
        return None, None

def calculate_technical_indicators(df):
    """
    Calculates technical indicators for the stock data.
    """
    df['SMA50'] = df['Close'].rolling(window=50).mean()
    df['SMA200'] = df['Close'].rolling(window=200).mean()
    return df

def forecast_stock_price(df, days_to_predict=30):
    """
    Forecasts the stock price using an ARIMA model.
    """
    model = ARIMA(df['Close'], order=(5,1,0))
    model_fit = model.fit()
    forecast = model_fit.forecast(steps=days_to_predict)
    forecast_dates = pd.to_datetime(df.index[-1]) + pd.to_timedelta(range(1, days_to_predict + 1), unit='D')
    return forecast, forecast_dates

def create_plot(df, forecast, forecast_dates, ticker_symbol):
    """
    Creates an interactive plot of the stock data and forecast.
    """
    fig = go.Figure()

    fig.add_trace(go.Scatter(x=df.index, y=df['Close'], name='Close', line=dict(color='blue')))
    fig.add_trace(go.Scatter(x=df.index, y=df['SMA50'], name='50-Day SMA', line=dict(color='yellow', dash='dash')))
    fig.add_trace(go.Scatter(x=df.index, y=df['SMA200'], name='200-Day SMA', line=dict(color='red', dash='dash')))
    fig.add_trace(go.Scatter(x=forecast_dates, y=forecast, name='Forecast', line=dict(color='green', dash='dot')))

    fig.update_layout(
        title=f'{ticker_symbol} Stock Price Analysis',
        xaxis_title='Date',
        yaxis_title='Price (USD)',
        template='plotly_dark',
        xaxis_rangeslider_visible=True
    )

    return fig.to_html(full_html=False)

def run_analysis(ticker_symbol):
    """
    Runs the full stock analysis.
    """
    info, hist = get_stock_data(ticker_symbol)
    if info is None:
        return {'error': f"Invalid ticker symbol or no data found for {ticker_symbol}."}

    hist = calculate_technical_indicators(hist)
    forecast, forecast_dates = forecast_stock_price(hist)
    plot_html = create_plot(hist, forecast, forecast_dates, ticker_symbol)

    return {
        'info': info,
        'plot_html': plot_html,
        'error': None
    }

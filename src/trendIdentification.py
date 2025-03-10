import pandas as pd
import numpy as np
from visualize import visualizeChart
import matplotlib.pyplot as plt

def linearRegression(data, keyValue="networkDiameter", keyName="Network Diameter"):
    from sklearn.linear_model import LinearRegression
    data = data.reset_index()
    data["dateOrdinal"] = data["date"].map(pd.Timestamp.toordinal)
    x = data[["dateOrdinal"]]
    y = data[keyValue].values
    model = LinearRegression()
    model.fit(x, y)
    last_date = data["date"].max()
    future_dates = pd.date_range(start=last_date, periods=105, freq="W-MON")[1:]
    future_dates_ord = future_dates.map(pd.Timestamp.toordinal).values.reshape(-1, 1)
    predictions = model.predict(future_dates_ord)
    # visualizeChart(data, "date", "networkDiameter", "Date", "Network Diameter", "Network Diameter Over Time")


    print(predictions)
    # Create combined visualization
    fig, ax = plt.subplots(figsize=(12, 7))

    # Plot original data
    ax.plot(data["date"], data[keyValue], 'o-', color='blue', label='Historical Data')

    # Plot predictions
    ax.plot(future_dates, predictions, '--', color='red', label='Predictions')

    # Add shading for prediction interval (simple approach)
    y_mean = np.mean(y)
    y_std = np.std(y)
    ax.fill_between(future_dates,
                    predictions - y_std,
                    predictions + y_std,
                    color='red', alpha=0.2,
                    label='Prediction Interval (±1σ)')

    # Add labels and title
    ax.set_xlabel("Date")
    ax.set_ylabel(keyValue)
    ax.set_title(f"{keyName}: Historical Data and Predictions")
    ax.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Add zoom functionality
    def zoom_fun(event):
        base_scale = 1.1
        cur_ylim = ax.get_ylim()
        xdata = event.xdata
        ydata = event.ydata
        if xdata is None or ydata is None:
            return
        if event.button == 'up':
            scale_factor = 1 / base_scale
        elif event.button == 'down':
            scale_factor = base_scale
        else:
            scale_factor = 1
        new_height = (cur_ylim[1] - cur_ylim[0]) * scale_factor
        rely = (cur_ylim[1] - ydata) / (cur_ylim[1] - cur_ylim[0])
        ax.set_ylim([ydata - new_height * (1 - rely), ydata + new_height * rely])
        plt.draw()

    fig.canvas.mpl_connect('scroll_event', zoom_fun)
    plt.show()

def ARIMAForecast(data, predict_weeks=100, keyValue="", keyName="Network Diameter", verbose = False):
    """
        Perform ARIMA modeling on time series data and visualize predictions.
        """
    from statsmodels.tsa.arima.model import ARIMA
    from statsmodels.tsa.stattools import adfuller

    # Reset index to work with the date column
    data = data.reset_index() if 'date' not in data.columns else data

    # Ensure date is datetime
    data['date'] = pd.to_datetime(data['date'])

    # Sort by date to ensure chronological order
    data = data.sort_values('date')

    # Set date as index with explicit weekly frequency
    data = data.set_index('date')

    # Resample to weekly frequency to handle any gaps
    time_series = data[keyValue].asfreq('W-MON')

    # Forward fill any missing values
    time_series = time_series.ffill()

    # Check stationarity if verbose
    if verbose:
        result = adfuller(time_series.dropna())
        print(f'ADF Statistic: {result[0]:.6f}')
        print(f'p-value: {result[1]:.6f}')
        print('Critical Values:')
        for key, value in result[4].items():
            print(f'\t{key}: {value:.6f}')

    # Fit ARIMA model (p,d,q) = (1,1,1) as default
    model = ARIMA(time_series, order=(5, 2, 5), freq="W-MON")
    model_fit = model.fit()
    if verbose:
        print(model_fit.summary())

    # Generate forecast
    last_date = time_series.index[-1]
    future_dates = pd.date_range(start=last_date, periods=predict_weeks + 1, freq="W-MON")[1:]
    forecast = model_fit.forecast(steps=predict_weeks)


    # Create visualization
    fig, ax = plt.subplots(figsize=(12, 7))

    # Plot original data
    ax.plot(time_series.index, time_series.values, 'o', color='blue', label='Historical Data')

    # Plot forecast
    ax.plot(future_dates, forecast, 'o', color='red', label='ARIMA Forecast')

    # Add prediction intervals
    forecast_std = np.std(time_series)

    # Add labels and title
    ax.set_xlabel("Date")
    ax.set_ylabel(keyName)
    ax.set_title(f"{keyName}: Historical Data and ARIMA Forecast")
    ax.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Add zoom functionality
    def zoom_fun(event):
        base_scale = 1.1
        cur_ylim = ax.get_ylim()
        xdata = event.xdata
        ydata = event.ydata
        if xdata is None or ydata is None:
            return
        if event.button == 'up':
            scale_factor = 1 / base_scale
        elif event.button == 'down':
            scale_factor = base_scale
        else:
            scale_factor = 1
        new_height = (cur_ylim[1] - cur_ylim[0]) * scale_factor
        rely = (cur_ylim[1] - ydata) / (cur_ylim[1] - cur_ylim[0])
        ax.set_ylim([ydata - new_height * (1 - rely), ydata + new_height * rely])
        plt.draw()

    fig.canvas.mpl_connect('scroll_event', zoom_fun)
    plt.show()

    return model_fit, forecast, future_dates


def trendIdentification(filename, verbose=False, method="linear", impute = False):
    data = pd.read_csv(filename)
    data["date"] = pd.to_datetime(data["date"])
    # Clean/impute missing weeks
    if impute:
       # Find rows where numVertices is 0
        zero_rows = data['numVertices'] == 0
        # Replace all values in those rows with NaN
        data.loc[zero_rows, :] = np.nan
        # Forward fill to impute missing values
        data.ffill(inplace=True)
    else: data = data[data['numVertices'] != 0].copy()
    # visualizeChart(data, "date", "networkDiameter", "Date", "Network Diameter", "Network Diameter Over Time")
    if method == "linear": linearRegression(data)
    elif method == "arima": ARIMAForecast(data, verbose=verbose)
    else:
        raise ValueError(f"Invalid method: {method}")


def main():
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument("-f", "--filename", help="Generates data from the file containing the given filename.")
    parser.add_argument("-v", "--verbose", help="Verbose output.", action="store_true")
    parser.add_argument("-m", "--method", help="Method to use to identify trends")
    parser.add_argument("-i", "--impute", help="Impute gaps", action="store_true")
    parser.add_argument("-p", "--plot", help="Plot trends", action="store_true")
    args = parser.parse_args()
    trendIdentification(args.filename, args.verbose, args.method, args.impute)

if __name__ == "__main__":
    main()
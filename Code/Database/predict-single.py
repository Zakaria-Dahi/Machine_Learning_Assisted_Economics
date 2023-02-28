import getopt
import sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM


from cleanData import get_reduced_database, Data

series = ["Alimentos y bebidas no alcohólicas. Índice.", "Bebidas alcohólicas y tabaco. Índice.",
          "Comunicaciones. Índice.", "De 1 a 2. Total de empresas. Total CNAE. Empresas.",
          "De 10 a 19. Total de empresas. Total CNAE. Empresas.",
          "De 100 a 199. Total de empresas. Total CNAE. Empresas.",
          "De 1000 a 4999. Total de empresas. Total CNAE. Empresas.",
          "De 20 a 49. Total de empresas. Total CNAE. Empresas.",
          "De 200 a 499. Total de empresas. Total CNAE. Empresas.",
          "De 3 a 5. Total de empresas. Total CNAE. Empresas.", "De 50 a 99. Total de empresas. Total CNAE. Empresas.",
          "De 500 a 999. Total de empresas. Total CNAE. Empresas.",
          "De 5000 o más asalariados. Total de empresas. Total CNAE. Empresas.",
          "De 6 a 9. Total de empresas. Total CNAE. Empresas.", "Enseñanza. Índice.", "Men Activity Percentage",
          "Men Employment Percentage", "Men Unemployment Percentage", "Men employment Percentage",
          "Ocio y cultura. Índice.", "Otros bienes y servicios. Índice.", "Restaurantes y hoteles. Índice.",
          "Sanidad. Índice.", "Sin asalariados. Total de empresas. Total CNAE. Empresas.",
          "Total. Total de empresas. Total CNAE. Empresas.", "Transporte. Índice.", "Vestido y calzado. Índice.",
          "Women Activity Percentage", "Women Employment  Percentage", "Women Unemployment  Percentage",
          "Women Unemployment Percentage", "Women employment Percentage", "Índice general. Variación mensual."]


def get_data(arguments):
    session = get_reduced_database()
    res = session.query(Data). \
        filter(Data.location_name == arguments["location"]). \
        filter(Data.serie_name == arguments["series"]). \
        order_by(Data.year.asc(), Data.period.asc()). \
        all()
    time = []
    data = []
    for r in res:
        data.append(r.value)
        time.append(f"{r.year}-{r.period}")

    if len(data) == 0:
        print("No values found!")
        sys.exit(0)

    df = pd.DataFrame(data, index=time, columns=[arguments["series"]])

    return df


def series_to_supervised(data, n_in=1, n_out=1, dropnan=True):
    n_vars = 1 if type(data) is list else data.shape[1]
    df = pd.DataFrame(data)
    cols, names = list(), list()
    # input sequence (t-n, ... t-1)
    for i in range(n_in, 0, -1):
        cols.append(df.shift(i))
        names += [('var%d(t-%d)' % (j + 1, i)) for j in range(n_vars)]
    # forecast sequence (t, t+1, ... t+n)
    for i in range(0, n_out):
        cols.append(df.shift(-i))
        if i == 0:
            names += [('var%d(t)' % (j + 1)) for j in range(n_vars)]
        else:
            names += [('var%d(t+%d)' % (j + 1, i)) for j in range(n_vars)]
    # put it all together
    agg = pd.concat(cols, axis=1)
    agg.columns = names
    # drop rows with NaN values
    if dropnan:
        agg.dropna(inplace=True)
    return agg


def modify_data(df):
    scaler = MinMaxScaler(feature_range=(0, 1))
    values = df.values.astype('float32')
    scaled_values = scaler.fit_transform(values)
    n_interval = 4
    df_reframed = series_to_supervised(scaled_values, n_interval, 1)
    return df_reframed, scaler


def _train(df_reframed, scaler, date_times):
    n_train_records = int(len(df_reframed.values) * .7)
    train = df_reframed.values[:n_train_records, :]
    test = df_reframed.values[n_train_records:, :]
    #print('Train shape:', train.shape)
    #print('Test shape:', test.shape)
    n_interval = 4
    n_features = 1
    test_date_times = date_times[n_train_records+n_interval:]
    n_obs = n_interval*n_features
    X_train, y_train = train[:, :n_obs], train[:, -1]
    X_test, y_test = test[:, :n_obs], test[:, -1]
    #print('X_train shape:', X_train.shape)
    #print('y_train shape:', y_train.shape)
    #print('\nX_test shape:', X_test.shape)
    #print('y_test shape:', y_test.shape)
    X_train = X_train.reshape((X_train.shape[0], n_interval, n_features))
    X_test = X_test.reshape((X_test.shape[0], n_interval, n_features))
    print('X_train shape:', X_train.shape)
    print('X_test shape:', X_test.shape)
    model = Sequential()
    model.add(LSTM(32, return_sequences=True, input_shape=(X_train.shape[1], X_train.shape[2])))
    model.add(LSTM(24, return_sequences=True))
    model.add(LSTM(12))
    model.add(Dense(1))
    model.compile(loss='mse', optimizer='adam')
    train_epochs = 50
    batch_size = 32
    validation_split = 0.3
    history = model.fit(X_train, y_train, epochs=train_epochs, batch_size=batch_size, validation_split=validation_split,
                        verbose=0, shuffle=False)
    yhat = model.predict(X_test, batch_size=batch_size)
    mse = mean_squared_error(y_test, yhat)
    rmse = np.sqrt(mse)
    print(f"RMSE: {rmse}")
    X_test = X_test.reshape((X_test.shape[0], n_interval * n_features))
    inv_yhat = np.concatenate((yhat, X_test[:, -1:]), axis=1)
    inv_yhat = scaler.inverse_transform(inv_yhat)
    inv_yhat = inv_yhat[:, 0]
    y_test = y_test.reshape((len(y_test), 1))
    inv_y = np.concatenate((y_test, X_test[:, -1:]), axis=1)
    inv_y = scaler.inverse_transform(inv_y)
    inv_y = inv_y[:, 0]
    """    test_date_times_desc = []
    for dt in date_times:
        cur = dt.split(' ')
        cur_t = cur[1].split(':')
        try:
            if cur[1] == '0:00':
                test_date_times_desc.append(cur[0])
            elif cur_t[1] == '00':
                test_date_times_desc.append(cur_t[0]+':'+cur_t[1])
            else:
                test_date_times_desc.append('')
        except:
            test_date_times_desc.append('')"""
    x_ticks_range = range(len(inv_y))
    x_axis_labels = test_date_times  # test_date_times_desc
    plt.figure(figsize=(16, 10))
    plt.plot(x_ticks_range, inv_y, label='actual')
    plt.plot(x_ticks_range, inv_yhat, label='predicted')
    plt.legend()
    plt.xticks(x_ticks_range, x_axis_labels, rotation=90)
    plt.ylabel('Serie')
    plt.savefig("file.png")

def main(args):
    df = get_data(args)
    print(df.head())
    date_times = df.index.values
    df_reframed, scaler = modify_data(df)
    print(df_reframed.head())
    _train(df_reframed, scaler, date_times)


def show_help():
    print("""Options:
    -h | --help \t\t\t This help
    -g | --global \t\t\t Global Min/Max values of value [False by default]
    -d | --show-date \t\t\t Show the date in the image [False by default]
    -y | --year <year> \t\t\t From 2003 to 2017 [2010 by default]
    -p | --period <period> \t\t From 0 to 11
    -l | --location <location> \t Name of the city
    -s | --series <series name> \t [Total. Total de empresas. Total CNAE. Empresas. by default]
    -o | --output <output file> \t [output.png by default]""")
    print("Data series available:")
    for s in series:
        print(f"\t{s}")


def parse_args(argv):
    arguments = {
        "year": 2010,
        "period": 0,
        "series": 'Total. Total de empresas. Total CNAE. Empresas.',
        "location": 'Albacete',
        "output": "output.png",
        "global": False,
        "show-date": False
    }
    try:
        opts, args = getopt.getopt(argv, "hy:p:s:o:l:dg",
                                   ["year=", "period=", "series=", "output=", "help", "location="])
    except getopt.GetoptError:
        show_help()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ['-h', "--help"]:
            show_help()
            sys.exit()
        elif opt in ("-y", "--year"):
            arguments["year"] = arg
        elif opt in ("-p", "--period"):
            arguments["period"] = arg
        elif opt in ("-s", "--series"):
            arguments["series"] = arg
        elif opt in ("-l", "--location"):
            arguments["location"] = arg
        elif opt in ("-o", "--output"):
            arguments["output"] = arg
        elif opt in ["-g", "--global"]:
            arguments["global"] = True
        elif opt in ["-d", "--show-date"]:
            arguments["show-date"] = True
    return arguments


if __name__ == "__main__":
    args = parse_args(sys.argv[1:])
    main(args)

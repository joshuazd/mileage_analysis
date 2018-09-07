from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file as oauth_file, client, tools
from matplotlib import pyplot as plt
from sklearn import linear_model
from sklearn.metrics import mean_squared_error
# from random import shuffle
import numpy as np
import sys
import datetime

SCOPES = 'https://www.googleapis.com/auth/spreadsheets.readonly'
SPREADSHEET_ID = '1x2Tmj_is1Rqp43LaTU8lHYl77qS3huiaiz9fWcfcJgA'
RANGE_NAME = 'Sheet1!A1:D'


def main(argv):
    print('Retrieving Data...', end='', flush=True)
    store = oauth_file.Storage('token.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('sheets', 'v4', http=creds.authorize(Http()))

    # Call the Sheets API
    result = service.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=RANGE_NAME).execute()
    values = result.get('values', [])
    if not values:
        print('No data found.')
    else:
        print('done!')

    headers = values[0]
    values = values[1:]

    # Build data array
    data = {}
    for value in values:
        if value[0] not in data:
            data[value[0]] = []
        entry = {}
        for index, field in enumerate(value[1:], 1):
            entry[headers[index]] = field
        data[value[0]] += [entry]

    if argv[1] == 'mvt':
        mileage_vs_ride_time(data)
    elif argv[1] == 'mvl':
        mileage_vs_ride_length(data)
    elif argv[1] == 'mot':
        mileage_over_time(data)
    elif argv[1] == 'ls':
        least_squares(data)


def least_squares(data):
    data = list(([float(r['Distance (mi)']), float(r['Length (min)']), day],
                float(r['MPG'])) for day in data for r in data[day])
    X, y = zip(*data)

    for x in X:
        month, day, year = x[2].split('-')
        date = datetime.date(int(year), int(month), int(day))
        x[2] = date.timetuple().tm_yday

    X_train, X_test = X[:-20], X[-20:]
    y_train, y_test = y[:-20], y[-20:]

    reg = linear_model.LinearRegression()
    reg.fit(X_train, y_train)
    y_pred = reg.predict(X_test)

    print('All features',
          mean_squared_error(y_test, y_pred),
          reg.score(X_test, y_test))

    dist_train = list(x_train[0] for x_train in X_train)
    dist_train = np.reshape(dist_train, (-1, 1))
    dist_test = list([x_test[0]] for x_test in X_test)
    dist_test = np.reshape(dist_test, (-1, 1))
    length_train = list(x_train[1] for x_train in X_train)
    length_train = np.reshape(length_train, (-1, 1))
    length_test = list(x_test[1] for x_test in X_test)
    length_test = np.reshape(length_test, (-1, 1))

    reg = linear_model.LinearRegression()
    reg.fit(dist_train, y_train)
    y_pred = reg.predict(dist_test)
    mse = mean_squared_error(y_test, y_pred)
    score = reg.score(dist_test, y_test)

    print('Distance', mse, score)

    plt.subplot(1, 2, 1)
    plt.scatter(dist_test, y_test, color='black')
    plt.plot(dist_test, y_pred, color='blue', linewidth=3)
    plt.title('Distance')
    plt.text(5, 30, 'score=%f' % score)

    reg = linear_model.LinearRegression()
    reg.fit(length_train, y_train)
    y_pred = reg.predict(length_test)
    mse = mean_squared_error(y_test, y_pred)
    score = reg.score(length_test, y_test)

    print('Length', mse, score)

    plt.subplot(1, 2, 2)
    plt.scatter(length_test, y_test, color='black')
    plt.plot(length_test, y_pred, color='blue', linewidth=3)
    plt.title('Length')
    plt.text(5, 30, 'score=%f' % score)
    plt.show()


def mileage_vs_ride_time(data):
    rides = [(float(r['Length (min)']), float(r['MPG']))
             for day in data.values() for r in day]
    time, mpg = zip(*rides)
    time = np.array(time)
    mpg = np.array(mpg)
    lin_fit = np.polyfit(time, mpg, 1)
    lin_fit_fn = np.poly1d(lin_fit)
    lm, lb = np.polyfit(np.log(time), mpg, 1)
    em, eb = np.polyfit(time, np.log(mpg), 1)
    plt.scatter(time, mpg)
    x = np.linspace(1, 40, 80)
    plt.plot(x, lin_fit_fn(x), '--k')
    plt.plot(x, lm*np.log(x)+lb, '-b')
    plt.plot(x, np.exp(eb+em*x), '-r')
    plt.show()


def mileage_vs_ride_length(data):
    rides = [(float(r['Distance (mi)']), float(r['MPG']))
             for day in data.values() for r in day]
    dist, mpg = zip(*rides)
    dist = np.array(dist)
    mpg = np.array(mpg)
    lin_fit = np.polyfit(dist, mpg, 1)
    lin_fit_fn = np.poly1d(lin_fit)
    lm, lb = np.polyfit(np.log(dist), mpg, 1)
    em, eb = np.polyfit(dist, np.log(mpg), 1)
    plt.scatter(dist, mpg)
    x = np.linspace(1, 15)
    plt.plot(x, lin_fit_fn(x), '--k')
    plt.plot(x, lm*np.log(x)+lb, '-b')
    plt.plot(x, np.exp(eb+em*x), '-r')
    plt.show()


def mileage_over_time(data):
    # Get totals of miles and gallons for each day
    raw = {}
    for date in data:
        data[date] = [
            x for x in data[date] if float(
                x['Length (min)']) >= 5 and float(
                x['Distance (mi)']) >= 2]
        for index, entry in enumerate(data[date]):
            data[date][index] = {
                key: float(value) for key,
                value in entry.items()}
            data[date][index]['Gallons'] = data[date][index]['Distance (mi)'] \
                / data[date][index]['MPG']

        miles = sum([x['Distance (mi)'] for x in data[date]])
        if miles != 0:
            gallons = sum([x['Gallons'] for x in data[date]])
            raw[date] = {'miles': miles, 'gallons': gallons}

    points = {}
    points['x'] = []
    for index, date in enumerate([date for date in raw]):
        month, day, year = date.split('-')
        points['x'].append(datetime.date(int(year), int(month), int(day)))
    points['y'] = [raw[date]['miles'] / raw[date]['gallons'] for date in raw]

    plt.axis(ymin=20, ymax=80)
    plt.yticks(range(20, 80, 10))
    plt.minorticks_on()
    plt.grid(b=True, which='both', axis='both')
    plt.plot(points['x'], points['y'], '.b')
    plt.show()

if __name__ == "__main__":
    main(sys.argv)

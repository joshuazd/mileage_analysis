from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file as oauth_file, client, tools
from matplotlib import pyplot as plt
import datetime

SCOPES = 'https://www.googleapis.com/auth/spreadsheets.readonly'
SPREADSHEET_ID = '1x2Tmj_is1Rqp43LaTU8lHYl77qS3huiaiz9fWcfcJgA'
RANGE_NAME = 'Sheet1!A1:D'


def main():
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

    data = {}
    for value in values:
        if value[0] not in data:
            data[value[0]] = []
        entry = {}
        for index, field in enumerate(value[1:], 1):
            entry[headers[index]] = field
        data[value[0]] += [entry]

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

    plt.scatter(points['x'], points['y'])
    plt.axis(ymin=20, ymax=80)
    plt.yticks(range(20, 80, 10))
    plt.show()

if __name__ == "__main__":
    main()

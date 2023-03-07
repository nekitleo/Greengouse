import requests
from flask import Flask, render_template, request
import time
from database_pr import Database

from config.settings import DATABASE_PATH

app = Flask(__name__)

ex = Database(DATABASE_PATH)
NAMES = ['air_hudration_1', 'air_hudration_2', 'air_hudration_3', 'air_hudration_4', 'soil_hudration_1',
         'soil_hudration_2', 'soil_hudration_3', 'soil_hudration_4', 'soil_hudration_5', 'soil_hudration_6',
         'air_temperature_1', 'air_temperature_2',
         'air_temperature_3', 'air_temperature_4', 'greengouse_condition', 'door_condition', 'watering_garden_1',
         'watering_garden_2', 'watering_garden_3', 'watering_garden_4', 'watering_garden_5', 'watering_garden_6',
         'all_watering_garden']
NAMES_RU = ['Влажность воздуха на датчике 1', 'Влажность воздуха на датчике 2', 'Влажность воздуха на датчике 3',
            'Влажность воздуха на датчике 4',
            'Влажность почвы на датчике 1', 'Влажность почвы на датчике 2', 'Влажность почвы на датчике 3',
            'Влажность почвы на датчике 4', 'Влажность почвы на датчике 5',
            'Влажность почвы на датчике 6',
            'Температура воздуха на датчике 1', 'Температура воздуха на датчике 2', 'Температура воздуха на датчике 3',
            'Температура воздуха на датчике 4',
            'Экстренный режим', 'Состояние форточек',
            'Полив грядки номер 1', 'Полив грядки номер 2', 'Полив грядки номер 3', 'Полив грядки номер 4',
            'Полив грядки номер 5', 'Полив грядки номер 6', 'Система увлажнения воздуха']
flag = True
flag_2 = True
flag_3 = True
extra_mode = False
data = [False]


def change():
    d = ex.get_data_last()
    for i in range(16, 22):
        d[i] = 0
    ex.send_data(d, time.strftime('%x %X', time.localtime()))


def middle(data):
    return sum(data) / len(data)


def change_flag():
    global flag, flag_2, flag_3, extra_mode
    if (not (middle(ex.get_data_last()[4:10]) > 80) and not (middle(ex.get_data_last()[4:10]) < 40)) or extra_mode:
        flag_2 = True
    else:
        flag_2 = False
        change()
    if (not (middle(ex.get_data_last()[10:14]) > 34) and not (middle(ex.get_data_last()[10:14]) < 25)) or extra_mode:
        flag = True
    else:
        flag = False
        d = ex.get_data_last()
        d[15] = 0
        ex.send_data(d, time.strftime('%x %X', time.localtime()))
    if (not (middle(ex.get_data_last()[:5]) > 80) and not (middle(ex.get_data_last()[:5]) < 40)) or extra_mode:
        flag_3 = True
    else:
        flag_3 = False
        d = ex.get_data_last()
        d[22] = 0
        ex.send_data(d, time.strftime('%x %X', time.localtime()))


@app.route("/1", methods=["POST"])
def all():
    global flag, flag_2, flag_3, extra_mode
    sl1 = ex.get_data()
    return render_template('v1.html', key=list(sl1.keys())[-1], menu=sl1[list(sl1.keys())[-1]],
                           names=NAMES_RU, flag=flag, flag_2=flag_2, flag_3=flag_3)


@app.route("/")
def index():
    global flag, flag_2
    change_flag()
    sl1 = ex.get_data()
    return render_template('v1.html', key=list(sl1.keys())[-1], menu=sl1[list(sl1.keys())[-1]],
                           names=NAMES_RU, flag=flag, flag_2=flag_2, flag_3=flag_3)


@app.route("/1", methods=["POST"])
def index_2():
    global flag, flag_2
    change_flag()
    sl1 = ex.get_data()
    return render_template('v1.html', key=list(sl1.keys())[-1], menu=sl1[list(sl1.keys())[-1]],
                           names=NAMES_RU, flag=flag, flag_2=flag_2, flag_3=flag_3)


@app.route('/door', methods=['POST'])
def doit():
    global flag, flag_2, flag_3, extra_mode
    change_flag()
    if flag:
        state = ex.get_data_last()[15]
        door_drive_request = "https://dt.miet.ru/ppo_it/api/fork_drive"
        patch = {
            "state": (state + 1) % 2
        }
        response = requests.patch(door_drive_request, params=patch)
        d = ex.get_data_last()
        d[15] = (state + 1) % 2
        print(d)
        ex.send_data(d, time.strftime('%x %X', time.localtime()))
        sl1 = ex.get_data()
        return render_template('v1.html', key=list(sl1.keys())[-1],
                               menu=sl1[list(sl1.keys())[-1]],
                               names=NAMES_RU, flag=flag, flag_2=flag_2, flag_3=flag_3)
    else:
        sl1 = ex.get_data()
        return render_template('v1.html', key=list(sl1.keys())[-1],
                               menu=sl1[list(sl1.keys())[-1]],
                               names=NAMES_RU, flag=flag, flag_2=flag_2, flag_3=flag_3)


@app.route('/watering_garden_<index>', methods=['POST'])
def doit_2(index):
    global flag, flag_2, flag_3, extra_mode
    change_flag()
    if flag_2:
        state = ex.get_data_last()[15 + int(index)]
        door_drive_request = "https://dt.miet.ru/ppo_it/api/watering"
        patch = {
            "id": index,
            "state": (state + 1) % 2
        }
        response = requests.patch(door_drive_request, params=patch)
        d = ex.get_data_last()
        d[15 + int(index)] = (state + 1) % 2
        print(d)
        print(1)
        ex.send_data(d, time.strftime('%x %X', time.localtime()))
        sl1 = ex.get_data()
        return render_template('v1.html', key=list(sl1.keys())[-1],
                               menu=sl1[list(sl1.keys())[-1]],
                               names=NAMES_RU, response=response, flag=flag, flag_2=flag_2, flag_3=flag_3)
    else:
        change()
        sl1 = ex.get_data()
        return render_template('v1.html', key=list(sl1.keys())[-1],
                               menu=sl1[list(sl1.keys())[-1]],
                               names=NAMES_RU, flag=flag, flag_2=flag_2, flag_3=flag_3)


@app.route('/watering_garden_all', methods=['POST'])
def doit_3():
    global flag, flag_2, flag_3, extra_mode
    change_flag()
    if flag_3:
        state = ex.get_data_last()[22]
        door_drive_request = "https://dt.miet.ru/ppo_it/api/total_hum"
        patch = {
            "state": (state + 1) % 2
        }
        response = requests.patch(door_drive_request, params=patch)
        d = ex.get_data_last()
        if d[22] == 0:
            d[22] = 1
        else:
            d[22] = 0
        print(response)
        ex.send_data(d, time.strftime('%x %X', time.localtime()))
        sl1 = ex.get_data()
        return render_template('v1.html', key=list(sl1.keys())[-1],
                               menu=sl1[list(sl1.keys())[-1]],
                               names=NAMES_RU, flag=flag, flag_2=flag_2, flag_3=flag_3)
    else:
        change()
        sl1 = ex.get_data()
        return render_template('v1.html', key=list(sl1.keys())[-1],
                               menu=sl1[list(sl1.keys())[-1]],
                               names=NAMES_RU, flag=flag, flag_2=flag_2, flag_3=flag_3)


@app.route('/extra_mode', methods=['POST'])
def doit_4():
    global flag, flag_2, flag_3, extra_mode
    change_flag()
    d = ex.get_data_last()
    if d[14] == 1:
        d[14] = 0
        extra_mode = False
    else:
        d[14] = 1
        extra_mode = True
        flag, flag_2, flag_3 = True, True, True
    ex.send_data(d, time.strftime('%x %X', time.localtime()))
    print(ex.get_data_last())
    sl1 = ex.get_data()
    response = 'hi'
    return render_template('v1.html', key=list(sl1.keys())[-1], menu=sl1[list(sl1.keys())[-1]],
                           names=NAMES_RU, response=response, flag=flag, flag_2=flag_2, flag_3=flag_3)


@app.route('/print')
def statistika():
    return render_template('img.html')


if __name__ == "__main__":
    app.run(debug=True, port=8080)

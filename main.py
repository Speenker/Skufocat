import math
import struct
from matplotlib import pyplot as plt
from matplotlib.widgets import Button
from matplotlib.lines import Line2D
import random

filename = 'data.bin'
SCOOTERS_AMOUNT = 150
STASHES_AMOUNT = 20
TIME = 20000

class Scooter:
    def __init__(self, x, y, charge):
        self.x = x
        self.y = y
        self.charge = charge
        self.reserved = False

    def __str__(self):
        return f"Scooter at coordinates ({self.x}, {self.y}) with charge {self.charge}%"

class ChargingStation:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.charged_accums = 10
        self.discharged_accums = 0
        self.visited = False

    def __str__(self):
        return f"Charging station at coordinates ({self.x}, {self.y}) with {self.charged_accums} charged and {self.discharged_accums} discharged accumulators"

def read_from_binary_file(filename, SCOOTERS_AMOUNT, STASHES_AMOUNT):
    scooters = []
    stashes = []
    with open(filename, 'rb') as f:
        for _ in range(SCOOTERS_AMOUNT):
            data = f.read(struct.calcsize('iiB'))
            if len(data) == struct.calcsize('iiB'):
                x, y, charge = struct.unpack('iiB', data)
                scooters.append(Scooter(x, y, charge))
        for _ in range(STASHES_AMOUNT):
            data = f.read(struct.calcsize('ii'))
            if len(data) == struct.calcsize('ii'):
                x, y = struct.unpack('ii', data)
                stashes.append(ChargingStation(x, y))
    return scooters, stashes

def plot_objects(ax, scooters, stashes, current_position=None, next_scooter=None):
    ax.cla()  # Очистка текущей оси
    ax.set_facecolor('#f0f0f0')  # Установка цвета фона
    for scooter in scooters:
        color = 'mo' if scooter.charge < 50 else 'co'  # бирюзовый кружок для самоката с зарядом >= 50%
        ax.plot(scooter.x, scooter.y, color)
    for stash in stashes:
        ax.plot(stash.x, stash.y, 'rs')  # Красный квадрат для зарядной станции
    if current_position:
        ax.plot(current_position[0], current_position[1], 'bo')  # Синий кружок для чарджера
    if next_scooter:
        ax.plot(next_scooter.x, next_scooter.y, 'go')  # Зеленый кружок для следующего самоката
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_title('Расположение объектов')


    # Вычисление и вывод среднего заряда
    avg_charge = sum(scooter.charge for scooter in scooters) / len(scooters)
    ax.text(0.95, 0.9, f'Avg: {avg_charge:.2f}%', transform=ax.figure.transFigure, fontsize=12, verticalalignment='bottom', horizontalalignment='right')

    legend_elements = [
        Line2D([0], [0], marker='o', color='w', label='< 50% charge', markerfacecolor='m', markersize=8),
        Line2D([0], [0], marker='o', color='w', label='>= 50% charge', markerfacecolor='c', markersize=8),
        Line2D([0], [0], marker='s', color='w', label='Charging Station', markerfacecolor='r', markersize=8),
        #Line2D([0], [0], marker='o', color='w', label='Charger', markerfacecolor='b', markersize=8),
        Line2D([0], [0], marker='o', color='w', label='Current Scooter', markerfacecolor='g', markersize=8)
    ]
    ax.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(0.52, -0.1),borderaxespad=0.,ncol=2)

    plt.draw()  # Обновление графика

def calculate_distance(point1, point2):
    if isinstance(point1, tuple):
        x1, y1 = point1
    else:
        x1, y1 = point1.x, point1.y

    if isinstance(point2, tuple):
        x2, y2 = point2
    else:
        x2, y2 = point2.x, point2.y

    return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

def find_nearest_station(charger_position, stashes):
    unvisited_stashes = [stash for stash in stashes if not stash.visited]
    nearest_station = min(unvisited_stashes, key=lambda stash: calculate_distance(charger_position, stash))
    return nearest_station

def find_nearest_scooters(charger_position, scooters, count=10):
    available_scooters = [scooter for scooter in scooters if not scooter.reserved and scooter.charge < 50]
    available_scooters.sort(key=lambda scooter: calculate_distance(charger_position, scooter))
    return available_scooters[:count]

def move_scooters_randomly(scooters, count=10):
    movable_scooters = [scooter for scooter in scooters if not scooter.reserved]
    for scooter in random.sample(movable_scooters, min(count, len(movable_scooters))):
        new_x = random.randint(0, 1000)  # Assuming the coordinate range is 0 to 1000
        new_y = random.randint(0, 1000)
        distance = calculate_distance((scooter.x, scooter.y), (new_x, new_y))
        scooter.x = new_x
        scooter.y = new_y
        scooter.charge -= distance * 0.1  # Assuming charge decreases by 0.01% per unit distance
        if scooter.charge < 0:
            scooter.charge = 0

def on_next_step(event):
    global current_position, scooters, stashes, current_scooter_index, nearest_scooters, charger_accums, total_distance

    if total_distance >= TIME:
        print("Лимит дистанции достигнут.")
        return

    move_scooters_randomly(scooters)  # Move 10 random scooters

    if charger_accums == 0:
        nearest_station = find_nearest_station(current_position, stashes)
        distance = calculate_distance(current_position, (nearest_station.x, nearest_station.y))
        if total_distance + distance > TIME:
            print("Лимит дистанции достигнут.")
            return
        current_position = (nearest_station.x, nearest_station.y)
        total_distance += distance
        charger_accums = 10
        nearest_station.visited = True
        nearest_station.charged_accums -= 10
        nearest_station.discharged_accums += 10
        nearest_scooters = find_nearest_scooters(current_position, scooters)
        current_scooter_index = 0
    else:
        nearest_scooters = find_nearest_scooters(current_position, scooters)  # Обновление списка ближайших самокатов
        if current_scooter_index < len(nearest_scooters):
            next_scooter = nearest_scooters[0]
            distance = calculate_distance(current_position, (next_scooter.x, next_scooter.y))
            if total_distance + distance > TIME:
                print("Лимит дистанции достигнут.")
                return
            current_position = (next_scooter.x, next_scooter.y)
            total_distance += distance
            next_scooter.charge = 100
            next_scooter.reserved = True
            charger_accums -= 1
            current_scooter_index += 1

    # Обновление отображения зеленой точки для следующего самоката
    next_scooter = nearest_scooters[0] if 0 < len(nearest_scooters) else None
    plot_objects(ax, scooters, stashes, current_position, next_scooter)

def on_end(event):
    global current_position, scooters, stashes, current_scooter_index, nearest_scooters, charger_accums, total_distance

    while total_distance < TIME:
        move_scooters_randomly(scooters)  # Move 10 random scooters

        if charger_accums == 0:
            nearest_station = find_nearest_station(current_position, stashes)
            if not nearest_station:
                break
            distance = calculate_distance(current_position, (nearest_station.x, nearest_station.y))
            if total_distance + distance > TIME:
                print("Лимит дистанции достигнут.")
                break
            current_position = (nearest_station.x, nearest_station.y)
            total_distance += distance
            charger_accums = 10
            nearest_station.visited = True
            nearest_station.charged_accums -= 10
            nearest_station.discharged_accums += 10
            nearest_scooters = find_nearest_scooters(current_position, scooters)
            current_scooter_index = 0
        else:
            nearest_scooters = find_nearest_scooters(current_position, scooters)  # Обновление списка ближайших самокатов
            if current_scooter_index < len(nearest_scooters):
                next_scooter = nearest_scooters[0]
                distance = calculate_distance(current_position, (next_scooter.x, next_scooter.y))
                if total_distance + distance > TIME:
                    print("Лимит дистанции достигнут.")
                    break
                current_position = (next_scooter.x, next_scooter.y)
                total_distance += distance
                next_scooter.charge = 100
                next_scooter.reserved = True
                charger_accums -= 1
                current_scooter_index += 1
            else:
                break

    # Обновление отображения зеленой точки для следующего самоката
    next_scooter = nearest_scooters[0] if 0 < len(nearest_scooters) else None
    plot_objects(ax, scooters, stashes, current_position, None)
    plt.draw()  # Обновление графика один раз в конце
    btn_end.label.set_text("Finished")
    btn_end.color = 'gray'
    btn_end.hovercolor = 'gray'
    btn_end.set_active(False)

    btn_next.label.set_text("Finished")
    btn_next.set_active(False)
    btn_next.color = 'gray'
    btn_next.hovercolor = 'gray'



# Инициализация данных
scooters, stashes = read_from_binary_file(filename, SCOOTERS_AMOUNT, STASHES_AMOUNT)

# Ввод координат чарджера
charger_x = float(input("Введите координату X чарджера: "))
charger_y = float(input("Введите координату Y чарджера: "))
current_position = (charger_x, charger_y)

# Инициализация переменных
charger_accums = 0
current_scooter_index = 0
nearest_scooters = []
total_distance = 0  # Добавлено для отслеживания пройденного расстояния

# Построение графика с кнопками
fig, ax = plt.subplots()
plt.subplots_adjust(bottom=0.2)
ax_next = plt.axes([0.81, 0.05, 0.1, 0.075])
btn_next = Button(ax_next, 'Next', color='lightblue', hovercolor='blue')
btn_next.on_clicked(on_next_step)

ax_end = plt.axes([0.7, 0.05, 0.1, 0.075])
btn_end = Button(ax_end, 'End', color='lightgreen', hovercolor='green')
btn_end.on_clicked(on_end)

plot_objects(ax, scooters, stashes, current_position)

plt.show()


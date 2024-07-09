import random
import struct

GRID_SIZE = 1000
SCOOTERS_AMOUNT = 150
STASHES_AMOUNT = 20
AVG_ZONE_CHARGE = 45

def generate_scooters(grid_size, scooters_amount, avg_charge):
    scooters = []
    for _ in range(scooters_amount):
        x = random.randint(0, grid_size - 1)
        y = random.randint(0, grid_size - 1)
        charge = random.gauss(avg_charge, 10)  # Средний заряд около 40% с нормальным распределением
        charge = max(0, min(100, charge))  # Уровень заряда должен быть в пределах 0-100%
        scooters.append((x, y, charge))
    return scooters

def generate_stashes(grid_size, stashes_amount):
    stashes = []
    step = grid_size / (stashes_amount ** 0.5)
    for i in range(stashes_amount):
        x = int((i % (stashes_amount ** 0.5)) * step + step / 2)
        y = int((i // (stashes_amount ** 0.5)) * step + step / 2)
        stashes.append((x, y))
    return stashes

def write_to_binary_file(filename, scooters, stashes):
    with open(filename, 'wb') as f:
        for scooter in scooters:
            f.write(struct.pack('iiB', scooter[0], scooter[1], int(scooter[2])))
        for stash in stashes:
            f.write(struct.pack('ii', stash[0], stash[1]))

scooters = generate_scooters(GRID_SIZE, SCOOTERS_AMOUNT, AVG_ZONE_CHARGE)
stashes = generate_stashes(GRID_SIZE, STASHES_AMOUNT)
write_to_binary_file('data.bin', scooters, stashes)
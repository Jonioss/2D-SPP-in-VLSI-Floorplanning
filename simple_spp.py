import pymprog as pp
import utils as u

# Width of chip
CHIP_WIDTH = 60

# Width and height of units
UNITS_WH = [
    [10, 5],
    [2, 4],
    [6, 7],
    [12, 13],
    [3, 8],
    [5, 6],
    [18, 4],
    [7, 14],
    [4, 9],
    [11, 13]
]

M = 10000

model = pp.model('Simple SPP')

xi = [model.var(f'x{i}', kind=float, bounds=(0, None)) for i in range(len(UNITS_WH))]
yi = [model.var(f'y{i}', kind=float, bounds=(0, None)) for i in range(len(UNITS_WH))]
lij = [[model.var(f'l{i}_{j}', kind=int, bounds=(0, 1)) for j in range(len(UNITS_WH))] for i in range(len(UNITS_WH))]
rij = [[model.var(f'r{i}_{j}', kind=int, bounds=(0, 1)) for j in range(len(UNITS_WH))] for i in range(len(UNITS_WH))]
bij = [[model.var(f'b{i}_{j}', kind=int, bounds=(0, 1)) for j in range(len(UNITS_WH))] for i in range(len(UNITS_WH))]
aij = [[model.var(f'a{i}_{j}', kind=int, bounds=(0, 1)) for j in range(len(UNITS_WH))] for i in range(len(UNITS_WH))]
H = model.var('H', kind=float, bounds=(0, None))

model.minimize(H)

for i in range(len(UNITS_WH)):
    xi[i] + UNITS_WH[i][0] <= CHIP_WIDTH
    yi[i] + UNITS_WH[i][1] <= H

    for j in range(i + 1, len(UNITS_WH)):
        xi[i] + UNITS_WH[i][0] <= xi[j] + M * (1 - lij[i][j])
        xi[j] + UNITS_WH[j][0] <= xi[i] + M * (1 - rij[i][j])
        yi[i] + UNITS_WH[i][1] <= yi[j] + M * (1 - bij[i][j])
        yi[j] + UNITS_WH[j][1] <= yi[i] + M * (1 - aij[i][j])
        lij[i][j] + rij[i][j] + bij[i][j] + aij[i][j] == 1

model.solve()
for i in range(len(UNITS_WH)):
    print(f"Unit {i}: x = {xi[i].primal:.2f}, y = {yi[i].primal:.2f}")

x = [xi[i].primal for i in range(len(UNITS_WH))]
y = [yi[i].primal for i in range(len(UNITS_WH))]
w = [UNITS_WH[i][0] for i in range(len(UNITS_WH))]
h = [UNITS_WH[i][1] for i in range(len(UNITS_WH))]
H_val = H.primal
u.plot_packing(x, y, w, h, CHIP_WIDTH, H_val)
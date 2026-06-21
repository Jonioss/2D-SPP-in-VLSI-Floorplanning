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

M = 1000

model = pp.model('Simple SPP')

# Variables for unit positions and dimensions
xi = [model.var(f'x{i}', kind=float, bounds=(0, None)) for i in range(len(UNITS_WH))]
yi = [model.var(f'y{i}', kind=float, bounds=(0, None)) for i in range(len(UNITS_WH))]
lij = [[model.var(f'l{i}_{j}', kind=int, bounds=(0, 1)) for j in range(len(UNITS_WH))] for i in range(len(UNITS_WH))]
rij = [[model.var(f'r{i}_{j}', kind=int, bounds=(0, 1)) for j in range(len(UNITS_WH))] for i in range(len(UNITS_WH))]
bij = [[model.var(f'b{i}_{j}', kind=int, bounds=(0, 1)) for j in range(len(UNITS_WH))] for i in range(len(UNITS_WH))]
aij = [[model.var(f'a{i}_{j}', kind=int, bounds=(0, 1)) for j in range(len(UNITS_WH))] for i in range(len(UNITS_WH))]
H = model.var('H', kind=float, bounds=(0, None))

# Variables for rotation of units
roti = [model.var(f'rot{i}', kind=int, bounds=(0, 1)) for i in range(len(UNITS_WH))]

# Definition of objective func
model.minimize(H)

# Constrains for SPP with rotation
for i in range(len(UNITS_WH)):
    weffi = UNITS_WH[i][0] * (1 - roti[i]) + UNITS_WH[i][1] * roti[i]
    heffi = UNITS_WH[i][1] * (1 - roti[i]) + UNITS_WH[i][0] * roti[i]

    xi[i] + weffi <= CHIP_WIDTH
    yi[i] + heffi <= H

    for j in range(i + 1, len(UNITS_WH)):

        weffj = UNITS_WH[j][0] * (1 - roti[j]) + UNITS_WH[j][1] * roti[j]
        heffj = UNITS_WH[j][1] * (1 - roti[j]) + UNITS_WH[j][0] * roti[j]

        xi[i] + weffi <= xi[j] + M * (1 - lij[i][j])
        xi[j] + weffj <= xi[i] + M * (1 - rij[i][j])
        yi[i] + heffi <= yi[j] + M * (1 - bij[i][j])
        yi[j] + heffj <= yi[i] + M * (1 - aij[i][j])
        lij[i][j] + rij[i][j] + bij[i][j] + aij[i][j] == 1

# Solve the model
model.solve()

# Extract results and print
for i in range(len(UNITS_WH)):
    print(f"Unit {i}: x = {xi[i].primal:.2f}, y = {yi[i].primal:.2f}")

x = [xi[i].primal for i in range(len(UNITS_WH))]
y = [yi[i].primal for i in range(len(UNITS_WH))]
w = [UNITS_WH[i][0] for i in range(len(UNITS_WH))]
h = [UNITS_WH[i][1] for i in range(len(UNITS_WH))]
H_val = H.primal

# For plotting; see utils.py > plot_packing()
w_plot = []
h_plot = []
for i in range(len(UNITS_WH)):
    w0, h0 = UNITS_WH[i]
    if roti[i].primal < 0.5:
        w_plot.append(w0)
        h_plot.append(h0)
    else:
        w_plot.append(h0)
        h_plot.append(w0)

u.plot_packing(x, y, w_plot, h_plot, CHIP_WIDTH, H_val)
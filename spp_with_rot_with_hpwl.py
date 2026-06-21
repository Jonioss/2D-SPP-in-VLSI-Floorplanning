import pymprog as pp
import utils as u

# Width of chip
CHIP_WIDTH = 30

# Width and height of units
UNITS_WH = [
    [10, 5],
    [2, 4],
    [6, 7],
    [12, 13],
    [3, 8],
    [5, 6],
]

M = 100

NETS = [
    {'pins': [(0,  5.0, 2.5), (1, 1.0, 2.0)]},
    {'pins': [(2,  3.0, 3.5), (3, 6.0, 6.5)]},
    {'pins': [(4,  1.5, 4.0), (5, 2.5, 3.0), (3, 9.0, 2.0)]},
    {'pins': [(2,  0.5, 1.5), (0, 5.0, 2.5)]},
    {'pins': [(3,  6.0, 6.5), (5, 1.0, 2.0)]},
]
num_nets = len(NETS)
 
# Objective weights - A for Height, B for HPWL
ALPHA = 1.0
BETA  = 0.05

model = pp.model('SP + Rotation + Wirelength')

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

# Variables for bounding boxes of nets
xp = [model.var(f'xp{k}', kind=float, bounds=(0, CHIP_WIDTH)) for k in range(num_nets)]
xm = [model.var(f'xm{k}', kind=float, bounds=(0, CHIP_WIDTH)) for k in range(num_nets)]
yp = [model.var(f'yp{k}', kind=float, bounds=(0, None))       for k in range(num_nets)]
ym = [model.var(f'ym{k}', kind=float, bounds=(0, None))       for k in range(num_nets)]

# Calculation of HPWL
HPWL = sum(((xp[k] - xm[k]) + (yp[k] - ym[k])) for k in range(num_nets))

# Definition of objective func
model.minimize(ALPHA * H + BETA * HPWL)

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

# Constraints for HPWL
for k, net in enumerate(NETS):
    for (bi, ox, oy) in net['pins']:
        wi_b, hi_b = UNITS_WH[bi]
 
        # Linear pin coordinates with rotation
        pin_x = xi[bi] + ox + (hi_b - oy - ox) * roti[bi]
        pin_y = yi[bi] + oy + (ox   - oy)       * roti[bi]
 
        # Bounding-box constraints
        xm[k] <= pin_x   # x⁻_N ≤ pin_x   (left  bound)
        pin_x <= xp[k]   # pin_x ≤ x⁺_N   (right bound)
        ym[k] <= pin_y   # y⁻_N ≤ pin_y   (lower bound)
        pin_y <= yp[k]   # pin_y ≤ y⁺_N   (upper bound)

# Solve the model
model.solve()

# Extract results and print
HPWL_val = sum(((xp[k].primal - xm[k].primal) + (yp[k].primal - ym[k].primal)) for k in range(num_nets))
 
print("=" * 30)
print(f"H = {H.primal:.4f}")
print(f"HPWL = {HPWL_val:.4f}")
print(f"Combined obj = {ALPHA * H.primal + BETA * HPWL_val:.4f}")
print("=" * 30)

for i in range(len(UNITS_WH)):
    print(f"Unit {i}: x = {xi[i].primal:.2f}, y = {yi[i].primal:.2f}")

x = [xi[i].primal for i in range(len(UNITS_WH))]
y = [yi[i].primal for i in range(len(UNITS_WH))]
w = [UNITS_WH[i][0] for i in range(len(UNITS_WH))]
h = [UNITS_WH[i][1] for i in range(len(UNITS_WH))]
H_val = H.primal

# For plotting; see utils.py > plot_packing_full()
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

# u.plot_packing(x, y, w_plot, h_plot, CHIP_WIDTH, H_val)
u.plot_packing_full(
    x, y, w_plot, h_plot, CHIP_WIDTH, H_val,
    nets=NETS,
    units_wh=UNITS_WH,
    roti=[roti[i].primal for i in range(len(UNITS_WH))]
)
# minZ = 89 (32x1A + 151x1B + 72x1C + 118x1D) + 81 (39x2A + 147x2B + 61x2C + 126x2D) + 84 (46x3A + 155x3B + 57x3C + 121x3D)
# x1A + x2A + x3A = 1
# x1B + x2B + x3B = 1
# x1C + x2C + x3C = 1
# x1D + x2D + x3D = 1
# 32x1A + 151x1B + 72x1C + 118x1D <= 160
# 39x2A + 147x2B + 61x2C + 126x2D <= 160
# 46x3A + 155x3B + 57x3C + 121x3D <= 160
# xij >= 0

import pymprog as pp

model = pp.model('task')

x1A = model.var('x1A', kind=float, bounds=(0, None))
x1B = model.var('x1B', kind=float, bounds=(0, None))
x1C = model.var('x1C', kind=float, bounds=(0, None))
x1D = model.var('x1D', kind=float, bounds=(0, None))

x2A = model.var('x2A', kind=float, bounds=(0, None))
x2B = model.var('x2B', kind=float, bounds=(0, None))
x2C = model.var('x2C', kind=float, bounds=(0, None))
x2D = model.var('x2D', kind=float, bounds=(0, None))

x3A = model.var('x3A', kind=float, bounds=(0, None))
x3B = model.var('x3B', kind=float, bounds=(0, None))
x3C = model.var('x3C', kind=float, bounds=(0, None))
x3D = model.var('x3D', kind=float, bounds=(0, None))

model.minimize(89 * (32*x1A + 151*x1B + 72*x1C + 118*x1D) + 81 * (39*x2A + 147*x2B + 61*x2C + 126*x2D) + 84 * (46*x3A + 155*x3B + 57*x3C + 121*x3D))

y1 = x1A + x2A + x3A == 1
y2 = x1B + x2B + x3B == 1
y3 = x1C + x2C + x3C == 1
y4 = x1D + x2D + x3D == 1

y5 = 32*x1A + 151*x1B + 72*x1C + 118*x1D <= 160
y6 = 39*x2A + 147*x2B + 61*x2C + 126*x2D <= 160
y7 = 46*x3A + 155*x3B + 57*x3C + 121*x3D <= 160

model.solve()

print(f"x1A = {x1A.primal}")
print(f"x1B = {x1B.primal:.2f}")
print(f"x1C = {x1C.primal:.2f}")
print(f"x1D = {x1D.primal:.2f}")

print(f"x2A = {x2A.primal:.2f}")
print(f"x2B = {x2B.primal:.2f}")
print(f"x2C = {x2C.primal:.2f}")
print(f"x2D = {x2D.primal:.2f}")

print(f"x3A = {x3A.primal:.2f}")
print(f"x3B = {x3B.primal:.2f}")
print(f"x3C = {x3C.primal:.2f}")
print(f"x3D = {x3D.primal:.2f}")

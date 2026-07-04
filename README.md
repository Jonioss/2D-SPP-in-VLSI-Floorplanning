# Joint Area and Wirelength Optimization for VLSI Strip Packing Problem

A linear programming approach to the VLSI *Strip Packing Problem* that jointly minimizes chip area and *Half-Perimeter Wirelength* (HPWL), with support for block rotation. Modeled and solved in Python with **Pymprog** (GLPK) and visualized with **Matplotlib**.

---

## Table of Contents

- [Introduction](#introduction)
  - [Purpose](#purpose)
  - [Motivation](#motivation)
  - [Methodological Approach](#methodological-approach)
- [Theoretical Background](#theoretical-background)
  - [The Strip Packing Problem](#the-strip-packing-problem)
  - [Floorplanning and Placement in VLSI](#floorplanning-and-placement-in-vlsi)
  - [Block Rotation](#block-rotation)
  - [Interconnections and Netlists](#interconnections-and-netlists)
  - [Half-Perimeter Wirelength](#half-perimeter-wirelength)
  - [Arithmetic Logic Unit](#arithmetic-logic-unit)
- [Basic Model: SPP Without Rotation](#basic-model-spp-without-rotation)
  - [Constants](#constants)
  - [Decision Variables](#decision-variables)
  - [Objective Function](#objective-function)
  - [Constraints](#constraints)
  - [Algorithm Execution](#algorithm-execution)
- [Model Extension with Block Rotation](#model-extension-with-block-rotation)
- [Introducing HPWL](#introducing-hpwl)
  - [New Data](#new-data)
  - [New Decision Variables](#new-decision-variables)
  - [New Objective Function](#new-objective-function)
  - [New Constraints](#new-constraints)
  - [A Note on Data Visualization](#a-note-on-data-visualization)
  - [Python Code Execution](#python-code-execution)
- [ALU: A Real-World Application](#alu-a-real-world-application)
- [References](#references)

---

## Introduction

### Purpose

The subject of this project is the study of the *Strip Packing Problem* (SPP) in the field of *Very Large Scale Integration* (VLSI). The application concerns the simultaneous minimization of the area of a chip composed of **units** — each performing a specific function — with the possibility of rotating each unit, as well as the minimization of the *Half-Perimeter Wirelength* (HPWL), i.e. the total length of the wiring between them. The problem is solved in Python using the *Pymprog* library for optimization and *Matplotlib* for visualizing the results.

### Motivation

This study is of genuine interest in the field of integrated circuit design in industry, since all modern software that performs placement of units on chips (e.g. *Innovus*, *Vivado*) seeks the most efficient organization possible, in order to minimize wiring and chip area — maximizing the circuit's performance and operating frequency, as well as the ease of its manufacturing in the fab.

### Methodological Approach

The problem is solved in this report following a clear methodology. First, the basic Strip Packing problem is defined, without a VLSI application and without the possibility of rotating blocks, laying the foundation on which the rest of the problem is built. Next, the decision variables and constraints concerning the rotation of each block are added. After that, the necessary additions and changes are made to the model so that HPWL is minimized as well. Finally, with the complete problem modeled, a real-world application is presented on an *Arithmetic Logic Unit* (**ALU**) circuit, which accepts three input words — two of 8 bits and one of 3 bits — and, depending on the third input, performs the corresponding operation on the first two.

At every step, a detailed mathematical analysis is provided for the definition of the respective problem, the objective function being minimized, the decision variables, and the constraints, along with the corresponding Python code.

---

## Theoretical Background

This chapter presents the definitions the reader should be familiar with before proceeding to the implementation of the project.

### The Strip Packing Problem

The Strip Packing Problem (SPP) is defined as follows. Given a surface of fixed, known width $W$, and rectangular blocks of known width and height, the goal is to place the blocks in such a way that the height of the surface — and therefore its area — is minimized.

The decision variables of such a problem are the coordinates of each block (specifically, the position of its bottom-left corner relative to the bottom-left corner of the surface) and the height $H$ of the surface.

The obvious constraints of such a problem are the *non-overlap* constraints (preventing any two blocks from overlapping each other) and the containment constraint, which keeps each block entirely within the surface.

### Floorplanning and Placement in VLSI

In the real-world VLSI problem, blocks correspond to functional units that must be placed efficiently on a chip and are capable of carrying out operations. Unlike the blocks of the classical SPP, these units also have **ports** — input and output pins — which are discussed in detail below.

### Block Rotation

In integrated circuit design, rotating units can be critical to placing them more efficiently on the chip. It is therefore important to model this as well, through new decision variables.

### Interconnections and Netlists

Also critical to understanding the final problem are the definitions of *netlists* and *pins*.

In the physical design of a circuit, besides the sizes of the units, the interconnections between them must also be defined mathematically. This description is given through the **netlist** — a set of electrical connections that determines which units are connected to which, and how.

**Pins** are defined as the contact points where each connection attaches to a unit, and can be located on its boundary or anywhere on it. It is also worth noting that a single unit can have multiple pins and can therefore be connected to many other units. Furthermore, each pin is described, within its unit, by an *offset* relative to some reference point of the unit.

### Half-Perimeter Wirelength

*HPWL* (Half-Perimeter Wirelength) is a simple and widely used method for estimating the length of a net, without needing to actually place the units and measure the wiring for every possible arrangement. This estimation method is based on finding the smallest rectangle that contains all the pins of a given net.

More precisely, for each net a **bounding box** is considered that contains all of its pins, with width $\Delta x$ and height $\Delta y$. Thus, for a given net $n$, HPWL is defined as:

$$HPWL_n = \Delta x + \Delta y$$

which is equal to half the perimeter of the bounding box (hence *Half-Perimeter*). The comparison metric used throughout this report is the sum of the HPWL values of every net.

This method has very low computational cost, but it remains an estimation method rather than an exact one. Therefore, for sufficiently large applications, it can carry significant error.

### Arithmetic Logic Unit

The *Arithmetic Logic Unit*, commonly known as the **ALU**, is a circuit that is used — under different implementations depending on the application — in processing units and beyond. Every time a digital operation must be performed, whether arithmetic (e.g. multiplication, addition) or logical (e.g. AND, OR), the ALU is responsible for computing the result while consuming as little time and energy as possible. Therefore, in a world where such units are executed billions of times per second, finding an efficient implementation of the ALU is critical to industry and remains a field of research worldwide.

---

## Basic Model: SPP Without Rotation

Having covered the necessary background, we can now begin implementing the problem.

### Constants

Let us first define the width of the chip, $W$:

$$W = 60$$

as well as the blocks we want to place on the surface, in terms of their width and height:

$$UNITS_{WH} = [(10,\ 5),\ \ldots,\ (11,\ 13)]$$

### Decision Variables

Next, we define the decision variables. First, we have the coordinates of the bottom-left corner of each block on the surface:

$$(x_i,\ y_i)$$

as well as binary variables (0 or 1) that determine, for each block $i$, whether it is to the right, left, above, or below some other block $j$:

$$r_{ij}\ (\text{right}),\quad l_{ij}\ (\text{left}),\quad a_{ij}\ (\text{above}),\quad b_{ij}\ (\text{below})$$

Finally, we define the last decision variable, representing the quantity we actually want to minimize — the height $H$ of the surface.

### Objective Function

The objective function to be minimized is simple:

$$\min H$$

### Constraints

For each block $i$, several constraints must be defined for the decision variables that concern it:

- **Containment** — the block must lie entirely within the surface:

$$x_i + W_i \leq W$$

$$y_i + H_i \leq H$$

- Constraints on the relative position of blocks with respect to one another (the **non-overlap** constraint). To linearize the requirement that, for every pair of blocks $i, j$, exactly one of $r$, $l$, $a$, and $b$ must be active (equal to 1), we introduce the following constraints, as covered in the lectures:

$$x_i + W_i \leq x_j + M(1-l_{ij})$$

$$x_j + W_j \leq x_i + M(1-r_{ij})$$

$$y_i + H_i \leq y_j + M(1-b_{ij})$$

$$y_j + H_j \leq y_i + M(1-a_{ij})$$

$$l_{ij}+r_{ij}+a_{ij}+b_{ij}=1$$

### Algorithm Execution

Having defined the entire problem mathematically, we can now write it in Python:

```python
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

# Big-M
M = 10000

# Definition of model
model = pp.model('Simple SPP')

# Definion of decision variables
xi = [model.var(f'x{i}', kind=float, bounds=(0, None)) for i in range(len(UNITS_WH))]
yi = [model.var(f'y{i}', kind=float, bounds=(0, None)) for i in range(len(UNITS_WH))]
lij = [[model.var(f'l{i}_{j}', kind=int, bounds=(0, 1)) for j in range(len(UNITS_WH))] for i in range(len(UNITS_WH))]
rij = [[model.var(f'r{i}_{j}', kind=int, bounds=(0, 1)) for j in range(len(UNITS_WH))] for i in range(len(UNITS_WH))]
bij = [[model.var(f'b{i}_{j}', kind=int, bounds=(0, 1)) for j in range(len(UNITS_WH))] for i in range(len(UNITS_WH))]
aij = [[model.var(f'a{i}_{j}', kind=int, bounds=(0, 1)) for j in range(len(UNITS_WH))] for i in range(len(UNITS_WH))]
H = model.var('H', kind=float, bounds=(0, None))

# definicion of objective function
model.minimize(H)

# Definition of constraints
for i in range(len(UNITS_WH)):
    xi[i] + UNITS_WH[i][0] <= CHIP_WIDTH
    yi[i] + UNITS_WH[i][1] <= H

    for j in range(i + 1, len(UNITS_WH)):
        xi[i] + UNITS_WH[i][0] <= xi[j] + M * (1 - lij[i][j])
        xi[j] + UNITS_WH[j][0] <= xi[i] + M * (1 - rij[i][j])
        yi[i] + UNITS_WH[i][1] <= yi[j] + M * (1 - bij[i][j])
        yi[j] + UNITS_WH[j][1] <= yi[i] + M * (1 - aij[i][j])
        lij[i][j] + rij[i][j] + bij[i][j] + aij[i][j] == 1

# Solve the problem
model.solve()

# Extract and print results
for i in range(len(UNITS_WH)):
    print(f"Unit {i}: x = {xi[i].primal:.2f}, y = {yi[i].primal:.2f}")

x = [xi[i].primal for i in range(len(UNITS_WH))]
y = [yi[i].primal for i in range(len(UNITS_WH))]
w = [UNITS_WH[i][0] for i in range(len(UNITS_WH))]
h = [UNITS_WH[i][1] for i in range(len(UNITS_WH))]
H_val = H.primal

# Plot results
u.plot_packing(x, y, w, h, CHIP_WIDTH, H_val)
```

The code follows the same logic described above. The final command, `u.plot_packing()`, visualizes the algorithm's results so that we can better understand them. This function is defined in the `utils.py` file, as follows:

```python
def plot_packing(x, y, w, h, chip_width, H):
    fig, ax = plt.subplots(figsize=(8, 6))

    # Outer strip
    ax.add_patch(
        patches.Rectangle((0, 0), chip_width, H,
                          edgecolor='black', facecolor='none', linewidth=2)
    )

    # Inner rectangles
    for i in range(len(x)):
        rect = patches.Rectangle(
            (x[i], y[i]), w[i], h[i],
            edgecolor='black', facecolor='skyblue', alpha=0.7, linewidth=1.5
        )
        ax.add_patch(rect)

        ax.text(
            x[i] + w[i] / 2,
            y[i] + h[i] / 2,
            f"R{i}",
            ha='center', va='center', fontsize=10
        )

    ax.set_xlim(0, chip_width)
    ax.set_ylim(0, H)
    ax.set_aspect('equal')
    ax.set_title(f"Strip Packing Result (H = {H:.2f})")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.grid(True, linestyle='--', alpha=0.3)
    plt.tight_layout()
    plt.show()
```

And the resulting plot:

<img width="800" height="600" alt="image" src="https://github.com/user-attachments/assets/758579ce-151a-44b4-b99f-10b01186906a" />

---

## Model Extension with Block Rotation

To account for the rotation of blocks, it is enough to add a new binary decision variable, $rot_i$, expressing whether a 90-degree clockwise rotation has been applied.

Next, we define the new constraints of the problem and modify some of the existing ones.

First, for each block we need to compute its *actual* width and height, since if rotation has occurred these two quantities are swapped. Therefore, the only change needed is that, instead of using:

$$W_i,\ W_j,\ H_i,\ H_j$$

we substitute, in every constraint:

$$W_{eff_i} = W_i \times (1-rot_i) + H_i \times rot_i$$

$$H_{eff_i} = H_i \times (1-rot_i) + W_i \times rot_i$$

and similarly for $j$.

The new code is as follows:

```python
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
```
*spp_with_rot.py*

We can again visualize the results as we did in the previous section — we just need to be careful, when extracting the data, to also account for the possible rotation of each block in the final result.

<img width="800" height="600" alt="image" src="https://github.com/user-attachments/assets/d7cc350c-54ff-4093-8252-a9b85c7316fb" />

---

## Introducing HPWL

We can now extend the basic SPP-with-rotation problem by adding the *Half-Perimeter Wirelength* criterion. Let us first assume that all wires have equal weight — this will be explained in full once we reach the point of applying the algorithm to the ALU unit.

### New Data

For each net $n$, we define the pins that it connects, as well as the *offset* of each pin — that is, its relative position with respect to the block on which it is located.

### New Decision Variables

For each net, we define 4 new decision variables, which determine the **bounding box** of that net:

$$x^+,\ x^-,\ y^+,\ y^-$$

and the $\Delta x, \Delta y$ of each net are then:

$$\Delta x = x^+ - x^-$$

$$\Delta y = y^+ - y^-$$

### New Objective Function

Therefore, each net's HPWL is:

$$HPWL_{net} = \Delta x_{net} + \Delta y_{net}$$

and the total HPWL that we want to minimize is:

$$HPWL = \sum_{net} HPWL_{net}$$

To incorporate this into the objective function, it must be combined with the surface height $H$ as a **weighted sum**. This gives the new objective:

$$\min(\alpha \times H + \beta \times HPWL)$$

The values of $\alpha$ and $\beta$ are obtained through tuning; however, it is reasonable to take $\beta$ smaller than $\alpha$, since minimizing the chip's area is more important than minimizing the wirelength. Thus, in the simple code below, the following values were chosen:

$$\alpha = 1.0,\quad \beta = 0.05$$

### New Constraints

Leaving the previous constraints as they are — since HPWL does not directly affect the constraints the way rotation did — we add new constraints concerning our new variables.

First, for each net $n$, let us consider the actual position of each pin $p$ as coordinates relative to the $(0,0)$ point of the surface:

$$pin_{x_i} = x_i + offsetx_i,\ \text{if } rot_i=0,\ \text{else } x_i + H_i - offsety_i$$

$$pin_{y_i} = y_i + offsety_i,\ \text{if } rot_i=0,\ \text{else } y_i + offsetx_i$$

Linearly, this can be written as:

$$pin_{x_i} = x_i + offsetx_i + (H_i + offsety_i - offsetx_i) \times rot_i$$

$$pin_{y_i} = y_i + offsety_i + (offsetx_i - offsety_i) \times rot_i$$

Therefore, the new constraints are:

$$x_i^- \leq pin_{x_i}$$

$$pin_{x_i} \leq x_i^+$$

$$y_i^- \leq pin_{y_i}$$

$$pin_{y_i} \leq y_i^+$$

### A Note on Data Visualization

To visualize the data under the HPWL criterion, *Perplexity AI* was used to more quickly put together a small script, contained in the `utils.py` file.

```python
def plot_packing_full(x, y, w, h, chip_width, H,
                      nets=None, units_wh=None, roti=None, labels=None):
    n = len(x)
    show_wires = (nets is not None
                  and units_wh is not None
                  and roti is not None)

    # ── figure + axes ────────────────────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(10, 7))

    # ── outer strip ──────────────────────────────────────────────────────────
    ax.add_patch(patches.Rectangle(
        (0, 0), chip_width, H,
        edgecolor='black', facecolor='none', linewidth=2
    ))

    # ── blocks ───────────────────────────────────────────────────────────────
    for i in range(n):
        ax.add_patch(patches.Rectangle(
            (x[i], y[i]), w[i], h[i],
            edgecolor='#2c3e50', facecolor='#aed6f1',
            alpha=0.75, linewidth=1.5
        ))
        ax.text(
            x[i] + w[i] / 2, y[i] + h[i] / 2, f"{labels[i]}" if labels else f"Block {i}",
            ha='center', va='center',
            fontsize=9, fontweight='bold', color='#1a252f'
        )

    # ── wires ────────────────────────────────────────────────────────────────
    if show_wires:
        num_nets = len(nets)
        # one colour per net from a qualitative colourmap
        cmap = plt.cm.get_cmap('tab10', max(num_nets, 1))
        hpwl = 0.0
        legend_handles = []

        for k, net in enumerate(nets):
            color = cmap(k)
            pins = []  # (global_x, global_y) per pin

            # ── compute pin global positions ──────────────────────────────
            for (bi, ox, oy) in net['pins']:
                wi_b, hi_b = units_wh[bi]
                rotated = roti[bi] > 0.5

                if rotated:  # 90° CW rotation
                    px = x[bi] + hi_b - oy
                    py = y[bi] + ox
                else:
                    px = x[bi] + ox
                    py = y[bi] + oy

                pins.append((px, py))

            if not pins:
                continue

            xs_pins = [p[0] for p in pins]
            ys_pins = [p[1] for p in pins]

            # ── HPWL bounding box (dashed, lightly filled) ───────────────
            bx = min(xs_pins); bw = max(xs_pins) - bx
            by = min(ys_pins); bh = max(ys_pins) - by
            ax.add_patch(patches.Rectangle(
                (bx, by), bw, bh,
                edgecolor=color, facecolor=color,
                alpha=0.07, linewidth=1.2,
                linestyle='--', zorder=2
            ))

            hpwl += bw + bh

            # ── wires between pins ────────────────────────────────────────
            if len(pins) == 2:
                # 2-pin net → direct line
                ax.plot(
                    [pins[0][0], pins[1][0]],
                    [pins[0][1], pins[1][1]],
                    color=color, linewidth=1.8, alpha=0.85, zorder=3
                )
            else:
                # multi-pin net → star from centroid (avoids clutter)
                cx = sum(xs_pins) / len(pins)
                cy = sum(ys_pins) / len(pins)
                ax.plot(cx, cy, '+', color=color,
                        markersize=7, markeredgewidth=1.5, zorder=4)
                for px, py in pins:
                    ax.plot(
                        [cx, px], [cy, py],
                        color=color, linewidth=1.8, alpha=0.85, zorder=3
                    )

            # ── pin markers ───────────────────────────────────────────────
            for px, py in pins:
                ax.plot(px, py, 'o',
                        color='white', markersize=6, zorder=5)
                ax.plot(px, py, 'o',
                        color=color, markersize=4, zorder=6)

            # ── legend entry ──────────────────────────────────────────────
            legend_handles.append(mlines.Line2D(
                [], [], color=color, linewidth=2,
                marker='o', markersize=5,
                label=f'Net {k}'
            ))

        # ── legend + HPWL annotation ──────────────────────────────────────
        if legend_handles:
            ax.legend(
                handles=legend_handles,
                loc='upper right', fontsize=8,
                framealpha=0.9, edgecolor='#cccccc'
            )

        title = (f"Strip Packing + Wirelength "
                 f"(H = {H:.2f}, HPWL = {hpwl:.2f})")
    else:
        title = f"Strip Packing Result (H = {H:.2f})"

    # ── axes formatting ───────────────────────────────────────────────────────
    ax.set_xlim(-0.5, chip_width + 0.5)
    ax.set_ylim(-0.5, H * 1.08)  # small top margin for legend
    ax.set_aspect('equal')
    ax.set_title(title, fontsize=11)
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.grid(True, linestyle='--', alpha=0.25)

    plt.tight_layout()
    plt.show()
```
*utils.py*

### Python Code Execution

The new code for this problem is as follows:

```python
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
    {'pins': [(0, 5.0, 2.5), (1, 1.0, 2.0)]},
    {'pins': [(2, 3.0, 3.5), (3, 6.0, 6.5)]},
    {'pins': [(4, 1.5, 4.0), (5, 2.5, 3.0), (3, 9.0, 2.0)]},
    {'pins': [(2, 0.5, 1.5), (0, 5.0, 2.5)]},
    {'pins': [(3, 6.0, 6.5), (5, 1.0, 2.0)]},
]
num_nets = len(NETS)

# Objective weights - A for Height, B for HPWL
ALPHA = 1.0
BETA = 0.05

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
yp = [model.var(f'yp{k}', kind=float, bounds=(0, None)) for k in range(num_nets)]
ym = [model.var(f'ym{k}', kind=float, bounds=(0, None)) for k in range(num_nets)]

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
        pin_y = yi[bi] + oy + (ox - oy) * roti[bi]

        # Bounding-box constraints
        xm[k] <= pin_x   # x⁻_N ≤ pin_x (left bound)
        pin_x <= xp[k]   # pin_x ≤ x⁺_N (right bound)
        ym[k] <= pin_y   # y⁻_N ≤ pin_y (lower bound)
        pin_y <= yp[k]   # pin_y ≤ y⁺_N (upper bound)

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

u.plot_packing_full(
    x, y, w_plot, h_plot, CHIP_WIDTH, H_val,
    nets=NETS,
    units_wh=UNITS_WH,
    roti=[roti[i].primal for i in range(len(UNITS_WH))]
)
```
*spp_with_rot_with_hpwl.py*

And the resulting output, visualized:

<img width="1000" height="700" alt="image" src="https://github.com/user-attachments/assets/50b89826-39aa-4489-98a2-0d647b2de7d0" />

In the image above, the randomly chosen pins on the blocks are shown together with the interconnection wires. We observe that the placement of Block 4 has clearly been influenced so that the brown wire lies in a straight line — that is, its pin is at the smallest possible distance from the pin of Block 5, and that one from the pin of Block 6.

---

## ALU: A Real-World Application

It is now time to apply the above to a real-world application: the ALU circuit.

<img width="708" height="710" alt="image" src="https://github.com/user-attachments/assets/79ef4f19-3270-4cbe-858a-fd9577f76b7a" />

In the circuit above, two 8-bit inputs, $A$ and $B$, are fed into 8 units — 4 for logical operations and 4 for arithmetic operations. The 8-bit output of each unit is carried to the **multiplexer**, which uses the 3-bit input $C$ to select which operation's result is passed to the output.

It is reasonable that a wire of length $N > 1$ bit is equivalent to $N$ wires of length 1 bit. We therefore need to introduce the notion of **weight** into our problem, since minimizing the wires of the inputs (16 bits combined, for $A$ and $B$ together) is far more important than minimizing the wires of the multiplexer's 3-bit select input $C$. To reflect this in the code, we add two new keys to each net's dictionary: `name`, which is more descriptive so the code stays readable, and `weight`, which equals 1.0 for the maximum bit-length wire in the circuit (16) and $b/16$ for the remaining wires. Describing this in the code only requires changing how HPWL is computed:

$$HPWL = \sum_{net} (\Delta x_{net} + \Delta y_{net}) \times weight_{net}$$

If we now define the units:

```python
# Width and height of units
UNITS_WH = [
    [12, 16],  # Input Block
    [22, 18],  # MOD Block
    [18, 16],  # MUL Block
    [14, 10],  # ADD Block
    [14, 10],  # SUB Block
    [8, 6],    # NOR Block
    [6, 5],    # NOT Block
    [8, 6],    # NAND Block
    [10, 6],   # XNOR Block
    [12, 14],  # MUX Block
    [8, 8],    # Output Block
]
```

The nets:

```python
NETS = [
    # Input register to operations
    {'name': 'IN->MOD',  'pins': [(0, 12.0, 8),  (1, 0.0, 9.0)],  'weight': 1.0},
    {'name': 'IN->MUL',  'pins': [(0, 12.0, 8),  (2, 0.0, 8.0)],  'weight': 1.0},
    {'name': 'IN->ADD',  'pins': [(0, 12.0, 8),  (3, 0.0, 5.0)],  'weight': 1.0},
    {'name': 'IN->SUB',  'pins': [(0, 12.0, 8),  (4, 0.0, 5.0)],  'weight': 1.0},
    {'name': 'IN->NOR',  'pins': [(0, 12.0, 8),  (5, 0.0, 3.0)],  'weight': 1.0},
    {'name': 'IN->NOT',  'pins': [(0, 12.0, 8),  (6, 0.0, 2.5)],  'weight': 1.0},
    {'name': 'IN->NAND', 'pins': [(0, 12.0, 8),  (7, 0.0, 3.0)],  'weight': 1.0},
    {'name': 'IN->XNOR', 'pins': [(0, 12.0, 8),  (8, 0.0, 3.0)],  'weight': 1.0},

    # operations to multiplexer
    {'name': 'MOD->MUX', 'pins': [(1, 22.0, 9.0), (9, 0.0, 11.2)], 'weight': 0.5},
    {'name': 'MUL->MUX', 'pins': [(2, 18.0, 8.0), (9, 0.0, 9.8)],  'weight': 0.5},
    {'name': 'ADD->MUX', 'pins': [(3, 14.0, 5.0), (9, 0.0, 8.4)],  'weight': 0.5},
    {'name': 'SUB->MUX', 'pins': [(4, 14.0, 5.0), (9, 0.0, 7.0)],  'weight': 0.5},
    {'name': 'NOR->MUX', 'pins': [(5, 8.0, 3.0),  (9, 0.0, 5.6)],  'weight': 0.5},
    {'name': 'NOT->MUX', 'pins': [(6, 6.0, 2.5),  (9, 0.0, 4.2)],  'weight': 0.5},
    {'name': 'NAND->MUX','pins': [(7, 8.0, 3.0),  (9, 0.0, 2.8)],  'weight': 0.5},
    {'name': 'XNOR->MUX','pins': [(8, 10.0, 3.0), (9, 0.0, 1.4)],  'weight': 0.5},

    # input control to multiplexer
    {'name': 'IN->MUX',  'pins': [(0, 12.0, 12),  (9, 6.0, 14.0)], 'weight': 3/16},

    # final multiplexer to output
    {'name': 'MUX->OUT', 'pins': [(9, 12.0, 7.0), (10, 0.0, 4.0)], 'weight': 0.5},
]
```

Let us now consider, for a start, $\beta = 0.001$, $\alpha = 1.0$, split $M$ into $M_x = 60$ and $M_y = 150$, with $W = 100$, and run the new code, `alu.py`:

```python
import pymprog as pp
import utils as u

# Width of chip
CHIP_WIDTH = 100

# Labels for units
UNITS_LABELS = [
    "IN",
    "MOD",
    "MUL",
    "ADD",
    "SUB",
    "NOR",
    "NOT",
    "NAND",
    "XNOR",
    "MUX",
    "OUT",
]

# Width and height of units
UNITS_WH = [
    [12, 16],  # Input Block
    [22, 18],  # MOD Block
    [18, 16],  # MUL Block
    [14, 10],  # ADD Block
    [14, 10],  # SUB Block
    [8, 6],    # NOR Block
    [6, 5],    # NOT Block
    [8, 6],    # NAND Block
    [10, 6],   # XNOR Block
    [12, 14],  # MUX Block
    [8, 8],    # Output Block
]

Mx = 60
My = 150

NETS = [
    # Input register to operations
    {'name': 'IN->MOD',  'pins': [(0, 12.0, 8),  (1, 0.0, 9.0)],  'weight': 1.0},
    {'name': 'IN->MUL',  'pins': [(0, 12.0, 8),  (2, 0.0, 8.0)],  'weight': 1.0},
    {'name': 'IN->ADD',  'pins': [(0, 12.0, 8),  (3, 0.0, 5.0)],  'weight': 1.0},
    {'name': 'IN->SUB',  'pins': [(0, 12.0, 8),  (4, 0.0, 5.0)],  'weight': 1.0},
    {'name': 'IN->NOR',  'pins': [(0, 12.0, 8),  (5, 0.0, 3.0)],  'weight': 1.0},
    {'name': 'IN->NOT',  'pins': [(0, 12.0, 8),  (6, 0.0, 2.5)],  'weight': 1.0},
    {'name': 'IN->NAND', 'pins': [(0, 12.0, 8),  (7, 0.0, 3.0)],  'weight': 1.0},
    {'name': 'IN->XNOR', 'pins': [(0, 12.0, 8),  (8, 0.0, 3.0)],  'weight': 1.0},

    # operations to multiplexer
    {'name': 'MOD->MUX', 'pins': [(1, 22.0, 9.0), (9, 0.0, 11.2)], 'weight': 0.5},
    {'name': 'MUL->MUX', 'pins': [(2, 18.0, 8.0), (9, 0.0, 9.8)],  'weight': 0.5},
    {'name': 'ADD->MUX', 'pins': [(3, 14.0, 5.0), (9, 0.0, 8.4)],  'weight': 0.5},
    {'name': 'SUB->MUX', 'pins': [(4, 14.0, 5.0), (9, 0.0, 7.0)],  'weight': 0.5},
    {'name': 'NOR->MUX', 'pins': [(5, 8.0, 3.0),  (9, 0.0, 5.6)],  'weight': 0.5},
    {'name': 'NOT->MUX', 'pins': [(6, 6.0, 2.5),  (9, 0.0, 4.2)],  'weight': 0.5},
    {'name': 'NAND->MUX','pins': [(7, 8.0, 3.0),  (9, 0.0, 2.8)],  'weight': 0.5},
    {'name': 'XNOR->MUX','pins': [(8, 10.0, 3.0), (9, 0.0, 1.4)],  'weight': 0.5},

    # input control to multiplexer
    {'name': 'IN->MUX',  'pins': [(0, 12.0, 12),  (9, 6.0, 14.0)], 'weight': 3/16},

    # final multiplexer to output
    {'name': 'MUX->OUT', 'pins': [(9, 12.0, 7.0), (10, 0.0, 4.0)], 'weight': 0.5},
]

num_nets = len(NETS)

# Objective weights - A for Height, B for HPWL
ALPHA = 1.0
BETA = 0.001

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
yp = [model.var(f'yp{k}', kind=float, bounds=(0, None)) for k in range(num_nets)]
ym = [model.var(f'ym{k}', kind=float, bounds=(0, None)) for k in range(num_nets)]

# Calculation of HPWL
HPWL = sum(((xp[k] - xm[k]) + (yp[k] - ym[k])) * NETS[k]['weight'] for k in range(num_nets))

# Definition of objective func
model.minimize(ALPHA * H + BETA * HPWL)

# Fix input block to the lower left side of the chip
xi[0] == 0
yi[0] == 0

# Fix output block to the lower right side of the chip
xi[-1] == CHIP_WIDTH - UNITS_WH[-1][0]
yi[-1] == 0

# Constrains for SPP with rotation
for i in range(len(UNITS_WH)):
    weffi = UNITS_WH[i][0] * (1 - roti[i]) + UNITS_WH[i][1] * roti[i]
    heffi = UNITS_WH[i][1] * (1 - roti[i]) + UNITS_WH[i][0] * roti[i]

    xi[i] + weffi <= CHIP_WIDTH
    yi[i] + heffi <= H

    for j in range(i + 1, len(UNITS_WH)):
        weffj = UNITS_WH[j][0] * (1 - roti[j]) + UNITS_WH[j][1] * roti[j]
        heffj = UNITS_WH[j][1] * (1 - roti[j]) + UNITS_WH[j][0] * roti[j]

        xi[i] + weffi <= xi[j] + Mx * (1 - lij[i][j])
        xi[j] + weffj <= xi[i] + Mx * (1 - rij[i][j])
        yi[i] + heffi <= yi[j] + My * (1 - bij[i][j])
        yi[j] + heffj <= yi[i] + My * (1 - aij[i][j])
        lij[i][j] + rij[i][j] + bij[i][j] + aij[i][j] == 1

# Constraints for HPWL
for k, net in enumerate(NETS):
    for (bi, ox, oy) in net['pins']:
        wi_b, hi_b = UNITS_WH[bi]

        # Linear pin coordinates with rotation
        pin_x = xi[bi] + ox + (hi_b - oy - ox) * roti[bi]
        pin_y = yi[bi] + oy + (ox - oy) * roti[bi]

        # Bounding-box constraints
        xm[k] <= pin_x   # x⁻_N ≤ pin_x (left bound)
        pin_x <= xp[k]   # pin_x ≤ x⁺_N (right bound)
        ym[k] <= pin_y   # y⁻_N ≤ pin_y (lower bound)
        pin_y <= yp[k]   # pin_y ≤ y⁺_N (upper bound)

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

u.plot_packing_full(
    x, y, w_plot, h_plot, CHIP_WIDTH, H_val,
    nets=NETS,
    units_wh=UNITS_WH,
    roti=[roti[i].primal for i in range(len(UNITS_WH))],
    labels=UNITS_LABELS
)
```

The following results are then obtained:

<img width="1000" height="700" alt="image" src="https://github.com/user-attachments/assets/197c1b2e-9780-4847-a171-0b538f8c104b" />

If we now pose a more demanding problem — placing the same chip at $W = 60$, this time fixing the *MOD* block, the largest unit, at the bottom-left of the chip ourselves (to reduce the very large number of operations the program has to perform), and letting it run for a considerable amount of time (~18,127.5 seconds, or **5 hours**) — a nicer result is obtained, one that highlights the strength of the algorithm:

<img width="1000" height="700" alt="image" src="https://github.com/user-attachments/assets/dd5635cb-7e3e-4b48-bdbb-71f6dc41bc16" />

---

## References

Lecture notes from the course *Linear and Combinatorial Optimization*, 2026.

J. Funke, S. Hougardy, and J. Schneider, "An exact algorithm for wirelength optimal placements in VLSI design," *INTEGRATION, the VLSI Journal*, vol. 52, pp. 355–366, 2016.

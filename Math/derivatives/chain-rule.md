<pre><code>```graph
# Set the bounding box and axis ticks
bbox: [-10, 10, 10, -10]
ticks: { x: 2, y: 2 }
grid: true

# Define functions
function: f(x) = x^2 - 4x + 3 [domain: -2..6] color=#007acc width=2
function: g(x) = -x + 5 [domain: -2..6] color=orange dashed

# Points
point: A = (1, f(1)) label="$A(1,\ f(1))$" color=blue size=3
point: B = (4, g(4)) label="$B(4,\ g(4))$" color=red size=3
point: C = intersection(f, g) label="$C$" color=green size=4

# Line through points
line: A-B color=gray width=1

# Segment and distance
segment: A-C color=purple label="dist(A, C)" showLabel=true

# Arrows and annotations
arrow: (2, f(2)) -> (2, g(2)) color=black label="Gap" head=full

# Text box with LaTeX
text: (5, 8) "$f(x)$ and $g(x)$ intersect at C" size=2

# Highlight region between two curves
area: f(x) to g(x) [domain: 1..4] color=rgba(0,128,0,0.2)

# Sliders (dynamic parameters)
slider: a = 1 [range: -5..5] label="Slope a" position=(6, -8)
function: h(x) = a * x [domain: -6..6] color=magenta

# Parametric curve
parametric: (cos(t), sin(t)) [t: 0..2π] color=teal width=1

# Polar curve
polar: r = 2 * sin(4θ) [θ: 0..2π] color=violet
```</code></pre>

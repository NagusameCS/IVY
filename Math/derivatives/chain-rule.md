# Chain Rule

The chain rule is used to differentiate compositions of functions.

## Statement

If \( y = f(g(x)) \), then:

\[
\frac{dy}{dx} = f'(g(x)) \cdot g'(x)
\]

## Example

Let \( y = \sin(x^2) \).  
Then:

\[
\frac{dy}{dx} = \cos(x^2) \cdot 2x
\]

## Graph

```plotly
{
  "data": [
    {
      "x": [-3, -2, -1, 0, 1, 2, 3],
      "y": [0.1411, -0.9093, -0.8415, 0, 0.8415, 0.9093, -0.1411],
      "type": "scatter",
      "name": "sin(x²)"
    }
  ],
  "layout": {
    "title": "Graph of y = sin(x²)",
    "xaxis": { "title": "x" },
    "yaxis": { "title": "y" }
  }
}

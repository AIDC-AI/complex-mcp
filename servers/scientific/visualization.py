# visualization.py
from io import BytesIO
from typing import Annotated, List
from pydantic import Field
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from fastmcp import Image

try:
    from mcp.server.fastmcp import Image  # 你的原始导入
except ImportError:
    # 如果失败，可替换为通用结构（如返回 dict 或 bytes）
    class Image:
        def __init__(self, data: bytes, format: str):
            self.data = data
            self.format = format

from sympy import symbols
import sympy as sp
from sympy.parsing.sympy_parser import (
    standard_transformations,
    implicit_multiplication_application,
    convert_xor,
    parse_expr,
)

# Symbol setup
x, y, z = symbols("x y z")
transforms = standard_transformations + (implicit_multiplication_application, convert_xor)
local_ns = {
    "x": x, "y": y, "z": z,
    "sin": sp.sin, "cos": sp.cos,
    "tan": sp.tan, "exp": sp.exp, "log": sp.log,
    "sqrt": sp.sqrt
}


def register_tools(mcp):
    @mcp.tool()
    def plot_vector_field(
        f_str: str,
        bounds: Annotated[
            List[float],
            Field(
                min_length=6,
                max_length=6,
                description="Bounds as [xmin, xmax, ymin, ymax, zmin, zmax]",
                examples=[[-1.0, 1.0, -1.0, 1.0, -1.0, 1.0]]
            )
        ] = [-1.0, 1.0, -1.0, 1.0, -1.0, 1.0],
        n: int = 10
    ) -> Image:
        """
        Plots a 3D vector field from a string "[u(x,y,z), v(x,y,z), w(x,y,z)]"

        Args:
            f_str: string representation of 3D field, e.g. "[z, -y, x]".
            bounds: [xmin, xmax, ymin, ymax, zmin, zmax]
            n: grid resolution per axis

        Returns:
            PNG image of the 3D quiver plot.
        """
        # Parse vector components
        raw = f_str.strip().lstrip("[").rstrip("]")
        u_s, v_s, w_s = [s.strip() for s in raw.split(",")]

        u_expr = parse_expr(u_s, local_dict=local_ns, transformations=transforms)
        v_expr = parse_expr(v_s, local_dict=local_ns, transformations=transforms)
        w_expr = parse_expr(w_s, local_dict=local_ns, transformations=transforms)

        # Convert to numpy functions
        u_fn = sp.lambdify((x, y, z), u_expr, "numpy")
        v_fn = sp.lambdify((x, y, z), v_expr, "numpy")
        w_fn = sp.lambdify((x, y, z), w_expr, "numpy")

        # Unpack bounds
        xmin, xmax, ymin, ymax, zmin, zmax = bounds

        # Create 3D grid
        X, Y, Z = np.meshgrid(
            np.linspace(xmin, xmax, n),
            np.linspace(ymin, ymax, n),
            np.linspace(zmin, zmax, n),
            indexing="ij"
        )

        try:
            U = u_fn(X, Y, Z)
            V = v_fn(X, Y, Z)
            W = w_fn(X, Y, Z)

            fig = Figure(figsize=(8, 6))
            canvas = FigureCanvas(fig)
            ax = fig.add_subplot(projection="3d")
            ax.quiver(X, Y, Z, U, V, W, length=0.1, normalize=True, color="blue")
            ax.set_xlabel("X")
            ax.set_ylabel("Y")
            ax.set_zlabel("Z")
            ax.set_title(f"3D Vector Field: {f_str}")

            buf = BytesIO()
            canvas.print_png(buf)
            return Image(data=buf.getvalue(), format="png")

        except Exception as e:
            raise ValueError(f"Error plotting vector field: {e}")

    @mcp.tool()
    def plot_function(
        expr_str: str,
        xlim: Annotated[
            List[float],
            Field(
                min_length=2,
                max_length=2,
                description="X-axis limits as [min, max]",
                examples=[[-5.0, 5.0]]
            )
        ] = [-5.0, 5.0],
        ylim: Annotated[
            List[float],
            Field(
                min_length=2,
                max_length=2,
                description="Y-axis limits as [min, max] (used only for 3D plots)",
                examples=[[-5.0, 5.0]]
            )
        ] = [-5.0, 5.0],
        grid: int = 200
    ) -> Image:
        """
        Plots a 2D or 3D mathematical function from a symbolic expression string.

        Args:
            expr_str: Function in x (e.g., "x**2") or x,y (e.g., "sin(sqrt(x**2 + y**2))")
            xlim: [xmin, xmax]
            ylim: [ymin, ymax] (ignored in 2D)
            grid: Plot resolution

        Returns:
            PNG image of the plot (2D line or 3D surface).
        """
        expr = parse_expr(expr_str, transformations=transforms, local_dict=local_ns)
        vars_used = expr.free_symbols

        fig = Figure()
        buf = BytesIO()

        if vars_used <= {x}:  # Only x or constant
            f_num = sp.lambdify(x, expr, modules=["numpy"])
            xs = np.linspace(xlim[0], xlim[1], grid)
            ys = f_num(xs)

            ax = fig.add_subplot()
            ax.plot(xs, ys, color="blue")
            ax.axhline(0, color="black", linewidth=0.8)
            ax.axvline(0, color="black", linewidth=0.8)
            ax.set_xlabel("x")
            ax.set_ylabel("f(x)")
            ax.set_title(f"f(x) = {expr_str}")

        elif vars_used >= {x, y}:  # Contains both x and y
            f_num = sp.lambdify((x, y), expr, modules=["numpy"])
            xs = np.linspace(xlim[0], xlim[1], grid)
            ys = np.linspace(ylim[0], ylim[1], grid)
            X, Y = np.meshgrid(xs, ys)
            Z = f_num(X, Y)

            ax = fig.add_subplot(projection="3d")
            surf = ax.plot_surface(X, Y, Z, cmap="viridis", edgecolor="none")
            fig.colorbar(surf, ax=ax, shrink=0.6)
            ax.set_title(f"f(x, y) = {expr_str}")
            ax.set_xlabel("x")
            ax.set_ylabel("y")
            ax.set_zlabel("f(x, y)")

        else:
            raise ValueError("Only functions of x (2D) or x and y (3D) are supported.")

        canvas = FigureCanvas(fig)
        canvas.print_png(buf)
        return Image(data=buf.getvalue(), format="png")
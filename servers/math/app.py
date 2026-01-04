from fastmcp import FastMCP
import math

mcp = FastMCP("MathServer")

@mcp.tool
async def add(a: float, b: float) -> float:
    """Adds a and b together."""
    return a + b

@mcp.tool
async def sub(a: float, b: float) -> float:
    """Subtracts b from a."""
    return a - b

@mcp.tool
async def mul(a: float, b: float) -> float:
    """Multiplies two numbers together."""
    return a * b

@mcp.tool
async def div(a: float, b: float) -> float:
    """Divides a by b."""
    if b == 0:
        raise ValueError("Division by zero")
    return a / b

@mcp.tool
async def pow(a: float, b: float) -> float:
    """Raises a to the power of b."""
    return a ** b

@mcp.tool
async def sqrt(a: float) -> float:
    """Calculates the square root of a."""
    if a < 0:
        raise ValueError("Square root of negative number")
    return a ** 0.5

@mcp.tool
async def abs_val(a: float) -> float:
    """Returns the absolute value of a."""
    return abs(a)

@mcp.tool
async def mod(a: float, b: float) -> float:
    """Finds the remainder of a divided by b."""
    if b == 0:
        raise ValueError("Modulo by zero")
    return a % b

@mcp.tool
async def floor_div(a: float, b: float) -> float:
    """Performs floor division of a by b."""
    if b == 0:
        raise ValueError("Division by zero")
    return a // b

@mcp.tool
async def max_val(a: float, b: float) -> float:
    """Returns the maximum of a and b."""
    return max(a, b)

@mcp.tool
async def min_val(a: float, b: float) -> float:
    """Returns the minimum of a and b."""
    return min(a, b)

@mcp.tool
async def round_val(a: float, ndigits: int = 0) -> float:
    """Rounds a to the given number of decimal places."""
    return round(a, ndigits)

@mcp.tool
async def log(a: float, base: float = 10) -> float:
    """Calculates the logarithm of a with the given base."""
    if a <= 0:
        raise ValueError("Logarithm of non-positive number")
    return math.log(a, base)

@mcp.tool
async def exp(a: float) -> float:
    """Calculates e raised to the power of a."""
    return math.exp(a)

@mcp.tool
async def sin(a: float) -> float:
    """Calculates the sine of a (in radians)."""
    return math.sin(a)

@mcp.tool
async def cos(a: float) -> float:
    """Calculates the cosine of a (in radians)."""
    return math.cos(a)

@mcp.tool
async def tan(a: float) -> float:
    """Calculates the tangent of a (in radians)."""
    return math.tan(a)

@mcp.tool
async def asin(a: float) -> float:
    """Calculates the arcsine of a."""
    if a < -1 or a > 1:
        raise ValueError("Input out of domain for arcsine")
    return math.asin(a)

@mcp.tool
async def acos(a: float) -> float:
    """Calculates the arccosine of a."""
    if a < -1 or a > 1:
        raise ValueError("Input out of domain for arccosine")
    return math.acos(a)

@mcp.tool
async def atan(a: float) -> float:
    """Calculates the arctangent of a."""
    return math.atan(a)

@mcp.tool
async def sinh(a: float) -> float:
    """Calculates the hyperbolic sine of a."""
    return math.sinh(a)

@mcp.tool
async def cosh(a: float) -> float:
    """Calculates the hyperbolic cosine of a."""
    return math.cosh(a)

@mcp.tool
async def tanh(a: float) -> float:
    """Calculates the hyperbolic tangent of a."""
    return math.tanh(a)

@mcp.tool
async def factorial(a: int) -> int:
    """Calculates the factorial of a."""
    if a < 0:
        raise ValueError("Factorial of negative number")
    return math.factorial(a)

@mcp.tool
async def gcd(a: int, b: int) -> int:
    """Calculates the greatest common divisor of a and b."""
    return math.gcd(a, b)

@mcp.tool
async def lcm(a: int, b: int) -> int:
    """Calculates the least common multiple of a and b."""
    if a == 0 or b == 0:
        return 0
    return abs(a * b) // math.gcd(a, b)

@mcp.tool
async def deg_to_rad(a: float) -> float:
    """Converts degrees to radians."""
    return math.radians(a)

@mcp.tool
async def rad_to_deg(a: float) -> float:
    """Converts radians to degrees."""
    return math.degrees(a)

@mcp.tool
async def is_even(a: int) -> bool:
    """Checks if a number is even."""
    return a % 2 == 0

@mcp.tool
async def is_odd(a: int) -> bool:
    """Checks if a number is odd."""
    return a % 2 != 0

@mcp.tool
async def is_prime(a: int) -> bool:
    """Checks if a number is prime."""
    if a <= 1:
        return False
    for i in range(2, int(a ** 0.5) + 1):
        if a % i == 0:
            return False
    return True

@mcp.tool
async def nth_fibonacci(n: int) -> int:
    """Calculates the nth Fibonacci number."""
    if n <= 0:
        raise ValueError("Fibonacci number index must be positive")
    a, b = 0, 1
    for _ in range(n - 1):
        a, b = b, a + b
    return b

@mcp.tool
async def sum_of_list(numbers: list[float]) -> float:
    """Calculates the sum of a list of numbers."""
    return sum(numbers)

@mcp.tool
async def product_of_list(numbers: list[float]) -> float:
    """Calculates the product of a list of numbers."""
    result = 1
    for num in numbers:
        result *= num
    return result

@mcp.tool
async def mean(numbers: list[float]) -> float:
    """Calculates the mean of a list of numbers."""
    if not numbers:
        raise ValueError("Mean of empty list")
    return sum(numbers) / len(numbers)

@mcp.tool
async def median(numbers: list[float]) -> float:
    """Calculates the median of a list of numbers."""
    if not numbers:
        raise ValueError("Median of empty list")
    sorted_numbers = sorted(numbers)
    n = len(sorted_numbers)
    mid = n // 2
    if n % 2 == 0:
        return (sorted_numbers[mid - 1] + sorted_numbers[mid]) / 2
    return sorted_numbers[mid]

@mcp.tool
async def mode(numbers: list[float]) -> float:
    """Calculates the mode of a list of numbers."""
    if not numbers:
        raise ValueError("Mode of empty list")
    return max(set(numbers), key=numbers.count)

@mcp.tool
async def variance(numbers: list[float]) -> float:
    """Calculates the variance of a list of numbers."""
    if not numbers:
        raise ValueError("Variance of empty list")
    mean_val = sum(numbers) / len(numbers)
    return sum((x - mean_val) ** 2 for x in numbers) / len(numbers)

@mcp.tool
async def standard_deviation(numbers: list[float]) -> float:
    """Calculates the standard deviation of a list of numbers."""
    return math.sqrt(await variance(numbers))

@mcp.tool
async def clamp(value: float, min_val: float, max_val: float) -> float:
    """Clamps a value between min_val and max_val."""
    return max(min_val, min(value, max_val))

@mcp.tool
async def hypot(a: float, b: float) -> float:
    """Calculates the hypotenuse of a right triangle with sides a and b."""
    return math.hypot(a, b)

@mcp.tool
async def cbrt(a: float) -> float:
    """Calculates the cube root of a."""
    return a ** (1 / 3)
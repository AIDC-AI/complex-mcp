from fastmcp import FastMCP
import math
import re

mcp = FastMCP("ChemServer")


PERIODIC = {
    'H': 1.008,
    'C': 12.011,
    'N': 14.007,
    'O': 15.999,
    'Cl': 35.45,
    'Na': 22.99,
    'S': 32.06,
    'P': 30.974,
}


@mcp.tool
async def molar_mass(formula: str) -> float:
    """Compute an approximate molar mass for `formula` using a small periodic table.

    This is a naive parser that matches element symbols followed by optional integer counts.
    Unknown elements contribute 0.0.
    """
    # very naive parser: element symbols followed by optional integer
    parts = re.findall(r"([A-Z][a-z]?)(\d*)", formula)
    mass = 0.0
    for el, num in parts:
        n = int(num) if num else 1
        mass += PERIODIC.get(el, 0.0) * n
    return mass


@mcp.tool
async def empirical_formula(formula: str) -> str:
    """Return the empirical (reduced) formula for `formula` by dividing element counts by their GCD."""
    parts = re.findall(r"([A-Z][a-z]?)(\d*)", formula)
    counts = {}
    for el, num in parts:
        counts[el] = counts.get(el, 0) + (int(num) if num else 1)
    # reduce by gcd
    from math import gcd

    vals = list(counts.values())
    g = vals[0]
    for v in vals[1:]:
        g = gcd(g, v)
    return ''.join(f"{el}{counts[el]//g if counts[el]//g>1 else ''}" for el in sorted(counts))


@mcp.tool
async def percent_composition(formula: str) -> dict:
    """Return percent by mass composition for each element in `formula`.

    Percentages sum to (approximately) 100 for known elements in the small periodic table.
    """
    mm = await molar_mass.fn(formula)
    parts = re.findall(r"([A-Z][a-z]?)(\d*)", formula)
    comp = {}
    for el, num in parts:
        n = int(num) if num else 1
        comp[el] = PERIODIC.get(el, 0.0) * n / mm * 100 if mm else 0
    return comp


@mcp.tool
async def balance_simple_reaction(reactants: dict, products: dict) -> dict:
    """Placeholder reaction balancer: returns input mapping unchanged.

    This function is a stub for offline use and does not perform true balancing.
    """
    # naive: return same as input (placeholder offline tool)
    return {"reactants": reactants, "products": products}


@mcp.tool
async def is_balanced(formula: str) -> bool:
    """Placeholder validator that currently always returns True for a formula's balance."""
    # placeholder: always True
    return True


@mcp.tool
async def ph_from_concentration(h_conc: float) -> float:
    """Convert hydrogen ion concentration `h_conc` (mol/L) to pH value."""
    if h_conc <= 0:
        raise ValueError("invalid")
    return -math.log10(h_conc)


@mcp.tool
async def concentration_from_ph(ph: float) -> float:
    """Convert pH value back to hydrogen ion concentration (mol/L)."""
    return 10 ** (-ph)


@mcp.tool
async def ideal_gas_pressure(n_moles: float, temp_k: float, volume_l: float) -> float:
    """Compute pressure (in SI units of kPa equivalently via ideal gas law) for given moles, temperature, and volume.

    Note: this uses a simple ideal gas approximation and performs unit conversions from liters.
    """
    # R in L*kPa/(mol*K) -> return kPa
    R = 8.31446261815324  # J/(mol*K)
    # convert volume liters to m^3
    V = volume_l / 1000.0
    return n_moles * R * temp_k / V


@mcp.tool
async def convert_moles_to_grams(moles: float, formula: str) -> float:
    """Convert an amount in `moles` of a substance with `formula` to mass in grams (approx)."""
    mm = await molar_mass.fn(formula)
    return moles * mm


@mcp.tool
async def convert_grams_to_moles(grams: float, formula: str) -> float:
    """Convert `grams` of a substance with `formula` to moles using approximate molar mass."""
    mm = await molar_mass.fn(formula)
    return grams / mm if mm else 0


@mcp.tool
async def normalize_formula(formula: str) -> str:
    """Return `formula` with whitespace removed for normalization."""
    return formula.replace(' ', '')


@mcp.tool
async def element_list(formula: str) -> list:
    """Return a list of element symbols present in `formula` in the order they appear."""
    return [el for el, _ in re.findall(r"([A-Z][a-z]?)(\d*)", formula)]


@mcp.tool
async def combustion_products(fuel_formula: str) -> dict:
    """Naive estimator of complete combustion products (CO2 and H2O) from a hydrocarbon `fuel_formula`.

    This is a heuristic estimator that assumes integer counts and complete combustion.
    """
    # naive: return CO2 and H2O counts based on C and H presence
    parts = dict(re.findall(r"([A-Z][a-z]?)(\d*)", fuel_formula))
    c = int(parts.get('C', '1'))
    h = int(parts.get('H', '0'))
    co2 = c
    h2o = h // 2
    return {'CO2': co2, 'H2O': h2o}


@mcp.tool
async def is_organic(formula: str) -> bool:
    """Return True if `formula` contains carbon (simple organic check)."""
    return 'C' in formula


@mcp.tool
async def simple_smiles_validate(smiles: str) -> bool:
    """Very small validator for a SMILES-like string: checks balanced parentheses only."""
    # placeholder: check parentheses balance
    stack = []
    for ch in smiles:
        if ch == '(':
            stack.append(ch)
        elif ch == ')':
            if not stack:
                return False
            stack.pop()
    return not stack


@mcp.tool
async def mole_fraction(partial_moles: float, total_moles: float) -> float:
    """Compute a mole fraction given `partial_moles` and `total_moles` (returns 0 if total is zero)."""
    return partial_moles / total_moles if total_moles else 0


@mcp.tool
async def clamp(value: float, lo: float, hi: float) -> float:
    """Clamp `value` between `lo` and `hi` and return the clamped float."""
    return max(lo, min(value, hi))


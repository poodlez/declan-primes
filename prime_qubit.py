"""
Prime-Quantum Correspondence: Core Module

Maps primes p ≡ 1 mod 12 to qubit states via dual factorization:
  - Gaussian integers Z[i]:  p = (a+bi)(a-bi)  → amplitude angle θ
  - Eisenstein integers Z[ω]: p = (c+dω)(c+dω²) → phase angle φ

Resulting qubit state: |ψ⟩ = cos(θ/2)|0⟩ + e^(iφ)·sin(θ/2)|1⟩
"""

import math

OMEGA_RE = -0.5
OMEGA_IM = math.sqrt(3) / 2


def is_prime(n):
    if n < 2:
        return False
    if n < 4:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True


def factor_gaussian(p):
    """Factor prime p in Z[i]. Returns (a, b, type) where p = (a+bi)(a-bi)."""
    if p == 2:
        return (1, 1, 'ramified')
    if p % 4 == 3:
        return (p, 0, 'inert')
    if p % 4 == 1:
        for a in range(1, int(math.isqrt(p)) + 1):
            b_sq = p - a * a
            b = int(math.isqrt(b_sq))
            if b * b == b_sq:
                return (max(a, b), min(a, b), 'split')
    return None


def factor_eisenstein(p):
    """Factor prime p in Z[ω]. Returns (a, b, type) where p = (a+bω)(a+bω²)."""
    if p == 3:
        return (1, 1, 'ramified')
    if p % 3 == 2:
        return (p, 0, 'inert')
    if p % 3 == 1:
        for a in range(0, p + 1):
            for b in range(1, p + 1):
                if a * a - a * b + b * b == p:
                    return (a, b, 'split')
    return None


def prime_to_qubit_angles(p):
    """
    For a prime p ≡ 1 mod 12, extract (theta, phi) from dual factorization.

    theta: from Gaussian factor angle, mapped to Bloch polar angle [0, pi]
        theta = 2 * arctan(b/a) where p = (a+bi)(a-bi)

    phi: from Eisenstein factor angle in complex plane
        phi = arg(c + d*omega) where p = (c+dω)(c+dω²)

    Returns dict with theta, phi, bloch_vector (x,y,z), and factor data.
    Returns None if prime doesn't split in both.
    """
    gf = factor_gaussian(p)
    ef = factor_eisenstein(p)

    if not gf or gf[2] != 'split' or not ef or ef[2] != 'split':
        return None

    a_g, b_g = gf[0], gf[1]
    a_e, b_e = ef[0], ef[1]

    # Theta from Gaussian
    theta = 2 * math.atan2(b_g, a_g)

    # Phi from Eisenstein
    e_re = a_e + b_e * OMEGA_RE
    e_im = b_e * OMEGA_IM
    phi = math.atan2(e_im, e_re)

    # Bloch vector
    x = math.sin(theta) * math.cos(phi)
    y = math.sin(theta) * math.sin(phi)
    z = math.cos(theta)

    # Qubit amplitudes
    alpha = math.cos(theta / 2)  # amplitude of |0>
    beta_mag = math.sin(theta / 2)  # magnitude of |1> amplitude

    return {
        'prime': p,
        'theta': theta,
        'phi': phi,
        'theta_deg': math.degrees(theta),
        'phi_deg': math.degrees(phi),
        'bloch': (x, y, z),
        'alpha': alpha,
        'beta_mag': beta_mag,
        'prob_0': alpha ** 2,
        'prob_1': beta_mag ** 2,
        'gaussian_factor': (a_g, b_g),
        'eisenstein_factor': (a_e, b_e),
    }


def get_mod12_primes(limit=500):
    """Get all primes ≡ 1 mod 12 up to limit."""
    return [p for p in range(2, limit + 1) if is_prime(p) and p % 12 == 1]

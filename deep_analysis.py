"""
Deep dive: Why do prime-derived qubit states cluster on the Bloch sphere?

Key questions:
1. Why is φ constrained to ~[91°, 118°]? Is this a fundamental constraint
   of the Eisenstein norm geometry, or does it open up for larger primes?
2. Is there a θ–φ correlation? Do the angles co-vary?
3. How does the distribution evolve as we go to larger primes?
4. What's the number-theoretic explanation for the clustering?
5. Are there hidden patterns in the Bloch vector coordinates?
"""

import math
import json
from prime_qubit import (
    prime_to_qubit_angles, get_mod12_primes, factor_gaussian,
    factor_eisenstein, OMEGA_RE, OMEGA_IM
)


def analyze_phi_constraint():
    """
    WHY is φ so narrow?

    φ = arg(a + bω) = atan2(b·sin(60°), a + b·cos(60°)) = atan2(b√3/2, a - b/2)

    But (a,b) aren't free — they satisfy a² - ab + b² = p.

    Let's look at the ratio b/a for Eisenstein factors and see what constrains φ.
    """
    print("=" * 70)
    print("ANALYSIS 1: Why is φ constrained?")
    print("=" * 70)
    print()
    print("φ = atan2(b·√3/2, a - b/2)  where  a² - ab + b² = p")
    print()
    print("The Eisenstein norm a² - ab + b² can be rewritten as:")
    print("  (a - b/2)² + (b√3/2)²  =  p")
    print()
    print("So if we define  u = a - b/2  and  v = b√3/2:")
    print("  u² + v² = p  and  φ = atan2(v, u)")
    print()
    print("This means (u,v) lies on a circle of radius √p!")
    print("But u and v aren't free — they're derived from INTEGER a,b.")
    print()
    print("Constraint: b ≥ 1 (we require splitting), a ≥ 0")
    print("  → v = b√3/2 > 0  always (so φ ∈ (0°, 180°))")
    print("  → u = a - b/2 can be positive, zero, or negative")
    print()

    # Let's see what actually happens
    limits = [500, 2000, 10000, 50000]
    for limit in limits:
        primes = get_mod12_primes(limit)
        phis = []
        ratios = []
        for p in primes:
            d = prime_to_qubit_angles(p)
            if d:
                phis.append(d['phi_deg'])
                ef = d['eisenstein_factor']
                a, b = ef
                u = a - b/2
                v = b * OMEGA_IM
                ratios.append(v / u if u != 0 else float('inf'))

        if phis:
            print(f"  Primes ≤ {limit:>6d}: n={len(phis):>4d}  "
                  f"φ ∈ [{min(phis):.1f}°, {max(phis):.1f}°]  "
                  f"mean={sum(phis)/len(phis):.1f}°  "
                  f"std={math.sqrt(sum((x-sum(phis)/len(phis))**2 for x in phis)/len(phis)):.1f}°")


def analyze_theta_constraint():
    """
    Same analysis for θ.

    θ = 2·atan2(b, a) where a² + b² = p and a > b > 0

    Since a > b (by our convention), atan2(b,a) ∈ (0, π/4)
    So θ ∈ (0, π/2) = (0°, 90°)

    This is a hard geometric constraint!
    """
    print()
    print("=" * 70)
    print("ANALYSIS 2: Why is θ constrained to (0°, 90°)?")
    print("=" * 70)
    print()
    print("θ = 2·atan2(b, a)  where  a² + b² = p  and  a ≥ b > 0")
    print()
    print("Since a ≥ b, we have atan2(b,a) ∈ (0, π/4]")
    print("→ θ ∈ (0°, 90°]")
    print()
    print("θ = 90° only when a = b, i.e., p = 2a². But p prime means p = 2 (trivial).")
    print("So for p > 2: θ ∈ (0°, 90°) strictly.")
    print()
    print("This means all prime qubits live in the NORTHERN hemisphere of the Bloch sphere!")
    print("z = cos(θ) > 0 always → P(|0⟩) > 50% for every prime.")
    print()

    limits = [500, 2000, 10000, 50000]
    for limit in limits:
        primes = get_mod12_primes(limit)
        thetas = []
        for p in primes:
            d = prime_to_qubit_angles(p)
            if d:
                thetas.append(d['theta_deg'])

        if thetas:
            print(f"  Primes ≤ {limit:>6d}: n={len(thetas):>4d}  "
                  f"θ ∈ [{min(thetas):.2f}°, {max(thetas):.2f}°]  "
                  f"mean={sum(thetas)/len(thetas):.1f}°  "
                  f"std={math.sqrt(sum((x-sum(thetas)/len(thetas))**2 for x in thetas)/len(thetas)):.1f}°")


def analyze_uv_geometry():
    """
    The Eisenstein factor (a,b) maps to (u,v) = (a - b/2, b√3/2) on a circle
    of radius √p. The angle φ = atan2(v,u).

    What determines where on this circle the integer solution lands?
    """
    print()
    print("=" * 70)
    print("ANALYSIS 3: Eisenstein (u,v) geometry on the √p circle")
    print("=" * 70)
    print()

    primes = get_mod12_primes(2000)
    print(f"  {'p':>6s}  {'a':>4s}  {'b':>4s}  {'u=a-b/2':>8s}  {'v=b√3/2':>8s}  "
          f"{'φ (deg)':>8s}  {'u/√p':>6s}  {'v/√p':>6s}  {'b/a':>6s}")
    print("  " + "-" * 80)

    phi_data = []
    for p in primes[:40]:
        d = prime_to_qubit_angles(p)
        if d:
            a, b = d['eisenstein_factor']
            u = a - b / 2
            v = b * OMEGA_IM
            sqp = math.sqrt(p)
            phi_data.append({
                'p': p, 'a': a, 'b': b, 'u': u, 'v': v,
                'phi': d['phi_deg'], 'u_norm': u/sqp, 'v_norm': v/sqp,
                'ratio': b/a if a > 0 else float('inf')
            })
            print(f"  {p:>6d}  {a:>4d}  {b:>4d}  {u:>8.2f}  {v:>8.2f}  "
                  f"{d['phi_deg']:>8.2f}  {u/sqp:>6.3f}  {v/sqp:>6.3f}  "
                  f"{b/a if a>0 else float('inf'):>6.3f}")

    print()
    print("  Key insight: u/√p and v/√p give the position on the UNIT circle.")
    print("  φ is determined by this position. Let's see the distribution of u/√p:")

    # For larger dataset
    all_u_norm = []
    all_v_norm = []
    for p in get_mod12_primes(50000):
        d = prime_to_qubit_angles(p)
        if d:
            a, b = d['eisenstein_factor']
            u = a - b / 2
            v = b * OMEGA_IM
            sqp = math.sqrt(p)
            all_u_norm.append(u / sqp)
            all_v_norm.append(v / sqp)

    print(f"\n  For {len(all_u_norm)} primes ≤ 50000:")
    print(f"    u/√p ∈ [{min(all_u_norm):.4f}, {max(all_u_norm):.4f}]  mean={sum(all_u_norm)/len(all_u_norm):.4f}")
    print(f"    v/√p ∈ [{min(all_v_norm):.4f}, {max(all_v_norm):.4f}]  mean={sum(all_v_norm)/len(all_v_norm):.4f}")


def analyze_theta_phi_correlation():
    """
    Is there a correlation between θ and φ?
    """
    print()
    print("=" * 70)
    print("ANALYSIS 4: θ–φ correlation")
    print("=" * 70)

    primes = get_mod12_primes(10000)
    thetas = []
    phis = []
    for p in primes:
        d = prime_to_qubit_angles(p)
        if d:
            thetas.append(d['theta_deg'])
            phis.append(d['phi_deg'])

    n = len(thetas)
    t_mean = sum(thetas) / n
    p_mean = sum(phis) / n
    t_std = math.sqrt(sum((t - t_mean)**2 for t in thetas) / n)
    p_std = math.sqrt(sum((p - p_mean)**2 for p in phis) / n)

    # Pearson correlation
    cov = sum((thetas[i] - t_mean) * (phis[i] - p_mean) for i in range(n)) / n
    corr = cov / (t_std * p_std) if t_std > 0 and p_std > 0 else 0

    print(f"\n  n = {n} primes ≡ 1 mod 12 up to 10000")
    print(f"  Pearson correlation(θ, φ) = {corr:.4f}")
    print(f"  {'Weak' if abs(corr) < 0.3 else 'Moderate' if abs(corr) < 0.7 else 'Strong'} "
          f"{'positive' if corr > 0 else 'negative'} correlation")
    print()

    # Bin by theta and look at phi
    bins = [(0, 20), (20, 40), (40, 60), (60, 80), (80, 90)]
    print("  φ distribution binned by θ:")
    for lo, hi in bins:
        bin_phis = [phis[i] for i in range(n) if lo <= thetas[i] < hi]
        if bin_phis:
            print(f"    θ ∈ [{lo}°,{hi}°): n={len(bin_phis):>4d}  "
                  f"φ mean={sum(bin_phis)/len(bin_phis):.1f}°  "
                  f"std={math.sqrt(sum((x-sum(bin_phis)/len(bin_phis))**2 for x in bin_phis)/len(bin_phis)):.1f}°  "
                  f"range=[{min(bin_phis):.1f}°, {max(bin_phis):.1f}°]")


def analyze_approach_to_boundaries():
    """
    As primes get larger, do θ and φ explore more of their range?
    Or do they converge?
    """
    print()
    print("=" * 70)
    print("ANALYSIS 5: Asymptotic behavior — do ranges widen with larger primes?")
    print("=" * 70)

    # Check in bands
    bands = [(0, 100), (100, 500), (500, 2000), (2000, 10000), (10000, 50000)]

    print(f"\n  {'Prime band':>16s}  {'n':>5s}  {'θ range':>20s}  {'φ range':>20s}")
    print("  " + "-" * 70)

    for lo, hi in bands:
        primes = [p for p in get_mod12_primes(hi) if p >= lo]
        thetas = []
        phis = []
        for p in primes:
            d = prime_to_qubit_angles(p)
            if d:
                thetas.append(d['theta_deg'])
                phis.append(d['phi_deg'])
        if thetas:
            print(f"  {lo:>7d}–{hi:<7d}  {len(thetas):>5d}  "
                  f"[{min(thetas):>6.2f}°, {max(thetas):>6.2f}°]  "
                  f"[{min(phis):>6.2f}°, {max(phis):>6.2f}°]")


def analyze_factorization_multiplicity():
    """
    For larger primes, there may be MULTIPLE Eisenstein factorizations
    (different (a,b) pairs with a² - ab + b² = p). Our brute force
    finds the first one. How many are there? Do different choices give
    different φ values?
    """
    print()
    print("=" * 70)
    print("ANALYSIS 6: Multiple factorizations — does choice matter?")
    print("=" * 70)

    primes = get_mod12_primes(2000)

    print(f"\n  {'p':>6s}  {'# Gauss':>8s}  {'# Eisen':>8s}  Gaussian pairs            Eisenstein pairs")
    print("  " + "-" * 85)

    for p in primes[:30]:
        # Find ALL Gaussian factorizations
        g_facts = []
        for a in range(1, int(math.isqrt(p)) + 1):
            b_sq = p - a * a
            b = int(math.isqrt(b_sq))
            if b > 0 and b * b == b_sq:
                g_facts.append((max(a, b), min(a, b)))

        # Find ALL Eisenstein factorizations
        e_facts = []
        for a in range(0, int(math.sqrt(p)) + 2):
            for b in range(1, int(math.sqrt(p)) + 2):
                if a * a - a * b + b * b == p:
                    e_facts.append((a, b))

        g_str = ", ".join(f"({a}+{b}i)" for a, b in g_facts)
        e_str = ", ".join(f"({a}+{b}ω)" for a, b in e_facts)

        # Different phi values from different Eisenstein factorizations
        phi_vals = []
        for a, b in e_facts:
            e_re = a + b * OMEGA_RE
            e_im = b * OMEGA_IM
            phi_vals.append(math.degrees(math.atan2(e_im, e_re)))

        print(f"  {p:>6d}  {len(g_facts):>8d}  {len(e_facts):>8d}  {g_str:<24s}  {e_str}")
        if len(e_facts) > 1:
            print(f"          → φ values: {', '.join(f'{v:.1f}°' for v in phi_vals)}")


def analyze_bloch_density():
    """
    Where exactly on the Bloch sphere do primes cluster?
    Let's look at the (x,y,z) distribution more carefully.
    """
    print()
    print("=" * 70)
    print("ANALYSIS 7: Bloch sphere clustering — where exactly?")
    print("=" * 70)

    primes = get_mod12_primes(10000)
    xs, ys, zs = [], [], []
    for p in primes:
        d = prime_to_qubit_angles(p)
        if d:
            xs.append(d['bloch'][0])
            ys.append(d['bloch'][1])
            zs.append(d['bloch'][2])

    n = len(xs)
    print(f"\n  n = {n} primes")
    print(f"  x: mean={sum(xs)/n:.4f}  std={math.sqrt(sum((v-sum(xs)/n)**2 for v in xs)/n):.4f}  range=[{min(xs):.4f}, {max(xs):.4f}]")
    print(f"  y: mean={sum(ys)/n:.4f}  std={math.sqrt(sum((v-sum(ys)/n)**2 for v in ys)/n):.4f}  range=[{min(ys):.4f}, {max(ys):.4f}]")
    print(f"  z: mean={sum(zs)/n:.4f}  std={math.sqrt(sum((v-sum(zs)/n)**2 for v in zs)/n):.4f}  range=[{min(zs):.4f}, {max(zs):.4f}]")

    print()
    print("  Interpretation:")
    print(f"    x is mostly negative (mean {sum(xs)/n:.4f}) — Eisenstein phase pulls toward -x")
    print(f"    y is strongly positive (mean {sum(ys)/n:.4f}) — dominant component")
    print(f"    z is positive (mean {sum(zs)/n:.4f}) — northern hemisphere, P(|0⟩) > 50%")

    # What's the centroid direction?
    cx, cy, cz = sum(xs)/n, sum(ys)/n, sum(zs)/n
    cmag = math.sqrt(cx**2 + cy**2 + cz**2)
    print(f"\n  Centroid direction: ({cx/cmag:.3f}, {cy/cmag:.3f}, {cz/cmag:.3f})")
    centroid_theta = math.degrees(math.acos(cz/cmag))
    centroid_phi = math.degrees(math.atan2(cy, cx))
    print(f"  Centroid angles: θ={centroid_theta:.1f}°  φ={centroid_phi:.1f}°")
    print(f"  Centroid magnitude: {cmag:.4f} (1.0 would mean all states identical)")


def analyze_number_theory():
    """
    The mathematical explanation for the constraints.
    """
    print()
    print("=" * 70)
    print("ANALYSIS 8: Number-theoretic explanation")
    print("=" * 70)
    print("""
  WHY θ ∈ (0°, 90°):
  -------------------
  θ = 2·atan(b/a) where a > b > 0 and a² + b² = p.

  The constraint a > b is a normalization choice (we pick the canonical
  representative with larger real part). This forces atan(b/a) < π/4,
  hence θ < π/2 = 90°.

  As p → ∞, the ratio b/a can approach 1 (when a ≈ b ≈ √(p/2)),
  so θ can approach 90°. It can also approach 0° (when a ≈ √p, b ≈ 0).

  The actual distribution of b/a for Gaussian factors of primes p ≡ 1 mod 4
  is related to the equidistribution of Hecke L-function zeros, and it is
  known that the angles atan(b/a) become equidistributed in (0, π/4) as
  p → ∞ (Hecke's theorem). So θ should be asymptotically uniform in (0°, 90°).

  WHY φ ∈ (~60°, ~120°):
  -----------------------
  φ = arg(a + bω) where a ≥ 0, b ≥ 1, a² - ab + b² = p.

  The Eisenstein integers have 6-fold symmetry. The fundamental domain
  for Eisenstein primes maps to arg ∈ (0°, 60°) per sextant, but our
  convention of taking a ≥ 0, b ≥ 1 selects a specific sextant.

  Since ω = e^(2πi/3), the element a + bω has:
    Re = a - b/2
    Im = b√3/2

  For b ≥ 1: Im > 0 always (upper half plane).
  For a ≥ b: Re = a - b/2 ≥ b/2 > 0, so φ < 90°
  For a = 0: Re = -b/2 < 0, Im = b√3/2, so φ = 120° exactly
  For a < b: Re can be negative, pushing φ toward 120°

  The maximum φ approaches 120° (when a << b).
  The minimum φ approaches ~60° (when a >> b, but constrained by a²-ab+b²=p).

  Actually, for the FIRST (smallest a) solution found by our search:
  The range is approximately (60°, 120°), which is exactly ONE SEXTANT
  of the Eisenstein lattice. This is the fundamental domain!

  SIMILAR equidistribution theorems apply: Eisenstein prime angles should
  become uniform in the fundamental domain as p → ∞.

  WHY THE CLUSTERING (avg Bloch dist << 1.333):
  -----------------------------------------------
  The states cluster because:
  1. θ is confined to (0°, 90°) — only the northern hemisphere
  2. φ is confined to (~60°, ~120°) — only one sextant
  3. These are HARD geometric constraints, not statistical flukes

  The full Bloch sphere would require:
    θ ∈ (0°, 180°) and φ ∈ (0°, 360°)

  Our primes only access about 1/8 of the sphere surface:
    θ range: 90°/180° = 1/2
    φ range: 60°/360° = 1/6
    Combined: ~1/12 of the sphere

  To access the FULL sphere, we'd need to:
  - Allow both a > b AND a < b for Gaussian (gives θ up to 180°)
  - Use all 6 sextants of Eisenstein symmetry (gives φ full 360°)

  This is actually a FEATURE: the canonical factorization picks a
  unique representative, and the resulting qubit state lives in a
  well-defined region. Different canonicalization choices would map
  to different regions.
""")


def analyze_equidistribution():
    """
    Test whether angles approach equidistribution as primes get large
    (as predicted by Hecke's theorem).
    """
    print("=" * 70)
    print("ANALYSIS 9: Testing equidistribution (Hecke's theorem)")
    print("=" * 70)

    # Normalize θ to [0,1] range within (0, 90°) and φ to [0,1] within its range
    # Then check if distribution is approximately uniform via Kolmogorov-Smirnov-like test

    primes = get_mod12_primes(50000)
    thetas = []
    phis = []
    for p in primes:
        d = prime_to_qubit_angles(p)
        if d:
            thetas.append(d['theta_deg'])
            phis.append(d['phi_deg'])

    n = len(thetas)

    # Normalize θ to [0,1] within (0, 90)
    theta_norm = sorted([t / 90.0 for t in thetas])
    # KS statistic: max |F_empirical - F_uniform|
    ks_theta = max(abs(theta_norm[i] - (i + 0.5) / n) for i in range(n))

    # For φ, normalize within observed range
    phi_min, phi_max = min(phis), max(phis)
    phi_norm = sorted([(p - phi_min) / (phi_max - phi_min) for p in phis])
    ks_phi = max(abs(phi_norm[i] - (i + 0.5) / n) for i in range(n))

    # Expected KS stat for uniform: ~1.36/√n
    expected_ks = 1.36 / math.sqrt(n)

    print(f"\n  n = {n} primes ≡ 1 mod 12 up to 50000")
    print(f"\n  θ normalized to [0,1] within (0°, 90°):")
    print(f"    KS statistic = {ks_theta:.4f}")
    print(f"    Expected (uniform) ≈ {expected_ks:.4f}")
    print(f"    {'CONSISTENT with uniform' if ks_theta < 2 * expected_ks else 'DEVIATES from uniform'}")

    print(f"\n  φ normalized to [0,1] within ({phi_min:.1f}°, {phi_max:.1f}°):")
    print(f"    KS statistic = {ks_phi:.4f}")
    print(f"    Expected (uniform) ≈ {expected_ks:.4f}")
    print(f"    {'CONSISTENT with uniform' if ks_phi < 2 * expected_ks else 'DEVIATES from uniform'}")

    # Quartile analysis for θ
    q1 = sum(1 for t in thetas if t < 22.5) / n
    q2 = sum(1 for t in thetas if 22.5 <= t < 45) / n
    q3 = sum(1 for t in thetas if 45 <= t < 67.5) / n
    q4 = sum(1 for t in thetas if 67.5 <= t) / n

    print(f"\n  θ quartile distribution (should each be ~25% if uniform):")
    print(f"    [0°,  22.5°): {q1*100:.1f}%")
    print(f"    [22.5°, 45°): {q2*100:.1f}%")
    print(f"    [45°, 67.5°): {q3*100:.1f}%")
    print(f"    [67.5°, 90°): {q4*100:.1f}%")


def generate_data_for_site():
    """
    Generate a JSON blob of analysis data that can be embedded in the site.
    """
    print()
    print("=" * 70)
    print("GENERATING DATA FOR SITE INTEGRATION")
    print("=" * 70)

    primes = get_mod12_primes(1000)
    data = []
    for p in primes:
        d = prime_to_qubit_angles(p)
        if d:
            data.append({
                'p': p,
                'theta': round(d['theta_deg'], 2),
                'phi': round(d['phi_deg'], 2),
                'x': round(d['bloch'][0], 4),
                'y': round(d['bloch'][1], 4),
                'z': round(d['bloch'][2], 4),
                'p0': round(d['prob_0'], 4),
                'gf': list(d['gaussian_factor']),
                'ef': list(d['eisenstein_factor']),
            })

    with open('prime_qubit_data.json', 'w') as f:
        json.dump(data, f, indent=2)

    print(f"  Wrote {len(data)} prime entries to prime_qubit_data.json")

    return data


if __name__ == '__main__':
    analyze_phi_constraint()
    analyze_theta_constraint()
    analyze_uv_geometry()
    analyze_theta_phi_correlation()
    analyze_approach_to_boundaries()
    analyze_factorization_multiplicity()
    analyze_bloch_density()
    analyze_number_theory()
    analyze_equidistribution()
    generate_data_for_site()

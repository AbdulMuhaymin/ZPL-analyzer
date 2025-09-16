import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# Constants
h = 6.62607015e-34
c = 299792458
eV_to_J = 1.602176634e-19
Ry_to_eV = 13.605693122994

def ry_to_eV(energy_Ry):
    return energy_Ry * Ry_to_eV

def eV_to_nm(E_eV):
    if E_eV <= 0:
        return np.nan
    wavelength_m = (h * c) / (E_eV * eV_to_J)
    return wavelength_m * 1e9

st.title("Excitation Energy Calculator + Diagram")

E0 = st.number_input("E0 (Ground min, Ry)", value=0.0, format="%.6f")
E1 = st.number_input("E1 (Vertical excitation, Ry)", value=0.0, format="%.6f")
E2 = st.number_input("E2 (Excited min, Ry)", value=0.0, format="%.6f")
E3 = st.number_input("E3 (Intersection point, Ry)", value=0.0, format="%.6f")

# Energies
VEE_eV = ry_to_eV(E1 - E0)
VEE_nm = eV_to_nm(VEE_eV)

AEE_eV = ry_to_eV(E2 - E0)  # corrected formula
AEE_nm = eV_to_nm(AEE_eV)

st.subheader("Results")
st.write(f"**Vertical Excitation Energy (VEE):** {VEE_eV:.6f} eV")
if not np.isnan(VEE_nm):
    st.write(f"→ {VEE_nm:.2f} nm")
st.write(f"**Adiabatic Excitation Energy (AEE / ZPL):** {AEE_eV:.6f} eV")
if not np.isnan(AEE_nm):
    st.write(f"→ {AEE_nm:.2f} nm")

# --- Diagram ---
x = np.linspace(-2, 4, 400)
a = 0.5

# Parabolas
y0 = a * (x - 0)**2 + E0
y1 = a * (x - 1.5)**2 + E2

fig, ax = plt.subplots(figsize=(6,5))

ax.plot(x, y0, 'k-', lw=1.5)  # ground
ax.plot(x, y1, 'r-', lw=1.5)  # excited

# Points
ax.scatter([0], [E0], c='k', zorder=5)   # E0
ax.scatter([0], [E1], c='k', zorder=5)   # E1 (left shoulder)
ax.scatter([1.5], [E2], c='r', zorder=5) # E2
ax.scatter([2.5], [E3], c='g', zorder=5) # E3

# Arrow color for VEE
vee_color = "black"
if 400 <= AEE_nm <= 700:
    import matplotlib.cm as cm
    colormap = cm.get_cmap("nipy_spectral")
    vee_color = colormap((700 - AEE_nm) / 300)  # map wavelength to color

# Draw arrows
ax.annotate("", xy=(0, E1), xytext=(0, E0),
            arrowprops=dict(arrowstyle="->", color=vee_color, lw=2))
ax.text(0.1, (E0+E1)/2, "VEE", va="center")

ax.annotate("", xy=(1.5, E2), xytext=(0, E0),
            arrowprops=dict(arrowstyle="->", color="blue", lw=2))
ax.text(0.7, (E0+E2)/2, "ZPL", va="center", color="blue")

ax.annotate("", xy=(2.5, E3), xytext=(1.5, E2),
            arrowprops=dict(arrowstyle="->", color="green", lw=2))
ax.text(2.0, (E2+E3)/2, "Relax", va="center", color="green")

ax.axis("off")
st.pyplot(fig)

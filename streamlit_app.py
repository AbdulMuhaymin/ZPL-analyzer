import streamlit as st
import numpy as np

# Physical constants
h = 6.62607015e-34      # Planck constant (J·s)
c = 299792458           # Speed of light (m/s)
eV_to_J = 1.602176634e-19   # eV to J
Ry_to_eV = 13.605693122994  # 1 Rydberg = 13.605693122994 eV

st.title("Excitation Energy Calculator")

st.markdown("""
This app calculates:
- **Vertical Excitation Energy (VEE)**: E1 - E0  
- **Adiabatic Excitation Energy (AEE / ZPL)**: E2 - E3 (assuming zero-point energies cancel)  
Both reported in **eV** and corresponding **wavelength in nm**.
""")

# User inputs
E0 = st.number_input("E0 (Ground State, in Ry)", value=0.0, format="%.6f")
E1 = st.number_input("E1 (Excited State Vertical, in Ry)", value=0.0, format="%.6f")
E2 = st.number_input("E2 (Excited State Min, in Ry)", value=0.0, format="%.6f")
E3 = st.number_input("E3 (Ground State Min, in Ry)", value=0.0, format="%.6f")

# Compute energies
def ry_to_eV(energy_Ry):
    return energy_Ry * Ry_to_eV

def eV_to_nm(E_eV):
    if E_eV <= 0:
        return np.nan
    wavelength_m = (h * c) / (E_eV * eV_to_J)
    return wavelength_m * 1e9  # convert to nm

# Vertical Excitation Energy (VEE)
VEE_eV = ry_to_eV(E1 - E0)
VEE_nm = eV_to_nm(VEE_eV)

# Adiabatic Excitation Energy (AEE / ZPL)
AEE_eV = ry_to_eV(E2 - E3)
AEE_nm = eV_to_nm(AEE_eV)

st.subheader("Results")

st.write(f"**Vertical Excitation Energy (VEE):** {VEE_eV:.6f} eV")
if not np.isnan(VEE_nm):
    st.write(f"→ Wavelength: {VEE_nm:.2f} nm")

st.write(f"**Adiabatic Excitation Energy (AEE / ZPL):** {AEE_eV:.6f} eV")
if not np.isnan(AEE_nm):
    st.write(f"→ Wavelength: {AEE_nm:.2f} nm")

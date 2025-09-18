import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from streamlit_gsheets import GSheetsConnection

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

st.title("cDFT/ΔSCF result analyzer")
st.markdown(r"$Q_g$ : ground state geometry")
st.markdown(r"$Q_e$ : excited state geometry")

url = "https://docs.google.com/spreadsheets/d/1ftggc6tT1A_CzN4W3OuZmMQfIy_g9a4biBwlLNkki1c/edit?usp=sharing"

conn = st.connection("gsheets", type=GSheetsConnection)

data = conn.read(spreadsheet=url)
a=data.to_html().replace("NaN","")
st.html(a)
st.dataframe(data)

with st.form("input_form"):
    col1, col2 = st.columns(2)
    with col1:
        E0 = st.text_input("E0 (Ground state at $Q_g$, Ry)", "")
        E1 = st.text_input("E1 (Excited state at $Q_g$, Ry)", "")
    with col2:
        E2 = st.text_input("E2 (Excited state at $Q_e$, Ry)", "")
        E3 = st.text_input("E3 (Ground state at $Q_e$, Ry)", "")

    title = st.text_input("Plot title (optional)")

    submitted = st.form_submit_button("Calculate")

if submitted:
    if E0 and E1 and E2 and E3:  # all fields filled
        E0, E1, E2, E3 = float(E0), float(E1), float(E2), float(E3)
        # Energies
        VEE_eV = ry_to_eV(E1 - E0)
        VEE_nm = eV_to_nm(VEE_eV)

        AEE_eV = ry_to_eV(E2 - E0)  # corrected formula
        AEE_nm = eV_to_nm(AEE_eV)

        st.subheader("Results")
        st.write(f"**Vertical Excitation Energy (VEE):** {VEE_eV:.3f} eV → {VEE_nm:.2f} nm")
        st.write(f"**Adiabatic Excitation Energy (AEE / ZPL):** {AEE_eV:.3f} eV → {AEE_nm:.2f} nm")


        # Visible spectrum ranges (in eV)
        visible_map = [
            (1.77, 1.91, "red"),
            (1.91, 2.10, "orange"),
            (2.10, 2.17, "yellow"),
            (2.17, 2.33, "green"),
            (2.33, 2.64, "cyan"),
            (2.64, 3.10, "blue"),
        ]

        # Telecom bands (in eV)
        telecom_map = [
            (0.912, 0.984, "O-band telecom (1260–1360 nm)"),
            (0.849, 0.912, "E-band telecom (1360–1460 nm)"),
            (0.810, 0.849, "S-band telecom (1460–1530 nm)"),
            (0.793, 0.810, "C-band telecom (1530–1565 nm)"),
            (0.764, 0.793, "L-band telecom (1565–1625 nm)"),
            (0.740, 0.764, "U-band telecom (1625–1675 nm)"),
        ]

        # Merge all ranges
        band_map = visible_map + telecom_map

        # Default comment
        comment = ""

        # Loop through ranges
        for low, high, label in band_map:
            if low <= AEE_eV < high:
                comment = f"ZPL is {label}"
                break

        st.write(f"**Comments:** {comment}")


        # --- Diagram ---
        def plot_configuration_diagram(zpl):
            # x range
            x1 = np.linspace(2, 6, 200)
            x2 = np.linspace(3, 7, 200)
            k = .5  # parabola "curvature"

            # ground state parabola, min at (0,0)
            y0 = k * (x1 - 4)**2
            # excited state parabola, min at (1,1)
            y1 = k * (x2 - 5)**2 + 4

            fig, ax = plt.subplots(figsize=(6,5))

            # plot parabolas
            ax.plot(x1, y0, 'k-', lw=2)
            ax.plot(x2, y1, 'k-', lw=2)

            # Points of interest
            E0 = (4, 0)   # ground min
            E1 = (4, 4 + k * (4 - 5)**2)   # vertical excitation
            E2 = (5, 4)   # excited min
            E3 = (5, k * (4 - 5)**2)   # intersection (just an example)

            # mark points
            ax.scatter(*E0, c='k')
            ax.scatter(*E1, c='k')
            ax.scatter(*E2, c='k')
            ax.scatter(*E3, c='k')
            
            ax.text(4.1, 3.3, f"{round(eV_to_nm(zpl))} nm")    
            ax.text(4.1, 3, f"{zpl:.2} eV")

            color_map = [
                (1.77, 1.91, "red"),
                (1.91, 2.10, "orange"),
                (2.10, 2.17, "yellow"),
                (2.17, 2.33, "green"),
                (2.33, 2.64, "cyan"),
                (2.64, 3.10, "blue"),
            ]

            zpl_color = "black"  # default if outside visible range

            for low, high, color in color_map:
                if low <= zpl <= high:
                    zpl_color = color
                    break

            # vertical excitation arrow (E0 -> E1)
            ax.annotate("", xy=E1, xytext=E0,
                        arrowprops=dict(arrowstyle="->", lw=1, color='black'),
                        ha="left", va="center")

            # ZPL arrow (E0 -> E2)
            ax.annotate("", xy=E2, xytext=E0,
                        arrowprops=dict(arrowstyle="<->", lw=2, color=zpl_color),
                        ha="center", va="center")

            # Relaxation arrow (E2 -> E3)
            ax.annotate("", xy=E3, xytext=E2,
                        arrowprops=dict(arrowstyle="->", lw=1, color="black"),
                        ha="center", va="center")

            # styling
            ax.set_title(title)
            ax.set_xlim(2, 7)
            ax.set_ylim(-1, 7)
            ax.axis("off")

            st.pyplot(fig)

        plot_configuration_diagram(AEE_eV)
    else:
        st.warning("Please fill in all inputs before submitting.")
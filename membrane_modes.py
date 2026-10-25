import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

Lx = 1
Ly = 1
c=100
RUN_TESTS = False

while True:
    try:
        f_target = float(input("Δώσε μια συχνότητα σε Hz: "))

        if f_target > 0 and np.isfinite(f_target):
            break
        else:
            print("Η συχνότητα πρέπει να είναι θετικός αριθμός.")

    except ValueError:
        print("Λανθασμένη είσοδος. Δώσε έναν αριθμό, π.χ. 250.")



x = np.linspace(0, Lx, 200)
y = np.linspace(0, Ly, 200)

X, Y = np.meshgrid(x, y)
                
def mode(X, Y, n, m, Lx, Ly):
    return np.sin(n*np.pi*X/Lx) * np.sin(m*np.pi*Y/Ly)

def frequency(n, m, Lx, Ly, c):
    return (c/2)*np.sqrt((n/Lx)**2+(m/Ly)**2)
#Το \(c\) εδώ είναι η ταχύτητα διάδοσης των εγκάρσιων
#κυμάτων στη μεμβράνη. Για ιδανική ομογενή μεμβράνη: c=sqrt(T/σ)
#όπου \(T\) είναι η τάση της μεμβράνης σε N/m
#και σ η επιφανειακή πυκνότητα μάζας σε kg/m².


def find_modes(f_target, Lx, Ly, c):
    all_modes = []

    for n in range(1, 6):
        for m in range(1, 6):

            f_nm = frequency(n, m, Lx, Ly, c)

            all_modes.append((n, m, f_nm))

    closest = min(
        all_modes,
        key=lambda item: abs(item[2] - f_target)
    )

    closest_f = closest[2]

    modes_found = []

    for n, m, f_nm in all_modes:

        if abs(f_nm - closest_f) < 1e-6:
            modes_found.append((n, m, f_nm))
    return closest_f, modes_found

def plot_2d(X, Y, W_total, f1, mode_labels):

    fig, ax = plt.subplots(1, 2, figsize=(12, 5))

    # Κατανομή απομάκρυνσης
    im = ax[0].contourf(
        X, Y, W_total,
        levels=30,
        cmap="RdBu_r"
    )

    ax[0].set_title("Κατανομή απομάκρυνσης")
    ax[0].set_xlabel("x (m)")
    ax[0].set_ylabel("y (m)")
    ax[0].set_aspect("equal")

    fig.colorbar(
        im,
        ax=ax[0],
        label="Σχετική απομάκρυνση"
    )

    # Κομβικές γραμμές
    ax[1].contour(
        X, Y, W_total,
        levels=[0],
        colors="black"
    )

    ax[1].set_title("Κομβικές γραμμές")
    ax[1].set_xlabel("x (m)")
    ax[1].set_ylabel("y (m)")
    ax[1].set_aspect("equal")

    plt.suptitle(
        f"Ιδιομορφές: {mode_labels} | f = {f1:.2f} Hz"
    )

    plt.tight_layout()
    plt.show()

    
def plot_3d(X, Y, W_physical, A0, f1, mode_labels):

    fig = plt.figure(figsize=(9, 7))

    ax = fig.add_subplot(111, projection="3d")

    ax.plot_surface(
        X, Y, W_physical,
        cmap="RdBu_r",
        vmin=-A0,
        vmax=A0
    )

    ax.set_xlabel("x (m)")
    ax.set_ylabel("y (m)")
    ax.set_zlabel("Displacement (m)")

    ax.set_zlim(-A0, A0)

    ax.set_title(
        f"Membrane modes: {mode_labels}\n"
        f"Frequency: {f1:.2f} Hz | Amplitude: {A0*1000:.1f} mm"
    )

    plt.show()

def animate_membrane(X, Y, W_normalized, A0, f1, mode_labels):

    T = 1 / f1

    fig_anim = plt.figure(figsize=(9, 7))

    ax_anim = fig_anim.add_subplot(111, projection="3d")

    def update(frame):

        ax_anim.clear()

        t = frame * T / 40

        W_t = A0 * W_normalized * np.cos(2 * np.pi * f1 * t)

        ax_anim.plot_surface(
            X, Y, W_t,
            cmap="RdBu_r",
            vmin=-A0,
            vmax=A0
        )

        ax_anim.set_xlabel("x (m)")
        ax_anim.set_ylabel("y (m)")
        ax_anim.set_zlabel("Displacement (m)")

        ax_anim.set_zlim(-A0, A0)

        ax_anim.set_title(
            f"Modes: {mode_labels} | f = {f1:.2f} Hz\n"
            f"Time: {t*1000:.2f} ms | Amplitude: {A0*1000:.1f} mm"
        )

    ani = FuncAnimation(
        fig_anim,
        update,
        frames=40,
        interval=50,
        repeat=True
    )

    plt.show()
    
    
closest_f, modes_found = find_modes(f_target, Lx, Ly, c)

frequency_difference = abs(f_target - closest_f)

print("\n--- Αποτελέσματα προσομοίωσης ---")

print(f"Συχνότητα χρήστη: {f_target:.2f} Hz")

print(f"Πλησιέστερη ιδιοσυχνότητα: {closest_f:.2f} Hz")

print(f"Διαφορά συχνοτήτων: {frequency_difference:.2f} Hz")


print("Ιδιομορφές:")

for n, m, f_nm in modes_found:
    print(n, m, round(f_nm, 2))

    
# Υπολογισμός συνολικής ιδιομορφής

W_total = np.zeros_like(X)

for n, m, f_nm in modes_found:
    W_total += mode(X, Y, n, m, Lx, Ly)

f1 = closest_f

mode_labels = ", ".join(
    f"({n},{m})" for n, m, f_nm in modes_found
)


# Κανονικοποίηση
max_displacement = np.max(np.abs(W_total))

if max_displacement > 0:
    W_normalized = W_total / max_displacement
else:
    W_normalized = W_total

# Φυσικό πλάτος ταλάντωσης
A0 = 0.001  # Πλάτος αναφοράς 1 mm
t = 0.0   # Αρχική χρονική στιγμή

W_physical = A0 * W_normalized * np.cos(2 * np.pi * f1 * t)

# 3D απεικόνιση της μεμβράνης
plot_3d(X, Y, W_physical, A0, f1, mode_labels)

# 3D animation της μεμβράνης

animate_membrane(X, Y, W_normalized, A0, f1, mode_labels)

plot_2d(X, Y, W_total, f1, mode_labels)

def run_tests():

# Έλεγχος θεωρητικών ιδιοσυχνοτήτων
    print("\n--- Έλεγχος ιδιοσυχνοτήτων ---")

    test_modes = [
        (1, 1),
        (1, 2),
        (2, 2),
        (2, 3),
        (3, 4),
        (4, 3)
    ]

    for n, m in test_modes:
        f_calculated = frequency(n, m, Lx, Ly, c)
        f_theoretical = 50 * np.sqrt(n**2 + m**2)

        error = abs(f_calculated - f_theoretical)

        print(
            f"Mode ({n},{m}): "
            f"Calculated = {f_calculated:.4f} Hz, "
            f"Theoretical = {f_theoretical:.4f} Hz, "
            f"Error = {error:.2e} Hz"
        )

# Έλεγχος οριακών συνθηκών

    print("\n--- Έλεγχος οριακών συνθηκών ---")

    W_test = mode(X, Y, 3, 4, Lx, Ly)

    left = np.max(np.abs(W_test[:, 0]))
    right = np.max(np.abs(W_test[:, -1]))
    bottom = np.max(np.abs(W_test[0, :]))
    top = np.max(np.abs(W_test[-1, :]))

    print(f"Αριστερό άκρο: {left:.2e}")
    print(f"Δεξί άκρο: {right:.2e}")
    print(f"Κάτω άκρο: {bottom:.2e}")
    print(f"Πάνω άκρο: {top:.2e}")


    # Έλεγχος σχέσης διασποράς

    print("\n--- Έλεγχος κυματικής εξίσωσης ---")

    n = 3
    m = 4

    f = frequency(n, m, Lx, Ly, c)
    omega = 2 * np.pi * f

    left_side = omega**2

    right_side = c**2 * (
        (n * np.pi / Lx)**2 +
        (m * np.pi / Ly)**2
    )

    error = abs(left_side - right_side)

    print(f"Αριστερό μέλος: {left_side:.6f}")
    print(f"Δεξί μέλος: {right_side:.6f}")
    print(f"Απόλυτη διαφορά: {error:.2e}")


    # Αριθμητικός έλεγχος κυματικής εξίσωσης

    print("\n--- Αριθμητικός έλεγχος κυματικής εξίσωσης ---")

    n = 3
    m = 4

    W_test = mode(X, Y, n, m, Lx, Ly)

    dx = x[1] - x[0]
    dy = y[1] - y[0]

    # Δεύτερες χωρικές παράγωγοι
    d2W_dx2 = (
        W_test[1:-1, 2:] -
        2 * W_test[1:-1, 1:-1] +
        W_test[1:-1, :-2]
    ) / dx**2

    d2W_dy2 = (
        W_test[2:, 1:-1] -
        2 * W_test[1:-1, 1:-1] +
        W_test[:-2, 1:-1]
    ) / dy**2

    laplacian = d2W_dx2 + d2W_dy2

    f_test = frequency(n, m, Lx, Ly, c)
    omega_test = 2 * np.pi * f_test

    left_side = -omega_test**2 * W_test[1:-1, 1:-1]
    right_side = c**2 * laplacian

    residual = left_side - right_side

    max_error = np.max(np.abs(residual))
    relative_error = max_error / np.max(np.abs(left_side))

    print(f"Μέγιστο απόλυτο σφάλμα: {max_error:.6f}")
    print(f"Σχετικό σφάλμα: {relative_error:.6%}")

if RUN_TESTS:
    run_tests()



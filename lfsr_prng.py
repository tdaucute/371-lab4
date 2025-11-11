"""
Lab 4 - Part 1: Pseudorandom Number Generator (LFSR)
with optional dynamic seeding, LED, and buzzer feedback
Platform: Raspberry Pi 5 (Python 3.11)

Implements a 6-bit LFSR PRNG with taps (5,4) -> x^6 + x^5 + 1
LED blinks for each generated bit; buzzer beeps at sequence completion.
"""

import time
import lgpio
import matplotlib.pyplot as plt
import random

# ---------------- CONFIGURATION ----------------
DYNAMIC_SEED = True   # Toggle True = different sequence each run; False = fixed reproducible seed
PIN_LED = 27          # LED pin
PIN_BUZZER = 18       # Buzzer pin
SEED_FIXED = 0b100111 # Fixed reproducible seed
TAPS = (5, 4)
N_BITS = 6
N_VALUES = (1 << N_BITS) - 1   # 63 outputs

# ---------------- GPIO SETUP ----------------
chip = lgpio.gpiochip_open(0)
lgpio.gpio_claim_output(chip, PIN_LED)
lgpio.gpio_claim_output(chip, PIN_BUZZER)

def beep(duration=0.1):
    """Emit a short beep from buzzer."""
    lgpio.gpio_write(chip, PIN_BUZZER, 1)
    time.sleep(duration)
    lgpio.gpio_write(chip, PIN_BUZZER, 0)

def blink_led(bit, duration=0.05):
    """Blink LED according to bit value."""
    lgpio.gpio_write(chip, PIN_LED, bit)
    time.sleep(duration)
    lgpio.gpio_write(chip, PIN_LED, 0)

# ---------------- LFSR CORE ----------------
def lfsr(seed, taps=TAPS, n_bits=N_BITS, n_values=N_VALUES):
    """Generate pseudorandom sequence using LFSR."""
    """TODO"""
    if seed == 0:
        seed = random.randint(1, 63)
        seed = format(seed, '06b')

    output = []

    for i in range(n_values):
        temp = 0
        lsb = seed & 1
        output.append(lsb)

        for j in taps:
            tap = (seed >> j) & 1
            temp ^= tap
        
        temp = temp << (n_bits - 1)
        seed = (seed >> 1) | temp

    return output

# ---------------- MAIN ----------------
def main():
    # Choose seed
    if DYNAMIC_SEED:
        # Use lower 6 bits of nanosecond clock as seed
        seed = int(time.time_ns()) & ((1 << N_BITS) - 1)
        if seed == 0:
            seed = 1  # avoid stuck zero state
        print(f"[Dynamic mode] Using seed: {seed:06b}")
    else:
        seed = SEED_FIXED
        print(f"[Fixed mode] Using seed: {seed:06b}")

    print("Running LFSR PRNG with LED/Buzzer output...\n")

    sequence = lfsr(seed)

    for value in sequence:
        bit = value & 1
        blink_led(bit)
        time.sleep(0.05)
    beep(0.15)

    print("Sequence complete! Generated", len(sequence), "values.")

    # Plot visualization
    plt.figure(figsize=(9, 4))
    plt.plot(sequence, marker='o', linestyle='-')
    plt.title(f"Write a title here mentioning the seed used")
    plt.xlabel("Write an xlabel here")
    plt.ylabel("Write a ylabel here")
    plt.grid(True)
    plt.show()

    lgpio.gpiochip_close(chip)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        lgpio.gpiochip_close(chip)
        print("\nInterrupted — GPIO released.")
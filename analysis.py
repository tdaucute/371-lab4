"""
Lab 4 - Part 3: PRNG vs TRNG Comparative Analysis
Platform: Raspberry Pi 5 (Python 3.11)

This script compares:
    - PRNG (LFSR-based pseudorandom generator)
    - TRNG (hardware jitter-based true random generator)

Outputs:
    - Entropy values for both
    - Histograms, autocorrelation plots
    - LED + buzzer feedback for higher entropy source
"""
#from lfsr_prng import lfsr
#from trng import trng
import lgpio
import time
import math
import matplotlib.pyplot as plt
import numpy as np

# ---------------- GPIO CONFIG ----------------
PIN_LED = 27
PIN_BUZZER = 18
PIN_INPUT = 17  # For TRNG input

chip = lgpio.gpiochip_open(0)
lgpio.gpio_claim_output(chip, PIN_LED)
lgpio.gpio_claim_output(chip, PIN_BUZZER)
lgpio.gpio_claim_input(chip, PIN_INPUT)

# ---------------- UTILITIES ----------------
def beep(duration=0.1):
    lgpio.gpio_write(chip, PIN_BUZZER, 1)
    time.sleep(duration)
    lgpio.gpio_write(chip, PIN_BUZZER, 0)

def blink_led(bit=1, duration=0.05):
    lgpio.gpio_write(chip, PIN_LED, bit)
    time.sleep(duration)
    lgpio.gpio_write(chip, PIN_LED, 0)

def trng(bits=512):
    """Redfine your trng function from trng.py here"""
    def von_neumann(bits):  # Extra credit
        output = []

        for i in range(0, (len(bits)-1), 2):
            if bits[i] != bits[i+1]:
                output.append(bits[i])
        
        return output
    
    count = 0
    timestamp = []
    delta = []
    raw = []

    while count <= bits:
        if lgpio.gpio_read(chip, PIN_INPUT) == 1:
            timestamp.append(time.time_ns())
            count += 1

    for i in range(len(timestamp)-1):
        diff = timestamp[i+1] - timestamp[i]
        delta.append(diff)

    for i in delta:
        extract = i & 1
        raw.append(extract)

    debiased = von_neumann(raw)  # Extra credit

    for i in debiased:
        blink_led(i)
        time.sleep(0.05)

    return debiased

def lfsr(seed=0b100111, taps=(5, 4), n_bits=6, n_values=63):
    """Redefine your lfsr function from lfsr_prng.py"""
    import random

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

def entropy(data):
    """Shannon entropy (bits per symbol)."""
    """TODO"""
    count0, count1 = 0, 0

    for i in data:
        if i == 0:
            count0 += 1
        if i == 1:
            count1 += 1
    
    p0 = count0/len(data)
    p1 = count1/len(data)

    if p0 == 0 or p1 == 0:
        h = 0
    else:
        h = -p0*math.log2(p0) - p1*math.log2(p1)

    return h

def autocorrelation(bits):
    """Compute lag-1 autocorrelation coefficient."""
    "TODO"
    bits = np.array(bits)

    cov = np.sum((bits[:-1] - np.mean(bits))*(bits[1:] - np.mean(bits)))
    var = np.sum((bits - np.mean(bits))**2)
    
    if var == 0.0:
        coeff = 0
    else:
        coeff = cov/var

    return coeff

def monobit(bits):  # Extra credit
    count0, count1 = 0, 0

    for i in bits:
        if i == 0:
            count0 += 1
        if i == 1:
            count1 += 1
    
    p = count1/len(bits)
    z = (count1-count0)/math.sqrt(len(bits))

    return count0, count1, p, z

def runs(bits):  # Extra credit
    countrun0 = 0
    countrun1 = 0

    if bits[-1] == 0:
        countrun0 += 1
    elif bits[-1] == 1:
        countrun1 += 1

    for i in range(0, (len(bits)-1)):
        if bits[i] == 0 and bits[i+1] == 1:
            countrun0 += 1
        elif bits[i] == 1 and bits[i+1] == 0:
            countrun1 += 1
    
    totrun = countrun0 + countrun1

    return countrun0, countrun1, totrun

def autocorrelation_mult(bits):  # Extra credit
    bits = np.array(bits)
    coeff = []

    for i in range(0, 11):
        cov = np.sum((bits[:-i] - np.mean(bits))*(bits[i:] - np.mean(bits)))
        var = np.sum((bits - np.mean(bits))**2)
    
        if var == 0.0:
            coeff[i] = 0
        else:
            coeff[i] = cov/var

    return coeff

def plot_comparison(prng_bits, trng_bits, H_prng, H_trng):
    plt.figure(figsize=(10, 4))
    plt.subplot(1, 2, 1)
    plt.hist(prng_bits, bins=2, color='skyblue', edgecolor='black')
    plt.title(f"Write a title here={H_prng:.3f}")
    plt.xticks([0, 1])
    plt.xlabel("Write the x label here")
    plt.ylabel("Write the y label here")

    plt.subplot(1, 2, 2)
    plt.hist(trng_bits, bins=2, color='orange', edgecolor='black')
    plt.title(f"Write a title here={H_trng:.3f}")
    plt.xticks([0, 1])
    plt.xlabel("Write the x label here")
    plt.ylabel("Write the x label here")

    plt.tight_layout()
    plt.show()

# ---------------- MAIN ----------------
def main():
    print("Collecting data from both generators...\n")

    prng_bits = lfsr()
    trng_bits = trng()

    H_prng = entropy(prng_bits)
    H_trng = entropy(trng_bits)
    R_prng = autocorrelation(prng_bits)
    R_trng = autocorrelation(trng_bits)

    print(f"PRNG Entropy = {H_prng:.3f} bits/bit,  Autocorr = {R_prng:.3f}")
    print(f"TRNG Entropy = {H_trng:.3f} bits/bit,  Autocorr = {R_trng:.3f}\n")

    plot_comparison(prng_bits, trng_bits, H_prng, H_trng)

    if H_trng > H_prng:
        print("TRNG shows higher entropy — more random.")
        blink_led(1)
        beep(0.2)
    else:
        print("PRNG appears more uniform in this run.")
        for _ in range(2):
            blink_led(1)
            time.sleep(0.1)
            blink_led(0)

    lgpio.gpiochip_close(chip)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        lgpio.gpiochip_close(chip)
        print("\nInterrupted — GPIO cleaned up.")
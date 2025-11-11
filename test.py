import random

def lfsr(seed, taps, n_bits, n_values):
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


def lfsr2(seed, taps, n_bits, n_values):
    state = seed
    outputs = []
    
    for _ in range(n_values):
        out = state & 1
        outputs.append(out)
        
        feedback = 0
        for t in taps:
            feedback ^= (state >> t) & 1
            
        state = (state >> 1) | (feedback << (n_bits - 1))
    
    return outputs




a = lfsr(0b100111, (5, 4), 6, 63)
b = lfsr2(0b100111, (5, 4), 6, 63)

print(len(a))
print(len(b))

for i in range(0, 63):
    if a[i] != b[i]:
        print('fuck')
    
    


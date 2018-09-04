from math import log1p, sqrt

# https://en.wikipedia.org/wiki/Birthday_attack
def birthdayProbability(masterset, hits):
    exponent = hits * (hits - 1) / 2
    probability = 1 - pow( 1 - (1 / masterset), exponent)
    return probability

def birthday2(probability_exponent, bits):
    probability = 10.0**probability_exponent
    outputs = 2.0**bits
    print(sqrt(2.0*outputs*-log1p(-probability)))

if __name__ == '__main__':
    #probability = birthdayProbability(65535, 700) * 100.00
    #probabilityB = birthdayProbability(4294967296, 10000) * 100.00
    probabilityHB = birthdayProbability(694967296, 60000) * 100.00

    #print('Probability of Success: %f %%' % probability)
    #print('probabilityB of Success: %f %%' % probabilityB)
    print('probabilityHB of Success: %f %%' % probabilityHB)

    #birthday2(-1,128)
    #birthday2(-10, 128)
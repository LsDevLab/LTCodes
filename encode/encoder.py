import sys
from random import choices
from lt_codes.util.distributions import *

def get_degree_from(p_dist):
    """ Returns the random degree from a given distribution of probabilities.
    The degrees distribution must look like a Poisson distribution and the 
    degree of the first drop is 1 to ensure the start of decoding.
    """
    block_indexes = list(range(0, len(p_dist)))
    return choices(block_indexes, p_dist, k=1)[0]
   
def encode(blocks, c=None, delta=DELTA): #n_symbols_max
    """ Iterative encoding - Encodes new symbols and yield them.
    Encoding one symbol is described as follows:

    1.  Randomly choose a degree according to the degree distribution, save it into "deg"
        Note: below we prefer to randomly choose all the degrees at once for our symbols.

    2.  Choose uniformly at random 'deg' distinct input blocs. 
        These blocs are also called "neighbors" in graph theory.
    
    3.  Compute the output symbol as the combination of the neighbors.
        In other means, we XOR the chosen blocs to produce the symbol.
    """

    blocks_n = len(blocks)

    p_dist = robust_distribution(blocks_n, c, delta)

    print("Ready for encoding.", flush=True)

    i = 0
    while True:

        # Generate random indexes associated to random degrees, seeded with the symbol id
        d = get_degree_from(p_dist)
        
        # Get the random selection, generated precedently (for performance)
        selection_indexes, d = generate_indexes(i, d, blocks_n)

        # Xor each selected array within each other gives the drop (or just take one block if there is only one selected)
        symbol_data = blocks[selection_indexes[0]]
        for n in range(1, d):
            symbol_data = np.bitwise_xor(symbol_data, blocks[selection_indexes[n]])

        # Create symbol, then log the process
        symbol = Symbol(index=i, degree=d, data=symbol_data)

        print("[ENCODER] Released symbol", i)

        i += 1

        yield symbol


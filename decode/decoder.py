import time
import numpy as np
from lt_codes.util.core import generate_indexes, log


def recover_graph(symbols, blocks_quantity):
    """
    Get back the same random indexes (or neighbors), thanks to the symbol id as seed.
    For an easy implementation purpose, we register the indexes as property of the Symbols objects.
    """

    for symbol in symbols:
        neighbours, deg = generate_indexes(symbol.index, symbol.degree, blocks_quantity)
        symbol.neighbours = {x for x in neighbours}
        symbol.degree = deg

    return symbols


def reduce_neighbors(block_index, blocks, symbols):
    """
    Loop over the remaining symbols to find for a common link between
    each symbol and the last solved block `block`

    To avoid increasing complexity and another for loop, the neighbors are stored as dictionnary
    which enable to directly delete the entry after XORing back.
    """

    for other_symbol in symbols:
        if other_symbol.degree > 1 and block_index in other_symbol.neighbours:
            # XOR the data and remove the index from the neighbors
            other_symbol.data = np.bitwise_xor(blocks[block_index], other_symbol.data)
            other_symbol.neighbours.remove(block_index)

            other_symbol.degree -= 1


def decode(symbols, blocks, solved_blocks_count):
    """ Iterative decoding - Decodes all the passed symbols to build back the data as blocks. 
    The function returns the data at the end of the process.
    
    1. Search for an output symbol of degree one
        (a) If such an output symbol y exists move to step 2.
        (b) If no output symbols of degree one exist, iterative decoding exits and decoding fails.
    
    2. Output symbol y has degree one. Thus, denoting its only neighbour as v, the
        value of v is recovered by setting v = y.

    3. Update.

    4. If all k input symbols have been recovered, decoding is successful and iterative
        decoding ends. Otherwise, go to step 1.
    """
    assert len(symbols) > 0, "There are no symbols to decode."

    # We keep `blocks_n` notation and create the empty list
    blocks_n = len(blocks)

    # Recover the degrees and associated neighbors using the seed (the index, cf. encoding).
    symbols = recover_graph(symbols, blocks_n)

    while True:

        # num of block solved in this iteration
        iteration_solved_count = 0

        # Search for solvable symbols
        for i, symbol in enumerate(symbols):

            # Check the current degree. If it's 1 then we can recover data
            if symbol.degree == 1:

                iteration_solved_count += 1
                block_index = next(iter(symbol.neighbours))
                symbols.pop(i)

                # This symbol is redundant: another already helped to decode the same block
                if blocks[block_index] is not None:
                    continue

                blocks[block_index] = symbol.data

                # Update the count and log the processing
                solved_blocks_count += 1

                print("[DECODER] Solved block", block_index)
                print("          Currently solved", solved_blocks_count, "/", blocks_n, "blocks.")

                # Reduce the degrees of other symbols that contains the solved block as neighbor             
                reduce_neighbors(block_index, blocks, symbols)

        if iteration_solved_count == 0:
            break

    return np.asarray(blocks, dtype=object), solved_blocks_count


import os
import keyboard as keyboard
import sys

sys.path.insert( 0, "/Users/luigisc/Library/CloudStorage/OneDrive-Personale/UniSa/Magistrale/MPSA/codes/lt_codes/LTCodes" )

from lt_codes.decode.decoder import decode
from lt_codes.encode.encoder import encode
from lt_codes.util.core import *

#########################################################
# HOW TO RUN?
# run from terminal, in mpsa folder
# 1 source venv/bin/activate
# 2 sudo python3 lt_codes/simulation.py

filename = "lt_codes/files/example_json.txt"
filename_decoded = "lt_codes/files/example_json_decoded.txt"

with open(filename, "rb") as file:

    filesize = os.path.getsize(filename)
    print("Filesize: {} bytes".format(filesize))

    # Split the file in blocks and compute how many symbols produce (according redundancy)
    blocks = blocks_read(file, filesize)
    n_blocks = len(blocks)
    redundancy_max = 100000
    n_symbols_max = int(n_blocks * redundancy_max)

    print("Blocks: {}".format(n_blocks))
    print("N Symbols: {}\n".format(n_symbols_max))

    symbols = []
    solved_blocks_count  = 0
    solved_blocks = [None] * n_blocks
    K = 0
    for curr_symbol in encode(blocks):

        # Simulating the loss of packets when pressing q
        if keyboard.is_pressed('q'):  # if key 'q' is pressed
            print("[PK_LOSS] Symbol", K, "lost!")
        else:
            symbols.append(curr_symbol)

        solved_blocks, solved_blocks_count = decode(symbols, solved_blocks, solved_blocks_count)
        K += 1

        time.sleep(0.01)

        if curr_symbol.index > n_symbols_max or solved_blocks_count == n_blocks:
            break

    # recovered_blocks, recovered_n = decode(symbols, blocks_quantity=n_blocks)
    if solved_blocks_count != n_blocks:
        print("\nAll blocks are not recovered!")
        exit()
    else:
        print("\nFile decoded correctly!")

    print("K =", K)
    print("rate =", n_blocks/K)

    # Write down the recovered blocks in a copy
    with open(filename_decoded, "wb") as file_decoded:
        blocks_write(solved_blocks, file_decoded)
    print("Wrote {} bytes in {}".format(os.path.getsize(filename_decoded), filename_decoded), "\n")

# refactoring codice e commenti
# provare a fare i programmi che fanno encoding e decoding
# benchmarks:
# - code rate aumenta all'aumentare della lunghezza del file
# - effetti della lunghezza di simbolo l sui tempi di esecuzione (anche sul code-rate???)
# - effetti del cambio dei parametri della RDS
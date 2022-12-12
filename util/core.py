import math
import time
import numpy as np
import random

l = 65536
DELTA = 0.01
NUMPY_TYPE = np.uint8 #np.uint64
EPSILON = 0.0001

class Symbol:
    __slots__ = ["index", "degree", "data", "neighbours"] # fixing attributes may reduce memory usage

    def __init__(self, index, degree, data):
        self.index = index
        self.degree = degree
        self.data = data

    def log(self, blocks_quantity):
        neighbours, _ = generate_indexes(self.index, self.degree, blocks_quantity)
        print("symbol_{} degree={}\t {}".format(self.index, self.degree, neighbours))

def generate_indexes(symbol_index, degree, blocks_quantity):
    """Randomly get `degree` indexes, given the symbol index as a seed

    Generating with a seed allows to save only the seed (and the amount of degrees) and not the whole array of indexes.
    This saves memory and bandwidth when packets are sent.

    The random indexes need to be unique because the decoding process uses dictionaries for performance enhancements.
    Additionally, even if XORing one block with itself among with other is not a problem for the algorithm,
    it is better to avoid uneffective operations like that.

    To be sure to get the same random indexes, we need to pass
    """
    random.seed(symbol_index)
    indexes = random.sample(range(blocks_quantity), degree)

    return indexes, degree

def log(process, iteration, start_time):
    """Log the processing in a gentle way, each seconds"""
    global log_actual_time
    
    if "log_actual_time" not in globals():
        log_actual_time = time.time()

    if time.time() - log_actual_time > 1:# or iteration == total - 1:
        
        log_actual_time = time.time()
        elapsed = log_actual_time - start_time + EPSILON

        print("{}: {} - ~{:.5f}s".format(
            process, iteration + 1, elapsed), end="\r", flush=True)


def blocks_read(file, filesize, l=l):
    """ Read the given file by blocks of `core.PACKET_SIZE` and use np.frombuffer() improvement.

    By default, we store each octet into a np.uint8 array space, but it is also possible
    to store up to 8 octets together in a np.uint64 array space.

    This process is not saving memory but it helps reduce dimensionnality, especially for the
    XOR operation in the encoding. Example:
    * np.frombuffer(b'\x01\x02', dtype=np.uint8) => array([1, 2], dtype=uint8)
    * np.frombuffer(b'\x01\x02', dtype=np.uint16) => array([513], dtype=uint16)
    """

    blocks_n = math.ceil(filesize / l)
    blocks = []

    # Read data by blocks of size core.PACKET_SIZE
    for i in range(blocks_n):

        data = bytearray(file.read(l))

        if not data:
            raise "stop"

        # The last read bytes needs a right padding to be XORed in the future
        if len(data) != l:
            data = data + bytearray(l - len(data))
            assert i == blocks_n - 1, "Packet #{} has a not handled size of {} bytes".format(i, len(blocks[i]))

        # Paquets are condensed in the right array type
        blocks.append(np.frombuffer(data, dtype=NUMPY_TYPE))

    return blocks


def blocks_write(blocks, file):
    """ Write the given blocks into a file
    """
    count = 0
    for data in blocks:
        for b in data:
            file.write(np.uint8(b))
        count += len(data)

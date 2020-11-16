from LZ77 import LZ77Compressor
from LZ77_improved import LZSSCompressor
import time

window_size = 1024
lab_size = 256
compressor = LZ77Compressor(window_size=window_size, lookahead_buffer_size=lab_size)  # window_size is optiona#l
#compressor = LZSSCompressor(window_size=window_size, lookahead_buffer_size=lab_size)  # window_size is optional
input_file_path = './Introduction to Data Compression.txt'
res_file_path = './temp.txt'
output_file_path = './Decompression.txt'
time_start = time.time()
compressor.compress(input_file_path, res_file_path, verbose=False)
time_mid = time.time()
compressor.decompress(res_file_path, output_file_path)
time_end = time.time()
print(f"Window size: {window_size} , Look-ahead-buffer size: {lab_size}")
print(f"Compressing Time: {format(time_mid - time_start,'.4f')} s")
print(f"Decompressing Time: {format(time_end - time_mid,'.4f')} s")

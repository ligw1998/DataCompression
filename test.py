from LZ77 import LZ77Compressor
from LZ77_improved import LZSSCompressor
import time

# search buffer size & look-ahead buffer size
window_size = 1023
lab_size = 255
# LZ77 compressor is the original LZ77 method, window_size <= 65535, lab_size <= 255
# bigger size may lead to booming time
compressor = LZ77Compressor(window_size=window_size, lookahead_buffer_size=lab_size)
# LZSS compressor is the improved LZ77 method, window_size <= 4095, lab_size <= 15
# compressor = LZSSCompressor(window_size=window_size, lookahead_buffer_size=lab_size)
input_file_path = './Introduction to Data Compression.docx'
res_file_path = './temp.txt'
output_file_path = './Decompression.docx'
time_start = time.time()
compressor.compress(input_file_path, res_file_path, verbose=False)  # print output if verbose = True
time_mid = time.time()
compressor.decompress(res_file_path, output_file_path)
time_end = time.time()
print(f"Window size: {window_size} , Look-ahead-buffer size: {lab_size}")
print(f"Compressing Time: {format(time_mid - time_start, '.4f')} s")
print(f"Decompressing Time: {format(time_end - time_mid, '.4f')} s")

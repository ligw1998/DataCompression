from LZ77 import LZ77Compressor

compressor = LZ77Compressor(window_size=500)  # window_size is optional
input_file_path = './Introduction to Data Compression.docx'
res_file_path = './temp.txt'
output_file_path = './Decompression.docx'
compressor.compress(input_file_path, res_file_path, verbose=False)
compressor.decompress(res_file_path, output_file_path)

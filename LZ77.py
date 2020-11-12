from bitarray import bitarray


class LZ77Compressor:
    """
    A simplified implementation of the LZ77 Compression Algorithm
    """
    MAX_WINDOW_SIZE = 65535

    def __init__(self, window_size=20, lookahead_buffer_size=15):
        self.window_size = min(window_size, self.MAX_WINDOW_SIZE)  # in case the matching process
        self.lookahead_buffer_size = lookahead_buffer_size  # length of match is at most 8 bits

    def compress(self, input_file_path, output_file_path=None, verbose=False):
        """
        Given the path of an input file, its content is compressed by applying a simple
        LZ77 compression algorithm.

        According to the rule given in the instruction, the compressed format is:
        16 bits pointer (distance to the start of the match from the current position) followed
        by 8 bits(length of the match) and then 8 bits(for the character)

        If a path to the output file is provided, the compressed data is written into
        a binary file. Otherwise, it is returned as a bit-array

        if verbose is enabled, the compression description is printed to standard output
        """
        data = None
        i = 0
        output_buffer = bitarray(endian='big')

        # read the input file
        try:
            with open(input_file_path, 'rb') as input_file:  # binary read input file
                data = input_file.read()
        except IOError:
            print('Could not open input file ...')
            raise
        #print(len(data))
        while i < len(data):
            #print(i)

            match = self.findLongestMatch(data, i)  # use function findLongestMatch to find the longest match

            if match:
                # Add 16 bits for distance, followed by 8 bits for length, and 8 bits for character of the match
                (bestMatchDistance, bestMatchLength) = match

                output_buffer.frombytes(bytes([bestMatchDistance >> 8]))
                output_buffer.frombytes(bytes([bestMatchDistance & 0xff]))
                output_buffer.frombytes(bytes([bestMatchLength]))

                i += bestMatchLength
                if i >= len(data):
                    break

                output_buffer.frombytes(bytes([data[i]]))

                if verbose:
                    print("<%i, %i, %s>" % (bestMatchDistance, bestMatchLength, data[i]), end='')
                i += 1

            else:
                # No useful match was found. Add 16 bits 0, followed by 8 bits 0, and 8 bits for the character
                output_buffer.frombytes(bytes([0]))
                output_buffer.frombytes(bytes([0]))
                output_buffer.frombytes(bytes([0]))
                output_buffer.frombytes(bytes([data[i]]))

                if verbose:
                    print("<0, 0, %s>" % data[i], end='')

                i += 1

        # fill the buffer with zeros if the number of bits is not a multiple of 8
        output_buffer.fill()

        # write the compressed data into a binary file if a path is provided
        if output_file_path:
            try:
                with open(output_file_path, 'wb') as output_file:
                    output_file.write(output_buffer.tobytes())
                    print("File was compressed successfully and saved to output path ...")
                    return None
            except IOError:
                print('Could not write to output file path. Please check if the path is correct ...')
                raise

        # an output file path was not provided, return the compressed data
        return output_buffer

    def decompress(self, input_file_path, output_file_path=None):
        """
        Given a string of the compressed file path, the data is decompressed back to its
        original form, and written into the output file path if provided. If no output
        file path is provided, the decompressed data is returned as a string
        """
        data = bitarray(endian='big')
        output_buffer = []

        # read the input file
        try:
            with open(input_file_path, 'rb') as input_file:
                data.fromfile(input_file)
        except IOError:
            print('Could not open input file ...')
            raise

        while len(data) >= 24:
            #print(len(data))

            byte1 = ord(data[0:8].tobytes())
            byte2 = ord(data[8:16].tobytes())
            byte3 = ord(data[16:24].tobytes())
            del data[0:24]
            distance = (byte1 << 8) | byte2
            length = byte3

            if distance == 0:
                byte = data[0:8].tobytes()
                output_buffer.append(byte)
                del data[0:8]
            else:
                for i in range(length):
                    output_buffer.append(output_buffer[-distance])
                if len(data) < 8:
                    break
                byte = data[0:8].tobytes()
                output_buffer.append(byte)
                del data[0:8]
        out_data = b''.join(output_buffer)

        if output_file_path:
            try:
                with open(output_file_path, 'wb') as output_file:
                    output_file.write(out_data)
                    print('File was decompressed successfully and saved to output path ...')
                    return None
            except IOError:
                print('Could not write to output file path. Please check if the path is correct ...')
                raise
        return out_data

    def findLongestMatch(self, data, current_position):
        """
        Finds the longest match to a substring starting at the current_position
        in the lookahead buffer from the history window
        """
        end_of_buffer = min(current_position + self.lookahead_buffer_size, len(data) + 1)

        best_match_distance = -1
        best_match_length = -1

        # Optimization: Only consider substrings of length 2 and greater, and just
        # output any substring of length 1 (8 bits uncompressed is better than 13 bits
        # for the flag, distance, and length)
        for j in range(current_position + 2, end_of_buffer):

            start_index = max(0, current_position - self.window_size)
            substring = data[current_position:j]

            for i in range(start_index, current_position):

                repetitions = len(substring) // (current_position - i)

                last = len(substring) % (current_position - i)

                matched_string = data[i:current_position] * repetitions + data[i:i + last]

                if matched_string == substring and len(substring) > best_match_length:
                    best_match_distance = current_position - i
                    best_match_length = len(substring)

        if best_match_distance > 0 and best_match_length > 0:
            return best_match_distance, best_match_length
        return None

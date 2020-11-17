#-*- coding:utf-8 -*-
import docx
from collections import OrderedDict
from bitarray import bitarray

def encode(text):
    start_point = 0
    length = len(text)
    encode_dict = OrderedDict()
    id = 1
    out = bitarray()
    while start_point < length:
        cur_str = bytes([text[start_point]])
        last_start = cur_str
        while cur_str in encode_dict:
            start_point += 1
            last_start = cur_str
            if start_point == length:
                break
            cur_str += bytes([text[start_point]])
        if cur_str in encode_dict:
            encode_dict[bytes('', encoding='utf8')] = {
                'id': id,
                'start': encode_dict[last_start]['id'],
                'end': bytes('', encoding='utf-8')
            }
            break
        if len(cur_str) == 1:
            encode_dict[cur_str] = {
                'id' : id,
                'start' : 0,
                'end' : bytes([cur_str[0]])
            }
        else:
            encode_dict[cur_str] = {
                'id' : id,
                'start' : encode_dict[last_start]['id'],
                'end' : bytes([cur_str[-1]])
            }
        start_point += 1
        id += 1
    for k in encode_dict:
        start = encode_dict[k]['start']
        end = encode_dict[k]['end']
        start = start.to_bytes(2, 'big')
        out.frombytes(start)
        out.frombytes(end)
    return out

def str2dict(encode_str):
    encode_dict = OrderedDict()
    id2token = {}
    cid = 1
    if len(encode_str) % 3 != 0:
        num_code = (len(encode_str) - 16) // 24
        for i in range(num_code):
            code = encode_str[i * 24 : (i + 1) * 24]
            code_id = int(code[:16].to01(), 2)
            code_end = code[16:].tobytes()
            if code_id == 0:
                k = code_end
            else:
                k = id2token[code_id] + code_end
            id2token[cid] = k
            encode_dict[k] = {
                'id' : cid,
                'start' : code_id,
                'end' : code_end
            }
            cid += 1
        k = bytes('', encoding='utf8')
        encode_dict[k] = {
            'id' : cid,
            'start' : int(encode_str[-16:].to01(), 2),
            'end' : bytes('', encoding='utf8')
        }
    else:
        num_code = len(encode_str) // 24
        for i in range(num_code):
            code = encode_str[i * 24: (i + 1) * 24]
            code_id = int(code[:16].to01(), 2)
            code_end = code[16:].tobytes()
            if code_id == 0:
                k = code_end
            else:
                k = id2token[code_id] + code_end
            id2token[cid] = k
            encode_dict[k] = {
                'id': cid,
                'start': code_id,
                'end': code_end
            }
            cid += 1
    return encode_dict, id2token

def decode(encode_str):
    text = bytes('', encoding='utf8')
    encode_dict, id2token = str2dict(encode_str)
    for k in encode_dict:
        if encode_dict[k]['start'] == 0:
            text += k
        else:
            start_id = encode_dict[k]['start']
            text += id2token[start_id] + encode_dict[k]['end']
    return text


class Node(object):
    def __init__(self, name=None, value=None):
        self.name = name
        self.value = value
        self.left = None
        self.right = None


class HuffmanTree(object):
    def __init__(self, char_weights):
        self.tree = [Node(k, char_weights[k]) for k in char_weights]
        while len(self.tree) != 1:
            self.tree.sort(key=lambda node: node.value, reverse=True)
            node = Node(value=(self.tree[-1].value + self.tree[-2].value))
            node.left = self.tree.pop(-1)
            node.right = self.tree.pop(-1)
            self.tree.append(node)
        self.root = self.tree[0]
        self.buffer = list(range(20))

    def pre(self, root, length, codebook):
        node = root
        if (not node):
            return
        elif node.name is not None:
            code = ''.join([f'{i}' for i in self.buffer[:length]])
            codebook[node.name] = code
            return
        self.buffer[length] = 0
        self.pre(node.left, length + 1, codebook)
        self.buffer[length] = 1
        self.pre(node.right, length + 1, codebook)

    def get_code(self):
        codebook = {}
        self.pre(self.root, 0, codebook)
        return codebook


def hft_encode(text, ecd_type = 'start'):
    start_point = 0
    length = len(text)
    encode_dict = OrderedDict()
    id = 1
    freq_dict = {}
    while start_point < length:
        cur_str = bytes([text[start_point]])
        last_start = cur_str
        while cur_str in encode_dict:
            start_point += 1
            last_start = cur_str
            if start_point == length:
                break
            cur_str += bytes([text[start_point]])
        if cur_str in encode_dict:
            encode_dict[bytes('', encoding='utf8')] = {
                'id': id,
                'start': encode_dict[last_start]['id'],
                'end': bytes('', encoding='utf-8')
            }
            if ecd_type == 'start':
                freq_dict[encode_dict[last_start]['id']] = freq_dict.get(encode_dict[last_start]['id'], 0) + 1
            else:
                freq_dict[bytes('', encoding='utf-8')] = freq_dict.get(bytes('', encoding='utf-8'), 0) + 1
            break
        if len(cur_str) == 1:
            encode_dict[cur_str] = {
                'id': id,
                'start': 0,
                'end': bytes([cur_str[0]])
            }
        else:
            encode_dict[cur_str] = {
                'id': id,
                'start': encode_dict[last_start]['id'],
                'end': bytes([cur_str[-1]])
            }
        if ecd_type == 'start':
            freq_dict[encode_dict[cur_str]['start']] = freq_dict.get(encode_dict[cur_str]['start'], 0) + 1
        else:
            freq_dict[encode_dict[cur_str]['end']] = freq_dict.get(encode_dict[cur_str]['end'], 0) + 1
        start_point += 1
        id += 1

    tree = HuffmanTree(freq_dict)
    codebook = tree.get_code()
    bits = ''
    l_cb = bin(len(codebook))[2:]
    bits += '0' * (16 - len(l_cb)) + l_cb
    for k in codebook:
        code = codebook[k]
        if ecd_type == 'start':
            key = bin(k)[2:]
        else:
            if len(k) == 0:
                bits += '0' * (13 - len(code)) + code
                continue
            else:
                key = bin(ord(k))[2:]
        key = '0' * (13 - len(key)) + key
        code = '1' + code
        code = '0' * (13 - len(code)) + code
        bits += key + code
    if ecd_type == 'start':
        for k in encode_dict:
            start = encode_dict[k]['start']
            end = encode_dict[k]['end']
            if len(end) == 0:
                end = ''
            else:
                end = bin(ord(end))[2:]
                end = '0' * (8 - len(end)) + end
            bits += codebook[start] + end
    else:
        for k in encode_dict:
            start = bin(encode_dict[k]['start'])[2:]
            start = '0' * (16 - len(start)) + start
            end = encode_dict[k]['end']
            bits += codebook[end] + start
    out = bitarray(bits)
    return out

def hft_decode(dec_str, ecd_type):
    dec_str = dec_str.tolist()
    dec_str = ''.join([str(int(i)) for i in dec_str])
    l_cb = int(dec_str[:16], 2)
    dec_tree = dec_str[16 : 16 + 26 * l_cb]
    dec_str = dec_str[16 + 26 * l_cb:]
    tree_dict = decode_tree(dec_tree, ecd_type)
    buffer = ''
    encode_dict = {}
    point = 0
    id = 1
    id2tokens = {}
    while point < len(dec_str):
        buffer += dec_str[point]
        point += 1
        if buffer in tree_dict:
            if ecd_type == 'start':
                start = tree_dict[buffer]
                code = dec_str[point : point + 8]
                point += 8
            else:
                code = tree_dict[buffer]
                if len(code) == 0:
                    code = ''
                else:
                    code = bin(ord(code))[2:]
                code = '0' * (8 - len(code)) + code
                start = dec_str[point : point + 16]
                point += 16
                start = int(start, 2)
            if start == 0:
                k = code
            else:
                k = id2tokens[start] + code
            encode_dict[k] = {
                'id': id,
                'start': start,
                'end': code
            }
            id2tokens[id] = k
            id += 1
            buffer = ''

    text = bytes('', encoding='utf8')
    for k in encode_dict:
        if encode_dict[k]['start'] == 0:
            v = bitarray(k).tobytes()
            text += v
        else:
            start_id = encode_dict[k]['start']
            v = id2tokens[start_id] + encode_dict[k]['end']
            text += bitarray(v).tobytes()
    return text


def decode_tree(dec_tree, ecd_type):
    num_code = len(dec_tree) // 26
    tree_dict = {}
    for i in range(num_code):
        kv_code = dec_tree[i * 26 : (i + 1) * 26]
        k = kv_code[:13]
        code = kv_code[13:]
        true_code = ''
        flag = False
        for ci in range(len(code)):
            if flag:
                true_code += code[ci]
            else:
                if code[ci] == '1':
                    flag = True
        # print(true_code)
        if ecd_type == 'start':
            k = int(k, 2)
        else:
            k = kv_code[5:13]
            k = bitarray(k).tobytes()
        tree_dict[true_code] = k
    return tree_dict

if __name__ in '__main__':
    path = 'Introduction to Data Compression.txt'
    docx_path = 'Introduction to Data Compression.docx'

    #For .docx
    # doc = docx.Document(docx_path)
    # with open('Introduction to Data Compression.txt', 'w') as f:
    #     for p in doc.paragraphs:
    #         f.write(p.text + '\n')

    with open(path, 'rb') as f:
        text = f.read()

    #Original LZ78
    lz78 = encode(text)
    with open('lz78.bin', 'wb') as f:
        lz78.tofile(f)
    decode_text = decode(lz78)
    print(decode_text == text)

    #LZ78-Hp
    lz78 = hft_encode(text, 'start')
    with open('lz78_hp.bin', 'wb') as f:
        lz78.tofile(f)
    decode_text = hft_decode(lz78, 'start')
    print(decode_text == text)

    #LZ78-Hs
    lz78 = hft_encode(text, 'end')
    with open('lz78_tail.bin', 'wb') as f:
        lz78.tofile(f)
    decode_text = hft_decode(lz78, 'end')
    print(decode_text == text)
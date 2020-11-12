def Lz77compress(win, message):
    length = 0  # 匹配到的长度
    pointer = 0  # 指针，初始指向第一个位置
    compressed_message = list()     #使用元组存储
    while True:
        if pointer - win < 0:
            match = message[0:pointer]
        else:
            match = message[pointer - win:pointer]
        while match.find(message[pointer:pointer + length + 1]) != -1:
            length += 1
        first = match.find(message[pointer:pointer + length])
        if pointer - win > 0:
            first += pointer - win
        if length != 0:
            a = (pointer - first, length, message[pointer + length])
            compressed_message.append(a)
            pointer += length + 1
        else:
            b = (0,0,message[pointer])
            compressed_message.append(b)
            pointer +=1
        length = 0
        if pointer == len(message):
            break
    print(compressed_message)
    return compressed_message

def Lz77decompress(compressed_message):
    de_msg = ""
    for s in compressed_message:
        if s[0] != 0:
            de_msg += de_msg[(len(de_msg) - s[0]): (len(de_msg) - s[0] + s[1])]
        de_msg += s[2]
    print(de_msg)

if __name__ == '__main__':
    message="abcdbbccaaabaeaaabaee"
    win=10
    comp=Lz77compress(win,message)
    Lz77decompress(comp)
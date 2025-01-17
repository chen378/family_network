import base64


def identity2finger(identity):
    return base64.b64decode(identity + "=").hex()


def the_data_handler(file_name, day, hour, last_dict, cur_dict):
    wholetext = read_the_file(file_name)
    mining(wholetext, day, hour, last_dict, cur_dict)


def read_the_file(file_name):
    file_object = open(file_name, "r")
    wholetext = file_object.read()
    file_object.close()
    return wholetext


def is_useful(wholetext):
    if "Measured" not in wholetext:
        return False
    return True


def mining(wholetext, day, hour, last_dict, cur_dict):
    linelist = wholetext.split('\n')
    line_idx = 0
    while not linelist[line_idx].startswith('r '):
        line_idx += 1
        continue

    for idx in range(line_idx, len(linelist)):
        cur_line = linelist[idx]
        if cur_line.startswith('r '):
            templist = cur_line.split(' ')
            try:
                if templist[2] == 'AVTVOeQJBteeXt7jmuJwZYU1eso':
                    print()
                finger = identity2finger(templist[2])
            except:
                print()
            if last_dict.__contains__(finger):
                last_seq = last_dict[finger]
                last_seq += "1"
                cur_dict[finger] = last_seq
            else:
                seq = ""
                for i in range(hour + 24 * (day - 1)):
                    seq += "0"
                seq += "1"
                cur_dict[finger] = seq
    key = [k for k in last_dict.keys() if k not in cur_dict.keys()]  # ֮ǰ�� ����û�� ����0
    for k in key:
        last_seq = last_dict[k]
        length = len(last_seq)
        dif = hour + 1 + 24 * (day - 1) - length
        for i in range(dif):
            last_seq += "0"
        cur_dict[k] = last_seq

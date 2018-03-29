#coding:utf-8
from collections import Counter


def input_reading():
    datalist = []
    with open("input-data.txt", "r") as data:
        for line in data:
            transaction = set([i.strip() for i in line.replace(
                "{", "").replace("}", "").split(",")]) - set([''])
            if transaction:
                datalist.append(transaction)
    return datalist


def parameter_reading():
    mis = {}
    sdc = 0
    cannot_be_together = []
    must_have = []
    with open("parameter-file.txt", "r") as parameter:
        for line in parameter:
            if line.startswith("MIS"):
                key = line[line.find('(') + 1:line.find(')')]
                value = float(line[line.find('=') + 1:])
                mis[key] = value
            elif line.startswith("SDC"):
                sdc = float(line[line.find('=') + 1:])
            elif line.startswith("cannot_be_together"):
                cannot_be_together = []
                cbt_list = [i.strip() for i in line[line.find(':') + 1:].split("}")]
                for i in cbt_list:
                    cbt = set([i.strip() for i in i.replace("{", "").split(",")])-set([''])
                    if cbt:
                        cannot_be_together.append(cbt)
            elif line.startswith("must-have"):
                must_have = [i.strip()
                             for i in line[line.find(':') + 1:].split("or")]
        return mis, sdc, cannot_be_together, must_have


def init_pass(datalist, mis):
    c = Counter()
    t_count = len(datalist)
    freset = []
    for t in datalist:
        for m in mis:
            # print(t,m[0])
            if m[0] in t:
                c[m] += 1
    for item, imis in c:
        freset.append({'data': item, 'count': c[
            (item, imis)], 'mis': imis, 'support': c[
            (item, imis)] / float(t_count)})

    return freset


def level2_candidate_gen(fre_list, sdc, t_count):
    fre_list = sorted(fre_list, key=lambda a: a['mis'])
    candidate = []

    for i in range(0, len(fre_list)):
        if fre_list[i]['count'] >= fre_list[i]['mis'] * t_count:
            for j in range(i + 1, len(fre_list)):
                # print(fre_list[i],fre_list[j])
                if fre_list[j]['count'] >= fre_list[i]['mis'] * t_count and abs(fre_list[j][
                        'support'] - fre_list[i]['support']) <= sdc + 0.0001:
                    candidate.append(
                        {'data': (fre_list[i]['data'], fre_list[j]['data']), 'count': 0, 'tailcount': 0})
    return candidate


def ms_candidate_gen(fre_list, sdc, t_count, mis, sup):
    candidate = []
    fre_list = [i['data'] for i in fre_list]
    n = len(fre_list[0])
    for i in range(0, len(fre_list)):
        for j in range(i + 1, len(fre_list)):
            # print(fre_list[i], fre_list[j])

            if str(fre_list[i][:n - 1]) == str(fre_list[j][:n - 1]) and abs(sup[
                    fre_list[i][n - 1]] - sup[fre_list[j][n - 1]]) < sdc:

                join = list(fre_list[i])
                join.append(fre_list[j][n - 1])
                insert = True
                # print(join)
                for index in range(0, n + 1):
                    tjoin = list(join)
                    del tjoin[index]
                    # print(tjoin)
                    if join[0] in tjoin or mis[join[0]] == mis[join[1]]:
                        if tjoin not in fre_list:
                            insert = False
                if insert:
                    candidate.append(
                        {'data': tuple(join), 'count': 0, 'tailcount': 0})
    return candidate


def ms_apriori(datalist, mis, sdc):
    t_count = len(datalist)
    # print(t_count)
    mis = sorted(mis.items(), key=lambda a: a[1])
    # print(mis)
    fre_list = []
    l = init_pass(datalist, mis)
    # print(l)
    fre_list.append(filter(lambda a: True if a[
                    'count'] >= a['mis'] * t_count else False, l))
    # for i in fre_list[0]:
    #     print(i)
    # print(len(fre_list))
    sup = dict([(i['data'], i['support']) for i in l])
    mis = dict(mis)

    while len(fre_list[len(fre_list) - 1]) != 0:
        # print(len(fre_list))
        if len(fre_list) == 1:
            temp_coll = level2_candidate_gen(l, sdc, t_count)
            del l
        else:
            temp_coll = ms_candidate_gen(
                fre_list[len(fre_list) - 1], sdc, t_count, mis, sup)

        for t in datalist:
            # print(temp_coll)
            for c in temp_coll:
                # print(t,c)
                if set(c['data']).issubset(t):
                    c['count'] += 1
                if set(c['data'][1:]).issubset(t):
                    c['tailcount'] += 1
        fre_list.append([])
        for c in temp_coll:
            if c['count'] >= mis[c['data'][0]] * t_count:
                fre_list[len(fre_list) - 1].append(c)
    return fre_list


def constraint_filter(fre_set, cannot_be_together, must_have):
    for i in fre_set:
        for j in range(0, len(i)):
            if type(i[j]['data']) == str:
                if i[j]['data'] not in must_have:
                    i[j] = 0
            else:
                if len(set(i[j]['data']) & set(must_have)) == 0:
                    i[j] = 0
                    continue
                for cbt in cannot_be_together:
                    if cbt.issubset(set(i[j]['data'])):
                        i[j] = 0
                        break

    fre_set = [list(filter(lambda a: True if a != 0 else False, item))
               for item in fre_set]

    return fre_set


def result_writing(freset):

    with open("output-patterns.txt", "w") as writefile:
        for itemsets in freset:
            if len(itemsets) > 0:

                if type(itemsets[0]['data']) == str:
                    writefile.write('Frequent 1-itemsets\n\n')
                    for fset in sorted(itemsets, key=lambda a: a['count']):
                        writefile.write('\t')
                        writefile.write(str(fset['count']))
                        writefile.write(' : {')
                        writefile.write(str(fset['data']))
                        writefile.write('}\n')

                else:
                    writefile.write(
                        'Frequent ' + str(len(itemsets[0]['data'])) + '-itemsets\n\n',)
                    for fset in sorted(itemsets, key=lambda a: a['count']):
                        writefile.write('\t')
                        writefile.write(str(fset['count']))
                        writefile.write(' : ')
                        writefile.write(str(fset['data']).replace(
                            "(", "{").replace(")", "}").replace("'", ""))
                        writefile.write('\nTailcount = ' +
                                        str(fset['tailcount']) + '\n')
                writefile.write(
                    '\n\tTotal number of freuqent 1-itemsets = ' + str(len(itemsets)))
                writefile.write('\n\n\n')

if __name__ == '__main__':
    datalist = input_reading()
    mis, sdc, cannot_be_together, must_have = parameter_reading()
    fre_set = ms_apriori(datalist, mis, sdc)
    fre_set = constraint_filter(fre_set, cannot_be_together, must_have)
    result_writing(fre_set)

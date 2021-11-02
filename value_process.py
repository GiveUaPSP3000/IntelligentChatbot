# so powerful process to extract the value in sentences and convert to correct number
# 今天原价30元的10块糖，我用了大约20块就买下来了40块糖
# 三十二块7毛八 32元8角

import re


def value_find(st):
    """
    check the true money spend in result
    :param st: original text
    :return: real money spend or False
    """
    ste_p = re.findall(
        "[一二两三四五六七八九][十百千万元块毛角新分\.,，][十百千零元块毛角新分\.,，一二三四五六七八九]*|[十][一二三四五六七八九元块毛角新分\.,，]+|[1-9][0-9]*[元块新角毛分\.,，0-9一二两三四五六七八九十]*",
        st)
    key_words = ['花了', '用了', '给了', '赚了', '付了', '转了', '亏了', '刷了', '借了', '交了', '得了', '收入', '用掉', '掉了']
    money_words = ['元', '块', '新', '分', '角', '毛']
    # 确定是否有多个结果
    if len(ste_p) > 1:
        loop_l = len(ste_p) - 2
        ste = []
        for r in range(0, loop_l):
            if st.find(ste_p[r]) + len(ste_p[r]) == st.find(ste_p[r + 1]):
                ste.append(ste_p[r] + ste_p[r+1])
                r += 1
            else:
                ste.append(ste_p[r])
        if st.find(ste_p[-2]) + len(ste_p[-2]) == st.find(ste_p[-1]):
            ste.append(ste_p[-2] + ste_p[-1])
        else:
            ste.append(ste_p[-2])
            ste.append(ste_p[-1])
        if len(ste) > 1:
            index_re = []
            # 查找离key_words最近的表达
            for money in ste:
                index_re.append([st.find(money), money])
            for key_word in key_words:
                k_index = st.find(key_word)
                if k_index != -1:
                    for index_s in index_re:
                        if index_s[0] > k_index:
                            return index_s[1].replace(',', '').replace('，', '')
            # 如果没有，再尝试找有金钱单位表达的
            for money in ste:
                for money_word in money_words:
                    if money_word in money:
                        return money.replace(',', '').replace('，', '')
            # 如果没有则返回错误
            return False
        else:
            return ste[0].replace(',', '').replace('，', '')
    else:
        return ste_p[0].replace(',', '').replace('，', '')


def _trans(s):
    digit = {'一': 1, '两': 2, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9}
    num = 0
    if s:
        idx_q, idx_b, idx_s = s.find('千'), s.find('百'), s.find('十')
        if idx_q != -1:
            num += digit[s[idx_q - 1:idx_q]] * 1000
        if idx_b != -1:
            num += digit[s[idx_b - 1:idx_b]] * 100
        if idx_s != -1:
            # 十前忽略一的处理
            num += digit.get(s[idx_s - 1:idx_s], 1) * 10
        if s[-1] in digit:
            num += digit[s[-1]]
    return num


def pre_pro(text):
    """
    process the text
    :param text:
    :return:
    """
    digit = {'零': 0, '一': 1, '两': 2, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9}
    for i in digit:
        text = text.replace(i, str(digit[i]))
    return text


def trans(chn):
    te_text = pre_pro(chn)
    if te_text.isdigit():
        return int(te_text)
    chn = chn.replace('零', '')
    idx_y, idx_w = chn.rfind('亿'), chn.rfind('万')
    if idx_w < idx_y:
        idx_w = -1
    num_y, num_w = 100000000, 10000
    if idx_y != -1 and idx_w != -1:
        return trans(chn[:idx_y]) * num_y + _trans(chn[idx_y + 1:idx_w]) * num_w + _trans(chn[idx_w + 1:])
    elif idx_y != -1:
        return trans(chn[:idx_y]) * num_y + _trans(chn[idx_y + 1:])
    elif idx_w != -1:
        return _trans(chn[:idx_w]) * num_w + _trans(chn[idx_w + 1:])
    return _trans(chn)


def value_get(o_text):
    if o_text.isdigit():
        return float(o_text)
    else:
        return trans(o_text)


def number_comp(text):
    value = 0.0
    for i in ['块', '元', '新']:
        text = text.replace(i, '.')
    for i in ['角', '毛']:
        text = text.replace(i, '*')

    text = text.strip('.')
    # 一定有块以及角或者分
    if '.' in text:
        list1 = text.split('.')
        value += value_get(list1[0])
        # 一定有块，且有角有分
        if '*' in list1[1]:
            list2 = list1[1].split('*')
            text3 = list2[1].strip('分')
            value += 0.1 * value_get(list2[0]) + 0.01 * value_get(text3)
        # 一定有块，且无角有分
        elif '分' in list1[1]:
            text3 = list1[1].strip('分')
            value += 0.01 * value_get(text3)
        # 一定有块，且有角无分
        else:
            cent_value = value_get(list1[1])
            if cent_value >= 10:
                value += 0.01 * cent_value
            else:
                value += 0.1 * cent_value
    # 无块，此时为角分组合，或者有且仅有块
    else:
        # 一定无块且是有角不确定分组合
        if '*' in text:
            text = text.strip('*')
            # 一定是角和分
            if '*' in text:
                list2 = text.split('*')
                text3 = list2[1].strip('分')
                value += 0.1 * value_get(list2[0]) + 0.01 * value_get(text3)
            # 一定只有角
            else:
                value += 0.1 * value_get(text)
        # 一定无块无角只有分
        elif '分' in text:
            text3 = text.strip('分')
            value +=0.01 * value_get(text3)
        # 一定只有块
        else:
            value += value_get(text)
    return value

import pickle
# load the stop words file
stpwrdpath = "stop_words.txt"
stpwrd_dic = open(stpwrdpath, 'r', encoding='utf-8')
stpwrd_content = (stpwrd_dic.read()).split('\n')
save_dict = {}
for word in stpwrd_content:
    if word not in save_dict:
        save_dict[word] = True
with open('stopwords_dict.pkl', 'wb') as tf:
    pickle.dump(save_dict, tf)

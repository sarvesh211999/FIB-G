from flask import Flask
from flask import render_template
from flask import url_for
from flask import request
from werkzeug import secure_filename
import os
from textblob import TextBlob
from rake_nltk import Rake
from textblob import Word
import nltk
import sys,re
import json
import spacy

nlp = spacy.load('en_core_web_lg')
app = Flask(__name__)
input = ''
data = ''
filename = ''

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/text',methods=['POST','GET'])
def result():
    outputs=[]
    filename = None
    input=request.form['comments']
    outputs.append(answer(input,filename))
    # print(outputs[0])
    return render_template("result.html",results=outputs[0],len=len(outputs))

@app.route('/uploader', methods = ['GET', 'POST'])
def upload_file():
    outputs=[]
    if request.method == 'POST':
        f = request.files['file']
        f.save(secure_filename(f.filename))
        filename = f.filename
    outputs=answer(input,filename)
    return render_template("result.html",results=outputs,len=len(outputs))

def answer(input,filename):
    temp=[]
    contents = []
    cindex = -1
    if(filename):
        with open(filename,'r') as f:
            data_in = f.read()
    else:
        data_in = input
        data_in="1.0 Placeholder\n"+data_in
    
    data_in = re.sub('\n{2,}','\n',data_in)
    if re.search('Summary',data_in):
        temp_summ = re.search('Summary',data_in).start()
        data_in = data_in[:temp_summ]
    # print(data_in)
    if re.search('[0-9]{1,2}\.1',data_in):
        temp_summ = re.search('[0-9]{1,2}\.1',data_in).start()
        data_in = data_in[temp_summ:]

    # print(data_in)

    data_in = re.sub(r"\b(FIG)\.\s[0-9\.]{2,}s?\b", "",data_in,flags=re.IGNORECASE)
    data_in = re.sub("(^|\s)(I|(II)|(III)|(IV)|(V)|(VI)|(VII)|(VIII)|(IX)|X)($|\s)","",data_in,flags=re.IGNORECASE)

    
    paras = data_in.split("\n")
    paras = [i.strip() for i in paras if i is not ""]

    for ele in paras:
        # print(ele)
        if re.search("^[0-9]{1,2}\.[0-9]",ele):
            # print(ele)
            cindex+=1
            contents.append([])
        else:
            if cindex==0:
                continue
            contents[cindex].append(ele)

    if(input):
        contents = []
        contents.append([input])
        # print(contents)

    for text in contents:
        if(input):
            d=nlp(str(input))
            temp_text = str(input)
            # print(d)
            land=[(x.text,x.label_) for x in d.ents]
            final=[]
            for iii in land:
                if iii[1]=="PERSON" or iii[1]=="LAW":
                    final.append(iii[0])
            for i in final:
                # print(temp_text)
                toappend_text=temp_text.replace(i,"____________"),
                # print(temp_text[0])
                temp.append((toappend_text[0],i))
        global output
        output=set()
        if len(text)==0:
            continue
        text=' '.join(text)
        text=re.sub(r'\’',r'',text)
        text=text.lower()
        text = TextBlob(text)
        par_text=TextBlob("")
        for sentence in text.sentences:
            par_text+=paraphrase(sentence)
            par_text+=" "

        par_text=par_text.strip()
        par_text=str(par_text)
        r=Rake()
        r.extract_keywords_from_text(par_text)
        par_text=TextBlob(par_text)
        #print(r.get_ranked_phrases())
        counter=0
        for i in r.get_ranked_phrases():
            counter+=1
            if counter>20:
                break
            for sentence in par_text.sentences:
                if i in sentence:
                    pos(sentence,i)

        count=0
        for i in output:
            count+=1
            temp.append(i)
            # print(i)
    return temp

def paraphrase(sentence):
    return sentence

def pos(sentence,i):
    sentence=str(sentence)
    global output
    re.sub(".*.∗","",sentence)
    re.sub("(^|\s)(I|(II)|(III)|(IV)|(V)|(VI)|(VII)|(VIII)|(IX)|X)($|\s)","",sentence,flags=re.IGNORECASE)
    re.sub(r"\b(FIG)\s[0-9\.]{2,}s?\b", "",sentence,flags=re.IGNORECASE)
    sentence=TextBlob(sentence)
    pos_broke=sentence.tags
    store=[]
    for j in range(len(pos_broke)-1):
        if pos_broke[j][1]=="CD" and pos_broke[j+1][1][:2]=="NN":
            store.append([j,str(pos_broke[j][0])])
        elif pos_broke[j][1][:2]=="JJ" and pos_broke[j+1][1][:2]=="NN":
            store.append([j,str(pos_broke[j][0])])
        elif pos_broke[j][1][:3]=="NNP":
            store.append([j,str(pos_broke[j][0])])
    if pos_broke[len(pos_broke)-1][1][:3]=="NNP":
        store.append([len(pos_broke)-1,str(pos_broke[len(pos_broke)-1][0])])
    
    remove=[]
    for j in store:
        if i.find(j[1])!=-1:
            if len(j[1].split())==2:
                remove=[j[0],j[0]+1]
            else:
                remove=[j[0]]

    sen=""
    if len(remove)!=0:
        for j in range(len(pos_broke)):
            if j in remove:
                ans=pos_broke[j][0]
                sen+="________ "
            else:
                sen+=pos_broke[j][0]
                sen+=" "
        output.add((sen,ans))



if __name__ == '__main__':
    app.run(debug=True, port=8080)
#    app.run(debug=True)
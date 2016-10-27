# -*- coding: utf-8 -*-
"""
Created on Mon Oct  3 11:09:41 2016

@author: Vergil
"""

import re
import nltk
from nltk import PCFG
from nltk.corpus import wordnet
from nltk.stem import WordNetLemmatizer
from nltk.tree import *
from nltk.draw import tree
import sys

s="""
S : NP VP 1.0;
VP : Vi 0.2
    | Vt NP 0.5
    | VP PP 0.2;        # VP not sum up to 1.0
NP : DT NN 0.8          # missing rule for DT
    | NP PP 0.2;
PP : IN NP 1.0          # missing ; for end rule
Vi -> sleeps 1.0;	# rule should not use ->
Vt : saw 1.0;
NN : man 0.1
     woman 0.1          # missing |
    | telescope 0.3
    | dog 0.5;
IN : with 0.6
    | in 0.4;
W = The man saw the dog with the telescope.
"""


#==============================================================================
# s="""
# S : NP VP 1.0;
# VP : Vi 0.3
#     | Vt NP 0.5
#     | VP PP 0.2;
# NP : DT NN 0.8
#     | NP PP 0.2;
# PP : IN NP 1.0;
# Vi : sleep 1.0;
# Vt : see 1.0;
# NN : man 0.1
#     | woman 0.1
#     | telescope 0.3
#     | dog 0.5;
# DT : the 1.0;
# IN : with 0.6
#     | in 0.4;
# W = The man saw the dog with the telescope.
# """
#==============================================================================

#==============================================================================
# s = """
# # starting with grammar
# # Terminal should always lower case, Nonterminal starts with capital case
# S  : NP Vp 1.0;
# NP : NP PP 0.4  # continue
#         | astronomer 0.1
#     |ear        0.18
#     | saw 0.04
#     | star 0.18
# | telescope 0.1;
# PP : P NP 1.0;
# Vp : V NP 0.7 | Vp PP 0.3;	# put in a single line
#  P : with 1.0;
#  V : see 1.0;
# #	test sentence
# W = Astronomers saw stars with ears.
# # don't forgot to put ENDFILE here
# """
#==============================================================================


#==============================================================================
# s = """# I am actually not sure about that
# S : NP VP 1.0; NP : NP PP 0.4  # This is great
# | astronomer 0.1 | ear 0.18
# | saw 0.04
# | star 0.18
# | telescope 0.1; PP : P NP 1.0;
# VP : V NP 0.7
# | VP PP 0.3; P : with 1.0;
# V : see 1.0;
# W = Astronomers saw stars with ears.
# """
#==============================================================================

#s = ''
#for line in sys.stdin:
#    s = s + line

s = re.sub('#.*\n','\n',s)
s = re.sub('\|',' | ', s)
    
def normalize(l):
    SUM = sum(l)
    for i in range(len(l)):
        l[i] = l[i]/SUM

def isfloat(value):
  try:
    float(value)
    return True
  except ValueError:
    return False

def isOP(value):
    if value == ';' or value == '|' or value == '=' or value == ':' or value == '.':
        return True
    else:
        return False

def isLegal(value):
    if not (value == 'NP' or value == 'S' or value == 'VP' or value == 'PP' or value == 'V' or value == 'P' or value == 'W'):
        return True
    else:
        return False
        
wordnet_lemmatizer = WordNetLemmatizer()

def printStuff(s):
    line = 1
    print('Stemmer:')
    for i in range(len(s)):
        if s[i-1] == ';' or (s[i] != ';' and isfloat(s[i-1]) == True):
            line = line + 1
        if isfloat(s[i]) == True:
            print(s[i] + ' DOUBLE ' + str(line))
        elif isOP(s[i]) == True:
            print(s[i] + ' OP ' + str(line))
        else:
            s[i] = s[i].lower()
            if isLegal(s[i]) and str(type(wordnet.morphy(s[i]))) != "<class 'NoneType'>":
                print(s[i] + ' STRING ' + str(line) + ' ' + wordnet.morphy(s[i]))
            else:
                print(s[i] + ' STRING ' + str(line))
    print('ENDFILE')

#==============================================================================
# def checkSumToOne(l):
#     pos1 = l.index(';')
#     pos2 = l[pos1+1:].index(';')
#     temp = []
#     for i in range(pos1,pos2):
#         if isfloat(l[i]):
#             temp.append(float(l[i]))
#     return temp
#==============================================================================

tokens = nltk.word_tokenize(s)

printStuff(tokens)

rules = s[:s.find('W')-1]
rules = rules.replace(':','->')

sentence = s[s.find('W')+4:]
sentence = sentence.lower()

rules = rules.split()

for i in range(len(rules)-1):
    match = re.match('[a-z]',rules[i+1])
    if isfloat(rules[i]) and match:
        rules[i+1] = '| ' + rules[i+1]

rules = ' '.join(rules)
rules = rules.split()

for i in range(len(rules)-1):
    match = re.match('[A-Z]',rules[i+1])
    if isfloat(rules[i]) and match:
        rules[i] = rules[i] + ';'

rules = ' '.join(rules)
temp1 = rules.split(';')
for i in range(len(temp1)):
    temp = []
    temp2 = temp1[i].split()
    for j in range(len(temp2)):
        if isfloat(temp2[j]):
            temp.append(float(temp2[j]))
    normalize(temp)
    z = 0
    j = 0
    for j in range(len(temp2)):
        if isfloat(temp2[j]):
            temp2[j] = str(temp[z])
            z = z + 1
    temp1[i] = ' '.join(temp2)
rules = ' ; '.join(temp1)
rules = rules.split()

for i in range(len(rules)):
    if isfloat(rules[i]):
        rules[i] = '[' + rules[i] + ']' 


for i in range(len(rules)):
    if rules[i] == ';':
        rules[i] = '\n'

for i in range(len(rules)):
    match = re.match('[a-z]',rules[i])
    if match:
        rules[i] = '"' + rules[i] + '"'

rules = ' '.join(rules)
if rules.find('DT ->') == -1:
    rules = rules +'DT -> "the" [1.0]'
rules = re.sub('saw','see',rules)
rules = re.sub('- >','->',rules)

grammar = nltk.PCFG.fromstring(rules)


sent = sentence.split()

for i in range(len(sent)):
    if sent[i][-1] == '.':
        sent[i] = sent[i][:-1]
    if wordnet.morphy(sent[i]) is not None:
        sent[i] = wordnet.morphy(sent[i])
    if sent[i] == 'saw':
        sent[i] = 'see'

print('\nParsed Tree:')
viterbi_parser = nltk.ViterbiParser(grammar)
for tree in viterbi_parser.parse(sent):
    print(tree)
#    tree.draw()

#for tree in viterbi_parser.parse(sent):
#    tree.draw()


#!/usr/bin/env python2

import nltk

def read_until(of, string="\n"):
    buffer = ""
    stop = False
    while not stop:        
        c = of.read(1)
        #print(c)
        stop = stop or c == ""
        if not stop:
            buffer += c
            stop = stop or buffer.endswith(string)
    return buffer

def read_string(of, string=""):
    initial_pos = of.tell()
    for c in string:
        if c != of.read(1):
            of.seek(initial_pos, 0)#reset cursor position
            return False
    else:
        return True
    
def iter_sentences(of):
    sentence = read_until(of, string="$$\n")
    while len(sentence) > 0:
        yield sentence.rstrip("$$\n")
        sentence = read_until(of, string="$$\n")

def parse_nominal(sentence):    
    if sentence[0] != "[":
        return ("", sentence)
    else:
        index = sentence.index("]")
        nom = sentence[0:index+1]
        return (nom[1:-1].strip(" ").split(" "), sentence[index+1:].lstrip(" "))
        
def parse_token(sentence):
    (token, _, rest) = sentence.partition(" ")
    return (token, rest)
    
def parse_sentence(str):
    nominals = []
    words = []
    current = str
    while len(current) > 0:
        if current[0] == "[":
            (nom, current) = parse_nominal(current)
            nominals.append(nom)
            words.extend(nom)
        else:
            (tok, current) = parse_token(current)
            words.append(tok)
        
    return {"nominals": nominals, "words": words}
        
        
if __name__ == "__main__":
    import sys
    print(sys.argv)
    with open(sys.argv[1], mode="r") as tagged_sentences:
        sentences = iter_sentences(tagged_sentences)
        s1 = next(sentences)
        print(s1)
        for (key, val) in parse_sentence(s1).items():
            print("%s : %s\n"%(key, val))

        
    

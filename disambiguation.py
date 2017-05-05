#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import nltk


def zipper_to_list(zipper):
    (a, b, c) = zipper
    return a + [b] + c

class Sentence(object):
    __slots__ = ['nominals', 'elements', 'target', 'target_class']
    def __init__(self, nominals, words, target, target_class):
        self.target = target # mot cible(e.g. "interest")
        self.target_class = target_class # classe du mot cible(i.e. sens)
        # les groupes nominaux et les mots de la phrase sont organisés en "zipper"
        # soit des triplets (avant, cible, après), où "cible" est le mot cible ou le groupe nominal le contenant
        self.nominals = partition_by(nominals, lambda ws: member_by(ws, lambda x: x[0] == target))
        self.elements = partition_by(words, lambda w: w[0] == target)
    
    def words_zipper(self):
        "zipper contenant uniquement les mots(sans la classe lexicale)"
        (b, f, a) = self.elements
        return (map(lambda x:x[0], b), f[0], map(lambda x: x[0], a))

    def words_list(self):
        return zipper_to_list(self.words_zipper())
    
    def pos_zipper(self):
        "zipper contenant uniquement les classes lexicales"
        (b, f, a) = self.elements
        return (map(lambda x:x[1], b), f[1], map(lambda x: x[1], a))

    def pos_list(self):
        return zipper_to_list(self.pos_zipper())
    
    def word_context(self, n):
        "fenêtre de contexte de taille n des mots alentour du mot cible"
        (b, f, a) = self.words_zipper()
        return ([b[len(b)-i] if i <= len(b) else None for i in range(n,0, -1)], [a[i] if i < len(a) else None for i in range(n)])
    
    def pos_context(self, n):
        "Fenêtre de contexte de taille n des classes lexicales alentour du mot cible"
        (b, f, a) = self.pos_zipper()
        return ([b[len(b)-i] if i <= len(b) else None for i in range(n,0, -1)], [a[i] if i < len(a) else None for i in range(n)])

    def __iter__(self):
        return iter(self.elements)

    def iter_words(self):
        for (w, _) in zipper_to_list(self.elements):
            yield w

    def iter_pos(self):
        for (_, pos) in zipper_to_list(self.elements):
            yield pos

    def get_tagged_words_string(self):
        return " ".join(map(lambda w: "{}/{}".format(w[0],w[1]), zipper_to_list(self.elements)))

    def get_words_string(self):
        return " ".join(self.words_list())
    
    def __repr__(self):
        return "Sentence (class %s) %s"%(str(self.target_class), str(self.elements))
    
    def __str__(self):
        (b, f, a) = self.elements        
        return "Sentence (class {0}) : {1}".format(self.target_class, self.get_tagged_sentence_string())
    
    
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

def partition_by(seq, pred):
    for (i, x) in enumerate(seq):
        if pred(x):
            return (seq[0:i], x, seq[i+1:])
    else:
        (seq, None, [])

def member_by(seq, pred):
    for x in seq:
        if pred(x):
            return True
    else:
        return False
       
    
def iter_sentences(of):
    sentence = read_until(of, string="$$\n")
    while len(sentence) > 0:
        yield sentence.lstrip("=").rstrip("$$\n")
        sentence = read_until(of, string="$$\n")

        
def parse_word(string, target):
    (word, _, pos) = string.partition("/")
    if word.startswith(target):
        (_, _, target_class) = word.partition("_")
        return (target, pos, target_class)
    else:
        return (word, pos, None)


def parse_words(rem, target):
    rem = rem.strip(" ")
    while len(rem) > 0:
        (word, _, rem) = rem.partition(" ")        
        yield parse_word(word, target)


def parse_sentence(sentence, target):
    nominals = []
    words = []
    target_class = None
    rem = sentence
    while len(rem) > 0:
        rem = rem.strip(" ")
        if rem[0] == "[":
            (nom_str, _, rem) = rem[1:].partition("]")            
            nom = []
            for (w, pos, tc) in parse_words(nom_str, target):
                nom.append((w,pos))
                target_class = target_class or tc
            nominals.append(nom)
            words.extend(nom)
        else:
            (tok, _, rem) = rem.partition(" ")
            (word, pos, tc) = parse_word(tok, target)
            target_class = target_class or tc
            words.append((word, pos))
    return Sentence(nominals, words, target, target_class)

def generate_context_arff(file_name, sentences, context_type, context_size):
    relation = "{}-{}-context".format(context_size, context_type)
    attributes = ([("pred-{}".format(i), "string") for i in range(context_size, 0, -1)] +
                  [("succ-{}".format(i), "string") for i in range(1, context_size+1)] + [("class", "string")])
    context_generators = {
        "pos": Sentence.pos_context,
        "word": Sentence.word_context
    }
    cg = context_generators[context_type]
    with open(file_name, mode="w") as output:
        output.write("@relation "+relation+"\n")
        output.write("\n")
        for (a, t) in attributes:
            output.write("@attribute {} {}\n".format(a,t))
        output.write("\n")
        output.write("@data\n")
        for s in sentences:
            (pred, succ) = cg(s, context_size)
            for x in (pred+succ):
                output.write("'{}',".format(x) if x else "?,")
            output.write(s.target_class+"\n")


if __name__ == "__main__":
    import sys
    print(sys.argv)
    with open(sys.argv[1], mode="r") as tagged_sentences:
        sentences = map(lambda s:parse_sentence(s, "interest"), iter_sentences(tagged_sentences))
        # for s in sentences:
        #     print(s.word_context(2))
        for i in range(5):
            generate_context_arff("{}-pos-context.arff".format(i+1), sentences, "pos", i+1)
            generate_context_arff("{}-word-context.arff".format(i+1), sentences, "word", i+1)

        
    

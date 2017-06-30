#!/usr/bin/env python

import os
import time
import codecs
import optparse
import numpy as np
from loader import prepare_sentence
from utils import create_input, iobes_iob, zero_digits
from model import Model

optparser = optparse.OptionParser()
optparser.add_option(
    "-m", "--model", default="",
    help="Model location"
)
optparser.add_option(
    "-i", "--input", default="",
    help="Input file location"
)
optparser.add_option(
    "-o", "--output", default="",
    help="Output file location"
)
optparser.add_option(
    "-d", "--delimiter", default="__",
    help="Delimiter to separate words from their tags"
)
opts = optparser.parse_args()[0]

# Check parameters validity
assert opts.delimiter
assert os.path.isdir(opts.model)
assert os.path.isfile(opts.input)

# Load existing model
print "Loading model..."
model = Model(model_path=opts.model)
parameters = model.parameters

# Load reverse mappings
word_to_id, char_to_id, tag_to_id = [
    {v: k for k, v in x.items()}
    for x in [model.id_to_word, model.id_to_char, model.id_to_tag]
]

# Load the model
_, f_eval = model.build(training=False, **parameters)
model.reload()

f_output = codecs.open(opts.output, 'w', 'utf-8')
start = time.time()

print 'Tagging...'
with codecs.open(opts.input, 'r', 'utf-8') as f_input:
    count = 0
    words = []
    y_labels = []
    prev = "" 
    for line in f_input:
	if line.strip() != "":
            ls = line.rstrip().split() 
            word,y_label = ls[0],ls[-1] 
            words.append(word)
            y_labels.append(y_label)
            prev = word
            continue
        else:
            if prev == "": continue
            # Lowercase sentence
            if parameters['lower']:
                line = line.lower()
            # Replace all digits with zeros
            if parameters['zeros']:
                line = zero_digits(line)
            # Prepare input
            sentence = prepare_sentence(words, word_to_id, char_to_id,
                                        lower=parameters['lower'])
            input = create_input(sentence, parameters, False)
            # Decoding
            if parameters['crf']:
                y_preds = np.array(f_eval(*input))[1:-1]
            else:
                y_preds = f_eval(*input).argmax(axis=1)
            y_preds = [model.id_to_tag[y_pred] for y_pred in y_preds]
            # Output tags in the IOB2 format
            if parameters['tag_scheme'] == 'iobes':
                y_preds = iobes_iob(y_preds)
            # Write tags
            assert len(y_preds) == len(words)
            print 'y_preds:',len(y_preds), 'words:',len(words), 'y_labels:',len(y_labels)
            assert len(y_preds) == len(y_labels)
            #f_output.write('%s\n' % ' '.join('%s%s%s' % (w, opts.delimiter, y)
                                             #for w, y in zip(words, y_preds)))
            elems = [ (words[i], y_labels[i], y_preds[i]) for i in range(len(y_labels))]
            for x,y,z in elems:
                f_output.write('%s %s %s\n' % (x, y, z) )

            f_output.write('\n')
            words = []
            y_labels = []
            prev = line.strip()
        count += 1
        if count % 100 == 0:
            print count

print '---- %i lines tagged in %.4fs ----' % (count, time.time() - start)
f_output.close()

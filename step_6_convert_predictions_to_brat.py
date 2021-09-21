# Part 6 of our pipeline:
# All predictions that are in BIO(SE) format until now are converted
# to the target BRAT format with standoff annotations
# Copyright (c) 2021 Robert Bosch GmbH
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import argparse
import os
from tqdm import tqdm
from collections import namedtuple
Annotation = namedtuple('Annotation', ['tid', 'type', 'start', 'end', 'text'])
Token = namedtuple('Token', ['id', 'text', 'begin', 'end', 'label'])

parser = argparse.ArgumentParser()
parser.add_argument('--input', type=str, required=True)
parser.add_argument('--output', type=str, required=True)
parser.add_argument('--text_files', type=str, required=True)

args = parser.parse_args()
args.input = args.input if args.input.endswith('/') else args.input + '/'
args.output = args.output if args.output.endswith('/') else args.output + '/'
args.text_files = args.text_files if args.text_files.endswith('/') else args.text_files + '/'
os.makedirs(args.output, exist_ok=True)
print('Print ensemble predictions to: ' + args.output)


def read_file_into_sentences(fname, as_flat=True, as_tokens=True):
    """Read the file content as Token objects"""
    with open(fname, 'r') as fin:
        content = fin.read().splitlines()
        all_ids, all_texts, all_labels = [[]], [[]], [[]]
        all_begins, all_ends = [[]], [[]]
        for line in content:
            if len(line.strip()) > 0:
                l = line.split('\t')
                ids, text, begin, end = l[0:4]
                pred_label = l[-1]
                if pred_label == '<unk>':
                    print(fname)
                #if pred_label != 'O' and not label_filter in pred_label:
                #    print(f"converted {pred_label} to O")
                #    pred_label = 'O'
                
                all_ids[-1].append(ids)
                all_texts[-1].append(text)
                all_labels[-1].append(pred_label)
                all_begins[-1].append(begin)
                all_ends[-1].append(end)
            elif len(all_ids[-1]) > 0:
                all_ids.append([])
                all_texts.append([])
                all_labels.append([])
                all_begins.append([])
                all_ends.append([])
        if as_flat:
            all_ids = [token for sent in all_ids for token in sent]
            all_texts = [token for sent in all_texts for token in sent]
            all_labels = [token for sent in all_labels for token in sent]
            all_begins = [token for sent in all_begins for token in sent]
            all_ends = [token for sent in all_ends for token in sent]
        if as_tokens:
            assert as_flat
            
            tokens = []
            for idx, text, label, begin, end in zip(all_ids, all_texts, all_labels, all_begins, all_ends):
                tokens.append(Token(idx, text, begin, end, label))
            return tokens
        return all_ids, all_texts, all_labels, all_begins, all_ends
    
def copy_text_file(infile, outfile):
    """Simply copies the content of a file"""
    with open(infile, 'r') as fin:
        content = fin.read()
    with open(outfile, 'w') as fout:
        fout.write(content)
    return content
    
def convert_to_ann(tokens, text):
    """Converts the BIO tokens to BRAT standoff annotations"""
    annotations = []
    anno_id = 1
    anno_start = -1
    anno_end = -1
    anno_text = []
    anno_type = ''

    for token in tokens:
        label = token.label

        # store annotation
        if (label[0] == 'B' or label[0] == 'S' or label == 'O') and anno_start > 0:
            #anno_text = ' '.join(anno_text)
            anno_text = text[anno_start:anno_end]
            annotations.append(Annotation(anno_id, anno_type, anno_start, anno_end, anno_text))
            anno_id += 1
            anno_start, anno_end = -1, -1
            anno_type = ''
            anno_text = []

        # start new annotation
        if label[0] == 'B' or label[0] == 'S':
            anno_start = int(token.begin)
            anno_end = int(token.end)
            anno_text.append(token.text)
            anno_type = label[2:]

        # continue annotation
        if label[0] == 'I' or label[0] == 'E': 
            anno_end = int(token.end)
            anno_text.append(token.text)

    if anno_start > 0:
        #anno_text = ' '.join(anno_text)
        anno_text = text[anno_start:anno_end]
        annotations.append(Annotation(anno_id, anno_type, anno_start, anno_end, anno_text))

    ann_content = ''
    for a in annotations:
        ann_content += 'T' + str(a.tid)
        ann_content += '\t'
        ann_content += a.type
        ann_content += ' '
        ann_content += str(a.start)
        ann_content += ' '
        ann_content += str(a.end)
        ann_content += '\t'
        ann_content += a.text.replace('\n', ' ')
        ann_content += '\n'
    return ann_content[:-1]



for fname in tqdm(os.listdir(args.input)):
    tokens = read_file_into_sentences(args.input + fname)

    txt_name = fname.replace('.bio', '.txt')
    text_content = copy_text_file(args.text_files + txt_name, args.output + txt_name)

    ann_name = fname.replace('.bio', '.ann')
    annotations = convert_to_ann(tokens, text_content)
    with open(args.output + ann_name, 'w') as fout:
        fout.write(annotations)

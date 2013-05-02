
import sys
import os.path
#import gzip
from glob import iglob

def scan_corpus(training_corpus_loc):
  """
  Scans through the training corpus and counts how many lines of text there are
  """
  uni_dict = {}
  bi_dict = {}
  term_count = 0
  for block_fname in iglob( os.path.join( training_corpus_loc, '*.txt' ) ):
    print >> sys.stderr, 'processing dir: ' + block_fname
    with open( block_fname ) as f:
      num_lines = 0
      for line in f:
        # remember to remove the trailing \n
        line = line.rstrip()
        words = line.split()
        
        for i in range(0, len(words)):
          if words[i] in uni_dict:
            uni_dict[words[i]] += 1
          else:
            uni_dict[words[i]] = 1
            term_count += 1
          if i > 0:
            tup = (words[i-1],words[i])
            if tup in bi_dict:
              bi_dict[tup] += 1
            else:
              bi_dict[tup] = 1
        num_lines += 1
      print >> sys.stderr, 'Number of lines in ' + block_fname + ' is ' + str(num_lines)
      print >> sys.stderr, 'num terms so far ' + str(term_count)

def read_edit1s(edit1s_loc):
  """
  Returns the edit1s data
  It's a list of tuples, structured as [ .. , (misspelled query, correct query), .. ]
  """
  edit1s = []
  with open(edit1s_loc) as f:
    # the .rstrip() is needed to remove the \n that is stupidly included in the line
    edit1s = [ line.rstrip().split('\t') for line in f if line.rstrip() ]
  return edit1s

if __name__ == '__main__':
  print(sys.argv)
  if len(sys.argv) == 3:
    edit1s_loc = sys.argv[2]
    corpus_loc = sys.argv[1]
    scan_corpus(corpus_loc)
    read_edit1s(edit1s_loc)
  else:
    print >> sys.stderr, 'extra credit not implemented'

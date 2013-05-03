
import sys
import os.path
#import gzip
from glob import iglob
import marshal

def serialize_data(data, fname):
  """
  Writes `data` to a file named `fname`
  """
  with open(fname, 'wb') as f:
    marshal.dump(data, f)

def find_difference(misspell, correct):
  length = min(len(misspell), len(correct))
  index = 0
  diff = False
  for i in range(0, length):
    if misspell[i] != correct[i]: 
      diff = True
      break
    index = index + 1
  prev = '$'
  if index != 0:
    prev = misspell[index - 1]
  if diff:
    return (misspell[index], correct[index], prev, index)
  else:
    if len(misspell) > len(correct):
      return (misspell[index], '$', prev, index)
    else:
      return ('$', correct[index], prev, index)

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
  # serializable data to be saved
  data = []
  data.append(term_count)
  data.append(uni_dict)
  data.append(bi_dict)
  serialize_data(data, "lang_model")

def read_edit1s(edit1s_loc):
  """
  Returns the edit1s data
  It's a list of tuples, structured as [ .. , (misspelled query, correct query), .. ]
  """
  uniletters_count = {}
  biletters_count = {}
  edit_map = {}
  edit1s = []
  with open(edit1s_loc) as f:
    # the .rstrip() is needed to remove the \n that is stupidly included in the line
    edit1s = [ line.rstrip().split('\t') for line in f if line.rstrip() ]
    for x in range(0, len(edit1s)):
      print >> sys.stderr, x
      misspell = edit1s[x][0]
      correct = edit1s[x][1]
      if "$" not in uniletters_count:
        uniletters_count["$"] = 1
      else:
        uniletters_count["$"] += 1
      for i in range(0, len(correct)):
        if i == 0:
          if "$" + correct[i] not in biletters_count:
            biletters_count["$" + correct[i]] = 1
          else:
            biletters_count["$" + correct[i]] += 1
        if correct[i] in uniletters_count:
          uniletters_count[correct[i]] = uniletters_count[correct[i]] + 1
        else:
          uniletters_count[correct[i]] = 1 
        if i != len(correct) -1:
          if correct[i:i+2] in biletters_count:
            biletters_count[correct[i:i+2]] = biletters_count[correct[i:i+2]] + 1
          else:
            biletters_count[correct[i:i+2]] = 1
      val = ("", '', '')   
      if (misspell != correct): 
        diff = find_difference(misspell, correct)
        if len(misspell) != len(correct):
          # DELETE
          if len(misspell)+1 == len(correct):
            val = ("DEL", diff[2], diff[1]) 
          # INSERT
          elif len(misspell) == len(correct)+1:
            val = ("INS", diff[2], diff[0])
        else:
          # SUBSTITUTE
          if misspell[0:diff[3]]+diff[1]+misspell[diff[3]+1:] == correct:
            val = ("SUBS", diff[1], diff[0])
          # TRANSPOSE
          elif misspell[0:diff[3]]+misspell[diff[3]+1]+misspell[diff[3]] == correct:
            val = ("TRANS", diff[1], correct[diff[3]+1])
      if val in edit_map:
        edit_map[val] = edit_map[val] + 1
      else:
        edit_map[val] = 1
  
  # serializable data to be saved
  data = []
  data.append(uniletters_count)
  data.append(biletters_count)
  data.append(edit_map)
  serialize_data(data, "edit1s_model")



if __name__ == '__main__':
  print(sys.argv)
  if len(sys.argv) == 3:
    edit1s_loc = sys.argv[2]
    corpus_loc = sys.argv[1]
    scan_corpus(corpus_loc)
    read_edit1s(edit1s_loc)
  elif len(sys.argv) == 4:
    edit1s_loc = sys.argv[3]
    corpus_loc = sys.argv[2]
    scan_corpus(corpus_loc)
    read_edit1s(edit1s_loc)
  else:
    print >> sys.stderr, 'incorrect usage'

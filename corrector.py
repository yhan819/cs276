
import sys
import marshal

queries_loc = 'data/queries.txt'
gold_loc = 'data/gold.txt'
google_loc = 'data/google.txt'

alphabet = "abcdefghijklmnopqrstuvwxyz0123546789&$+_' "

def unserialize_data(fname):
  with open(fname, 'rb') as f:
    return marshal.load(f)

def read_query_data(qry_file):
  """
  all three files match with corresponding queries on each line
  NOTE: modify the signature of this method to match your program's needs
  """
  queries = []
  gold = []
  google = []
  with open(qry_file) as f:
    for line in f:
      queries.append(line.rstrip())
  with open(gold_loc) as f:
    for line in f:
      gold.append(line.rstrip())
  with open(google_loc) as f:
    for line in f:
      google.append(line.rstrip())
  #assert( len(queries) == len(gold) and len(gold) == len(google) )
  return (queries, gold, google)

def get_1edit_word(word):
  ans = []
  ans.append(word)
  for i in range(0,len(word)):
    #insertion
    for a in alphabet:
      ans.append(word[0:i] + a + word[i:])
      if a != word[i]:
        #substitution
        ans.append(word[0:i] + a + word[i+1:]) 
    #deletion
    ans.append(word[0:i] + word[i+1:])
    if i < len(word) - 1:
      ans.append(word[0:i] + word[i+1] + word[i] + word[i+1:])
  return ans

def generate_cand(data, query):
  uni_dict = data[1]
  bi_dict = data[2]
  '''
  look at bigram, if it doesn't exist, generate 1-edit words
  '''
  cand = []
  words = query.split()
  fixed = False
  for i in range(1,len(words)):
    if (words[i-1], words[i]) not in bi_dict:
      fixed = True
      if i == 1:
        org = words[i-1]
        edit_1 = get_1edit_word(words[i-1])
        for c in edit_1:
          if c in uni_dict:
            words[i-1] = c
            cand.append(' '.join(words))
        words[i-1] = org
       
      org = words[i]
      edit_1 = get_1edit_word(words[i])
      for c in edit_1:
        if c in uni_dict:
          words[i] = c
          cand.append(' '.join(words))
      words[i] = org
  if not fixed:
    cand.append(query)
  return cand
      

def correct_uniform(data, queries, gold, google):
  num_term = data[0]
  uni_dict = data[1]
  bi_dict = data[2]
  
  print >> sys.stderr, bi_dict[('mw','tth')]
  for i in range(0, len(queries)):
    candidates = generate_cand(data, queries[i])   
    for c in candidates:
      print >> sys.stderr, c
  

if __name__ == '__main__':
  print(sys.argv)
  lm = sys.argv[1]
  qry_file = sys.argv[2]

  (queries, gold, google) = read_query_data(qry_file)
  print >> sys.stderr, "read query data"

  if lm == "uniform":
    data = unserialize_data("lang_model")
    
    correct_uniform(data, queries, gold, google)   
    
    print >> sys.stderr, len(queries)
    



import sys
import marshal
import math

queries_loc = 'data/queries.txt'
gold_loc = 'data/gold.txt'
google_loc = 'data/google.txt'

alphabet = "abcdefghijklmnopqrstuvwxyz0123546789&$+_' "

#assumed probability of typo in uniform edit
pe1 = 0.01
pqisr = 0.95
#interpolation lambda
lamb = 0.2

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

def get_pq(data, candidate):
  num_term = data[0]
  uni_dict = data[1]
  bi_dict = data[2]
  words = candidate.split()
  # adding P(w1)
  if words[0] not in uni_dict:
    return 0
  score = math.log(float(uni_dict[words[0]]) / num_term)
  
  for i in range(1,len(words)):
    if (words[i-1],words[i]) in bi_dict:
      score += math.log(lamb * float(uni_dict[words[i]]) / num_term + (1-lamb)* \
        float(bi_dict[(words[i-1],words[i])]) / uni_dict[words[i-1]])
    else:
      if words[i] not in uni_dict:
        return 0
      score += math.log(lamb * float(uni_dict[words[i]]) / num_term)
  return score   
  

def get_prq_uniform(cand, query):
  if cand == query:
    return math.log(pqisr)
  else:
    return (len(cand) - 1) * math.log(1 - pe1) + math.log(pe1)

def get_best_cand(data, query, candidates, uniform):
  num_term = data[0]
  uni_dict = data[1]
  bi_dict = data[2]
  result = query
  
  max_score = -99999
  for c in candidates:
    #print >> sys.stderr, c
    if uniform:
      prq = get_prq_uniform(c, query)
      pq = get_pq(data, c)
      if pq == 0:
        score = 0
      else:
        score = prq + pq
      if score > max_score:
        max_score = score
        result = c
      #print score
  return result
  

def correct_uniform(data, queries, gold, google):
  num_term = data[0]
  uni_dict = data[1]
  bi_dict = data[2]
  num_cor = 0
  
  for i in range(0, len(queries)):
    candidates = generate_cand(data, queries[i])   
    cand = get_best_cand(data, queries[i], candidates, True)
    if cand == gold[i]:
      num_cor += 1
  
  print >> sys.stderr, num_cor
  print >> sys.stderr, float(num_cor) / len(gold)

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
    


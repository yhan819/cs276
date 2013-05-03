
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
mu = 1

lenless = 0

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


def get_1edit_word(data, word):
  uni_dict = data[1]
  ans = []
  ans.append((word,""))
  
  for i in range(0,len(word)):
    #insertion
    for a in alphabet:
      ins = word[0:i] + a + word[i:]
      if i-1 < 0:
        ans.append((ins,"del$" + a))
      else:
        ans.append((ins,"del" + word[i-1] + a))
      #substitution
      if a != word[i]:
        subs = word[0:i] + a + word[i+1:]
        ans.append((subs, "sub" + a + word[i])) 
    #deletion
    dele = word[0:i] + word[i+1:]
    if i-1<0:
      ans.append((dele,"ins$" + word[0]))
    else:
      ans.append((dele,"ins" + word[i-1] + word[i]))
    if i < len(word) - 1:
      trans = word[0:i] + word[i+1] + word[i] + word[i+1:]
      ans.append((trans,"trans" + word[i+1] + word[i]))
  
  return ans


def generate_cand(data, query):
  uni_dict = data[1]
  bi_dict = data[2]
  ans = get_1edit_word(data, query)
  
  rst = []
  one_wrong = []
  for s in ans:
    words = s[0].split()
    add = True
    num_wrong = 0
    for w in words:
      if w not in uni_dict:
        num_wrong += 1
        add = False
    if add:
      rst.append((s[0],[s[1]]))
    if num_wrong == 1:
      one_wrong.append(s)
  print >> sys.stderr, "len " + str(len(rst))
  print >> sys.stderr, "len " + str(len(one_wrong))
  if len(rst) < 10:
    for o in one_wrong:
      new_r = get_1edit_word(data, o[0])
      for n in new_r:
        words = n[0].split()
        add = True
        for w in words:
          if w not in uni_dict:
            add = False
        if add:
          rst.append((n[0],[o[1],n[1]]))

  return rst

def get_pq(data, candidate):
  num_term = data[0]
  uni_dict = data[1]
  bi_dict = data[2]
  words = candidate.split()
  # adding P(w1)
  score = math.log(float(uni_dict[words[0]]) / num_term)
  
  for i in range(1,len(words)):
    if (words[i-1],words[i]) in bi_dict:
      score += math.log(lamb * float(uni_dict[words[i]]) / num_term + (1-lamb)* \
        float(bi_dict[(words[i-1],words[i])]) / uni_dict[words[i-1]])
    else:
      score += math.log(lamb * float(uni_dict[words[i]]) / num_term)
  return score   
  

def get_prq_uniform(cand, query, d):
  if cand == query:
    return math.log(pqisr)
  else:
    return (len(cand) - d) * math.log(1 - pe1) + d * math.log(pe1)

def get_prq_empirical(cand, query, d):
  if cand == query:
    return len(cand) * math.log(pqisr)
  else:
    #return (len(cand) - d) * math.log(1 - pe1) + d * math.log(pe1)
    return len(d) * math.log(pe1)

def get_best_cand(data, query, candidates, uniform):
  num_term = data[0]
  uni_dict = data[1]
  bi_dict = data[2]
  result = query

  if not uniform:
    # load more data
    pass
  
  max_score = -99999
  for c in candidates:
    #print >> sys.stderr, c
    if uniform:
      prq = get_prq_uniform(c[0], query, len(c[1]))
    else:
      prq = get_prq_empirical(c[0], query, c[1])
      pass
    pq = get_pq(data, c[0])
    if pq == 0:
      score = 0
    else:
      score = prq + mu * pq
    if score > max_score:
      max_score = score
      result = c[0]
      #print score
      
  return result
  

def correct_uniform(data, queries, gold, google, isUniform):
  num_term = data[0]
  uni_dict = data[1]
  bi_dict = data[2]
  num_cor = 0
  num_gc = 0
  for i in range(0, len(queries)):
    print >> sys.stderr, i
    candidates = generate_cand(data, queries[i])   
    cand = get_best_cand(data, queries[i], candidates, isUniform)
    print >> sys.stdout, cand
    if cand == gold[i]:
      num_cor += 1
      print >> sys.stderr, "correct"
    if cand == google[i]:
      num_gc += 1
  
  print >> sys.stderr, num_cor
  print >> sys.stderr, float(num_cor) / len(gold)
  print >> sys.stderr, "google : " + str(float(num_gc) / len(gold))

if __name__ == '__main__':
  print(sys.argv)
  lm = sys.argv[1]
  qry_file = sys.argv[2]

  (queries, gold, google) = read_query_data(qry_file)
  print >> sys.stderr, "read query data"

  data = unserialize_data("lang_model")
  if lm == "uniform":
    
    correct_uniform(data, queries, gold, google, True)   
    
    print >> sys.stderr, len(queries)
  elif lm == "empirical":
    '''
    add more to data
    '''
    correct_empirical(data, queries, gold, google, False)
    


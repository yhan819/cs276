
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

logzero = 0.01

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
  ans.append((word,"NONE"))
  
  for i in range(0,len(word)):
    #insertion
    for a in alphabet:
      if a != " ":
        ins = word[0:i] + a + word[i:]
        if i-1 < 0:
          ans.append((ins,("DEL","$", a)))
        else:
          ans.append((ins,("DEL",word[i-1],a)))
        #substitution
        if a != word[i]:
          subs = word[0:i] + a + word[i+1:]
          ans.append((subs, ("SUBS", a, word[i]))) 
      else:
        if i > 0 and i < (len(word) - 1) and word[i+1] != " " and word[i-1] != " ":
          ins = word[0:i] + a + word[i:]
          if i-1 < 0:
            ans.append((ins,("DEL","$", a)))
          elif word[i] != " ":
            ans.append((ins,("DEL",word[i-1],a)))
          #substitution
          if a != word[i]:
            subs = word[0:i] + a + word[i+1:]
            ans.append((subs, ("SUBS", a, word[i]))) 
    #deletion
    dele = word[0:i] + word[i+1:]
    if i-1<0:
      ans.append((dele,("INS","$",word[0])))
    else:
      ans.append((dele,("INS",word[i-1],word[i])))
    if i < len(word) - 1:
      trans = word[0:i] + word[i+1] + word[i] + word[i+1:]
      ans.append((trans,("TRANS", word[i+1], word[i])))
    '''
    for a in alphabet:
      ins = word + a
      ans.append((ins,("DEL",word[len(word)-1],a)))
    '''
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

def get_prq_empirical(cand, query, edit, data):
  if cand == query:
    return math.log(pqisr)
  else:
    unilet_cnt = data[3]
    bilet_cnt = data[4]
    edits = data[5]
    score = 0
    numwrong = 0
    
    
    for e in edit:
      numwrong += 1
      if e == "NONE":
        numwrong -= 1
        pass
      elif e[0] == "DEL":
        if e in edits:
          score += math.log(edits[e]+1)   
          score -= math.log(bilet_cnt[e[1]+e[2]] + 1)
        else:
          score += math.log(logzero)
          if e[1]+e[2] not in bilet_cnt:
            score -= math.log(1 + len(alphabet) * len(alphabet))
          else:  
            score -= math.log(bilet_cnt[e[1]+e[2]] + 1)
      elif e[0] == "INS":
        if e in edits:
          score += math.log(edits[e]+1)   
          score -= math.log(unilet_cnt[e[1]] * len(alphabet))
        else:
          score += math.log(logzero)
          score -= math.log(unilet_cnt[e[1]] * len(alphabet))
      elif e[0] == "SUBS":
        if e in edits:
          score += math.log(edits[e]+1)   
          score -= math.log(unilet_cnt[e[1]] * len(alphabet))
        else:
          score += math.log(logzero)
          score -= math.log(unilet_cnt[e[1]] * len(alphabet))
      elif e[0] == "TRANS":
        if e in edits:
          score += math.log(edits[e]+1)   
          score -= math.log(bilet_cnt[e[1]+e[2]] + 1)
        else:
          score += math.log(logzero)
          if e[1]+e[2] not in bilet_cnt:
            score -= math.log(1 + len(alphabet) * len(alphabet))
          else:  
            score -= math.log(bilet_cnt[e[1]+e[2]] + 1)
        
    #return (len(cand) - d) * math.log(1 - pe1) + d * math.log(pe1)
    return score

def get_best_cand(data, query, candidates, uniform):
  num_term = data[0]
  uni_dict = data[1]
  bi_dict = data[2]
  result = query

  max_score = -99999
  for c in candidates:
    if uniform:
      prq = get_prq_uniform(c[0], query, len(c[1]))
    else:
      prq = get_prq_empirical(c[0], query, c[1], data)
    pq = get_pq(data, c[0])
    if pq == 0:
      score = 0
    else:
      score = prq + mu * pq
    if score > max_score:
      max_score = score
      result = c[0]
      
  return result
  

def correct_queries(data, queries, gold, google, isUniform):
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

if __name__ == '__main__':
  print(sys.argv)
  lm = sys.argv[1]
  qry_file = sys.argv[2]

  (queries, gold, google) = read_query_data(qry_file)
  print >> sys.stderr, "read query data"

  data = unserialize_data("lang_model")
  if lm == "uniform":
    
    correct_queries(data, queries, gold, google, True)   
    
    print >> sys.stderr, len(queries)
  elif lm == "empirical":
    '''
    add more to data
    '''
    emp_data = unserialize_data("edit1s_model")
    data.append(emp_data[0])
    data.append(emp_data[1])
    data.append(emp_data[2])
    correct_queries(data, queries, gold, google, False)
    


from tqdm import tqdm
import glob
from nltk.tokenize import sent_tokenize
import torch
import scipy.cluster.hierarchy as sch

# Helpers
def find_sub_list(sl,l):
    results=[]
    sll=len(sl)
    for ind in (i for i,e in enumerate(l) if e==sl[0]):
        if l[ind:ind+sll]==sl:
            results.append((ind,ind+sll-1))

    return results

# Get word embedding
def getWordEmbeddingFromPhrase(df, folder_src,tokenizer, model, domean=True, earlyStop=None, term_name=None):
    if term_name is None:
        return None
    all_file_names = (df[df['Term'] == term_name]['documentURL']).tolist()
    all_file_names = [file_name.split('/')[-1] for file_name in all_file_names]
    all_embeddings = []
    max_doc = len(all_file_names)
    if earlyStop is not None:
        max_doc = min(earlyStop,len(all_file_names)) 
    for j in tqdm(range(max_doc)):
        file_name = all_file_names[j]
        path_to_doc = None
        for path in glob.glob(f'{folder_src}/*/*.txt', recursive=True):
            if file_name in str(path):
                path_to_doc = path
                break
        # If file path found
        if path_to_doc is not None:
            # Find all sentences with word
            filtered_sentences = []
            with open(path_to_doc, 'r') as file:
                text = file.read()
                all_sentences = sent_tokenize(text)
                for sent in all_sentences:
                    for split_sent in sent.split('\n'):
                        splint_sent_trunc = split_sent[:min(len(split_sent),512)]
                        if term_name.lower() in splint_sent_trunc.lower():
                            filtered_sentences.append(splint_sent_trunc)
            
            # For each sentence
            term_vec = tokenizer.tokenize(term_name)
            for sent in filtered_sentences:
                sent_vec,sent_tok = getTokenVecs(tokenizer,model,sent)
                sent_term_indexes = find_sub_list(term_vec, sent_tok)
                for term_tuple in sent_term_indexes:
                    all_embeddings.append(sent_vec[term_tuple[0]:term_tuple[1]+1])
    if len(all_embeddings) > 0:
        embedding_matrix = all_embeddings[0]
        for i in range(1,len(all_embeddings)):
            embedding_matrix = torch.cat((embedding_matrix,all_embeddings[i]),dim=0)
        if domean:
            return torch.mean(embedding_matrix,dim=0)
        else:
            return torch.sum(embedding_matrix,dim=0)
    else:
        return None


# Sentence Embedding
def getTokenVecs(tokenizer, model, text):
    marked_text = "[CLS] " + text + " [SEP]"
    # Tokenize our sentence with the BERT tokenizer.
    tokenized_text = tokenizer.tokenize(marked_text)
    # Map the token strings to their vocabulary indeces.
    indexed_tokens = tokenizer.convert_tokens_to_ids(tokenized_text)
    segments_ids = [1] * len(tokenized_text)
    # Convert inputs to PyTorch tensors
    tokens_tensor = torch.tensor([indexed_tokens])
    segments_tensors = torch.tensor([segments_ids])
    # Predict hidden states features for each layer
    with torch.no_grad():
        encoded_layers, _ = model(tokens_tensor, segments_tensors)
    token_vecs = encoded_layers[11][0]
    return (token_vecs,tokenized_text)


def count_clusters(dendrogram):
    curentColor = dendrogram['leaves_color_list'][0]
    count = 1
    for i in range(1, len(dendrogram['leaves_color_list'])):
        if curentColor != dendrogram['leaves_color_list'][i]:
            curentColor = dendrogram['leaves_color_list'][i]
            count += 1
    return count

def create_tree(Z, labellist):
    clusters = {}
    to_merge = Z
    for i, merge in enumerate(to_merge):
        if merge[0] <= len(to_merge):
            # if it is an original point read it from the centers array
            a = labellist[int(merge[0])]
        else:
            # other wise read the cluster that has been created
            a = clusters[int(merge[0])]

        if merge[1] <= len(to_merge):
            b = labellist[int(merge[1])]
        else:
            b = clusters[int(merge[1])]
        # the clusters are 1-indexed by scipy
        clusters[1 + i + len(to_merge)] = {
            'children' : [a, b]
        }
        # ^ you could optionally store other info here (e.g distances)
    return clusters
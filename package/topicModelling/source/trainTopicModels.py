from itertools import combinations
import learningAgents
import utilities
from model import Model
from documentCleaner import DocumentCleaner
import gensim
import pandas as pd
from pdftextExtractor import PDFTextExtractor
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.decomposition import NMF
from sklearn.preprocessing import normalize
import pickle

utils = utilities.Utils()


def trainModel(agent, type, use_tfidf=True, minTopics = 10, maxTopics = 100):
    ''' Type is either LDA or NMF. Set tfidf to true or false (LDA only) '''
    if not (type == "NMF" or type == "LDA"): 
        return "Error! type needs to be either LDA or NMF"
    if use_tfidf: 
        addin = "TFIDF"
    else:
        addin = ""
    topic_coherence = []
    for num_topics in range(minTopics, maxTopics, 1):
        print("Training " + type + " model on ", str(num_topics), " topics with" + addin)
        topics = agent.train(num_topics, use_tfidf=use_tfidf)
        score = calculate_coherence(topics)
        topic_coherence.append(score)
        print("Topic coherence for ", num_topics, "topics is ", score)
    ymax = max(topic_coherence)
    print("Max Topic Coherence", ymax)
    num_topics = topic_coherence.index(ymax) + 10
    topics = agent.train(num_topics, use_tfidf=use_tfidf)

def calculate_coherence(topics_df, top = 3):
    skipped_over = 0
    num_topics = topics_df.shape[1]
    topics_df = topics_df.head(top) # how many words do we actually want to look at?
    overall_coherence = 0.0
    for column in topics_df:
        # check each pair of terms
        pair_scores = []
        for pair in combinations(topics_df[column], 2 ):
            if not pair[0] in utils.wordL or not pair[1] in utils.wordL:
                skipped_over += 1
                continue   # skip if not there 
            score = utils.score(pair[0], pair[1]) 
            pair_scores.append(score)
            if score > 1 or score < -1: 
                print("problem!")
                print(score)
        # get the mean for all pairs in this topic
        topic_score = sum(pair_scores) / len(pair_scores)
        overall_coherence += topic_score
    # get the mean score across all topics
    return overall_coherence / num_topics, skipped_over


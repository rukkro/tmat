#http://www.nltk.org/howto/sentiment.html
import warnings
warnings.filterwarnings("ignore")
import mongo
from nltk.sentiment.util import *
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.classify import NaiveBayesClassifier
from nltk.corpus import subjectivity
from nltk.sentiment import SentimentAnalyzer

def initialize():
    n_instances = 100
    subj_docs = [(sent, 'subj') for sent in subjectivity.sents(categories='subj')[:n_instances]]
    obj_docs = [(sent, 'obj') for sent in subjectivity.sents(categories='obj')[:n_instances]]
    len(subj_docs), len(obj_docs)

    train_subj_docs = subj_docs[:80]
    test_subj_docs = subj_docs[80:100]
    train_obj_docs = obj_docs[:80]
    test_obj_docs = obj_docs[80:100]
    training_docs = train_subj_docs +train_obj_docs
    testing_docs = test_subj_docs+test_obj_docs
    sentim_analyzer = SentimentAnalyzer()
    all_words_neg = sentim_analyzer.all_words([mark_negation(doc) for doc in training_docs])

    unigram_feats = sentim_analyzer.unigram_word_feats(all_words_neg, min_freq=4)
    sentim_analyzer.add_feat_extractor(extract_unigram_feats, unigrams=unigram_feats)

    training_set = sentim_analyzer.apply_features(training_docs)
    test_set = sentim_analyzer.apply_features(testing_docs)

    trainer = NaiveBayesClassifier.train
    classifier = sentim_analyzer.train(trainer, training_set)

    for key,value in sorted(sentim_analyzer.evaluate(test_set).items()):
         print('{0}: {1}'.format(key, value))

def analyze(coll):
    if not mongo.connected:
        print("MongoDB must be connected to perform sentiment analysis!")
        return
    sentences = []
    #paragraph = "test text"
    cursor = coll.find({})
    for i in cursor:
        if "text" not in i:
            continue
        sentences.append(i["text"])
    #lines_list = tokenize.sent_tokenize(paragraph)
    #sentences.extend(lines_list)
    sid = SentimentIntensityAnalyzer()
    for i in sentences:
        print(i)
        ss = sid.polarity_scores(i)
        for k in sorted(ss):
            print('{0}: {1}, '.format(k,ss[k]), end='')
        print()


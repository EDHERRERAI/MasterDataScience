import gensim
import gensim.corpora as corpora
from gensim.utils import simple_preprocess
from gensim.models import CoherenceModel
from pprint import pprint
import pyLDAvis
import pyLDAvis.gensim


def SenToWords(sentences):
    for sentence in sentences:
        # https://radimrehurek.com/gensim/utils.html#gensim.utils.simple_preprocess
        yield(gensim.utils.simple_preprocess(str(sentence), deacc=True))  # deacc=True elimina la puntuación

    #data_words = list(sent_to_words(data))
    #print(data_words[:1])


# Construimos modelos de bigrams y trigrams
# https://radimrehurek.com/gensim/models/phrases.html#gensim.models.phrases.Phrases
def setNGramsDocs(pDataWords):
    vData_Words = pDataWords
    vBigram = gensim.models.Phrases(vData_Words, min_count=5, threshold=100)
    vTrigram = gensim.models.Phrases(vBigram[vData_Words], threshold=100)  

    # Aplicamos el conjunto de bigrams/trigrams a nuestros documentos
    vBigraMod = gensim.models.phrases.Phraser(vBigram)
    vTrigraMod = gensim.models.phrases.Phraser(vTrigram)

    #print(bigram_mod[data_words[0]])
    #print(trigram_mod[bigram_mod[data_words[0]]])

    return (vBigraMod,vTrigraMod)


# Hacer bigrams
def MakeBigrams(pTexts, pBigraMod):
    return [pBigraMod[doc] for doc in pTexts]

# Hacer trigrams
def MakeTrigrams(pTexts, pBigraMod, pTrigraMod):
    return [pTrigraMod[pBigraMod[doc]] for doc in pTexts]

# Lematización basada en el modelo de POS de Spacy
def lemmatization(pTexts, allowed_postags=['NOUN', 'ADJ', 'VERB', 'ADV']):
    """https://spacy.io/api/annotation"""
    texts_out = []
    for sent in pTexts:
        doc = (" ".join(sent)) 
        texts_out.append([token.lemma_ for token in doc if token.pos_ in allowed_postags])
    return texts_out


def setLemmasWords(pDataNGramsWords):
    # Lematizamos preservando únicamente noun, adj, vb, adv
    data_lemmatized = lemmatization(pDataNGramsWords, allowed_postags=['NOUN', 'ADJ', 'VERB', 'ADV'])
    #print(data_lemmatized[:1])

    return data_lemmatized


def setDictionaryWords(pDataLematized):
    # Creamos diccionario
    vDicword = corpora.Dictionary(pDataLematized)

    return vDicword

def setCorpus(pDictionaryId, pTexts):
    vCorpus = [pDictionaryId.doc2bow(text) for text in pTexts]

    return vCorpus

def getCorpus(pDictionaryId, pCorpus):
    # Human readable format of corpus (term-frequency)
    [[(pDictionaryId[id], freq) for id, freq in cp] for cp in pCorpus[:1]]

def getLdaModel (pDictionaryId, pCorpus):
    vLdaModel = gensim.models.ldamodel.LdaModel(corpus=pCorpus,
                                                id2word=pDictionaryId,
                                                num_topics=20, 
                                                random_state=100,
                                                update_every=1,
                                                chunksize=100,
                                                passes=10,
                                                alpha='auto',
                                                per_word_topics=True)
    # Print the Keyword in the 10 topics
    pprint(vLdaModel.print_topics())
    return vLdaModel

def getLdaPerplexityModel(pLdaModel, pCorpus):
    #Perplejidad: a measure of how good the model is. lower the better.
    vPerplexity = pLdaModel.log_perplexity(pCorpus)

    return vPerplexity

def getLdaCoherenceModel(pLdaModel, pDictionaryId, pDataLematize):
    # Score de coherencia
    coherence_model_lda = CoherenceModel(model=pLdaModel, texts=pDataLematize, dictionary=pDictionaryId, coherence='c_v')
    coherence_lda = coherence_model_lda.get_coherence()

    return coherence_lda

def getVisualizacionTemas(pLdaModel, pCorpus, pDictionaryId):
    # Visualizamos los temas
    pyLDAvis.enable_notebook()
    vis = pyLDAvis.gensim.prepare(pLdaModel, pCorpus, pDictionaryId)
    vis
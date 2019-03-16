#Importing useful Libraries 
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
import re
import gensim
from gensim.models import Doc2Vec
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from sklearn.cluster import KMeans
import pickle

class Cluster_bot:
#Cluster class includes functions for reading, cleaning, pre-processing data.    
    def __init__(self):
#reading input csv file (News Corpus)        
        self.Reading_Data = pd.read_csv("news_articles.csv", nrows=50000)
        self.Reading_Data = self.Reading_Data[:len(self.Reading_Data )]
        #print(type(self.Reading_Data))
        self.all_content = []

    def cleaning(self, text):
#Lowering text and splitting text, removing stop words         
        Text  = text.lower()    
        # clean and tokenize document string
        content = Text.split()    
        stop_words = set(stopwords.words('english'))
        word_list = []
        for i in content:
            #x = 0
            if (('http' not in i) and ('@' not in i) and ('<.*?>' not in i) 
                and i.isalnum() and (not i in stop_words)):
                word_list += [i]        
        return word_list 

#Data Pre-processing
    def preprocessing(self, text):    
        # remove numbers
        number_tokens = [re.sub(r'[\d]', ' ', i) for i in text]
        number_tokens = ' '.join(number_tokens).split()
        # stem tokens
        p_stemmer = PorterStemmer()
        stemmed_tokens = [p_stemmer.stem(i) for i in number_tokens]
        # remove empty
        length_tokens = [i for i in stemmed_tokens if len(i) > 1]
        return length_tokens       
        
    def vectorProcessing(self):    
#loading gensim model to pass token of given news corpus  
        LabeledSentence = gensim.models.doc2vec.TaggedDocument    
        #texts = []
        j=0
        k=0
#Loop to read each news and pass it to cleaning and preprocessing functions
        for em in self.Reading_Data.Content:           
            #Data cleaning
            clean_content = self.cleaning(em)        
            #Pre-processing
            processed = self.preprocessing(clean_content)        
            # add tokens to list
            if processed:
                self.all_content.append(LabeledSentence(processed,[j]))
                j= j+1
            k+=1
            
#Doc2vec - Doc2Vec model is loaded to which all token to create 300 dimension vector
#Alpha here is training rate which is ver low. 
        d2v_model = Doc2Vec(self.all_content, window = 10, min_count = 5, 
                            workers=4, alpha=0.0025)
#Training d2v Model with actuall news corpus. 
        d2v_model.train(self.all_content, total_examples=d2v_model.corpus_count, epochs=30) 

        #Pickle to load model in a object which can be used later
        list_pickle_path = 'list_pickle.pkl'
        # Create an variable to pickle and open it in write mode
        list_pickle = open(list_pickle_path, 'wb')
        pickle.dump(d2v_model, list_pickle)
        list_pickle.close()
#Clustering - To cluster vectos into labelled data i.e. 5 clusters are created here  using Kmeans algorithm
        kmeans_model = KMeans(n_clusters=5, init='k-means++', max_iter=100)
        #X = kmeans_model.fit(d2v_model.docvecs.doctag_syn0)
        X = kmeans_model.fit(d2v_model.docvecs.vectors_docs)
        labels=X.labels_.tolist() 
        new_label=pd.DataFrame(labels)
    
        self.Reading_Data['Cluster'] = new_label+1
        self.Reading_Data.to_csv('Clustered_Data.csv',index=False)
        #self.Reading_Data.head()
        print("Clustering has been completed & labelled data has been written to Clustered_Data.csv File .")    
    
def main():
    bot = Cluster_bot();
    bot.vectorProcessing()
    
if __name__ == '__main__':
    main()

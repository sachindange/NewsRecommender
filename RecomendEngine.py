# -*- coding: utf-8 -*-
"""
Created on Wed Apr  4 22:19:05 2018

@author: sachinD
"""
import pandas as pd
from svdRec import svdRec
import numpy as np
from scipy.sparse import coo_matrix
import random
import pickle

#Constants for recomendation types
Random = "Random"
Content = "Content"
Collab = "Collab"
Average = "Average"
Vector = "Doc2Vec"

class RecomEngine:

    def __init__(self, userid, userClicks, Newscluster):
        self.userid = userid
        self.userClicks = pd.DataFrame(userClicks)
        self.Newscluster = Newscluster
        self.articlesShown = self.articlesShown()

    def getCluster(self,newsIDs):
        cluster = self.Newscluster.Cluster[self.Newscluster['ArticleID'].isin(newsIDs)]
        return list(set(cluster.tolist()))
    
    def assignWeights(self):
        
        weightDict = { }
        
        userClusters = self.userClicks[ self.userClicks [ 'Click' ] == "Yes"  ]
        userClusters = userClusters[userClusters ['TimeSpent'] > 30]        
        clickedAllUsers = len(userClusters)        
        userClusters = ( userClusters[userClusters[ 'UserId' ] == self.userid ]  )        
        clickedThisUser = len(userClusters)        
       
        if(clickedThisUser > 0):         
            
            weightLoggedUser = clickedThisUser/clickedAllUsers
            
            if( weightLoggedUser <= 0.2 ):
                weightLoggedUser = 0.2
            elif (0.2 < weightLoggedUser < 0.6):
                weightLoggedUser = 0.4
            else :
                weightLoggedUser = 0.5
            
            weightAvgUser = round(0.5 - weightLoggedUser,2)
        
        else:
            weightAvgUser = 0.5
            weightLoggedUser = 0.0
          
        weightDict[Random] = 2.0
        weightDict[Content] = weightLoggedUser*10
        weightDict[Average] = weightAvgUser*10
        weightDict[Collab] = 3.0
        weightDict[Vector] = round((weightLoggedUser*10)/2)
        
        #print("weightDict", weightDict )
        #print("User Ratio:", clickedThisUser/clickedAllUsers)
        #print("weightAvgUser:", weightAvgUser)
        #print("weightLoggedUser:", weightLoggedUser)
        
        return weightDict
      
        
    #Get recomendation based on average user / most viewed
    def getAverageRecom(self):
        ArticleCount = self.userClicks['ArticleID'].value_counts()
        mostSeenArticles = ArticleCount[ArticleCount>1].keys()       
        #print("mostSeenArticles :", mostSeenArticles)        
        articlesRecom = []
        articlesRecom.append(set(mostSeenArticles) - set(self.articlesShown))
        avgrecomNews = pd.DataFrame(columns=['Type', 'Cluster', 'ArticleID'])
        avgrecomNews['ArticleID'] = list(articlesRecom)
        avgrecomNews['Cluster'] = "N/A"
        avgrecomNews['Type'] = Average

        #print("avgrecomNews :", avgrecomNews)
        return avgrecomNews
    
    #Get recomendation based on random articles
    def getRandomNews(self):
        
        ramdomNews = random.sample(range(1,len(self.Newscluster) ), 10)
        #print("getRandomNews :", ramdomNews)
        
        articlesRecom = []
        articlesRecom.append(set(ramdomNews) - set(self.articlesShown))
        avgrecomNews = pd.DataFrame(columns=['Type', 'Cluster', 'ArticleID'])
        avgrecomNews['ArticleID'] = list(articlesRecom)
        avgrecomNews['Cluster'] = "N/A"
        avgrecomNews['Type'] = Random
        
        #print("getRandomNews :", avgrecomNews)
        return avgrecomNews
    
    def getDoc2VecNews(self):                

        #print("You liked Articles in getDoc2VecNews: ",self.articlesLiked )
        
        file_Name = "list_pickle.pkl"
        fileObject = open(file_Name,'rb')  
        d2v_model = pickle.load(fileObject)  
        fileObject.close()
        
        lenLiked = len(self.articlesLiked)
        
        count=0
        vecRecom = []
        
        while( count < lenLiked ):
            #add 2 recomendations per like item
            vecRecom.append( d2v_model.docvecs.most_similar(self.articlesLiked[count])[0][0] )
            vecRecom.append( d2v_model.docvecs.most_similar(self.articlesLiked[count])[1][0] )
            count = count+1
        
        # shows the similar docs with id = 99
        #print ("d2v_model.docvecs.most_similar: ", d2v_model.docvecs.most_similar(2)[0][0])
        
        #ramdomNews = random.sample(range(1,len(self.Newscluster) ), 10)
        #print("getRandomNews :", ramdomNews)        
        
        articlesRecom = []
        articlesRecom.append(set(vecRecom) - set(self.articlesShown))
        vecrecomNews = pd.DataFrame(columns=['Type', 'Cluster', 'ArticleID'])
        vecrecomNews['ArticleID'] = list(articlesRecom)
        vecrecomNews['Cluster'] = "N/A"
        vecrecomNews['Type'] = Vector
        
        #print("vecrecomNews :", vecrecomNews)
        return vecrecomNews

    #Get list of overall recomendatins, max 10
    def getOverallRecom(self):
        contentRecom = self.getContentRecom()
        collabRecom = self.getCollabRecom()
        AverageRecom = self.getAverageRecom()
        randomeRecom = self.getRandomNews()
        doc2VecNews = self.getDoc2VecNews()
        
        #print("overallRecom2 :", overallRecom2)
        
        newsWeights = self.assignWeights()
        
        overallRecom = [];
        
        lenContentRecon = len(contentRecom)
        wtContent = newsWeights[Content]
        contentToAddPerCluster = abs(wtContent/lenContentRecon)
        
        overallAdded = 0;
        
        #print("Length content:", lenContentRecon)
        #print("Weight content:", wtContent )
        #print("contentToAddPerCluster :", contentToAddPerCluster )
        
        if( lenContentRecon > 0) :
            overCount = 0
            
            while( overCount < lenContentRecon ):
                inClusterCount = 0;
                
                while( inClusterCount < contentToAddPerCluster ):                  
                    pList = list(contentRecom['ArticleID'][overCount])
                    overallRecom.append(pList[inClusterCount])
                    inClusterCount = inClusterCount+1;                
                    
                overCount = overCount+1         
     
        overallRecom = overallRecom + self.getItemsAsPerWeight(newsWeights[Average], AverageRecom)
        overallRecom = overallRecom + self.getItemsAsPerWeight(newsWeights[Collab], collabRecom)
        overallRecom = overallRecom + self.getItemsAsPerWeight(newsWeights[Vector], doc2VecNews)
        
        #print("overallRecom:", overallRecom)        
        #overallRecom = random.shuffle(overallRecom)
        random.shuffle(overallRecom)
        #print("overallRecom after shuffling:", overallRecom) 
        overallAdded = len(set(overallRecom))        
        randomToAdd = 10-overallAdded
        
        overallRecom = overallRecom + self.getItemsAsPerWeight(randomToAdd+2, randomeRecom)
        
        return set(overallRecom)
    
    def getItemsAsPerWeight(self, weight, item):
        
        lenrecom = len(item['ArticleID'][0])
        recomItems = []
        #print("item :", item['ArticleID'][0])
        #print("getItemsAsPerWeight:", weight)
        #print("lenrecom:", lenrecom)
        
        if( lenrecom > 0) :
            overCount = 0
            
            if( lenrecom < weight ):
                maxItems = lenrecom
            else:
                maxItems = weight
            
            #print("maxItems:", maxItems)
                
            while( overCount < maxItems ):
               
                pList = list(item['ArticleID'][0])
                recomItems.append(pList[overCount])
                overCount = overCount+1;  
                
        #print("recomItems:", recomItems)
        return recomItems

    #Get articles already shown to user from clickstream
    def articlesShown(self):
        userClusters = ( self.userClicks[self.userClicks[ 'UserId' ] == self.userid ]  )
        articlesShown = userClusters['ArticleID'].tolist()
        #print("You were served Articles: ",articlesShown )
        return articlesShown

    #Get recomendations using collaboration
    def getCollabRecom(self):
        viewedNews = self.userClicks[ self.userClicks [ 'Click' ] == "Yes"  ]
        svdInput = viewedNews[['UserId','ArticleID','TimeSpent']].copy()
        #svdInput['Click'] = int(1)
        u =  np.array(svdInput['UserId'].tolist(), dtype ='int')
        m =  np.array(svdInput['ArticleID'].tolist())
        r =  np.array(svdInput['TimeSpent'].tolist())
        cooMatrix = coo_matrix((r, (u-1, m-1)), shape=(u.max(), m.max()))
        svd = svdRec()
        svd.load_data_numpy(cooMatrix)
        svd.SVD()
        collabRecom = svd.recs_from_closest_user(int(self.userid),num_users=1)

        #print("Items for User to check out based on similar user:\n" , np.array(collabRecom)+1)
        articlesRecom = []
        articlesRecom.append(set(np.array(collabRecom)+1) - set(self.articlesShown))
        recomNews = pd.DataFrame(columns=['Type', 'Cluster', 'ArticleID'])
        recomNews['ArticleID'] = list(articlesRecom)
        recomNews['Cluster'] = "N/A"
        recomNews['Type'] = Collab
        #print("Collab Recom: ", recomNews)
        return recomNews

    #Get recomendations based on content
    def getContentRecom(self):

        userClusters = ( self.userClicks[self.userClicks[ 'UserId' ] == self.userid ]  )
        userClusters = userClusters[ userClusters [ 'Click' ] == "Yes"  ]
        userClusters = userClusters[userClusters ['TimeSpent'] > 30]

        self.articlesLiked = userClusters['ArticleID'].tolist()
        #print("You liked Articles: ",self.articlesLiked )
        clustersLiked = self.getCluster(self.articlesLiked)
        #print("You liked Clusters: ", clustersLiked)
        return self.getLatestNews( Content, clustersLiked, self.articlesShown)

    #Get latest new articles for specified clusters, without the ones that were already served
    def getLatestNews(self, Type, clusters, articlesShown ):

        articles = []
        cluster = []
        count = 0

        while count < len(clusters):

            #print("clusters :",clusters[count])
            #print("Articles", self.Newscluster.ArticleID[ self.Newscluster['Cluster'] == clusters[count]].tolist())

            newArticles = self.Newscluster.ArticleID[ self.Newscluster['Cluster']
                == clusters[count]].tolist()

            articles.append( set(newArticles) - set(articlesShown))
            cluster.append(clusters[count])
            count += 1

        recomNews = pd.DataFrame(columns=['Type', 'Cluster', 'ArticleID'])
        recomNews['Cluster'] = cluster
        recomNews['Type'] = Type
        recomNews['ArticleID'] = articles
        #print("contentRecom: ", recomNews)

        return recomNews


############### Driver for Testing ENgine ######################################

def getNewsCluster() :

    df=pd.read_csv('LessNews.csv', sep=',', header='infer'
                   , parse_dates=['Date'])

    #print (df.dtypes)
    return df

def getClickstream() :

    cStream=pd.read_csv('CStream.csv', sep=',', header='infer'
                        , dtype= {'Click' : np.str, 'UserId': np.str, 'TimeSpent' : np.int64} )

    #print (cStream.dtypes)
    return cStream

def main():

    print("---------------------------------------------------------------")
    print("Driver for Engine")
    print("---------------------------------------------------------------  ")

    #Get latest news based on clusters
    Newscluster = getNewsCluster();

    #Get user clickstream
    userClicks = getClickstream();

    userid = "1"
    print("Welcome...", userid)

    recomEngine = RecomEngine(userid, userClicks, Newscluster)
    overallRecom = recomEngine.getOverallRecom()

    print("overallRecom...", overallRecom)
    #newsRecomendation = recommendation_bot(userid,  userClicks, News_clusters)
    #displayRecom(newsRecomendation)


if __name__ == '__main__':
    main()

# -*- coding: utf-8 -*-
"""
Created on Tue Apr  3 22:19:46 2018

@author: sachin
"""

import pandas as pd
import numpy as np

import RecomendEngine as RE

#!/usr/bin/env python

#Core recomedation engine that recomends based on the User id, CLickstream & News Cluster
def recommendation_bot(userid, userClicks, Newscluster):    

    recomEngine = RE.RecomEngine(userid, userClicks, Newscluster)    
    recomNews = recomEngine.getOverallRecom()
    return recomNews

#Get the news clustered by Bot 1 - Clusterer
def getNewsCluster() :   
   
    df=pd.read_csv('Clustered_Data.csv', sep=',', header='infer'
                   , parse_dates=['Date'])
    
    #print(df["Cluster"])
    return df

def getClickstream() :    
    
    cStream=pd.read_csv('CStream.csv', sep=',', header='infer'
                        , dtype= {'Click' : np.str, 'UserId': np.str, 'TimeSpent' : np.int64} )
    
    #print(cStream)
    return cStream

#Display the 10 items
def displayRecom(newsRecomendation,Newscluster):
    
    print("---------------------------------------------------------------")
    print("Our Personalised recommendations  for you.")
    print("---------------------------------------------------------------  ")
    
    lenNewscluster = len(newsRecomendation)
    show = 0;
    
    print("SrNo  ", "News")
    count = 0;
    
    if( lenNewscluster > 10 ):
        show = 10
    else:
        show = lenNewscluster   
       
    while True:
        
        while(count < show):
            newsItem = (Newscluster[Newscluster.ArticleID==newsRecomendation[count]].Title).item()
            print(count+1,"]   ", newsItem)
            count=count+1
        
        choice = input("Select the number to open ( from  1 to 10 ), Q to quit :")
        print("You choose: ", choice)
        #end = False;

        if choice == 'Q':
           #end = True
           break
        else:
           try:
              option_choice = int(choice)
              if option_choice < 1 or option_choice > 10:
                     print("Invalid Choice.. Try Again..")
                     #end = True
                     continue
              else:
                  newsDetail = (Newscluster[Newscluster.ArticleID==newsRecomendation[option_choice-1]].Content).item()
                  print(newsDetail)
                  continue
           except:
              print("Invalid Choice.. Try Again..")
              continue

def main():
   
    print("---------------------------------------------------------------")
    print("Jhakas News. The latest & best for you !!")
    print("---------------------------------------------------------------  ")

    #Get latest news based on clusters
    News_clusters = getNewsCluster();
    
    #Get user clickstream
    userClicks = getClickstream();
    
    while True:
        choice = input("Welcome Guest. Enter your userid, Q to Quit: ")
        end = False;

        if choice == 'Q':
           end = True
           break
        else:
           try:
              userid = choice
           except:
              print("Invalid Choice.. Try Again..")
              continue

        if end == True:
            print("Exiting..")
        else:
            print("Welcome : ", userid)
            newsRecomendation = recommendation_bot(userid,  userClicks, News_clusters)  
            #print("Generated recom for...", newsRecomendation)

            displayRecom(list(newsRecomendation),News_clusters)
            break

if __name__ == '__main__':
    main()

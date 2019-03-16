# -*- coding: utf-8 -*-
"""
Created on Sun Apr 15 20:46:55 2018

@author: hp
"""
import pickle
import numpy as np

def expo(u):
    return 1/(1+np.exp(-u))

def getDoc2VecNews():               
       
    file_Name = "list_pickle.pkl"
    fileObject = open(file_Name,'rb')  
    d2v_model = pickle.load(fileObject)  
    fileObject.close()
    
    from scipy.sparse import coo_matrix
    a = d2v_model.docvecs[0] 
    a.shape
    n = len(a)
    print(n)
    row = []
    col=[]
    data=[]
    M = coo_matrix((data, (row, col)), shape=(n,1)).toarray()
    M.shape
    
    e = np.repeat(1, M.shape[1]).reshape((M.shape[1],1))
    E = e.dot(e.T)
    beta = 0.9
    M = beta*M+(1-beta)*(1/M.shape[1])*E
    M = M/sum(M)
    
    new_M= expo(E+a)
    click =  np.random.binomial(size=new_M.shape, n=1, p=new_M);
   
    print(click)

        
user_id = np.arange(1,21)
print(user_id)
for x in user_id:
    s = np.random.poisson(1, 1000)
    t = np.random.binomial(size=3, n=1, p= 0.5)
    mu = 45
    sig = 20
    time_spent = np.random.normal(mu,sig,x)
    time_spent1 = np.round(time_spent, 2)
    print ('user_id',x,s[1], time_spent1[0])
    
    #df = pd.DataFrame(data={"user_id": user_id, "article_id": s})
    #df.to_csv("dummy1.csv", sep=',',index=False)

for l in time_spent:
    if l < 20:
        print('clicked by mistake')
    elif l > 20 and l < 35:
        print('story read partially')
    elif l > 35 :
        print('story read by user')
        
        
r = print(user_id)
i = print(time_spent1)


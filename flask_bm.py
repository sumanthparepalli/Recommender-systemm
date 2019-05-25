import numpy as np
import pandas as pd
import torch
from sklearn.preprocessing import LabelEncoder


class RBM():
    def __init__(self, nv, nh):
        self.W = torch.randn(nh, nv)
        self.a = torch.randn(1, nh)
        self.b = torch.randn(1, nv)
    def sample_h(self, x):
        wx = torch.mm(x, self.W.t())
        activation = wx + self.a.expand_as(wx)
        p_h_given_v = torch.sigmoid(activation)
        return p_h_given_v, torch.bernoulli(p_h_given_v)
    def sample_v(self, y):
        wy = torch.mm(y, self.W)
        activation = wy + self.b.expand_as(wy)
        p_v_given_h = torch.sigmoid(activation)
        return p_v_given_h, torch.bernoulli(p_v_given_h)
    def train(self, v0, vk, ph0, phk):
        self.W += (torch.mm(v0.t(), ph0) - torch.mm(vk.t(), phk)).t()
        self.b += torch.sum((v0 - vk), 0)
        self.a += torch.sum((ph0 - phk), 0)

def rec(tts,nb_epoch,nh):
    df=pd.read_csv('abc.csv')
    lb=LabelEncoder()
    df.PID=lb.fit_transform(df.PID)
    df=df[['USERID','PID','RATING']]
    # Preparing the training set and the test set
    msk = np.random.rand(len(df)) < tts
    training_set = df[msk]
    training_set = np.array(training_set, dtype = 'int')
    test_set = df[~msk]
    test_set = np.array(test_set, dtype = 'int')

    # Getting the number of users and movies
    nb_users = int(max(max(training_set[:,0]), max(test_set[:,0])))
    nb_prods = int(max(max(training_set[:,1]), max(test_set[:,1])))

    # Converting the data into an array with users in lines and movies in columns
    def convert(data):
        new_data = []
        for id_users in range(1, nb_users + 1):
            id_prods = data[:,1][data[:,0] == id_users]
            id_ratings = data[:,2][data[:,0] == id_users]
            ratings = np.zeros(nb_prods)
            ratings[id_prods - 1] = id_ratings
            new_data.append(list(ratings))
        return new_data
    training_set = convert(training_set)
    test_set = convert(test_set)

    # Converting the data into Torch tensors
    training_set = torch.FloatTensor(training_set)
    test_set = torch.FloatTensor(test_set)

    # Converting the ratings into binary ratings 1 (Liked) or 0 (Not Liked)
    training_set[training_set == 0] = -1
    training_set[training_set == 1] = 0
    training_set[training_set == 2] = 0
    training_set[training_set >= 3] = 1
    test_set[test_set == 0] = -1
    test_set[test_set == 1] = 0
    test_set[test_set == 2] = 0
    test_set[test_set >= 3] = 1

    nv = len(training_set[0])
    # nh = 10
    batch_size = 16
    rbm = RBM(nv, nh)

    # op="Result\n"
    op=""
    # Training the RBM
    # nb_epoch = 10
    for epoch in range(1, nb_epoch + 1):
        train_loss = 0
        s = 0.
        for id_user in range(0, nb_users - batch_size, batch_size):
            vk = training_set[id_user:id_user+batch_size]
            v0 = training_set[id_user:id_user+batch_size]
            ph0,_ = rbm.sample_h(v0)
            for k in range(10):
                _,hk = rbm.sample_h(vk)
                _,vk = rbm.sample_v(hk)
                vk[v0<0] = v0[v0<0]
            phk,_ = rbm.sample_h(vk)
            rbm.train(v0, vk, ph0, phk)
            train_loss += torch.mean(torch.abs(v0[v0>=0] - vk[v0>=0]))
            s += 1.
        op=op+('epoch: '+str(epoch)+' loss: '+str(train_loss/s))+"\n"

    # Testing the RBM
    test_loss = 0
    s = 0.
    for id_user in range(nb_users):
        v = training_set[id_user:id_user+1]
        vt = test_set[id_user:id_user+1]
        if len(vt[vt>=0]) > 0:
            _,h = rbm.sample_h(v)
            _,v = rbm.sample_v(h)
            test_loss += torch.mean(torch.abs(vt[vt>=0] - v[vt>=0]))
            s += 1.
    op=op+('test loss: '+str(test_loss/s))+"\n"
    return op

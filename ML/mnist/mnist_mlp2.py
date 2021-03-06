from __future__ import print_function
import keras
from keras.datasets import mnist
from keras.models import Sequential
from keras.layers import Dense, Activation
from keras.optimizers import SGD
from keras.callbacks import LearningRateScheduler, Callback
from keras.layers import GaussianNoise as GN
from keras.layers.normalization import BatchNormalization as BN
import sys
import math

def main():
    
    # PARAMS
    batch_size, num_classes, epochs = 128, 10, 100

    # DATA
    x_train, x_test, y_train, y_test = setData(num_classes)

    # TOPO
    model = setModel(num_classes)
    model.summary()

    # CALLBACKS
    lrate = LearningRateScheduler(step_decay)
    error = TestCallback(x_test, y_test, model, save=True, filePath='weights.hdf5')
    callbacks_list = [lrate, error]

    # TRAIN MODEL
    #model.load_weights(filePath, by_name=False)
    model.fit(x_train, y_train,batch_size=batch_size,epochs=epochs,verbose=1,callbacks=callbacks_list)

    # RESULTS
    error.printError("error.dat")

def setData(num_classes):
    # read data
    (x_train, y_train),(x_test, y_test)=mnist.load_data()
    # reshape data
    x_train = x_train.reshape(60000, 784)
    x_test = x_test.reshape(10000, 784)
    x_train = x_train.astype('float32')
    x_test = x_test.astype('float32')
    # Normalize [0..255]-->[0..1]
    x_train /= 255
    x_test /= 255
    print(x_train.shape[0], 'train samples')
    print(x_test.shape[0], 'test samples')
    # convert class vectors to binary class matrices
    y_train = keras.utils.to_categorical(y_train, num_classes)
    y_test = keras.utils.to_categorical(y_test, num_classes)
    return x_train, x_test, y_train, y_test


def setModel(num_classes):
    model = Sequential()
    model.add(Dense(512, input_shape=(784,)))
    model.add(BN())
    model.add(GN(0.3))
    model.add(Activation('relu'))
    model.add(Dense(512))
    model.add(BN())
    model.add(GN(0.3))
    model.add(Activation('relu'))
    model.add(Dense(num_classes, activation='softmax'))
    sgd=SGD(lr=0.01, decay=1e-6, momentum=0.9)
    model.compile(loss='categorical_crossentropy',optimizer=sgd,metrics=['accuracy'])
    return model

# error evolution
class TestCallback(Callback):
    def __init__(self, x_test, y_test, model, save=False, filePath=''):
        self.x_test = x_test
        self.y_test = y_test
        self.err = []
        self.model = model
        self.best = 100
        self.save = save
        self.filePath = filePath

    def on_epoch_end(self, epoch, logs={}):
        score = self.model.evaluate(self.x_test, self.y_test, verbose=0)
        error = 100 - score[1]*100
        print('\nTesting error: {} %\n'.format(error))
        self.err.append(error)
        if error < self.best and self.save:
            self.best = error
            self.model.save_weights(self.filePath)
            print("Best error, printing weigths")

    def printError(self,fileName):
        with open(fileName, 'w') as file:
            for i in self.err:
                file.write(str(i)+'\n')

# learning rate schedule
def step_decay(epoch):
    initial_lrate = 0.1
    drop = 0.5
    epochs_drop = 20
    lrate = initial_lrate * math.pow(drop, math.floor((1+epoch)/epochs_drop))
    if epoch % epochs_drop == 0:
        print("New learning rate: ", lrate)
    return lrate

main()


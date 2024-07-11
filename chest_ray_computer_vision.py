# -*- coding: utf-8 -*-
"""chest_ray_computer_vision.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1TkSH94MM51Wmt1Q-0WgIjaDoZwkNllxJ
"""

from getpass import getpass
import os

! mkdir ~/.kaggle
! cp kaggle.json ~/.kaggle/
! chmod 600 ~/.kaggle/kaggle.json

!kaggle competitions download copy-of-shai-level-2-training

!chmod 777 *

!unzip copy-of-shai-level-2-training.zip

#importing libraries
import keras
import tensorflow as tf
from keras.models import Sequential

from keras.layers import Dense, Dropout, Flatten

from keras.layers import Conv2D, MaxPooling2D

import numpy as np

import pandas as pd

import matplotlib.pyplot as plt
import seaborn as sns
import random

from keras.preprocessing.image import ImageDataGenerator

from keras.callbacks import ModelCheckpoint, EarlyStopping

train_datagen = ImageDataGenerator(
        rescale=1./255,
        shear_range=0.2,
        zoom_range=0.2,
        horizontal_flip=True,
        validation_split=0.2,fill_mode='nearest')

valid_datagen=ImageDataGenerator(
        rescale=1./255,
        shear_range=0.2,
        zoom_range=0.2,
        validation_split=0.2,fill_mode='nearest')

train_generator = train_datagen.flow_from_directory(
    directory=r"/content/train",
    target_size=(224, 224),
    color_mode="grayscale",
    batch_size=32,
    class_mode="categorical",
    shuffle=True,
    seed=42,
    subset='training'
)

valid_generator= train_datagen.flow_from_directory(
    directory=r"/content/train",
    target_size=(224, 224),
    color_mode="grayscale",
    batch_size=32,
    class_mode="categorical",
    shuffle=True,
    seed=42,subset='validation')

STEP_SIZE_TRAIN=train_generator.n//train_generator.batch_size
STEP_SIZE_VALID=valid_generator.n//valid_generator.batch_size

class_names = train_generator.class_indices
print(class_names)

class_names1 = ["covid", "normal", "virus"]  # List of class names
class_counts1 = [295, 468,433]  # Number of samples per class

#plotting classes
sns.barplot(x=class_names1, y=class_counts1)
plt.xlabel("Class")
plt.ylabel("Number of Samples")
plt.title("Class Distribution")
plt.xticks(rotation=45)  # Rotate x-axis labels for readability
plt.show()

#plotting an image
i = random.randint(0,31)

batch=next(train_generator)
print(batch[0].shape)
img=batch[0][i]
print (img.shape)
plt.imshow(img)

model = Sequential()

model.add(Conv2D(32, kernel_size=(3, 3),activation='relu',input_shape=(224,224,1)))

model.add(Conv2D(64, (3, 3), activation='relu'))
model.add(Conv2D(64, (3, 3), activation='relu'))


model.add(MaxPooling2D(pool_size=(2, 2)))

model.add(Dropout(0.25))
model.add(Conv2D(128, (3, 3), activation='relu'))
model.add(Conv2D(128, (3, 3), activation='relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Dropout(0.25))



model.add(Flatten())

model.add(Dense(128, activation='relu'))

model.add(Dropout(0.5))

model.add(Dense(3, activation='softmax'))

model.summary()

model.compile(
    optimizer='adam',
    loss='categorical_crossentropy',
    metrics=['accuracy'],
)

history=model.fit_generator(generator=train_generator,
                    steps_per_epoch=STEP_SIZE_TRAIN,
                    validation_data=valid_generator,
                    validation_steps=STEP_SIZE_VALID,
                    epochs=50,callbacks=EarlyStopping(monitor='val_loss', mode='min', verbose=2, patience=5)
)

acc = history.history['accuracy']
val_acc = history.history['val_accuracy']
loss = history.history['loss']
val_loss = history.history['val_loss']

epochs = range(len(acc))

plt.plot(epochs, acc, 'bo', label='Training acc')
plt.plot(epochs, val_acc, 'b', label='Validation acc')
plt.title('Training and validation accuracy')
plt.legend()

plt.figure()

plt.plot(epochs, loss, 'bo', label='Training loss')
plt.plot(epochs, val_loss, 'b', label='Validation loss')
plt.title('Training and validation loss')
plt.legend()

plt.show()

model.evaluate_generator(generator=valid_generator,
steps=STEP_SIZE_VALID)



test_datagen = ImageDataGenerator(rescale=1./255)

test_generator = test_datagen.flow_from_directory(
    directory=r"/content/drive/MyDrive/test1",
    target_size=(224, 224),
    color_mode="grayscale",
    batch_size=1,
    class_mode=None,
    shuffle=False,
    seed=42
)

STEP_SIZE_TEST=test_generator.n//test_generator.batch_size
test_generator.reset()
pred=model.predict_generator(test_generator,
steps=STEP_SIZE_TEST,
verbose=1)

predicted_class_indices=np.argmax(pred,axis=1)

labels = (train_generator.class_indices)
labels = dict((v,k) for k,v in labels.items())
predictions = [labels[k] for k in predicted_class_indices]

sample_submission=pd.read_csv('/content/sample_submission.csv')

sample_submission['Label']=predictions

sample_submission.to_csv('sample_cnn.csv', header=True, index=False)
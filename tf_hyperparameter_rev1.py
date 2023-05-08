# -*- coding: utf-8 -*-
"""TF_hyperparameter_rev1.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1hwy6laEnk_FEyfQN36RS8KcEUMRVvqW-

**TensorFlow AlexNet CNN Implementation**

Load Libraries
"""

import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import cv2
import numpy as np

"""Mount Google Drive"""

from google.colab import drive
drive.mount('/content/drive')

"""Define Train/Test Libraries"""

# folders would have pictures for their respective class
train_dir = "/content/drive/MyDrive/TensorFlowCNN/dataset/train"

#Define the directory for testing images (format to train_dir): 
test_dir = '/content/drive/MyDrive/TensorFlowCNN/dataset/test'

"""Define function to build and fit model"""

from keras import callbacks
from keras import optimizers
import matplotlib.pyplot as plt
import time
import os
import random
import pandas as pd

# define function to train and test AlexNet CNN with input parameters
def anet(train_dir, epochs, batch_size, optimizer, learning_rate, dropout, frac):

  t0 = time.time() #begin stopwatch to gauge runtime

  npix = 256 #define width x heigth of images for CNN i.e. size = npix x npix 

  # Get the list of all files in the training directory
  all_train_files = []
  for subdir in os.listdir(train_dir):
      subdir_path = os.path.join(train_dir, subdir)
      if os.path.isdir(subdir_path):
        for filename in os.listdir(subdir_path):
            filepath = os.path.join(subdir_path, filename)
            all_train_files.append((filepath, subdir)) # store the filepath and the class label

  # Shuffle the list of training files
  random.shuffle(all_train_files)

  # Select a random subset of the training files, with ratio = frac
  subset_size = int(len(all_train_files) * frac)
  subset_train_files = all_train_files[:subset_size]

  # Split the training subset into training and validation sets
  train_size = int(len(subset_train_files) * 0.8)
  train_files = subset_train_files[:train_size]
  val_files = subset_train_files[train_size:]

  # Define the ImageDataGenerator and specify the augmentation parameters
  train_datagen = ImageDataGenerator(
      rescale=1./255,
      rotation_range=20,
      width_shift_range=0.2,
      height_shift_range=0.2,
      shear_range=0.2,
      zoom_range=0.2,
      horizontal_flip=True,
      fill_mode='nearest'
  )

  # Generate the training data from the images in train directory
  train_generator = train_datagen.flow_from_dataframe(
      dataframe=pd.DataFrame(train_files, columns=['filepath', 'class']),
      directory=None,
      x_col='filepath',
      y_col='class',
      target_size=(npix, npix),
      batch_size=batch_size,
      class_mode='binary', # use 'categorical' if you have more than 2 classes
      shuffle=True
  )

  # Generate the validation data from the images in train directory
  val_generator = train_datagen.flow_from_dataframe(
      dataframe=pd.DataFrame(val_files, columns=['filepath', 'class']),
      directory=None,
      x_col='filepath',
      y_col='class',
      target_size=(npix, npix),
      batch_size=batch_size,
      class_mode='binary', # use 'categorical' if you have more than 2 classes
      shuffle=True
  )

  # Define the AlexNet CNN model layers
  model = tf.keras.Sequential([
      # First convolutional layer
      tf.keras.layers.Conv2D(96, (11,11), strides=(4,4), activation='relu', input_shape=(npix, npix, 3)),
      tf.keras.layers.BatchNormalization(),
      tf.keras.layers.MaxPooling2D(pool_size=(3,3), strides=(2,2)),
      
      # Second convolutional layer
      tf.keras.layers.Conv2D(256, (5,5), activation='relu', padding='same'),
      tf.keras.layers.BatchNormalization(),
      tf.keras.layers.MaxPooling2D(pool_size=(3,3), strides=(2,2)),
      
      # Third convolutional layer
      tf.keras.layers.Conv2D(384, (3,3), activation='relu', padding='same'),
      
      # Fourth convolutional layer
      tf.keras.layers.Conv2D(384, (3,3), activation='relu', padding='same'),
      
      # Fifth convolutional layer
      tf.keras.layers.Conv2D(256, (3,3), activation='relu', padding='same'),
      tf.keras.layers.MaxPooling2D(pool_size=(3,3), strides=(2,2)),
      
      # Flatten the output from the convolutional layers
      tf.keras.layers.Flatten(),
      
      # First fully connected layer
      tf.keras.layers.Dense(4096, activation='relu'),
      tf.keras.layers.Dropout(dropout),
      
      # Second fully connected layer
      tf.keras.layers.Dense(4096, activation='relu'),
      tf.keras.layers.Dropout(dropout),
      
      # Output layer
      tf.keras.layers.Dense(1, activation='sigmoid')
  ])

  # Compile the model
  if optimizer == 'Adam':
    model.compile(optimizer = optimizers.Adam(learning_rate=learning_rate),
                  loss='binary_crossentropy',
                  metrics=['accuracy'])
  elif optimizer == 'SGD':
    model.compile(optimizer = optimizers.SGD(learning_rate=learning_rate),
                loss='binary_crossentropy',
                metrics=['accuracy'])
  elif optimizer == 'Adadelta':
    model.compile(optimizer = optimizers.Adadelta(),
                loss='binary_crossentropy',
                metrics=['accuracy'])   
  elif optimizer == 'Adamax':
    model.compile(optimizer = optimizers.Adamax(learning_rate=learning_rate),
                loss='binary_crossentropy',
                metrics=['accuracy'])
  else:
    print('Optimizer not found')

  # Train the model using the training data
  earlystopping = callbacks.EarlyStopping(monitor="accuracy",
                                          mode="max", min_delta=1,
                                          restore_best_weights=True)

  history = model.fit(train_generator, validation_data=val_generator, steps_per_epoch = train_generator.samples/train_generator.batch_size, 
                      validation_steps=val_generator.samples/val_generator.batch_size, epochs=epochs)
  
  val_acc = history.history['val_accuracy'][-1] #validation accuracy
  train_acc = history.history['accuracy'][-1] #training accuracy

  t1 = time.time() - t0 #overall runtime

  return {'val_acc':val_acc, 'train_acc':train_acc, 'run_time':t1, 'model':model}

"""Define parameters and fit/validate model"""

batch_sizes_gs = [32]
optimizers_gs = ['Adam']
learning_rates_gs = [0.00001]
dropouts_gs = [0.5]
frac = 1
epoch_gs = 26

result_dict = {'batch_size':[],
               'optimizer':[],
               'learning_rate':[],
               'dropout':[],
               'epoch':[],
               'val_acc':[],
               'train_acc':[],
               'run_time':[],
               }

for i in range(len(batch_sizes_gs)):
  batch_size = batch_sizes_gs[i]
  dropout = dropouts_gs[i]
  optimizer = optimizers_gs[i]
  learning_rate = learning_rates_gs[i]

  output = anet(train_dir=train_dir, epochs=epoch_gs, batch_size=batch_size, optimizer=optimizer, learning_rate=learning_rate, dropout=dropout, frac=frac)
  result_dict['batch_size'].append(batch_size)
  result_dict['optimizer'].append(optimizer)
  result_dict['learning_rate'].append(learning_rate)
  result_dict['dropout'].append(dropout)
  result_dict['epoch'].append(epoch_gs)
  result_dict['val_acc'].append(output['val_acc'])
  result_dict['train_acc'].append(output['train_acc'])
  result_dict['run_time'].append(output['run_time'])

  print('Completed another hyperparameter test iteration:')
  print(result_dict)

"""Input any image(s) and test predication"""

# Load the image
img = cv2.imread("/content/drive/MyDrive/TensorFlowCNN/IMG_5933.jpg")

# Resize the image to npix x npix
npix=256
img = cv2.resize(img, (npix, npix))

# Convert the color space from BGR to RGB
img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

# Scale the pixel values to [0, 1]
img = img / 255.0

# Add a batch dimension to the image
img = np.expand_dims(img, axis=0)

model = output['model']
y_pred = model.predict(img)

# Print the predicted class label and probability
if y_pred < 0.5:
    print('Fresh fruit (prob={:.2f})'.format(1 - y_pred[0][0]))
else:
    print('Rotten fruit (prob={:.2f})'.format(y_pred[0][0]))
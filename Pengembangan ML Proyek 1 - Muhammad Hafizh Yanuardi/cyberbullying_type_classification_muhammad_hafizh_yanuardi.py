# -*- coding: utf-8 -*-
"""Cyberbullying Type Classification_Muhammad Hafizh Yanuardi.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1imDkU5B59iSXXK4L61baoeY15vcmPzoe
"""

import pandas as pd
from sklearn.model_selection import train_test_split
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.callbacks import Callback
from timeit import default_timer as timer
import tensorflow as tf
import matplotlib.pyplot as plt

message = '--- Mengimport berbagai library yang akan digunakan pada project ini ---'
print(message)

df = pd.read_csv('./cyberbullying_tweets.csv')
info = df.info()

message = '--- Mengimport data dari dataset cyberbullying_tweets.csv ---'
print(message)

values = df['cyberbullying_type'].value_counts()

message = '--- Menampilkan tipe-tipe cyberbullying dalam dataset ---'
print(message + '\n')
print(values)

X = df.copy(deep=True)

message = '--- Menyalin dataset pada variabel X untuk dilakukan preprocessing ---'
print(message)

X['tweet_text'] = X['tweet_text'].str.replace(r'@\w+', '', regex=True)     # Menghapus mentions
X['tweet_text'] = X['tweet_text'].str.replace(r'[!#?*,.]', '', regex=True)       # Menghapus simbol
X['tweet_text'] = X['tweet_text'].str.replace(r'http\://\S+', '', regex=True)  # Menghapus link
X['tweet_text'] = X['tweet_text'].str.replace(r'https\://\S+', '', regex=True)

message = '--- Membersihkan tweet-tweet yang ada dalam dataset untuk dapat diproses lebih efisien ---'
print(message)

delcount = 0
deldex = []
for i in range(47692):
  if len(X['tweet_text'][i]) > 200:
    delcount += 1
    deldex.append(i)

message = '--- Memasukkan index-index sampel yang tweetnya memiliki lebih dari 200 karakter untuk dihapus ---'
print(message)
print("--- " + str(delcount) + " sampel akan dihapus ---")

X = X.drop(deldex)

message = '--- Menghapus sampel-sampel dimana jumlah karakter tweet lebih dari 200 untuk mempersimpel proses training ---'
print(message)

values2 = X['cyberbullying_type'].value_counts()

message = '--- Mengecek perubahan jumlah sampel setiap kategori tipe cyberbullying ---'
print(message + '\n')
print(values2)

X.drop(X[X['cyberbullying_type'].isin(['not_cyberbullying', 'other_cyberbullying'])].index, inplace=True)

message = '--- Menghapus kolom not_cyberbullying dan other_cyberbullying ---'
print(message)

values3 = X['cyberbullying_type'].value_counts()

message = '--- Mengecek perubahan kategori tipe cyberbullying ---'
print(message + '\n')
print(values3)

y_dummies = pd.get_dummies(X['cyberbullying_type'])

message = '--- Melakukan One-Hot Encoding pada kolom cyberbullying_type dan memasukkannya dalam variabel y_dummies ---'
print(message)

message = '--- Melihat hasil One-Hot Encoding ---'
print(message + '\n')
print(y_dummies)

y = y_dummies
X_attributes = X['tweet_text'].values

message = '--- Memasukkan hasil One-Hot Encoding pada y, dan tweet pada X ---'
print(message)

X_train, X_test, y_train, y_test = train_test_split(X_attributes, y, test_size=0.2)

message = '--- Membagi X dan y menjadi training set dan validation set ---'
print(message)

tokenizer = Tokenizer(num_words=25000, oov_token='<oov>')
tokenizer.fit_on_texts(X_train)

seq_train = tokenizer.texts_to_sequences(X_train)
seq_test = tokenizer.texts_to_sequences(X_test)

padded_train = pad_sequences(seq_train, maxlen=200)
padded_test = pad_sequences(seq_test, maxlen=200)

message = '--- Melakukan tokenize pada kata-kata dalam tweet ---'
print(message)

# Commented out IPython magic to ensure Python compatibility.
# Callback untuk menghentikan training ketika akurasi validasi diatas 90%.
# Dalam kode ditambahkan 0.01% untuk memastikan bahwa akurasi lebih dari 90.00%
class ValAccCallback(Callback):
    def on_epoch_end(self, epoch, logs={}):
        if(logs.get('val_accuracy') >= 0.9001 and logs.get('accuracy') >= 0.9001):
          self.model.stop_training = True
          print("\n[accuracy | val_accuracy yang didapatkan senilai %2.2f%% | %2.2f%%, training dihentikan.]\n"
#                 % ((logs.get('accuracy')*100), (logs.get('val_accuracy')*100)))

        else:
          print("\n[accuracy | val_accuracy yang didapatkan senilai %2.2f%% | %2.2f%%, lanjut ke epoch berikutnya]\n"
#                 % ((logs.get('accuracy')*100), (logs.get('val_accuracy')*100)))


message = '--- Membuat class Callback yang menghentikan proses training apabila akurasi model melebihi 90% ---'
print(message)

val_acc_callback = ValAccCallback()

message = '--- Menempatkan fungsi callback pada variabel ---'
print(message)

model = tf.keras.Sequential([
    tf.keras.layers.Embedding(25000, 128, input_length=200),
    tf.keras.layers.LSTM(128),
    tf.keras.layers.Dense(512, activation='relu'),
    tf.keras.layers.Dropout(0.2),
    tf.keras.layers.Dense(128, activation='relu'),
    tf.keras.layers.Dense(4, activation='softmax')
])
model.compile(loss='categorical_crossentropy', optimizer=tf.optimizers.SGD(), metrics=['accuracy'])

message = '--- Membuat model menggunakan metode Sequential ---'
print(message)

num_epochs = 100

message = '--- Melakukan training ---'
print(message)

history = model.fit(
    padded_train,
    y_train,
    epochs=num_epochs,
    validation_data=(padded_test, y_test),
    callbacks=[val_acc_callback],
    verbose=1,
    )

# Menampilkan output dari training

message = '--- Menampilkan output dari training ---'
print(message)

acc = history.history['accuracy']
val_acc = history.history['val_accuracy']

loss = history.history['loss']
val_loss = history.history['val_loss']

plt.figure(figsize=(8, 8))
plt.subplot(2, 1, 1)
plt.plot(acc, label='Akurasi Training')
plt.plot(val_acc, label='Akurasi Validation')
plt.legend(loc='lower right')
plt.ylabel('Akurasi')
plt.ylim([min(plt.ylim()),1])
plt.title('Akurasi Training dan Validation')

plt.subplot(2, 1, 2)
plt.plot(loss, label='Training Loss')
plt.plot(val_loss, label='Validation Loss')
plt.legend(loc='upper right')
plt.ylabel('Cross Entropy')
plt.ylim([0,1.5])
plt.title('Training dan Validation Loss')
plt.xlabel('epoch')
plt.show()
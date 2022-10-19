# -*- coding: utf-8 -*-

import streamlit as st
import pandas as pd
from nsepy import get_history as gh
import datetime as dt
from datetime import date
import plotly.express as px
import plotly.graph_objects as go
import pickle
from tensorflow.keras.models import load_model
#from tensorflow.keras.Model import load_weights
import tensorflow as tf


page_bg_img = '''
<style>
.stApp {
background-image: url("https://i.ibb.co/wJ1YZz0/pexels-lukas-590014.jpg");
background-size: cover;
}
</style>
'''
st.set_page_config(page_title='Movie Recommendation App', page_icon=None, layout="centered", initial_sidebar_state="auto", menu_items=None)
st.markdown(page_bg_img, unsafe_allow_html=True)

st.title('Track and estimate stock prices of NSE:FEDERALBNK')

start = dt.date(2013,11,1)
end = date.today()

stk_data = gh(symbol='FEDERALBNK',start=start,end=end)
st.subheader(('Historical Price Data of FEDERALBNK'))
fig = go.Figure()
fig.add_trace(go.Scatter(x=stk_data.index,y=stk_data['Open'],name='Open', mode="lines"))
fig.add_trace(go.Scatter(x=stk_data.index,y=stk_data['Close'],name='Close', mode="lines"))

st.plotly_chart(fig, use_container_width=True)
stk_data['Date'] = stk_data.index
data2 = pd.DataFrame(columns = ['Date', 'Open', 'High', 'Low', 'Close'])
data2['Date'] = stk_data['Date']
data2['Open'] = stk_data['Open']
data2['High'] = stk_data['High']
data2['Low'] = stk_data['Low']
data2['Close'] = stk_data['Close']

print(data2)

x_train=data2['Close']

def windowed_dataset(series, window_size, batch_size, shuffle_buffer):
    """Generates dataset windows

    Args:
      series (array of float) - contains the values of the time series
      window_size (int) - the number of time steps to average
      batch_size (int) - the batch size
      shuffle_buffer(int) - buffer size to use for the shuffle method

    Returns:
      dataset (TF Dataset) - TF Dataset containing time windows
    """
  
    # Generate a TF Dataset from the series values
    dataset = tf.data.Dataset.from_tensor_slices(series)
    
    # Window the data but only take those with the specified size
    dataset = dataset.window(window_size + 1, shift=1, drop_remainder=True)
    
    # Flatten the windows by putting its elements in a single batch
    dataset = dataset.flat_map(lambda window: window.batch(window_size + 1))

    # Create tuples with features and labels 
    dataset = dataset.map(lambda window: (window[:-1], window[-1]))

    # Shuffle the windows
    dataset = dataset.shuffle(shuffle_buffer)
    
    # Create batches of windows
    dataset = dataset.batch(batch_size).prefetch(1)
    
    return dataset

window_size = 5
batch_size = 50
shuffle_buffer_size = 1000

train_set = windowed_dataset(x_train, window_size, batch_size, shuffle_buffer_size)
# Reset states generated by Keras
tf.keras.backend.clear_session()

# Build the model
model = tf.keras.models.Sequential([
  tf.keras.layers.Conv1D(filters=128, kernel_size=3,
                      strides=1, padding="causal",
                      activation="relu",
                      input_shape=[window_size, 1]),
  tf.keras.layers.LSTM(64, return_sequences=True),
  tf.keras.layers.LSTM(32),
  tf.keras.layers.Dense(16, activation='relu'),
  tf.keras.layers.Dense(1),
  tf.keras.layers.Lambda(lambda x: x * 200)
])

# Print the model summary
st.write(model.summary())
#train_set1 = windowed_dataset(train_cl, window_size, batch_size, shuffle_buffer_size)

#filename = r"C:\Users\User\Downloads\finalized_model.h5"
#path= r'C:\Users\User\Downloads'

#@loaded_moldel =tf.keras.Model.load_weights(path,'weights.h5')



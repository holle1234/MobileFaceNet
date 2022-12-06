from tensorflow.keras.models import Model
from tensorflow.keras.applications.mobilenet_v2 import MobileNetV2
from tensorflow.keras.layers import Dense, Lambda
import tensorflow as tf


def get_model():
    model = MobileNetV2(input_shape=(160, 160, 3), alpha=0.75, include_top=False, pooling="max")
    x = Dense(256, activation="relu")(model.layers[-1].output)
    x = Lambda(lambda d: tf.math.l2_normalize(d, axis=1), name="l2-norm")(x)

    model = Model(inputs=[model.input], outputs=[x])
    model.load_weights(r"resources/84_0.151.h5", by_name=True, skip_mismatch=False)

    return model
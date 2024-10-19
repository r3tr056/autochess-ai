
import ftplib
import hashlib
import json
import os

from keras.engine.topology import Input
from keras.engine.training import Model
from keras.layers.convolutional import Conv2D
from keras.layers.core import Activation, Dense, Flatten
from keras.layers.merge import Add
from keras.layers.normalization import BatchNormalization
from keras.regularizers import l2

from auto_chess_engine.core.api import ChessModelAPI
from auto_chess_engine.config import Config

logger = getLogger(__name__)

class ChessModel:
    def __init__(self, config):
        self.config = config
        self.model = None
        self.digest = None
        self.api = None

    def get_pipes(self, num=1):
        if self.api is None:
            self.api = ChessModelAPI(self)
            self.api.start()
        return [self.api.create_pipe() for _ in range(num)]

    def build(self):
        ''' Build the model using Keras and store in `self.model` '''
        mc = self.config.model
        in_x = x = Input((18, 8, 8))

        x = Conv2D(filters=mc.cnn_filter_num, kernel_size=mc.cnn_first_filter_size, padding="same", data_format="channels_first", use_bias=False, kernel_regularizer=l2(mc.l2_reg), name="input_conv-" + str(mc.cnn_first_filter_size) + '-' + str(mc.cnn_filter_num))(x)
        x = BatchNormalization(axis=1, name="input_batchnorm")(x)
        x = Activation("relu", name="input_reul")(x)

        for i in range(mc.res_layer_num):
            x = self._build_residual_block(x, i + 1)

        # Output from the residual network
        res_out = x

        # Policy estimation block
        # generates a attention weight matrix
        attention = Conv2D(1, (1, 1), activation='sigmoid', use_bias=False, name='attention')(res_out)
        # mutliply with the res_out to apply attention
        x = Multiply()([res_out, attention])

        x = Conv2D(filters=2, kernel_size=1, data_format="channels_first", use_bias=False, kernel_regularizer=l2(mc.l2_reg),
                    name="policy_conv-1-2")(res_out)
        x = BatchNormalization(axis=1, name="policy_batchnorm")(x)
        x = Activation("relu", name="policy_relu")(x)
        x = Flatten(name="policy_flatten")(x)
        # no output for 'pass'
        policy_out = Dense(self.config.n_labels, kernel_regularizer=l2(mc.l2_reg), activation="softmax", name="policy_out")(x)

        # for value output
        x = Conv2D(filters=4, kernel_size=1, data_format="channels_first", use_bias=False, kernel_regularizer=l2(mc.l2_reg),
                    name="value_conv-1-4")(res_out)
        x = BatchNormalization(axis=1, name="value_batchnorm")(x)
        x = Activation("relu",name="value_relu")(x)
        x = Flatten(name="value_flatten")(x)
        x = Dense(mc.value_fc_size, kernel_regularizer=l2(mc.l2_reg), activation="relu", name="value_dense")(x)
        value_out = Dense(1, kernel_regularizer=l2(mc.l2_reg), activation="tanh", name="value_out")(x)

        # Store the compiled model in `self.model`
        self.model = Model(in_x, [policy_out, value_out], name="chess_model")

    def _build_residual_block(self, x, index):
        mc = self.config.model
        in_x = x
        res_name = "res"+str(index)

        # first convolution bolck
        x = Conv2D(filters=mc.cnn_filter_num, kernel_size=mc.cnn_filter_size, padding="same",
                   data_format="channels_first", use_bias=False, kernel_regularizer=l2(mc.l2_reg), 
                   name=res_name+"_conv1-"+str(mc.cnn_filter_size) + "-"+str(mc.cnn_filter_num))(x)
        x = BatchNormalization(axis=1, name=res_name+"_batchnorm1")(x)
        x = Activation("relu",name=res_name+"_relu1")(x)

        # second conv block
        x = Conv2D(filters=mc.cnn_filter_num, kernel_size=mc.cnn_filter_size, padding="same",
                   data_format="channels_first", use_bias=False, kernel_regularizer=l2(mc.l2_reg), 
                   name=res_name+"_conv2-"+str(mc.cnn_filter_size)+"-"+str(mc.cnn_filter_num))(x)
        x = BatchNormalization(axis=1, name="res"+str(index)+"_batchnorm2")(x)

        # residual addition
        x = Add(name=res_name+"_add")([in_x, x])
        # final activation
        x = Activation("relu", name=res_name+"_relu2")(x)
        return x

    @staticmethod
    def fetch_digest(weight_path):
        if os.path.exists(weight_path):
            m = hashlib.sha256()
            with open(weight_path, 'rb') as f:
                m.update(f.read())
            return m.hexdigest()

    def train(self, X_train, y_policy_train, y_value_train, epochs=10):
        """
        Train the chess model using the provided data
        """
        if self.model is None:
            logger.error("Model not built. Call build() method first")
            return

        checkpoint_filepath = 'model_checkpoint.h5'
        model_checkpoint = ModelCheckpoint(
            filepath=checkpoint_filepath,
            save_best_only=true,
            monitor='val_loss',
            mode='min',
            verbose=1
        )

        # Split the data into train and validation sets
        validation_split = 0.2
        num_validation_samples = int(validation_split * len(X_train))

        X_val = X_train[:num_validation_samples]
        y_policy_val = y_policy_train[:num_validation_samples]
        y_value_val = y_value_train[:num_validation_samples]

        X_train = X_train[num_validation_samples:]
        y_policy_train = y_policy_train[num_validation_samples:]
        y_value_train = y_value_train[num_validation_samples:]

        # train the model
        history = self.model.fit(
            X_train, {'policy_out': y_policy_train, 'value_out': y_value_train},
            validation_data=(X_val, {'policy_out': y_policy_val, 'value_out': y_value_val}),
            epochs=epochs,
            batch_size=batch_size,
            callbacks=[model_checkpoint],
            verbose=1
        )

        self.model.load_weights(checkpoint_filepath)
        os.remove(checkpoint_filepath)

        return history

    def load(self, config_path, weight_path):
        mc = self.config.model
        resources = self.config.resource

        if mc.distributed and config_path == resources.model_best_config_path:
            try:
                logger.debug('Loading model from server')
                with ftplib.FTP(
                    resources.model_best_distrubuted_ftp_server,
                    resources.model_best_distrubuted_ftp_user,
                    resources.model_best_distrubuted_ftp_password,
                ) as ftp_connection:
                    ftp_connection.cwd(resources.model_best_distrubuted_ftp_remote_path)
                    ftp_connection.retrbinary('RETR model_best_config.json', open(config_path, 'wb').write)
                    ftp_connection.retrbinary('RETR model_best_weight.h5', open(weight_path, 'wb').write)
            except Exception as e:
                logger.error(f'Error occured {e}')

        if os.path.exists(config_path) and os.path.exists(weight_path):
            logger.debug(f"Loading model from {config_path}")
            with open(config_path, "rt") as f:
                self.model = Model.from_config(json.load(f))
            self.model.load_weights(weight_path)
            self.model._make_predict_function()
            self.digest = self.fetch_digest(weight_path)
            logger.debug(f"Loaded model digest = {self.digest}")
            return True
        else:
            logger.debug(f"model file does not exist at {config_path} and {weight_path}")
            return False

    def save(self, config_path, weight_path):
        logger.debug(f"Save model to {config_path}")
        with open(config_path, 'wt') as f:
            json.dump(self.model.get_config(), f)
            self.model.save_weights(weight_path)
        self.digest = self.fetch_digest(weight_path)
        logger.debug(f"Saved model digest { self.digest }")

        mc = self.config.model
        resources = self.config.resource

        if mc.distributed and config_path == resources.model_best_config_path:
            try:
                logger.debug("Saving model to server")
                with ftplib.FTP(
                    resources.model_best_distrubuted_ftp_server,
                    resources.model_best_distrubuted_ftp_user,
                    resources.model_best_distrubuted_ftp_password,
                ) as ftp_connection:

                    ftp_connection.cwd(resources.model_best_distrubuted_ftp_remote_path)
                    with open(config_path, 'rb') as config_file:
                        ftp_connection.storbinary('STOR model_best_config.json', config_file)

                    with open(weight_path, 'rb') as weight_file:
                        ftp_connection.storbinary('STOR model_best_weight.h5', weight_file)
            except Exception as e:
                logger.error(f'Error occured : {e}')



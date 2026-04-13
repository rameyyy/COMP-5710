from sklearn.neighbors import KNeighborsClassifier
from sklearn import datasets, linear_model
import pandas as pd
import numpy as np
import mnist
from sklearn.model_selection import KFold
from sklearn.datasets import load_iris
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Dense, Flatten
from tensorflow.keras.utils import to_categorical
from tensorflow import keras
import myLogger

# Obtain a shared logger object for all functions in this module.
# Using the instructor-provided logger writes timestamped entries to W7-LOGGER.log,
# which creates a persistent audit trail for forensic review.
logger = myLogger.giveMeLoggingObject()

def readData():
    # LOG LOCATION 1 — Resource access (poisoning attack surface)
    # Logging before dataset load documents which data source is being consumed.
    # If an attacker substitutes a poisoned dataset file, the log entry pinpoints
    # exactly when and what resource was accessed, supporting forensic investigation.
    logger.info("readData: Loading Iris dataset from sklearn.datasets")

    iris = datasets.load_iris()
    print(type(iris.data), type(iris.target))
    X = iris.data
    Y = iris.target
    df = pd.DataFrame(X, columns=iris.feature_names)

    # LOG LOCATION 2 — Dataset shape validation (poisoning attack indicator)
    # A poisoning attack may alter the number of samples or features in the dataset.
    # Logging the shape after load lets us detect unexpected dimensions that could
    # indicate tampered or substituted input data.
    logger.info("readData: Dataset loaded successfully — shape: %s, target shape: %s",
                X.shape, Y.shape)

    print(df.head())
    return df

def makePrediction():
    # LOG LOCATION 3 — Resource access (poisoning attack surface)
    # Same rationale as readData: recording the data source consumed by the KNN
    # classifier gives forensic visibility into what the model was trained on.
    logger.info("makePrediction: Loading Iris dataset for KNN classifier")

    iris = datasets.load_iris()
    knn = KNeighborsClassifier(n_neighbors=6)
    knn.fit(iris['data'], iris['target'])
    X = [
        [5.9, 1.0, 5.1, 1.8],
        [3.4, 2.0, 1.1, 4.8],
    ]
    prediction = knn.predict(X)

    # LOG LOCATION 4 — Prediction output (model tricking indicator)
    # Logging raw prediction results lets us audit the model's output over time.
    # Unexpected or systematically wrong predictions are a key indicator that the
    # model is being tricked (adversarial inputs or a compromised model).
    logger.info("makePrediction: KNN prediction result for inputs %s -> %s", X, prediction.tolist())

    print(prediction)

def doRegression():
    # LOG LOCATION 5 — Resource access (poisoning attack surface)
    # Logging the dataset being loaded for regression documents the resource used.
    # A poisoning attack could introduce corrupted samples into the diabetes dataset,
    # skewing the regression coefficients; the log provides a forensic starting point.
    logger.info("doRegression: Loading diabetes dataset for linear regression")

    diabetes = datasets.load_diabetes()
    diabetes_X = diabetes.data[:, np.newaxis, 2]
    diabetes_X_train = diabetes_X[:-20]
    diabetes_X_test = diabetes_X[-20:]
    diabetes_y_train = diabetes.target[:-20]
    diabetes_y_test = diabetes.target[-20:]
    regr = linear_model.LinearRegression()
    regr.fit(diabetes_X_train, diabetes_y_train)
    diabetes_y_pred = regr.predict(diabetes_X_test)

    # LOG LOCATION 6 — Regression coefficients (model tricking indicator)
    # Logging the learned coefficient and intercept after training exposes the model's
    # internal state. Abnormal coefficient values can signal that poisoned training data
    # has skewed the model, which is a sign of a poisoning or model-tricking attack.
    logger.info("doRegression: Trained regression — coefficient: %s, intercept: %s",
                regr.coef_, regr.intercept_)


def doDeepLearning():

    # LOG LOCATION 7 — Resource access (poisoning attack surface)
    # The MNIST dataset is loaded from keras; logging this event documents the data
    # source for the CNN. A poisoning attack could swap in a corrupted version of the
    # dataset, and this log entry marks the moment of access for forensic analysis.
    logger.info("doDeepLearning: Loading MNIST dataset via keras.datasets.mnist")

    (train_images, train_labels), (test_images, test_labels) = keras.datasets.mnist.load_data()

    # LOG LOCATION 8 — Dataset shape validation (poisoning attack indicator)
    # Recording the shape of training and test splits after load lets us detect
    # unexpected dataset sizes that could indicate a poisoned or tampered data source.
    logger.info("doDeepLearning: MNIST loaded — train shape: %s, test shape: %s",
                train_images.shape, test_images.shape)

    train_images = (train_images / 255) - 0.5
    test_images = (test_images / 255) - 0.5

    train_images = np.expand_dims(train_images, axis=3)
    test_images = np.expand_dims(test_images, axis=3)

    num_filters = 8
    filter_size = 3
    pool_size = 2

    model = Sequential([
    Conv2D(num_filters, filter_size, input_shape=(28, 28, 1)),
    MaxPooling2D(pool_size=pool_size),
    Flatten(),
    Dense(10, activation='softmax'),
    ])

    # Compile the model.
    model.compile(
    'adam',
    loss='categorical_crossentropy',
    metrics=['accuracy'],
    )

    # Train the model.
    model.fit(
    train_images,
    to_categorical(train_labels),
    epochs=3,
    validation_data=(test_images, to_categorical(test_labels)),
    )

    model.save_weights('cnn.weights.h5')

    predictions = model.predict(test_images[:5])
    predicted_classes = np.argmax(predictions, axis=1)

    # LOG LOCATION 9 — CNN prediction output vs ground truth (model tricking indicator)
    # Logging predicted classes alongside true labels lets us detect discrepancies
    # that indicate the CNN is being tricked. If predictions systematically diverge
    # from known ground truth, it is a strong signal of an adversarial model attack.
    logger.info("doDeepLearning: CNN predictions (first 5): %s | Ground truth: %s",
                predicted_classes.tolist(), test_labels[:5].tolist())

    print(np.argmax(predictions, axis=1)) # [7, 2, 1, 0, 4]
    print(test_labels[:5]) # [7, 2, 1, 0, 4]

def k_fold_cv_mlp(n_splits):

  # LOG LOCATION 10 — Cross-validation configuration and resource access (poisoning + model tricking)
  # Logging n_splits and the dataset being used documents both the resource consumed
  # and the evaluation configuration. Unexpected splits or dataset sizes can indicate
  # poisoning. Logging per-fold accuracy (below) catches model-tricking by surfacing
  # folds with abnormally low scores that would suggest adversarial manipulation.
  logger.info("k_fold_cv_mlp: Starting %d-fold cross-validation on Iris dataset", n_splits)

  iris_data = load_iris()
  X_data = pd.DataFrame(iris_data.data, columns=iris_data.feature_names)
  ## to numpy
  X=  X_data.to_numpy()
  y = iris_data.target

  kf = KFold(n_splits)
  folds = []

  for train_index, test_index in kf.split(X):
      folds.append((train_index, test_index))

  # Initialize machine learning model, MLP
  model = MLPClassifier(hidden_layer_sizes=(256,128,64,32),activation="relu",random_state=1)

  # Initialize a list to store the evaluation scores
  scores = []
  ## Initialize fold index
  fold_index = 0


  # Iterate through each fold
  for train_indices, test_indices in folds:
      X_train, y_train = X[train_indices], y[train_indices]
      X_test, y_test = X[test_indices], y[test_indices]

      fold_index += 1
      print(f"Fold {fold_index}:")

      # scale data
      sc_X = StandardScaler()
      X_train_scaled=sc_X.fit_transform(X_train)
      X_test_scaled=sc_X.transform(X_test)

      # Train the model on the training data
      model.fit(X_train_scaled, y_train)

      # Make predictions on the test data
      y_pred = model.predict(X_test_scaled)

      # Calculate the accuracy score for this fold
      fold_score = accuracy_score(y_test, y_pred)
      print(f"Fold test score {fold_score}:")

      # LOG LOCATION 11 — Per-fold accuracy (model tricking indicator)
      # Logging each fold's accuracy score creates a forensic record of model performance.
      # A legitimate model should produce consistently high scores across folds on Iris.
      # An unusually low fold score is a red flag that adversarial inputs or a manipulated
      # model is producing incorrect predictions — a hallmark of a model tricking attack.
      logger.info("k_fold_cv_mlp: Fold %d accuracy: %.4f", fold_index, fold_score)

      # Append the fold score to the list of scores
      scores.append(fold_score)

  # Calculate the mean accuracy across all folds
  mean_accuracy = np.mean(scores)
  print("K-Fold Cross-Validation Scores:", scores)
  print("Mean Accuracy:", mean_accuracy)

  # LOG LOCATION 12 — Mean cross-validation accuracy (model tricking indicator)
  # The mean accuracy across all folds is the most reliable summary of model health.
  # Logging it provides a single auditable metric: if mean accuracy drops significantly
  # from a known baseline, it strongly suggests the model has been tricked or the
  # training data has been poisoned, warranting immediate forensic investigation.
  logger.info("k_fold_cv_mlp: Mean accuracy across %d folds: %.4f", n_splits, mean_accuracy)

if __name__=='__main__':
    data_frame = readData()
    makePrediction()
    doRegression()
    my_k_fold = input('Type in k for cross valdation: ')
    my_k_fold = int(my_k_fold)
    k_fold_cv_mlp(my_k_fold)
    doDeepLearning()

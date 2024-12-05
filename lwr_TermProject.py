import matplotlib.pyplot as plt
import numpy as np
import util


def main(tau, train_path, eval_path):
    """Problem: Locally weighted regression (LWR)

    Args:
        tau: Bandwidth parameter for LWR.
        train_path: Path to CSV file containing dataset for training.
        eval_path: Path to CSV file containing dataset for evaluation.
    """
    # Load training set
    x_train, y_train = util.load_dataset(train_path, add_intercept=True)

    # *** START CODE HERE ***
    # Fit a LWR model
    clf = LocallyWeightedLinearRegression(tau)
    clf.fit(x_train, y_train)
    x_eval, y_eval = util.load_dataset(eval_path, add_intercept=True)
    y_pred = clf.predict(x_eval)
    # Get MSE value on the validation set
    n = np.size(y_pred)
    MSE = (np.linalg.norm(y_pred - y_eval)**2)/n
    print(MSE)
    # Plot validation predictions on top of training set
    plt.scatter(x_eval[:,1],y_pred, label = "Prediction", marker = "o", c = "red")
    plt.scatter(x_train[:,1],y_train, label = "Training Set", marker = "x", c = "blue")
    plt.legend(["Prediction","Training Set"], loc = "lower center")
    plt.title('tau = '+str(tau)+', MSE = '+str(MSE))
    plt.savefig('plot2b.png')
    plt.clf()
    # No need to save predictions
    # *** END CODE HERE ***


class LocallyWeightedLinearRegression():
    """Locally Weighted Regression (LWR).

    Example usage:
        > clf = LocallyWeightedLinearRegression(tau)
        > clf.fit(x_train, y_train)
        > clf.predict(x_eval)
    """

    def __init__(self, tau):
        super(LocallyWeightedLinearRegression, self).__init__()
        self.tau = tau
        self.x = None
        self.y = None

    def fit(self, x, y):
        """Fit LWR by saving the training set.

        """
        # *** START CODE HERE ***
        self.x = x.T
        self.y = y.T
        # *** END CODE HERE ***

    def predict(self, x):
        """Make predictions given inputs x.

        Args:
            x: Inputs of shape (m, n).

        Returns:
            Outputs of shape (m,).
        """
        # *** START CODE HERE ***
        x = x.T
        W_diags = np.exp(-((np.linalg.norm(self.x[np.newaxis, :, :] - x[:, np.newaxis, :], axis=2) / self.tau)**2)/2)
        m = np.size(x,0)
        n = np.size(x,1)
        y_pred = np.zeros((m,n))
        for i in range(m):
            W = np.diag(W_diags[i,:])
            theta_i = np.linalg.solve(np.transpose(self.x)@W@self.x,np.transpose(self.x)@W@self.y)
            y_pred[i,:] = theta_i.T @ x[i,:]
        return y_pred.T
        # *** END CODE HERE ***

if __name__ == '__main__':
    main(tau=5e-1,
         train_path='./train.csv',
         eval_path='./valid.csv')

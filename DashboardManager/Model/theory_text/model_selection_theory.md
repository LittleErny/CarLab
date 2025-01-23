### Short Descriptions of Models

#### 1. **Linear Regression**

A simple model that predicts prices by drawing a straight line through the data. It works best when the relationship
between features and price is straightforward.

#### 2. **Ridge Regression**

Similar to Linear Regression but adds a penalty to avoid overfitting. It helps when the data has many features or some
are highly related.

#### 3. **Lasso Regression**

Like Ridge Regression, but it can completely remove unimportant features, making the model simpler. It’s helpful when
there are too many unnecessary features.

#### 4. **Decision Tree Regressor**

This model predicts by asking a series of "yes/no" questions, splitting the data into groups. It’s good for capturing
patterns but can overfit without limits.

#### 5. **Random Forest Regressor**

Uses many Decision Trees and combines their predictions to make a better guess. It's more accurate and stable but takes
more time and memory.

#### 6. **XGBoost Regressor**

XGBoost stands for **eXtreme Gradient Boosting**. It works by creating a series of simple decision trees. Each tree
tries to fix the mistakes made by the previous ones. Here's how:

1. The first tree makes predictions (usually starting with averages).
2. The second tree focuses on fixing the biggest errors from the first tree.
3. This process continues, with each new tree improving the overall prediction.
4. Finally, all the trees' predictions are combined for the final result.

This method is powerful because it keeps learning from errors and is very fast due to optimizations like parallel
processing.

#### 7. **CatBoost Regressor**

CatBoost is short for **Categorical Boosting**. It is also a type of gradient boosting but is specially designed to
handle data with categorical features (like "color: red, blue, green"). Here's how it works:

1. Instead of turning categories into numbers manually, CatBoost automatically processes them during training.
2. Like XGBoost, it builds trees step by step, focusing on improving where errors occur.
3. It uses a unique trick called *ordered boosting*, which reduces overfitting by carefully managing how trees learn
   from the data.

CatBoost is great because it works well out-of-the-box, handles messy data smoothly, and requires less tweaking to
perform well.
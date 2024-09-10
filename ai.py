import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

def train_model():
    # Load data
    data = pd.read_json('game_data.json', lines=True)

    # Perform one-hot encoding for dealerCards and yourCardsA
    dealer_cards_df = pd.DataFrame(data['dealerCards'].tolist())
    dealer_cards_df = dealer_cards_df.add_prefix('dealer_card_')
    your_cardsA_df = pd.DataFrame(data['yourCardsA'].tolist())
    your_cardsA_df = your_cardsA_df.add_prefix('your_cardA_')
    your_cardsB_df = pd.DataFrame(data['yourCardsB'].tolist())
    your_cardsB_df = your_cardsB_df.add_prefix('your_cardB_')

    # Concatenate the one-hot encoded features with the original data
    data_encoded = pd.concat([data.drop(columns=['dealerCards', 'yourCardsA', 'yourCardsB']), dealer_cards_df, your_cardsA_df, your_cardsB_df], axis=1)

    # Feature selection
    features = data_encoded.drop(columns=['action', 'outcome'])  # Exclude target columns
    target = data_encoded['action']  # Assuming 'action' is the target variable for classification

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(features, target, test_size=0.2, random_state=42)

    # Train model
    model = RandomForestClassifier()
    model.fit(X_train, y_train)

    # Evaluate model
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    return accuracy

# Run the training and evaluation process multiple times
accuracies = []
iterations = 100  # Set a reasonable number of iterations
for i in range(iterations):
    accuracy = train_model()
    accuracies.append(accuracy)
    print(f"Iteration {i+1}: Accuracy = {accuracy}")

# Calculate and print the average accuracy
average_accuracy = sum(accuracies) / len(accuracies)
print(f"Average Accuracy: {average_accuracy}")

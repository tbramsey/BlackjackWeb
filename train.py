from agent import Agent
from game import BlackjackGame
import random
import torch
import matplotlib.pyplot as plt
from IPython import display
plt.ion()


def train():
    plot_scores = []
    plot_mean_scores = []
    total_score = 0
    record = 0
    agent = Agent()
    game = BlackjackGame()  # Initialize your game
    decks_remaining = 6
    for x in range(300):  # Number of episodes
        while decks_remaining > 2:
            game.reset_hands()
            state_old = agent.get_state(game)
            action = agent.get_action(state_old)
            #action = random.randint(0, 6)
            game.set_bet(action)
            print("bet", game.bet)
            reward = 0
            done = False
            
            # Collect initial experience
            agent.remember(state_old, action, reward, state_old, done)
            agent.train_short_memory(state_old, action, reward, state_old, done)
            
            game.deal()
            game.dealerTurn()
            action = -1
            times = 0
            
            while action != 0 and times < 8:
                state_old = agent.get_state(game)
                action = agent.get_action(state_old)
                #action = random.randint(0, 6)
                reward, score, decks_remaining, action = game.play_step(action)
                state_new = agent.get_state(game)
                
                if not game.split:
                    done = True
                
                # Collect experiences
                agent.remember(state_old, action, reward, state_new, done)
                agent.train_short_memory(state_old, action, reward, state_new, done)
                
                times += 1
                
            if game.split:
                while action == 3 and times < 8:
                    state_old = agent.get_state(game)
                    action = agent.get_action(state_old)
                    #action = random.randint(0, 6)
                    reward, score, decks_remaining, action = game.play_step2(action)
                    state_new = agent.get_state(game)
                    done = True
                    
                    # Collect experiences
                    agent.remember(state_old, action, reward, state_new, done)
                    agent.train_short_memory(state_old, action, reward, state_new, done)
                    
                    times += 1
            
            if done:
                score = game.evaluate()
        
        game.reset()
        decks_remaining = 6
        agent.n_games += 1
        
        # Train model periodically
        agent.train_long_memory()
        
        if score > record:
            record = score
            
        
        plot_scores.append(score)
        total_score += score
        mean_score = total_score / agent.n_games
        plot_mean_scores.append(mean_score)
        plot(plot_scores, plot_mean_scores)
        print('Game', agent.n_games, 'Score', score, 'Record:', record, 'Average:', mean_score)


def print_model_parameters(model):
    for name, param in model.named_parameters():
        if param.requires_grad:
            print(f"Layer: {name} | Size: {param.size()} | Values: {param.data}") 


def plot(scores, mean_scores):
    display.clear_output(wait=True)
    display.display(plt.gcf())
    plt.clf()
    plt.title('Training...')
    plt.xlabel('Number of Games')
    plt.ylabel('Score')
    plt.plot(scores)
    plt.plot(mean_scores)
    plt.ylim(ymin=0)
    plt.text(len(scores)-1, scores[-1], str(scores[-1]))
    plt.text(len(mean_scores)-1, mean_scores[-1], str(mean_scores[-1]))
    plt.show(block=False)
    plt.pause(.1)

if __name__ == '__main__':
    train()

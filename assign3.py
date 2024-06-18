# -*- coding: utf-8 -*-
"""Assign3.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1WdcwUJpYFJ736RuGBGg7QKF0DNNeva2x
"""

from collections import defaultdict
import hashlib, uuid, sys
import numpy as np
import argparse

np.random.seed(29)

# Categories
categories = ["Politics", "Economics", "Science", "Technology", "Health", "Sports"]
func = lambda x: "Real" if x>5 else ("Fake" if x<5 else "Tie")

# User Model
class User:
    def __init__(self, address, balance):
        self.address = address # public address or name
        self.balance = balance # balance of that user
        self.categoryTrustScore = defaultdict(lambda: 50) # initial 50 score, 0-100 score possible

# News Model
class News:
    def __init__(self, requester, category, content_hash, max_votes, minimum_trust, registration_fee, participation_reward, max_reward):
        self.requester = requester # one who requestes the vote pool
        self.category = category # category of news
        self.content_hash = content_hash # news content has directly
        self.max_votes = max_votes # max votes before stop
        self.minimum_trust = minimum_trust # trust required to register for voting
        self.registration_fee = registration_fee # fee required inorder to register for a News
        self.participation_reward = participation_reward # reward you get when u register for news
        self.max_reward = max_reward # max reward you can get it you are right

        self.score = 5 # Scale 0-10, 0: Fake & 10 Real
        self.registered = [] # register the users
        self.voters = [] # store the voters
        self.votes = [] # store the voters
        self.confidences = [] # store the confidence
        self.truthfulness = defaultdict(lambda: 0) # update truthness of each voter, this gets added to categorytrustscore
        self.finish = False # to state is contest is over or running
        self.status = "Tie" # status of the news vote

        # voting contest is valid only if requester of the news has enough money to give rewards
        self.valid = requester.balance >= (max_reward+participation_reward-registration_fee)*max_votes

# DApp Model
class FactCheckSystem:
    def __init__(self):
        self.users = {} # list of users
        self.news_items = {} # list of news

    # adding user
    def add_user_to_system(self, address, balance=10000):
        self.users[address] = User(address, balance)

    # adding news
    def request_fact_check(self, address, category, content_hash, max_votes=50, minimum_trust=25, registration_fee=10, participation_reward=1, max_Reward=100):
        new_news = News(self.users[address], category, content_hash, max_votes, minimum_trust, registration_fee, participation_reward, max_Reward)
        if new_news.valid: self.news_items[content_hash] = new_news # only add if valid

    # register for news
    def register_fact_check(self, address, content_hash):
        user = self.users[address]
        news_item = self.news_items[content_hash]

        # if not already in registered
        if user not in news_item.registered:
            # if meets the minimum trust criteria
            if user.categoryTrustScore[news_item.category] >= news_item.minimum_trust:
                # if has the balance to register
                if user.balance >= news_item.registration_fee:
                    # if news contest is valid and not finished
                    if news_item.valid and not news_item.finish:
                        user.balance -= news_item.registration_fee # reduce balance of registered
                        news_item.requester.balance += news_item.registration_fee # add fund in the creater of contest
                        news_item.registered.append(user) # registered the user

    # update score and confidence of each voter of the news
    def update_score_confidences(self, content_hash, update_by=5):
        # Compute the new score using numpy for performance
        news_item = self.news_items[content_hash]
        news_item.score = np.average(news_item.votes, weights=news_item.confidences)

        # Determine the news status based on the score
        if news_item.score > 5: news_item.status = "Real"
        elif news_item.score < 5: news_item.status = "Fake"
        else: news_item.status = "Tie"

        # Define rewards and their reversal only once
        factor = np.array([-1, -0.8, -0.6, -0.4, -0.2, 0, 0.2, 0.4, 0.6, 0.8, 1])
        reverse_factor = factor[::-1]
        category = news_item.category

        # Update each voter's category trust score
        for voter, vote in zip(news_item.voters, news_item.votes):
            # Select the correct reward based on the news status
            if news_item.status == "Real": reward = factor[vote]
            elif news_item.status == "Fake": reward = reverse_factor[vote]
            else: reward = 0

            # Calculate the new score with clamping to the range [0, 100]
            news_item.truthfulness[voter] = reward * update_by

    # distribute rewards on the news
    def distribute_rewards(self, content_hash):
        news_item = self.news_items[content_hash] # get the news
        votes = np.array(news_item.votes) # all votes
        confidences = np.array(news_item.confidences) # all total confidences

        score = np.array([-1, -0.8, -0.6, -0.4, -0.2, 0, 0.2, 0.4, 0.6, 0.8, 1])
        reverse_score = score[::-1]

        if news_item.status == "Real": reward = [score[vote] for vote in votes]
        elif news_item.status == "Fake": reward = [reverse_score[vote] for vote in votes]
        else: reward = [0 for vote in votes]

        # Calculate reward factors
        factors = confidences * np.array(reward)
        factors = np.clip(factors, 0, None)  # Ensure no negative factors i.e all correct voters

        total = np.sum(factors)
        if float(total) == 0.0: final_rewards = [0 for vote in votes]
        else: final_rewards = (factors / total) * news_item.max_reward

        # Distribute votes
        for voter, reward in zip(news_item.voters, final_rewards):
            voter.balance += reward  # add reward to the right voters
            news_item.requester.balance -= reward # reduce fund from the creater of contest
            if news_item.status != "Tie":
                voter.categoryTrustScore[news_item.category] += news_item.truthfulness[voter] # update catergory trust scores
                voter.categoryTrustScore[news_item.category] = max(0, min(100, voter.categoryTrustScore[news_item.category])) # update catergory trust scores

        news_item.finish = True # end of voting

    # vote on a news
    def vote_on_news(self, address, content_hash, score):
        user = self.users[address]
        news_item = self.news_items[content_hash]

        # if not already in voted
        if user not in news_item.voters:
            # if registered
            if user in news_item.registered:
                # if news contest is valid and not finished
                if news_item.valid and not news_item.finish:
                    news_item.voters.append(user) # add to voters
                    news_item.votes.append(score) # add score
                    total_confidence = user.balance * user.categoryTrustScore[news_item.category] # total confidence = balance*trust
                    news_item.confidences.append(total_confidence) # add total confidence

                    user.balance += news_item.participation_reward # Participation Reward to user
                    news_item.requester.balance -= news_item.participation_reward # reduce fund in the creater of contest
                    self.update_score_confidences(content_hash) # update score

                    if len(news_item.votes) == news_item.max_votes: # if contested has ended
                        self.distribute_rewards(content_hash) # distribute score to all

    # Simulating environment
    def simulate_voting(self, N, p, q, rounds):
        # Initialize users
        num_honest = int(N * (1 - q))
        num_malicious = N - num_honest
        num_trustworthy = int(num_honest * p)
        num_less_trustworthy = num_honest - num_trustworthy

        probability_correct = {}
        news_truth_values = {}

        # This user creates all voting polls
        self.add_user_to_system("Simulator", balance=int(1e10))

        # Create trustworthy, less trustworthy, and malicious users
        for i in range(num_trustworthy):
            name = f'honest_trustworthy_{i}'
            self.add_user_to_system(name, balance=1)
            probability_correct[name] = 0.9

        for i in range(num_less_trustworthy):
            name = f'honest_less_trustworthy_{i}'
            self.add_user_to_system(name, balance=1)
            probability_correct[name] = 0.7

        for i in range(num_malicious):
            name = f'malicious_{i}'
            self.add_user_to_system(name, balance=1)
            probability_correct[name] = 0.0

        # Simulate voting over multiple rounds
        for i in range(rounds):
            content_hash = hashlib.sha256(str(uuid.uuid4()).encode()).hexdigest()
            self.request_fact_check("Simulator", "Politics", content_hash, N, 0, 0, 0, 10)
            truth_value = np.random.randint(2)  # Randomly choose news as true (1) or fake (0)
            news_truth_values[content_hash] = truth_value

            voted = {}
            for address in list(self.users.keys()):
                if address != "Simulator":
                    self.register_fact_check(address, content_hash)
                    vote = np.random.choice([truth_value, 1 - truth_value], p=[probability_correct[address], 1 - probability_correct[address]])*10
                    self.vote_on_news(address, content_hash, vote)
                    voted[address] = vote

            print('-' * 50)
            print(f'Round {i}')
            score = round(self.news_items[content_hash].score, 2)
            print(f'Pool {content_hash[:10]}: Truth = {func(truth_value*10)}, Estimated = {func(score)}, Score = {score}')
            for address, user in self.users.items():
                if address != 'Simulator':
                    print(f'{address}: Rewards = {round(user.balance-1, 2)}, Trust = {user.categoryTrustScore["Politics"]}, Voted = {func(10*voted[address])}')
            print('-' * 50)

daap = FactCheckSystem()
daap.simulate_voting(N=10, p=0.7, q=0.3, rounds=10)
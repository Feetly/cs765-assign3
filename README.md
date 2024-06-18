# FactCheckSystem

This Python script simulates a decentralized fact-checking system using classes and objects. The system consists of three main components:

1. **User Model**: Represents users participating in the fact-checking system. Each user has a public address or name, a balance, and a category trust score.

2. **News Model**: Represents news items that are subjected to fact-checking. Each news item has a requester, category, content hash, maximum votes allowed, minimum trust required for voting, registration fee, participation reward, maximum reward, score, and voting-related attributes.

3. **DApp Model (FactCheckSystem)**: Implements the decentralized application (DApp) for the fact-checking system. It manages users and news items, provides functions to add users and request fact-checks, handles user registration and voting on news items, updates scores and confidences, distributes rewards, and simulates the voting environment.

## Code Overview

The code is organized into the following sections:

1. **Imports and Setup**: Import necessary libraries and set up the environment, including seeding the random number generator.

2. **User Model**: Defines the `User` class, which represents users participating in the system.

3. **News Model**: Defines the `News` class, which represents news items subjected to fact-checking.

4. **DApp Model (FactCheckSystem)**: Defines the `FactCheckSystem` class, which implements the decentralized application for the fact-checking system. It includes functions for adding users, requesting fact-checks, registering for news, voting on news, updating scores and confidences, distributing rewards, and simulating the voting environment.

5. **Simulation**: Initializes the `FactCheckSystem` and simulates the voting environment over multiple rounds.

## Usage

To use this script:

1. Run the provided Python code in a suitable environment. (Use command python3 assgn3.py)
2. Adjust the parameters of the `simulate_voting` function call as needed (e.g., number of users, trust probabilities, rounds).
3. Execute the script to simulate the fact-checking process.

The output will display the results of each round of simulation, including the news pool, truthfulness estimates, user rewards, and trust scores.

## Dependencies

The script relies on the following libraries:

- `collections`: Used for defaultdict to initialize category trust scores.
- `hashlib`: Used for generating content hashes.
- `uuid`: Used for generating unique identifiers.
- `numpy`: Used for mathematical computations and random number generation.

Ensure that these libraries are installed in your Python environment before running the script.

## License

This code is provided under the MIT License. You are free to modify and distribute it as needed. See the [LICENSE](link-to-license) file for more details.

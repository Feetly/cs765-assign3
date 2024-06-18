pragma solidity ^0.8.0;

contract FactCheckSystem {
    // Structs
    struct User {
        uint balance;
        mapping(string => uint) categoryTrustScore;
        bool exists;
    }
    
    struct News {
        address requester;
        string category;
        string contentHash;
        uint maxVotes;
        uint minimumTrust;
        uint registrationFee;
        uint participationReward;
        uint maxReward;
        uint score;
        bool finish;
        string status;
        bool valid;
        mapping(address => bool) registered;
        address[] voters;
        int[] votes;
        uint[] confidences;
        mapping(address => int) truthfulness;
    }
    
    // State variables
    mapping(address => User) public users;
    mapping(string => News) public newsItems;

    // Events
    event NewsRegistered(string contentHash, address requester);
    event NewsVoted(string contentHash, address voter, int score);
    event ScoreUpdated(string contentHash, uint newScore);
    event RewardsDistributed(string contentHash);

    // Functions
    function addUser(address _address, uint _balance) external {
        require(!users[_address].exists, "User already exists");
        users[_address] = User(_balance, true);
    }

    function requestFactCheck(address _address, string memory _category, string memory _contentHash, uint _maxVotes, uint _minimumTrust, uint _registrationFee, uint _participationReward, uint _maxReward) external {
        require(!newsItems[_contentHash].valid, "News already exists");
        newsItems[_contentHash] = News(_address, _category, _contentHash, _maxVotes, _minimumTrust, _registrationFee, _participationReward, _maxReward, 5, false, "Tie", true);
        emit NewsRegistered(_contentHash, _address);
    }

    function registerFactCheck(address _address, string memory _contentHash) external {
        require(users[_address].exists, "User does not exist");
        require(!newsItems[_contentHash].registered[_address], "User already registered");
        require(users[_address].categoryTrustScore[newsItems[_contentHash].category] >= newsItems[_contentHash].minimumTrust, "User does not meet minimum trust criteria");
        require(users[_address].balance >= newsItems[_contentHash].registrationFee, "Insufficient balance to register");

        users[_address].balance -= newsItems[_contentHash].registrationFee;
        newsItems[_contentHash].registered[_address] = true;
    }

    function voteOnNews(address _address, string memory _contentHash, int _score) external {
        require(users[_address].exists, "User does not exist");
        require(newsItems[_contentHash].registered[_address], "User not registered for this news");
        require(newsItems[_contentHash].valid && !newsItems[_contentHash].finish, "Voting not allowed");

        newsItems[_contentHash].voters.push(_address);
        newsItems[_contentHash].votes.push(_score);
        uint totalConfidence = users[_address].balance * users[_address].categoryTrustScore[newsItems[_contentHash].category];
        newsItems[_contentHash].confidences.push(totalConfidence);
        users[_address].balance += newsItems[_contentHash].participationReward;

        emit NewsVoted(_contentHash, _address, _score);
        updateScoreConfidences(_contentHash);
    }

    function updateScoreConfidences(string memory _contentHash) internal {
    News storage newsItem = newsItems[_contentHash];

    // Compute the new score
    uint totalScoreWeighted = 0;
    for (uint i = 0; i < newsItem.votes.length; i++) {
        totalScoreWeighted += uint(newsItem.votes[i]) * newsItem.confidences[i];
    }
    newsItem.score = totalScoreWeighted / newsItem.confidences.length;

    // Determine the news status based on the score
    if (newsItem.score > 5) {
        newsItem.status = "Real";
    } else if (newsItem.score < 5) {
        newsItem.status = "Fake";
    } else {
        newsItem.status = "Tie";
    }

    // Define rewards and their reversal only once
    int[11] memory scoreFactors = [-10, -8, -6, -4, -2, 0, 2, 4, 6, 8, 10];
    int[11] memory reverseScoreFactors = [-10, -8, -6, -4, -2, 0, 2, 4, 6, 8, 10];

    // Update each voter's category trust score
    for (uint j = 0; j < newsItem.voters.length; j++) {
        address voter = newsItem.voters[j];
        int vote = newsItem.votes[j];
        int reward;

        // Select the correct reward based on the news status
        if (keccak256(abi.encodePacked(newsItem.status)) == keccak256(abi.encodePacked("Real"))) {
            reward = scoreFactors[vote];
        } else if (keccak256(abi.encodePacked(newsItem.status)) == keccak256(abi.encodePacked("Fake"))) {
            reward = reverseScoreFactors[vote];
        } else {
            reward = 0;
        }

        // Calculate the new score with clamping to the range [0, 100]
        newsItem.truthfulness[voter] = reward * 5; // assuming update_by = 5
    }
}

function distributeRewards(string memory _contentHash) internal {
    News storage newsItem = newsItems[_contentHash];
    int[11] memory scoreFactors = [-10, -8, -6, -4, -2, 0, 2, 4, 6, 8, 10];
    int[11] memory reverseScoreFactors = [-10, -8, -6, -4, -2, 0, 2, 4, 6, 8, 10];

    uint totalConfidence = 0;
    uint totalRewards = 0;

    // Calculate total confidence and total rewards
    for (uint i = 0; i < newsItem.votes.length; i++) {
        totalConfidence += newsItem.confidences[i];
        if (keccak256(abi.encodePacked(newsItem.status)) == keccak256(abi.encodePacked("Real"))) {
            totalRewards += uint(scoreFactors[newsItem.votes[i]]) * newsItem.confidences[i];
        } else if (keccak256(abi.encodePacked(newsItem.status)) == keccak256(abi.encodePacked("Fake"))) {
            totalRewards += uint(reverseScoreFactors[newsItem.votes[i]]) * newsItem.confidences[i];
        }
    }

    // Distribute rewards proportionally
    for (uint j = 0; j < newsItem.voters.length; j++) {
        address voter = newsItem.voters[j];
        uint reward = (newsItem.confidences[j] * totalRewards) / totalConfidence;

        users[voter].balance += reward;
        newsItem.requester.balance -= reward;

        // Update category trust scores
        if (keccak256(abi.encodePacked(newsItem.status)) != keccak256(abi.encodePacked("Tie"))) {
            users[voter].categoryTrustScore[newsItem.category] += newsItem.truthfulness[voter];
            users[voter].categoryTrustScore[newsItem.category] = clamp(users[voter].categoryTrustScore[newsItem.category], 0, 100);
        }
    }

    newsItem.finish = true;
}

function clamp(uint value, uint min, uint max) internal pure returns (uint) {
    if (value < min) return min;
    if (value > max) return max;
    return value;
}

    // Other helper functions can be added here
}

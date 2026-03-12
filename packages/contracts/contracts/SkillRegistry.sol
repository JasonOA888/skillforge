// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/token/ERC20/extensions/ERC20Burnable.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title SKILL Token
 * @dev ERC20 token for SkillForge ecosystem
 */
contract SkillToken is ERC20, ERC20Burnable, Ownable {
    uint256 public constant TOTAL_SUPPLY = 1_000_000_000 * 10**decimals();
    
    constructor() ERC20("SkillForge", "SKILL") Ownable(msg.sender) {
        _mint(msg.sender, TOTAL_SUPPLY);
    }
}

/**
 * @title SkillRegistry
 * @dev Decentralized registry for evolved agent skills
 * 
 * This contract implements the core SkillForge functionality:
 * - Submit skills with stake
 * - Report success/failure
 * - Stake slashing for low-quality skills
 * - Rewards for high-quality skills
 */
contract SkillRegistry {
    struct Skill {
        bytes32 id;
        address creator;
        string name;
        string description;
        bytes gene; // GEP-encoded skill
        uint256 successes;
        uint256 failures;
        uint256 stake;
        uint256 createdAt;
        uint256 lastUsedAt;
        bool active;
    }
    
    struct Validator {
        address addr;
        uint256 stake;
        uint256 validations;
        uint256 correctValidations;
        uint256 lastValidationAt;
        bool active;
    }
    
    // State variables
    SkillToken public immutable token;
    
    mapping(bytes32 => Skill) public skills;
    mapping(address => Validator) public validators;
    mapping(bytes32 => address[]) public skillValidators;
    
    bytes32[] public skillIds;
    address[] public validatorAddresses;
    
    // Configuration
    uint256 public constant MIN_SKILL_STAKE = 100 * 10**18; // 100 SKILL
    uint256 public constant MIN_VALIDATOR_STAKE = 1000 * 10**18; // 1000 SKILL
    uint256 public constant SUCCESS_THRESHOLD = 80; // 80% success rate required
    uint256 public constant SLASH_PERCENTAGE = 10; // 10% stake slashed on failure
    uint256 public constant REWARD_PERCENTAGE = 1; // 1% of stake as reward
    
    address public owner;
    
    // Events
    event SkillSubmitted(bytes32 indexed skillId, address indexed creator, string name, uint256 stake);
    event SkillReported(bytes32 indexed skillId, address indexed reporter, bool success);
    event SkillSlashed(bytes32 indexed skillId, uint256 amount, string reason);
    event ValidatorRegistered(address indexed validator, uint256 stake);
    event ValidationSubmitted(bytes32 indexed skillId, address indexed validator, bool approved);
    event RewardsDistributed(bytes32 indexed skillId, uint256 amount);
    
    // Modifiers
    modifier onlyOwner() {
        require(msg.sender == owner, "Not owner");
        _;
    }
    
    modifier skillExists(bytes32 skillId) {
        require(skills[skillId].id != bytes32(0), "Skill not found");
        _;
    }
    
    modifier skillActive(bytes32 skillId) {
        require(skills[skillId].active, "Skill not active");
        _;
    }
    
    constructor(address _token) {
        token = SkillToken(_token);
        owner = msg.sender;
    }
    
    /**
     * @dev Submit a new skill to the registry
     * @param name Skill name
     * @param description Skill description
     * @param gene GEP-encoded skill data
     */
    function submitSkill(
        string calldata name,
        string calldata description,
        bytes calldata gene
    ) external returns (bytes32) {
        require(bytes(name).length > 0, "Name required");
        require(gene.length > 0, "Gene required");
        
        bytes32 skillId = keccak256(abi.encodePacked(name, msg.sender, block.timestamp));
        
        // Transfer stake
        require(token.transferFrom(msg.sender, address(this), MIN_SKILL_STAKE), "Stake transfer failed");
        
        skills[skillId] = Skill({
            id: skillId,
            creator: msg.sender,
            name: name,
            description: description,
            gene: gene,
            successes: 0,
            failures: 0,
            stake: MIN_SKILL_STAKE,
            createdAt: block.timestamp,
            lastUsedAt: 0,
            active: true
        });
        
        skillIds.push(skillId);
        
        emit SkillSubmitted(skillId, msg.sender, name, MIN_SKILL_STAKE);
        
        return skillId;
    }
    
    /**
     * @dev Report a skill usage result
     * @param skillId Skill ID
     * @param success Whether the skill succeeded
     * @param contextHash Hash of usage context (for verification)
     */
    function reportSkillUsage(
        bytes32 skillId,
        bool success,
        bytes32 contextHash
    ) external skillExists(skillId) skillActive(skillId) {
        Skill storage skill = skills[skillId];
        
        if (success) {
            skill.successes += 1;
            
            // Reward creator
            uint256 reward = (skill.stake * REWARD_PERCENTAGE) / 100;
            if (token.balanceOf(address(this)) >= reward) {
                token.transfer(skill.creator, reward);
                emit RewardsDistributed(skillId, reward);
            }
        } else {
            skill.failures += 1;
            
            // Check if skill should be slashed
            uint256 totalUses = skill.successes + skill.failures;
            if (totalUses >= 10) {
                uint256 successRate = (skill.successes * 100) / totalUses;
                
                if (successRate < SUCCESS_THRESHOLD) {
                    // Slash stake
                    uint256 slashAmount = (skill.stake * SLASH_PERCENTAGE) / 100;
                    skill.stake -= slashAmount;
                    token.burn(slashAmount);
                    
                    emit SkillSlashed(skillId, slashAmount, "Low success rate");
                    
                    // Deactivate if stake too low
                    if (skill.stake < MIN_SKILL_STAKE / 2) {
                        skill.active = false;
                    }
                }
            }
        }
        
        skill.lastUsedAt = block.timestamp;
        
        emit SkillReported(skillId, msg.sender, success);
    }
    
    /**
     * @dev Register as a validator
     */
    function registerValidator() external {
        require(validators[msg.sender].addr == address(0), "Already registered");
        
        // Transfer stake
        require(token.transferFrom(msg.sender, address(this), MIN_VALIDATOR_STAKE), "Stake transfer failed");
        
        validators[msg.sender] = Validator({
            addr: msg.sender,
            stake: MIN_VALIDATOR_STAKE,
            validations: 0,
            correctValidations: 0,
            lastValidationAt: block.timestamp,
            active: true
        });
        
        validatorAddresses.push(msg.sender);
        
        emit ValidatorRegistered(msg.sender, MIN_VALIDATOR_STAKE);
    }
    
    /**
     * @dev Submit validation for a skill
     * @param skillId Skill ID
     * @param approved Whether validator approves the skill
     * @param reasoningHash Hash of validation reasoning
     */
    function submitValidation(
        bytes32 skillId,
        bool approved,
        bytes32 reasoningHash
    ) external skillExists(skillId) {
        require(validators[msg.sender].active, "Not an active validator");
        
        Validator storage validator = validators[msg.sender];
        validator.validations += 1;
        validator.lastValidationAt = block.timestamp;
        
        skillValidators[skillId].push(msg.sender);
        
        emit ValidationSubmitted(skillId, msg.sender, approved);
    }
    
    /**
     * @dev Get skill details
     */
    function getSkill(bytes32 skillId) external view skillExists(skillId) returns (
        string memory name,
        string memory description,
        address creator,
        uint256 successes,
        uint256 failures,
        uint256 stake,
        bool active
    ) {
        Skill storage skill = skills[skillId];
        return (
            skill.name,
            skill.description,
            skill.creator,
            skill.successes,
            skill.failures,
            skill.stake,
            skill.active
        );
    }
    
    /**
     * @dev Get skill success rate
     */
    function getSkillSuccessRate(bytes32 skillId) external view skillExists(skillId) returns (uint256) {
        Skill storage skill = skills[skillId];
        uint256 total = skill.successes + skill.failures;
        
        if (total == 0) return 0;
        return (skill.successes * 100) / total;
    }
    
    /**
     * @dev Get total number of skills
     */
    function getSkillCount() external view returns (uint256) {
        return skillIds.length;
    }
    
    /**
     * @dev Get top skills by success rate
     */
    function getTopSkills(uint256 limit) external view returns (bytes32[] memory) {
        uint256 count = skillIds.length;
        if (limit > count) limit = count;
        
        bytes32[] memory topSkills = new bytes32[](limit);
        
        // Simple implementation - return first N skills
        // In production, would sort by success rate
        for (uint256 i = 0; i < limit; i++) {
            topSkills[i] = skillIds[i];
        }
        
        return topSkills;
    }
    
    /**
     * @dev Withdraw validator stake
     */
    function withdrawValidatorStake() external {
        Validator storage validator = validators[msg.sender];
        require(validator.active, "Not an active validator");
        require(block.timestamp >= validator.lastValidationAt + 30 days, "Cooldown period");
        
        uint256 stake = validator.stake;
        validator.active = false;
        validator.stake = 0;
        
        token.transfer(msg.sender, stake);
    }
    
    /**
     * @dev Withdraw skill stake (creator only)
     */
    function withdrawSkillStake(bytes32 skillId) external skillExists(skillId) {
        Skill storage skill = skills[skillId];
        require(msg.sender == skill.creator, "Not creator");
        require(!skill.active, "Skill still active");
        require(block.timestamp >= skill.lastUsedAt + 90 days, "Cooldown period");
        
        uint256 stake = skill.stake;
        skill.stake = 0;
        
        token.transfer(msg.sender, stake);
    }
    
    /**
     * @dev Update owner
     */
    function setOwner(address newOwner) external onlyOwner {
        require(newOwner != address(0), "Invalid address");
        owner = newOwner;
    }
}

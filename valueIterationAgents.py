# valueIterationAgents.py
# -----------------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


# valueIterationAgents.py
# -----------------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


import mdp, util

from learningAgents import ValueEstimationAgent
import collections


class ValueIterationAgent(ValueEstimationAgent):
    """
        * Please read learningAgents.py before reading this.*

        A ValueIterationAgent takes a Markov decision process
        (see mdp.py) on initialization and runs value iteration
        for a given number of iterations using the supplied
        discount factor.
    """

    def __init__(self, mdp, discount=0.9, iterations=100):
        """
          Your value iteration agent should take an mdp on
          construction, run the indicated number of iterations
          and then act according to the resulting policy.

          Some useful mdp methods you will use:
              mdp.getStates()
              mdp.getPossibleActions(state)
              mdp.getTransitionStatesAndProbs(state, action)
              mdp.getReward(state, action, nextState)
              mdp.isTerminal(state)
        """
        self.mdp = mdp
        self.discount = discount
        self.iterations = iterations
        self.values = util.Counter()  # A Counter is a dict with default 0
        self.runValueIteration()

    def runValueIteration(self):
        # Write value iteration code here
        "*** YOUR CODE HERE ***"

        # print(self.values)
        # # {}
        # print(self.mdp.getStates())
        # # ['TERMINAL_STATE', (0, 0), (0, 1), (0, 2)]
        # for state in self.mdp.getStates() :
        #     print(self.mdp.getPossibleActions(state))
        # # ('exit',)
        # # ('north', 'west', 'south', 'east')
        # # ('exit',)
        # # (0, 1)
        # print(self.mdp.getStates()[2])
        # print(self.mdp.getTransitionStatesAndProbs(self.mdp.getStates()[2], self.mdp.getPossibleActions(self.mdp.getStates()[2])[2]))
        # # [((0, 0), 1.0), ((0, 1), 0.0)]
        for state in self.mdp.getStates():
            if not self.mdp.isTerminal(state):
                self.values[state] = 0
            # else:
            #     print("terminal")
            #     print(self.values[state])

        for i in range(self.iterations):
            newValues = util.Counter()
            for state in self.mdp.getStates():
                value = float('-inf')
                for action in self.mdp.getPossibleActions(state):  # ()
                    qValue = self.computeQValueFromValues(state, action)
                    if qValue > value:
                        value = qValue
                        newValues[state] = value
            self.values = newValues

    def getValue(self, state):
        """
          Return the value of the state (computed in __init__).
        """
        return self.values[state]

    def computeQValueFromValues(self, state, action):
        """
          Compute the Q-value of action in state from the
          value function stored in self.values.
        """
        "*** YOUR CODE HERE ***"
        nextStates = self.mdp.getTransitionStatesAndProbs(state, action)
        sum = 0
        for nextState in nextStates:
            sum += nextState[1] * (
                        self.mdp.getReward(state, action, nextState) + self.discount * self.values[nextState[0]])
        return sum
        # util.raiseNotDefined()

    def computeActionFromValues(self, state):
        """
          The policy is the best action in the given state
          according to the values currently stored in self.values.

          You may break ties any way you see fit.  Note that if
          there are no legal actions, which is the case at the
          terminal state, you should return None.
        """
        "*** YOUR CODE HERE ***"
        if self.mdp.isTerminal(state):
            return None
        maxAction = self.mdp.getPossibleActions(state)[0]
        maxValue = float('-inf')
        for action in self.mdp.getPossibleActions(state):
            value = self.computeQValueFromValues(state, action)
            if value > maxValue:
                maxValue = value
                maxAction = action
        return maxAction
        # util.raiseNotDefined()

    def getPolicy(self, state):
        return self.computeActionFromValues(state)

    def getAction(self, state):
        "Returns the policy at the state (no exploration)."
        return self.computeActionFromValues(state)

    def getQValue(self, state, action):
        return self.computeQValueFromValues(state, action)


class PrioritizedSweepingValueIterationAgent(ValueIterationAgent):
    """
        * Please read learningAgents.py before reading this.*

        A PrioritizedSweepingValueIterationAgent takes a Markov decision process
        (see mdp.py) on initialization and runs prioritized sweeping value iteration
        for a given number of iterations using the supplied parameters.
    """

    def __init__(self, mdp, discount=0.9, iterations=100, theta=1e-5):
        """
          Your prioritized sweeping value iteration agent should take an mdp on
          construction, run the indicated number of iterations,
          and then act according to the resulting policy.
        """
        self.theta = theta
        ValueIterationAgent.__init__(self, mdp, discount, iterations)

    def runValueIteration(self):
        "*** YOUR CODE HERE ***"
        """Compute predecessors of all states."""
        predecessors = {state: set() for state in self.mdp.getStates()}
        for state in self.mdp.getStates():
            for action in self.mdp.getPossibleActions(state):
                for nextState, prob in self.mdp.getTransitionStatesAndProbs(state, action):
                    if prob > 0:
                        # print("state: ", state)
                        predecessors[nextState].add(state)

        """Initialize an empty priority queue."""
        priorityQueue = util.PriorityQueue()

        "For each non-terminal state s, do something"
        for state in self.mdp.getStates():
            if self.mdp.isTerminal(state):
                continue
            maxQValue = float('-inf')
            for action in self.mdp.getPossibleActions(state):
                maxQValue = max(maxQValue, self.computeQValueFromValues(state, action))
            diff = abs(self.values[state] - maxQValue)
            priorityQueue.push(state, -diff)

        "For iteration in 0, 1, 2, ..., self.iterations - 1, do something"
        for it in range(self.iterations):
            if priorityQueue.isEmpty():
                break
            state = priorityQueue.pop()

            if not self.mdp.isTerminal(state):
                value = float('-inf')
                for action in self.mdp.getPossibleActions(state):
                    # print("1: ", state, action)
                    qValue = self.computeQValueFromValues(state, action)
                    if qValue > value:
                        value = qValue
                # print(self.values[state], value)
                self.values[state] = value

            # For each predecessor p of s, do something
            for preState in predecessors[state]:
                # print(preState)
                maxQValue = float('-inf')
                for action in self.mdp.getPossibleActions(preState):
                    # print("2: ", preState, action)
                    QValue = self.computeQValueFromValues(preState, action)
                    if QValue > maxQValue:
                        maxQValue = QValue
                # print(maxQValue)
                diff = abs(self.values[preState] - maxQValue)
                if diff > self.theta and preState not in priorityQueue.heap:
                    priorityQueue.update(preState, -diff)

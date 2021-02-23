''' An example of learning a Deep-Q Agent on Texas No-Limit Holdem
'''

import tensorflow as tf
import os

import rlcard
from rlcard.agents import DQNAgent
from rlcard.agents import RandomAgent
from rlcard.agents import NolimitholdemHumanAgent
from rlcard.utils import set_global_seed, tournament
from rlcard.utils import Logger




# Make environment
env = rlcard.make('no-limit-holdem', config={'record_action': True,  "game_over_print": False})
eval_env = rlcard.make('no-limit-holdem', config={'record_action': True, "game_over_print": False})

# Set the iterations numbers and how frequently we evaluate the performance
evaluate_every = 200
evaluate_num = 2000
episode_num = 10000

# The intial memory size
memory_init_size = 1000

# Train the agent every X steps
train_every = 1

# The paths for saving the logs and learning curves
log_dir = './experiments/nolimit_holdem_dqn_result/'

# Set a global seed
# set_global_seed(0)

with tf.Session() as sess:

    # Initialize a global step
    global_step = tf.Variable(0, name='global_step', trainable=False)

    with tf.variable_scope('agent1'):
        # Set up the agents
        agent1 = DQNAgent(sess,
                         scope='dqn',
                         action_num=env.action_num,
                         replay_memory_init_size=memory_init_size,
                         train_every=train_every,
                         state_shape=env.state_shape,
                         mlp_layers=[1280, 1280])

    with tf.variable_scope('agent2'):
        agent2 = DQNAgent(sess,
                         scope='dqn',
                         action_num=eval_env.action_num,
                         replay_memory_init_size=memory_init_size,
                         train_every=train_every,
                         state_shape=eval_env.state_shape,
                         mlp_layers=[512, 512])

    random_agent = RandomAgent(action_num=eval_env.action_num)
    human_agent = NolimitholdemHumanAgent(eval_env.action_num)

    env.set_agents([agent1, agent2])
    eval_env.set_agents([agent1, agent2])

    # Initialize global variables
    sess.run(tf.global_variables_initializer())

    # Init a Logger to plot the learning curve
    logger = Logger(log_dir)

    for episode in range(episode_num):

        # Generate data from the environment
        trajectories, _ = env.run(is_training=True)

        # Feed transitions into agent memory, and train the agent
        for ts1 in trajectories[0]:
            agent1.feed(ts1)

        for ts2 in trajectories[1]:
            agent2.feed(ts2)

        # Evaluate the performance. Play with random agents.
        if episode % evaluate_every == 0:
            logger.log_performance(env.timestep, tournament(eval_env, evaluate_num)[0])

    env.set_agents([agent1, random_agent])
    eval_env.set_agents([agent1, random_agent])
    # env.game_over_print = True
    # eval_env.game_over_print = True

    for episode in range(episode_num//4):

        # Generate data from the environment
        trajectories, _ = env.run(is_training=False)
        # Evaluate the performance. Play with random agents.
        if episode % evaluate_every == 0:
            logger.log_performance(env.timestep, tournament(eval_env, evaluate_num)[0])

    env.set_agents([agent2, random_agent])
    eval_env.set_agents([agent2, random_agent])

    for episode in range(episode_num//4):

        # Generate data from the environment
        trajectories, _ = env.run(is_training=False)
        # Evaluate the performance. Play with random agents.
        if episode % evaluate_every == 0:
            logger.log_performance(env.timestep, tournament(eval_env, evaluate_num)[0])

    # Close files in the logger
    logger.close_files()

    # Plot the learning curve
    logger.plot('DQN')

    # Save model
    save_dir = 'models/nolimit_holdem_dqn'
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    saver = tf.train.Saver()
    saver.save(sess, os.path.join(save_dir, 'model'))

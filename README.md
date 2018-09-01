Issue : How to optimize staff scheduling for 18 bakeries taking into account constraints such as labor laws, staff leave and sick days, preferences, etc...

This is a constrained combinatorial optimization problem.
I will attempt to solve it by implementing a genetic algorithm.

The chromosomes are implemented as schedule objects which main attribute is a list of assignment objects. A schedule covers a week.

Since I could not come up with a good way of representing the chromosomes as binary sequences, mutations are implemented as follows. They affect the assignment objects in six possible different ways :
    - Extend : adds 15 minutes to the assignment, if two assignments conflict, the mutated one has priority
    - Reduce : -15 minutes
    - Split : splits an assignment in two down the middle
    - Merge : merges two touching assignments
    - Swap : swaps the workers on two assignments
    - Change : changes the worker on an assignment


Fitness is determined as follows :
There are mutiple factors taken into account in order to determine fitness, such as :
    - Remaining available working hours for the week
    - Max consecutive worked hours
    - Job descrition
    - Prefered bakery
    - Prefered schedule 
    - ...
A config file determines bonus and penalties for respecting or not each of the constraints. The fitness is the sum of these scores

For crossovers, the days are randomly swapped between the two chromosomes.

Json files are used as inputs and outputs to easily interface with the web app developped in parallel.

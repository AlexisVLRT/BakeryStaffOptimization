Issue : How to optimize staff scheduling for 18 bakeries taking into account constraints such as labor laws, staff leave and sick days, preferences, etc...

This is a constrained combinatorial optimization problem.
I will attempt to solve it by implementing a genetic algorithm.

We have 2 types of constraints : 

  - Hard constraints : 
    - Remaining available working hours for the week
    - Max consecutive worked hours
    - ...
    
  - Soft constraints : 
    - Job descrition
    - Prefered bakery
    - Prefered schedule 
    - ...
    
A solution not satisfying all of the hard constraints would be discarded from the solution set

The fitness score will likely be a linear combination of weighted factors derived from the soft constraints. The weights are to be determined with the client.

It is likely that this program will have Json files as inputs and outputs to easily interface with the web app developped in parallel.

---
layout: post
title: Optimizing a Chemical Reaction with Bayesian Optimization
date: 2025-10-30 18:50 +0100
categories: [Projects, toyExample]
tags: [machine learning, baysian optimization, python]
published: false
---

{% assign image_path = "/assets/images/projects/bayesianOptimizationChemistry/" %}




## Table of contents
  - [Table of contents](#table-of-contents)
  - [Background](#background)
  - [The problem to optimize](#the-problem-to-optimize)
  - [Solving the optimization with Bayesian](solving-the-optimization-with-bayesian)


## Background

A few years ago during my Master's, I followed a course on advanced optimization techniques. As the final project, we had to find an optimization problem and implement a solution to solve it in MATLAB. At that time, I really wanted to have my own implementation of a Genetic Algorithm (GA) but didn't have any specific problem in mind. Luckily, one of my classmates had a chemical reaction to optimize from their work. So we teamed up, and I implemented a GA to optimize the reaction conditions.

The time has passed since then, and Bayesian optimization have become a field that I want to tackle. In this notebook, I will try to tackle exactly the same optimization problem, but using Bayesian optimization. 

## The problem to optimize

The problem involved the production of a chemical molecule, thanks to a chemical reaction. The chemical reaction was perfomed on a catalytic bed in microreactor. Our goal was to perform an efficient reaction with the best possible yield and costs.

Therefore, multiple parameters with potential influences on the yield were selected as:

- concentration of catalyst [%/mMol]
- concentration of main reagent [mol/L]
- temperature [°C], feed rate [L/min]
- mixing rate [RPM]

 Thanks to a DOE and the required Anova analysis and normal probability plot, the actual effect of these parameters and their interactions with each other on the chemical reaction were identified and thus, only three of them and their interactions were kept to define the objective function:

- Concentration of main reagent [mol/L]
- Concentration of catalyst [ % / mmol]
- temperature [°C]

Futhermore, the optimization was subject to the following constraints:

- The reaction yield has to be higher than 60%
- Concentration of catalyst has to be between 0 and 3 mMol
- Concentration of reagent has to be between 0 and 3 mMol
- Temperature has to be between 30 and 60°C
- Heating cost is 0.20 CHF per °C
- reagent cost is 22 CHF / mol/L
- catalyst cost is 10 CHF / mmol
- Spend maximum 1 CHF per yield percentage
- all three parameters where reduced centred between [-1 and 1]

The following equation was build to represent the yield:
$$
g = 91.99 + 2.81x + -1.099y +2.81z - 7.99x^{2} - 16.64y^{2} -7.99z^{2} - 5.34xy - 5.34yz;
$$

and the following equation to represent the cost:
$$
h = 10 * (3-\frac{(1-x)*3}{2}) + 0.2(60-\frac{(1-y)*30}{2}) + 22(3-\frac{(1-z)*3}{2});
$$
finally the objective function was defined as:
$$
f = g-h
$$
with:
- x = catalyst concentration [mmol/L]
- y = Temperature [°C]
- z = reagent concentration [mol/L]

## Solving the optimization with Bayesian

As stated in the background of this post, our goal will be to solve the previously shown optimization problem using Bayesian optimization. However, we won't tackle the Bayesian optimization from scratch, instead we will use the [bayesian optimization python library](https://bayesian-optimization.github.io/BayesianOptimization/3.1.0/).

### Installing the library

First in a dedicated virtual environment, we can install the library with 

```python
pip install bayesian-optimization
``` 

From there we will need to express our problem in a way the library can understand it.

### Specifying the function to optimize

Bayesian optimization is like most optimization algorithm, we have to define a function to optimize.

Luckly we already have one! Following the [provided example](https://bayesian-optimization.github.io/BayesianOptimization/3.1.0/basic-tour.html) and using our definition we can define the **yield** and **cost** functions.


```python
def yieldfunction(x, y, z):
"""
Yield of the chemical reaction. The goal is to maximize this value
"""


    return 91.99 + 2.81*x + -1.099*y + 2.81*z - 7.99*(x**2) - 16.64*(y**2) -7.99*(z**2) -5.34*x*y -5.34*y*z
```

```python
def costfunction(x, y, z):
"""
Cost of the chemical reaction. The goal is to minimize this value
"""

    return 10 * (3-(1-x)*3/2) + 0.2 * (60 - (1-y)*30/2) + 22 * (3 - (1-z)*3/2)
```

following our previous logic we then can get our function to optimize:

```python
def function_to_optimize(x, y, z):

    yield_ = yieldfunction(x,y,z)
    cost_ = costfunction(x,y,z)

    return yield_ - cost_
```

### Considering the constraints

That could be it. However, we have some constraints to apply. We can code the single constraints on the value directly in the objective function.

```python
pbounds = {'x':(-1,1), 'y':(-1,1), 'z':(-1,1)}
```

We also said that the yield should be at least 60%. We can use the previously created yieldfunction for that and apply a limit.

```python

constraint_limit = 0.6

constraint = NonlinearConstraint(yieldfunction, constraint_limit, 1)
```

### Reversing the scaling

As stated in the problem definition, the parameters are already scaled and centered to be in the range [-1, 1]. We would like to have a function that takes a result in and return the raw parameters.

```python
def reverse_scaling(result):

    new_result = result.copy()

    new_result["params"]["x"] = 1.5*(result["params"]["x"]+1)
    new_result["params"]["y"] = 15*(result["params"]["y"]+1)+30
    new_result["params"]["z"] = 1.5*(result["params"]["z"]+1)

    return new_result
```


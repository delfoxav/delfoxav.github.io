---
# the default layout is 'page'
icon: fas fa-info-circle
order: 4
---
![Desktop View](/assets/images/me.jpg){: width="972" height="589" .w-50 .right}
Hey There!  
I'm Xavier, a Life Sciences engineer, currently  {% assign birth_year = 1996 %}{% assign birth_month = 11 %}{% assign birth_day = 12 %}
{% assign now = 'now' | date: '%s' %}
{% assign birthdate = birth_year | append: '-' | append: birth_month | append: '-' | append: birth_day | date: '%s' %}
{% assign age = now | minus: birthdate | divided_by: 31556952 %}
{{ age }} years old.

I am kind of a free electron some might say. I old a Bachelor's degree in Life Sciences Technology from the University of Applied Sciences of Western Switzerland (HES-SO) and a Master's degree in Computational Life Sciences from the University of Applied Sciences of Zurich (ZHAW).

Throughout my studies, I developed a strong interest in process control and automation, which led me to my Bachelor work at the Technical University of Vienna (TU Wien) in the field of process analytical technologies. I then continued my studies at the ZHAW, where I focused on the application of machine learning in life sciences. My Master's thesis was conducted in collaboration with the company I was working for at that time. It consisted of integrating an electronic nose to a multi-bioreactors system to monitor the fermentation process of a cell culture and serve as an early warning system for process deviations.

I am currently working as data scientist lead for a project in Fintech for a big trading company. I am responsible for the development of our machine learning models and tutoring younger data scientists on how to develop and deploy them. I am also responsible for the development of our data pipeline and the integration of our models into the production environment.

During my free time, I tend to "play" with whatever I can think of. Like building an incubator with an old bulb led, finding crazy idea to connect a raspberry pi to or even creating my personal ML home lab. So far, my main issue is that I probably don't have enough time to do everything I want.

On the long time horizon, I would like to start a PhD in the field of machine learning and life sciences. I am particularly interested in the application of machine learning in the field of process analytical technologies and the development of new algorithms for the analysis of complex data sets.

I decided to create this website to share my projects and ideas with the world. I hope you will find it interesting and that it will inspire you to do your own projects. If you have any questions or suggestions, please feel free to contact me.

    
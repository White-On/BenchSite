# GeneratedVelocity

## What is GeneratedVelocity ▶️

GeneratedVelocity is a platform designed to **compare the performance of different libraries and frameworks**. It
provides a detailed report of each library's speed, precision, and other parameters, making it easier for
developers to choose the best library for their project.

You can access the following information on this pages too with extra details : https://white-on.github.io/BenchSite/

## GeneratedVelocity Brief explained 📰

GeneratedVelocity is designed to automate the process of comparing and testing different libraries. To
achieve this, the test are written in configuration files, then given to GeneratedVelocity. The tests are executed in a
controlled environment, and the results are then analyzed and compiled into easy-to-read reports. These reports
are output as HTML files structured and then published on dedicated GitHub pages, where users can access them and see how the different libraries perform
in a variety of scenarios. By automating the testing process, the website enables developers to save time and
effort when evaluating libraries, and helps them make informed decisions.

<img src="about_page/how_it_works.png" width="100%" alt="graph explaning the structure of the directory needed to create a benchmark">

## First steps 👣
           
First of all, you'll need to get the project on your computer. To do so, you can either download the project
directly from GitHub, or clone it using the following command:

`git clone https://github.com/White-On/BenchSite`

Once you have the project on your computer, you can start creating your own benchmark. To do so, you'll need to
create a new directory with a specific structure. The directory should contain 3 subdirectories: **targets**,
**themes**, and **site**. The **targets** directory contains the configuration files for the libraries
you want to test. The **themes** directory contains the configuration files for the tests you want to run. The
**site** directory contains the configuration files for the website. 


<details>
    <summary>For more information on the structure of the directory</summary>
    <img src="about_page/infrastructure_explanations.png" width="100%" alt="graph explaning the structure of the directory needed to create a benchmark">
</details>

## Setup and Launch 🚀
Once you've installed the project and create your benchmark, we're going to need to install all the required
libraries. We recommend to use a virtual environment.

To ease your install, there is a **Makefile**. To see available commands run:

`make help`

To install all the required libraries, run:

`make install`

You're now ready to launch your benchmark. Depending on where your benchmark is located, either locally or
online, on a github repository, or if you want to publish the results on a github page, you'll need to run a
different command. To see available commands run:

`python main.py --help`

## How we compare the targets 🤔
For the time being, we decided to compare results base on the **Lexicographic Maximal Ordering Algorithm (LexMax)**.
Each ranking is based on the number of wins, ties, and losses of each library. The target with the highest
number of wins is ranked first, followed by the library with the second-highest number of wins, and so on. In
the case of a tie, both libraries are ranked equally. The algorithm does not take into account the magnitude of the wins or losses, only the number of them.

We use it to compare all the data generated by the benchmarking process. For example, we run a task on a set of
libraries, and we get the results. Each result is compared to the other result with the same argument, and we get a
score for each argument. On the entire task, we get a vector of score for each library. We use the LexMax
algorithm to compare the vector of score for each library and we get a ranking of the libraries for that task.
We do this for each task and repeat it for the theme and the global ranking.

## How to contribute ✍️
The benchmark website is an open-source project, and contributions from the community are welcome. To contribute,
users can fork the project on GitHub, make changes to the code, and submit a pull request. Users can also
contribute by reporting bugs, suggesting improvements, or sharing their benchmarking results.    


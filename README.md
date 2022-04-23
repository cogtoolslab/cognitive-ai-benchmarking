# Cognitive-AI Benchmarking (CAB)
Project Template for Implementing Human Behavioral Experiments

<!-- ALL-CONTRIBUTORS-BADGE:START - Do not remove or modify this section -->
[![All Contributors](https://img.shields.io/badge/all_contributors-8-orange.svg?style=flat-square)](#contributors-)
<!-- ALL-CONTRIBUTORS-BADGE:END -->

1. [Overview](#overview)
2. [Installation](#installation)
3. [Implementing your experiment](#implementing-your-experiment)
4. [Contributors](#contributors)

-----
# Overview

The purpose of this repo is to provide a starting point for researchers planning to conduct a Cognitive-AI Benchmarking (CAB) project. 
A CAB project will typically combine three elements: (1) stimulus generation; (2) human behavioral experiments; (3) analysis of behavioral data and comparison to model outputs. 

The examples here are adapted from the [Physion project](https://github.com/cogtoolslab/physics-benchmarking-neurips2021).

## Repo organizatoin
It contains several subdirectories that will contain standard components of the human behavioral experimental infrastructure that will support a variety of Cognitive-AI Benchmarking projects.

- `analysis` (aka `notebooks`): This directory will typically contain jupyter/Rmd notebooks for exploratory code development and data analysis.
- `experiments`: If this is a project that will involve collecting human behavioral data, this is where you want to put your experimental code. If this is a project that will involve evaluation of a computational model's behavior on a task, this is also where you want to put the task code.
- `results`: This directory is meant to contain "intermediate" results of your computational/behavioral experiments. It should minimally contain two subdirectories: `csv` and `plots`. So `/results/csv/` is the path to use when saving out `csv` files containing tidy dataframes. And `/results/plots/` is the path to use when saving out `.pdf`/`.png` plots, a small number of which may be then polished and formatted for figures in a publication. *Important: Before pushing any csv files containing human behavioral data to a public code repository, triple check that these data files are properly anonymized. This means no bare AMT Worker ID's.* It is generally recommended that "raw" behavioral data be stored in a database rather than as part of this repo.
- `stimuli`: This directory is meant to contain any download/preprocessing scripts for data that are _inputs_ to this project. For many projects, these will be images. This is also where you want to place any scripts that will upload your data to our `stimuli`  MongoDB database and any image data to Amazon S3 (so that it has a semi-permanent URL you can use to insert into your web experiment.)

## Different ways to use this repo

The examples in this repo have been organized in a modular fashion: you can either use  the entire stack or mix and match components of this stack with other tools if you prefer.

- Level 1: Example client-side JavaScript code for prototyping tasks quickly
- Level 2: Example integration with node.js server for hosting your experiment and writing data to file without a database
- Level 3: Example integration with an already running mongodb server

## The central concepts in this repo

When working on a project, you will oftentimes run many different experiments that are related to each other. We propose a way of thinking about these related experiments that makes keeping track of them easy.

At the top of the hierarchy is the **project**—for example *Physion*. This corresponds to a repository.

There are **datasets**—for example one particular scenario from the Physion dataset, eg. *dominoes*.

The questions that we might ask of these datasets might change: we might ask whether people can predict the outcome a physical interaction (Object Contact Prediction Task, OCP) or whether they find the same video interest. This is what we call a **task**.
Each task will usually have a different client front end in the `experiments/[task]` directory.

A particular **experiment** is a combination of a dataset and a task. For example, in this repository we show the `dominoes_OCP`. The convention for naming experiments is to use the dataset name followed by a _ followed by the task name.
Which stimuli are passed to a task are usually determined by an URL parameter when the experiment is loaded in the user's browser.

For each experiment, there are small changes that the researcher might make, for example showing the videos for longer. These different versions of an experiment are called **iterations**. 

| Concept | Example | Correspondence | 
| --- | --- | --- |
| **project** | Physion | Repository, name of database ([proj]_stims`,[proj]_resp`) |
| **dataset** | dominoes | *lives somewhere else* |
| **task** | OCP | subfolders of `experiments/` |
| **experiment** | dominoes_OCP | collection in `[proj]_stims` and `[proj]_resp` database |
| **iteration** | iteration_1 | field of record in database |

## Database organization

A mongoDB instance is ran by an organization (ie. your lab). 
For each project, there are two databases: `[proj]_stims` and `[proj]_resp`. 
In the `[proj]_stims` database (for stimuli, what is shown to the user), each collection determines a set of stimuli in a certain order that can be shown to a user ("sesion template"). 
While running an experiment, this database will only be read from.

The data that is collected during an experiment goes into the `[proj]_resp` database (for responses, which we get from the user).
There, each document corresponds to a single event that we care about, such as the user giving a single rating to a single video. Each document contains field that allow us to group it into experiments and iterations, etc.
While running an experiment, this database will only be written into.

# Installation

## Configruation

To configure your environment for using CAB, you will need to create a config file called `.cabconfig`. 
The purpose of this file is to define variables that apply to all of your CAB projects (e.g., username and password to access the mongo database).
By default, this config file should be saved as a hidden file in your home directory, with file path `HOME/.cabconfig`.
If you want to store this file in a different location, you can specify the path by setting the enviroment variable `CAB_CONFIGFILE` to the desired path.

Here is an example of a `.cabconfig` file, which follows the [INI](https://en.wikipedia.org/wiki/INI_file) file format.

```
[DB]
password=mypassword #required
username=myusername #optional, default if unspecified is "cabUser"
host=myhost #optional, default if unspecified is 127.0.0.1
port=myport #optional, default if unspecified is 27017
```
## Client-side tools
- [jsPsych](https://www.jspsych.org/7.2/)

## Server-side tools
- [node.js](https://nodejs.org/en/) 
- [mongodb](https://www.mongodb.com/)

# Implementing your experiment

## Prepare your stimuli
This repo assumes that you have already generated your stimuli elsewhere. 
Once you've done this, check out this [README](stimuli/README.md).

## Design your task user interface
Check out this [README](experiments/README.md).

## Configure your experiment according to research design
- creating and uploading the experiment config (including projName, expName, iterationName)
- splitting and batching trials into sessions
- defining the criteria by which a session is valid.

## launching your experiment on a web server

If you want to test your experiment on the server but don't want to worry about MongoDB, you can do the following:

First, create a directory in the `stimuli` folder specified by your database name and collection name (e.g. `stimuli/BACH/dominoes/`). 

Then run the `generate_metadata.ipynb` jupyter notebook to generate your stimuli and save the is as a `.json` file in the directory you just created.

Next, run `node app.js --gameport PORT --local_store`. This needs to be ran from the experiments folder (ie. do `cd experiments` before running this).

This should be it! When you try out the experiment, your data will be saved on the server (as opposed to MongoDB) in the direcotry: `results/databaseName_resp/collectionName.csv` (e.g. `results/BACH_resp/dominoes.csv`) that you can check and help you debug.

## Validate data input
- Once you launch the experiment, test it out and verify that your stimuli are being read in properly from mongodb.

## Validate data output
- Next, you will want to verify that all trial metadata and response variables are being written out properly to mongodb. Here is an [example notebook](analysis/analyze_BACH_dominoes.ipynb) you can adapt that guides you through the standard steps involved in fetching & analyzing your data, including constructing exploratory visualizations of response variables w.r.t. key axes of variation in your stimuli.
- TODO: In a future release of CAN, we will include a tool that enables you to monitor  which sessions are valid on an ongoing basis ("watchdog"), and automatically recruit more participants as needed to reach a target sample size.

## Post your experiment to a recruiting platform (e.g., Prolific)
**TODO: Add information about how to post an experiment to Prolific.**

# Contributors ✨

Thanks goes to these wonderful people ([emoji key](https://allcontributors.org/docs/en/emoji-key)):

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<table>
  <tr>
    <td align="center"><a href="http://ac.felixbinder.net"><img src="https://avatars.githubusercontent.com/u/24477285?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Felix Binder</b></sub></a><br /><a href="#maintenance-felixbinder" title="Maintenance">🚧</a> <a href="#mentoring-felixbinder" title="Mentoring">🧑‍🏫</a></td>
    <td align="center"><a href="http://yonifriedman.com"><img src="https://avatars.githubusercontent.com/u/26826815?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Yoni Friedman</b></sub></a><br /><a href="https://github.com/cogtoolslab/cognitive-ai-benchmarking/commits?author=yifr" title="Code">💻</a></td>
    <td align="center"><a href="https://github.com/yamins81"><img src="https://avatars.githubusercontent.com/u/231307?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Dan Yamins</b></sub></a><br /><a href="#eventOrganizing-yamins81" title="Event Organizing">📋</a></td>
    <td align="center"><a href="https://github.com/thomaspocon"><img src="https://avatars.githubusercontent.com/u/5657644?v=4?s=100" width="100px;" alt=""/><br /><sub><b>thomaspocon</b></sub></a><br /><a href="https://github.com/cogtoolslab/cognitive-ai-benchmarking/commits?author=thomaspocon" title="Code">💻</a></td>
    <td align="center"><a href="https://github.com/HaoliangWang"><img src="https://avatars.githubusercontent.com/u/26497509?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Haoliang Wang</b></sub></a><br /><a href="https://github.com/cogtoolslab/cognitive-ai-benchmarking/commits?author=HaoliangWang" title="Code">💻</a></td>
    <td align="center"><a href="https://github.com/justintheyang"><img src="https://avatars.githubusercontent.com/u/51468707?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Justin Yang</b></sub></a><br /><a href="https://github.com/cogtoolslab/cognitive-ai-benchmarking/commits?author=justintheyang" title="Code">💻</a></td>
    <td align="center"><a href="http://rxdhawkins.com"><img src="https://avatars.githubusercontent.com/u/5262024?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Robert Hawkins</b></sub></a><br /><a href="#tool-hawkrobe" title="Tools">🔧</a></td>
  </tr>
  <tr>
    <td align="center"><a href="https://cogtoolslab.github.io"><img src="https://avatars.githubusercontent.com/u/3938264?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Judy Fan</b></sub></a><br /><a href="#example-judithfan" title="Examples">💡</a></td>
  </tr>
</table>

<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->

This project follows the [all-contributors](https://github.com/all-contributors/all-contributors) specification. Contributions of any kind welcome!

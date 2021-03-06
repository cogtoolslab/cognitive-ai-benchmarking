# Cognitive-AI Benchmarking (CAB)

Project Template for Implementing Human Behavioral Experiments

<!-- ALL-CONTRIBUTORS-BADGE:START - Do not remove or modify this section -->

[![All Contributors](https://img.shields.io/badge/all_contributors-8-orange.svg?style=flat-square)](#contributors-)

<!-- ALL-CONTRIBUTORS-BADGE:END -->

1. [Overview](#overview)
2. [Implementing your experiment](#implementing-your-experiment)
3. [Installation](#installation)
4. [Database organization](#database-organization)
5. [Integration with experiment platforms](#integration-with-experiment-platforms)
6. [Contributors](#contributors-✨)

---

# Overview

The purpose of this repo is to provide a starting point for researchers planning to conduct a **Cognitive-AI Benchmarking (CAB)** project.
A CAB project will typically combine three elements: (1) stimulus generation; (2) human behavioral experiments; (3) analysis of behavioral data and comparison to model outputs.

This repository provides example code to setup and run the Object Contact Prediction (OCP) task on the dominoes scenario of the [Physion dataset](https://github.com/cogtoolslab/physics-benchmarking-neurips2021).

<!-- ## Repo organization

It contains several subdirectories that will contain standard components of the human behavioral experimental infrastructure that will support a variety of Cognitive-AI Benchmarking projects.

- `analysis`: contains notebooks and scripts to download and analyze behavioral data.
- `experiments`: contains the backend and frontend code to serve the experiments. The experiment specific wordings and task are defined here.
- `results`: This directory is meant to contain "intermediate" results of your computational/behavioral experiments. It should minimally contain two subdirectories: `csv` and `plots`. So `/results/csv/` is the path to use when saving out `csv` files containing tidy dataframes. And `/results/plots/` is the path to use when saving out `.pdf`/`.png` plots, a small number of which may be then polished and formatted for figures in a publication. _Important: Before pushing any csv files containing human behavioral data to a public code repository, triple check that these data files are properly anonymized. This means no Prolific ID's._ It is generally recommended that "raw" behavioral data be stored in a database rather than as part of this repo.
- `stimuli`: This directory is meant to contain any download/preprocessing scripts for data that are _inputs_ to this project. For many projects, these will be images. This is also where you want to place any scripts that will upload your data to our `stimuli` MongoDB database and any image data to Amazon S3 (so that it has a semi-permanent URL you can use to insert into your web experiment.) This is also where the scripts that determine the order the images or videos are presented in the experiment are located. -->

<!-- ## Different ways to use this repo

The examples in this repo have been organized in a modular fashion: you can either use  the entire stack or mix and match components of this stack with other tools if you prefer.

- Level 1: Example client-side JavaScript code for prototyping tasks quickly. Check out this [README](OCP_local/README.md).
- Level 2: Everything in Level 1, plus integration with node.js server for hosting your experiment and writing data to file without a database. See section entitled `Launch your experiment on a web server` below (see `app.js --local_storage`).
- Level 3: Everything in Level 2, plus integration with an already running mongodb server (`app.js`). -->

## The central concepts in this repo

When working on a project, you will oftentimes run many different experiments that are related to each other. We propose a way of thinking about these related experiments that makes keeping track of them easy.

At the top of the hierarchy is the **project**—for example _Physion_. This corresponds to a repository.

There are **datasets**—for example one particular scenario from the Physion dataset, eg. _dominoes_.

The questions that we might ask of these datasets might change: we might ask whether people can predict the outcome a physical interaction (Object Contact Prediction Task, OCP) or whether they find the same video interest. This is what we call a **task**.
Each task will usually have a different client front end in the `experiments/[task]` directory.

A particular **experiment** is a combination of a dataset and a task. For example, in this repository we show the `dominoes_OCP`. The convention for naming experiments is to use the dataset name followed by a \_ followed by the task name.
Which stimuli are passed to a task are usually determined by an URL parameter when the experiment is loaded in the user's browser.

For each experiment, there are small changes that the researcher might make, for example showing the videos for longer. These different versions of an experiment are called **iterations**.

| Concept        | Example      | Correspondence                                                |
| -------------- | ------------ | ------------------------------------------------------------- |
| **project**    | Physion      | Repository, name of database (`[proj]_input`,`[proj]_output`) |
| **dataset**    | dominoes     | _lives somewhere else_                                        |
| **task**       | OCP          | subfolders of `experiments/`                                  |
| **experiment** | dominoes_OCP | collection in `[proj]_input` and `[proj]_output` database     |
| **iteration**  | iteration_1  | field of record in database                                   |

# Implementing your experiment

To implement your own experiment, we suggest that you fork this repository and then adapt the example code provided to your purposes.

Preparing and running an iteration of your experiment is involves the following steps:

## 1. Prepare the videos or images—[`stimuli/`](stimuli/)

This repo assumes that you have already generated the images or videos that are being shown to the participants elsewhere.
Use [stimuli/upload_to_s3.py](stimuli/upload_to_s3.py) to upload your stimuli to S3 (for an usage example, see [stimuli/stimulus_setup_example.ipynb](stimuli/stimulus_setup_example.ipynb)).
<!-- Once you've done this, check out this [README](stimuli/README.md). -->

## 2. Design your task user interface—[`experiments/`](experiments/)

[`experiments/`](experiments/) contains the front end code for your experiment. A folder corresponds to a particular task (ie. [Object Contact Prediction Task](experiments/OCP/)).
Adapt the front end code in ['setup.js](experiments/OCP/js/setup.js) as well as the [jsPsych plugins](experiments/OCP/js/plugins/jspsych-video-overlay-button-response.js) to your particular task.
Check out this [README](experiments/README.md).

If you want to see demo of the front end code, launch [experiments/OCP_local/index.html](experiments/OCP_local/index.html) using a web browser from your local machine. 

## 3. Create session templates—[`stimuli/`](stimuli/)

Session templates are entries in the database that determine the precise order in which a participant will be shown the stimuli. These are created using [stimuli/stimuli/stimulus_setup_example.ipynb](stimuli/stimuli/stimulus_setup_example.ipynb), which also points to code to upload them to the MongoDB database that the experiment is served from.

<!-- - creating and uploading the experiment config (including projName, expName, iterationName)
- splitting and batching trials into sessions
- defining the criteria by which a session is valid. -->

## 4. Launch your experiment on a web server—[`app.js`](experiments/app.js)

[`app.js`](app.js) is the main entry point for your experiment. It is responsible for serving the experiment and handling the communication between the experiment and the participants.

To serve the experiment, run `node experiments/app.js`.

For development purposes, you can run `node experiments/app.js --local_storage` to run the experiment without access to a database. For more information, see this [README](experiments/README.md).

<!-- If you want to test your experiment on the server but don't want to worry about MongoDB, you can do the following:

First, create a directory in the `stimuli` folder specified by your database name and collection name (e.g. `stimuli/BACH/dominoes/`).

Then run the `generate_metadata.ipynb` jupyter notebook to generate your stimuli and save the is as a `.json` file in the directory you just created.

Next, run `node app.js --gameport PORT --local_store`. This needs to be ran from the experiments folder (ie. do `cd experiments` before running this).

This should be it! When you try out the experiment, your data will be saved on the server (as opposed to MongoDB) in the direcotry: `results/databaseName_output/collectionName.csv` (e.g. `results/BACH_output/dominoes.csv`) that you can check and help you debug. -->

## 5. Test your experiment

### Validate data input

Once you launch the experiment, test it out and verify that your stimuli are being read in properly.
Do this by checking the experiment in the browser.

### Validate data output

Next, you will want to verify that all trial metadata and response variables are being saved properly.
Use the analysis tools outlined in [step 7](<#7.-Fetch-and-analyze-the-behavioral-data—[`analysis/`](analysis/)>) to make sure that your data is being saved properly.

 <!-- Here is an [example notebook](analysis/analyze_BACH_dominoes.ipynb) you can adapt that guides you through the standard steps involved in fetching & analyzing your data, including constructing exploratory visualizations of response variables w.r.t. key axes of variation in your stimuli. -->

## 6. Post your experiment to a recruiting platform (e.g., Prolific)

Publish your experiment and watch the data roll in!

## 7. Fetch and analyze the behavioral data—[`analysis/`](analysis/)

[`analysis/`](analysis/) contains the code for downloading the behavioral data from the database.

# Installation

## Configuration

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

# Database organization

A mongoDB instance is ran by an organization (ie. your lab).
For each project, there are two databases: `[proj]_input` and `[proj]_output`.
In the `[proj]_input` database (for stimuli, what is shown to the user), each collection determines a set of stimuli in a certain order that can be shown to a user ("sesion template").
While running an experiment, this database will only be read from.

The data that is collected during an experiment goes into the `[proj]_output` database (for responses, which we get from the user).
There, each document corresponds to a single event that we care about, such as the user giving a single rating to a single video. Each document contains field that allow us to group it into experiments and iterations, etc.
While running an experiment, this database will only be written into.

# Integration with experiment platforms

## Prolific

- To post your experiment to Prolific, go to [https://www.prolific.co](https://www.prolific.co) and sign in using your lab/organization's account.
- Click the `New study` tab to create a new study for your experiment. Here are the steps:
- give your study a name (title field in the first line), remember that this name is visible to your participants, so please make this title easy to understand (don't use technical terms) and attractive (in order to recruit participants more efficiently).
- the internal name (second line) should include some identifier of the experiment, e.g. BACH_dominoes_pilot1, please do not use very generic names like pilot1 because the messaging system only displays the internal name, so it’s hard to know who to poke about messages without diving into the study details.
- To include the URL of your study, you can figure it out with the URL parameters (eg. `https://cogtoolslab.org:8881/dominoes/index.html?projName=BACH&expName=dominoes_OCP&iterName=it1`) and choose `I'll use URL parameters` for `How do you want to record Prolific IDs`, which will add additional URL parameters that tell us which participant is doing the study. Please run `app.js` and make sure that your study is accessible from the web.
- Prolific will suggest a completion code—this can be added into `setup.js` to automatically accept participants who have finished it in Prolific. So please select "I'll redirect them using a URL".
- For study cost, please pay attention to the minimum wage in your state.
- Then simply open the Prolific study and watch the responses roll in!

Be aware that the `Prolific_ID` uniquely identifies a single person and is therefore personally identifiable data and needs to be treated confidentially. It must not be made publicly available.

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
    <td align="center"><a href="https://github.com/thomaspocon"><img src="https://avatars.githubusercontent.com/u/5657644?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Thomas O'Connell</b></sub></a><br /><a href="https://github.com/cogtoolslab/cognitive-ai-benchmarking/commits?author=thomaspocon" title="Code">💻</a></td>
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

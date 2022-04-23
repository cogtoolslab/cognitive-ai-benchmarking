# The central concepts in this repo

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
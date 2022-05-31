`OCP` is an example version of the frontend code for the Object Contact Predition Task. It will need a webserver (`app.js`) to serve it (but it can be used to collect data).

Here, instead of a database, a local `.json` in `stimuli/` is used to read session templates and the results are saved into a `.csv` in `results/`.

To run the experiment, run `node app.js --gameport PORT` where PORT is the port number you want to use. If don't want to use the mongoDB backend, run `node app.js --gameport PORT --local_store`. 
Note that `--local_store` IS ONLY MEANT FOR TESTING PURPOSES—DO NOT USE THIS FOR LARGE SCALE DATA COLLLECTION.
This needs to be ran from the experiments folder (ie. run `cd experiments` before running this).
Only one version of `app.js` needs to be run for all experiments.

The experiments are opened by using `https://SERVER.TLD:PORT/experiment/index.html?projName=PROJ&expName=EXP&iterName=ITER` where `SERVER.TLD` is the server name, `PORT` is the port number, `PROJ` is the project name, `EXP` is the experiment name, and `ITER` is the iteration name.

For the example here, we are using the following values:
| Parameter | example value |
| --- | --- |
| project name | BACH |
| experiment name | domninoes_OCP |
| iteration_name | iteration_1 |

Here, we would use [https://cogtoolslab.org:8881/dominoes/index.html?projName=BACH&expName=dominoes_OCP&iterName=it1](https://cogtoolslab.org:8881/dominoes/index.html?projName=BACH&expName=dominoes_OCP&iterName=it1).

### Checklist for starting data collection on new online experiment
-[ ] Complete your OSF pre-registration worksheet
-[ ] Make sure that data is being saved correctly by drafting your analysis notebook
-[ ] Write instructions
-[ ] Figure out how subject payment is going to work
-[ ] Add consent form to appear before instructions

<!-- #### Using Amazon Mechanical Turk?
- Configure HIT settings using nosub: https://github.com/longouyang/nosub
- Test task out in MTurk Sandbox -->

### Using Prolific
The example study is set up to use Prolific. To submit it, run `app.js` and make sure that your study is accessible from the web.
Then, figure out the URL with the URL parameters (eg. `https://cogtoolslab.org:8881/dominoes/index.html?projName=BACH&expName=dominoes_OCP&iterName=it1`) and add this to a Prolific study.
Select "I'll use URL parameters" in the Prolific form, which will add additional URL parameters that tell us which participant is doing the study.
Prolific will suggest a completion code—this can be added into `setup.js:504` to automatically accept participants who have finished it in Prolific. 
Issue #62 aims to make this process easier.

Then simply open the Prolific study and watch the responses roll in.


## Want to just look at the experiment? 
You can navigate to `OCP_local` to locally run the experiment by clicking on `index.html`. The data is not stored, and the input is hardcoded—this is merely meant to be a quick way to see what the experiment looks like.

<!-- # How to build an experiment (Client Side)

By now, you should have:

- Uploaded stimuli where they need to be
- Saved all the trial data to a database somewhere

For the purposes of this tutorial, let's imagine that in your experiment, someone sees an image and either clicks a button that says "Red" if the image looks red, or "Blue" if the image looks blue. You should have all of that session templates saved somewhere, where - for each trial, you have the url of the image, and the true answer (whether it looks "Red" or "Blue").

## URL Structure

You can access different experiments based on the url structure. At a high level, the URL structure looks like:

```
<server_name>.com/<port number>:<experiment_folder>/index.html?projName=<PROJECT NAME>&expName=<EXPERIMENT NAME>&iterName=<ITERATION NAME>
```

The `projName`, `expName` and `iterName` are variables that will be used to retrieve your session template from MongoDB, and should correspond to the
database, collection name, and iteration name where that information is stored.

For example, let's say my project is titled: `color_study`. The specific experiment name I'm running is `color_estimate_natural_scenes`, and it's the
third iteration, so the iteration name is `v3`. On MongoDB, there should be a database called `color_study` with a collection titled `color_estimate_natural_scenes`. In that collection should be all the sessions you would like to serve (filtered by iteration name).

You should have your client side code set up in a folder titled `color_estimate` and an `index.html` file in that folder. Let's say you're running your experiment at colorlab.org on port 8888 - the url you would enter should be:

```
colorlab.org:8888/index.html?projName=color_study&expName=color_estimate_natural_scenes&iterName=v3
```

## Client side code

So you have a folder for your experiment, titled appropriately. Inside that folder you have an `index.html` file. That could be a very bare bones file (like the one in the `OCP` example. At a high level, it is your responsibility when writing the client side code to take in the experiment config / metadata and build your experiment from that. In the `OCP` example, the way this works is as follows:

There is a `setup.js` file in the `js` folder. `setup.js` is responsible for making a request for the session template and building a jsPsych timeline from that. Some key utility functions / code that you might want to keep around:

1. The URL params (lines: 1 - 11). If you want to add in URL parameters of your own, you can do that there.
2. The function `logTrialToDB` -- this takes in a dictionary and logs it to a database collection (with the same title as the location where the input stimulus is stored)
3. The function `launchExperiment` on line 45. This experiment makes the actual request to the server to fetch your experiment trials.

To actually build and run your experiment, you'll want to modify the function `buildAndRunExperiment` on line 75. Here you'll have access to the
session templates that you stored on MongoDB. If you have a jsPsych experiment, this is where you'll build your experiment timeline and launch it.
Make sure that each trial you add in has an `on_finish` function attached to it that calls `logTrialToDB`, otherwise you won't actually save any information. -->

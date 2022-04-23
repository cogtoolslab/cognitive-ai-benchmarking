# Quickly prototyping experiments with client-side JavaScript
Level 1: Example client-side JavaScript code for prototyping tasks quickly

-----

Typically, when designing an experiment, the first step we want to take after generating a study idea is to mock up a simple prototype of what that experiment would
look like without needing to implement server-side infrastructure. 

A common framework behavioral researchers use to implement web experiment tasks is jsPsych. [jsPsych](https://www.jspsych.org/6.3/) is a client-side 
JavaScript framework which abstracts away the experimental design parameters from the individual trial-by-trial experiment layout. We recommend going through the 
[tutorials](https://www.jspsych.org/6.3/tutorials/hello-world/) before writing your own local experiment.

This `experiments/OCP_local` directory is a serverless instantiation of a web experiment, which can be directly run on the local machine my simply opening `index.html`
into a web browser. With this serverless instantiation, one can directly modify the files in the directory, and refresh the browser, to automatically see the changes
to the experiment without needing to modify or reset anything on the server. 

A jsPsych experiment using this setup has a few main components:
- `index.html` is the file that is actually rendered on the web browser. We generally keep this file minimal, only including the function `launchExperiment()` on page load and file imports.
- `setup.js` builds the jsPsych timeline which defines which trials are shown with which stimuli, in what order. Changing this file generally does not change the display of the individual trial, but rather the display of the overall experimental session. 
- `js/plugins/` contains jsPsych plugins which handle the display of each individual trial type. Of these plugins, all are provided by jsPsych except for `jspsych-video-overlay-button-response.js`. Documentation for the other plugins, as well as minimal working examples, are provided in [jsPsych](https://www.jspsych.org/6.3/plugins/list-of-plugins/).
- `js/plugins/jspsych-video-overlay-button-response.js` is the only trial-level plugin we create ourselves. It handles the visuals and logic of each trial in our experiment.

A typical experiment one develops will contain a custom plugin, such as `jspsych-video-overlay-button-response.js`. Most of the code in this file is boilerplate code to work with JavaScript, as detailed [in this guide](https://www.jspsych.org/6.3/overview/plugins/#creating-a-new-plugin).
To change the trial's visuals and logic, you would update the [`plugin.trial`](https://github.com/cogtoolslab/cognitive-ai-benchmarking/blob/master/experiments/OCP_local/js/plugins/jspsych-video-overlay-button-response.js#L150) function. In these plugins, the structure of the HTML file is defined in the `XXX_html` variables. These html variables are rendered onto the web browser when we update the `display_element` variable. Finally, we can add dynamics to this webpage by adding listeners to the components of the `display_element`, such as in [line 265](https://github.com/cogtoolslab/cognitive-ai-benchmarking/blob/master/experiments/OCP_local/js/plugins/jspsych-video-overlay-button-response.js#L265).

Directory to contain experiment code (e.g., HTML/CSS/JavaScript) for this project.

To run the experiment, run `node app.js --gameport PORT` where PORT is the port number you want to use. If don't want to use the mongoDB backend (we recommend using the mongoDB backend), run `node app.js --gameport PORT --local_store`. 
This needs to be ran from the experiments folder (ie. do `cd experiments` before running this).
Only one version of `app.js` needs to be run for all experiments.

The experiments are called using `https://SERVER.TLD:PORT/experiment/index.html/

For the example here, we are using the following values:
| Parameter | example value |
| --- | --- |
| project name | BACH |
| experiment name | domninoes_OCP |
| iteration_name | iteration_1 |

For example, use [https://cogtoolslab.org:8881/dominoes/index.html?projName=BACH&expName=dominoes_OCP&iterName=it1](https://cogtoolslab.org:8881/dominoes/index.html?projName=BACH&expName=dominoes_OCP&iterName=it1).

### Checklist for starting data collection on new online experiment
- Complete your OSF pre-registration worksheet
- Make sure that data is being saved correctly by drafting your analysis notebook
- Write instructions
- Figure out how subject payment is going to work
- Add consent form to appear before instructions

#### Using Amazon Mechanical Turk?
- Configure HIT settings using nosub: https://github.com/longouyang/nosub
- Test task out in MTurk Sandbox

### Using Prolific
The example study is set up to use Prolific. To submit it, run `app.js` and make sure that your study is accessible from the web.
Then, figure out the URL with the URL parameters (eg. `https://cogtoolslab.org:8881/dominoes/index.html?projName=BACH&expName=dominoes_OCP&iterName=it1`) and add this to a Prolific study.
Select "I'll use URL parameters" in the Prolific form, which will add additional URL parameters that tell us which participant is doing the study.
Prolific will suggest a completion code—this can be added into `setup.js:504` to automatically accept participants who have finished it in Prolific. 
Issue #62 aims to make this process easier.

Then simply open the Prolific study and watch the responses roll in.


### Want to just look at the experiment? 
You can navigate to `dominoes_local` to locally run the experiment by clicking on `index.html`
